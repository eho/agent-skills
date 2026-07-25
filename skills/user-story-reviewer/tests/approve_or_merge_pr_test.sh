#!/bin/bash
set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SCRIPT_DIR/scripts/approve_or_merge_pr.sh"
FAKE_BIN="$TEST_DIR/bin"
CALL_LOG="$TEST_DIR/gh-calls.log"
REVIEW_FILE="$TEST_DIR/review.txt"

mkdir -p "$FAKE_BIN"
printf '%s\n' "Verified test acceptance criteria." > "$REVIEW_FILE"

cat > "$FAKE_BIN/gh" <<'EOF'
#!/bin/sh
if [ "$1" = "pr" ] && [ "$2" = "view" ]; then
  printf '%s\n' "test-user"
  exit 0
fi
if [ "$1" = "api" ] && [ "$2" = "user" ]; then
  printf '%s\n' "test-user"
  exit 0
fi
printf '%s\n' "$*" >> "$GH_CALL_LOG"
EOF
chmod +x "$FAKE_BIN/gh"

export GH_CALL_LOG="$CALL_LOG"
export PATH="$FAKE_BIN:$PATH"

reset_log() {
  : > "$CALL_LOG"
}

assert_log_contains() {
  if ! grep -Fq "$1" "$CALL_LOG"; then
    echo "Expected gh call containing: $1" >&2
    cat "$CALL_LOG" >&2
    exit 1
  fi
}

assert_rejected() {
  if "$SCRIPT" 42 "$REVIEW_FILE" "$@" >/dev/null 2>&1; then
    echo "Expected arguments to be rejected: $*" >&2
    exit 1
  fi
}

reset_log
"$SCRIPT" 42 "$REVIEW_FILE" --comment-only
assert_log_contains "pr review 42 --comment"

reset_log
"$SCRIPT" 42 "$REVIEW_FILE" --merge --queue
assert_log_contains "pr review 42 --comment"
assert_log_contains "pr merge 42"

reset_log
"$SCRIPT" 42 "$REVIEW_FILE" --merge --merge-method rebase --auto
assert_log_contains "pr merge 42 --rebase --auto"

assert_rejected --comment-only --merge --merge-method squash
assert_rejected --merge --comment-only
assert_rejected --merge-method squash
assert_rejected --auto
assert_rejected --delete-branch
assert_rejected --queue
assert_rejected --merge
assert_rejected --merge --queue --merge-method squash

echo "approve_or_merge_pr tests passed"
