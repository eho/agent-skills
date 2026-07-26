#!/bin/bash
set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SCRIPT_DIR/scripts/approve_or_merge_pr.sh"
FAKE_BIN="$TEST_DIR/bin"
CALL_LOG="$TEST_DIR/gh-calls.log"
HEAD_COUNT="$TEST_DIR/head-count"
REVIEW_FILE="$TEST_DIR/review.txt"

mkdir -p "$FAKE_BIN"
printf '%s\n' "Verified acceptance criteria." > "$REVIEW_FILE"

cat > "$FAKE_BIN/gh" <<'EOF'
#!/bin/sh
set -eu

if [ "$1" = "pr" ] && [ "$2" = "view" ]; then
  field=""
  previous=""
  for argument in "$@"; do
    if [ "$previous" = "--json" ]; then
      field=$argument
      break
    fi
    previous=$argument
  done
  case "$field" in
    state) printf '%s\n' "${GH_PR_STATE:-OPEN}" ;;
    isDraft) printf '%s\n' "${GH_PR_DRAFT:-false}" ;;
    headRefOid)
      count=0
      [ ! -f "$GH_HEAD_COUNT" ] || count=$(cat "$GH_HEAD_COUNT")
      count=$((count + 1))
      printf '%s\n' "$count" > "$GH_HEAD_COUNT"
      if [ "${GH_CHANGE_HEAD_AFTER_REVIEW:-false}" = "true" ] && [ "$count" -gt 1 ]; then
        printf '%s\n' "changed-head"
      else
        printf '%s\n' "${GH_PR_HEAD:-expected-head}"
      fi
      ;;
    baseRefName) printf '%s\n' "${GH_PR_BASE:-main}" ;;
    statusCheckRollup) printf '%b\n' "${GH_CHECK_LINES:-ci\tSUCCESS\t}" ;;
    mergeable) printf '%s\n' "${GH_MERGEABLE:-MERGEABLE}" ;;
    mergeStateStatus) printf '%s\n' "${GH_MERGE_STATE:-CLEAN}" ;;
    author) printf '%s\n' "${GH_PR_AUTHOR:-test-user}" ;;
    reviewDecision) printf '%s\n' "${GH_REVIEW_DECISION:-APPROVED}" ;;
    mergedAt) printf '%s\n' "${GH_MERGED_AT:-}" ;;
    *) echo "Unexpected pr view field: $field" >&2; exit 1 ;;
  esac
  exit 0
fi

if [ "$1" = "repo" ] && [ "$2" = "view" ]; then
  case "$*" in
    *defaultBranchRef*) printf '%s\n' "main" ;;
    *nameWithOwner*) printf '%s\n' "owner/repo" ;;
    *MergeAllowed*) printf '%s\n' "${GH_MERGE_METHOD_ALLOWED:-true}" ;;
    *) echo "Unexpected repo view: $*" >&2; exit 1 ;;
  esac
  exit 0
fi

if [ "$1" = "api" ] && [ "$2" = "user" ]; then
  printf '%s\n' "test-user"
  exit 0
fi

if [ "$1" = "api" ] && [ "$2" = "graphql" ]; then
  printf '%s\n' "${GH_QUEUE_STATE:-QUEUED}"
  exit 0
fi

if [ "$1" = "api" ] && [ "$2" = "--method" ] && [ "$3" = "POST" ]; then
  printf '%s\n' "$*" >> "$GH_CALL_LOG"
  exit 0
fi

if [ "$1" = "api" ] &&
   { [ "$2" = "repos/owner/repo/rules/branches/main" ] ||
     [ "$2" = "repos/owner/repo/rules/branches/release%2F1" ]; }; then
  case "$*" in
    *required_status_checks*) printf '%s\n' "${GH_POLICY_REQUIRED:-}" ;;
    *merge_queue*) printf '%s\n' "${GH_QUEUE_RULES:-1}" ;;
    *) echo "Unexpected branch rules query: $*" >&2; exit 1 ;;
  esac
  exit 0
fi

if [ "$1" = "api" ] &&
   { [ "$2" = "repos/owner/repo/branches/main/protection/required_status_checks" ] ||
     [ "$2" = "repos/owner/repo/branches/release%2F1/protection/required_status_checks" ]; }; then
  printf '%b\n' "${GH_CLASSIC_REQUIRED:-}"
  exit 0
fi

printf '%s\n' "$*" >> "$GH_CALL_LOG"
EOF
chmod +x "$FAKE_BIN/gh"

export GH_CALL_LOG="$CALL_LOG"
export GH_HEAD_COUNT="$HEAD_COUNT"
export PATH="$FAKE_BIN:$PATH"

reset_state() {
  : > "$CALL_LOG"
  rm -f "$HEAD_COUNT"
  unset GH_PR_STATE GH_PR_DRAFT GH_PR_HEAD GH_PR_BASE GH_CHECK_LINES
  unset GH_MERGEABLE GH_MERGE_STATE GH_PR_AUTHOR GH_REVIEW_DECISION
  unset GH_MERGED_AT GH_CHANGE_HEAD_AFTER_REVIEW
  unset GH_MERGE_METHOD_ALLOWED GH_QUEUE_STATE GH_QUEUE_RULES GH_POLICY_REQUIRED
  unset GH_CLASSIC_REQUIRED
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
    echo "Expected arguments or state to be rejected: $*" >&2
    exit 1
  fi
}

reset_state
"$SCRIPT" 42 "$REVIEW_FILE" --comment-only --expected-head expected-head
assert_log_contains "commit_id=expected-head"
assert_log_contains "event=COMMENT"

reset_state
export GH_PR_AUTHOR=other-user
"$SCRIPT" 42 "$REVIEW_FILE" --approve --expected-head expected-head --required-check ci
assert_log_contains "event=APPROVE"
assert_log_contains "commit_id=expected-head"

reset_state
export GH_PR_DRAFT=true
assert_rejected --approve --expected-head expected-head --required-check ci

reset_state
export GH_CHECK_LINES='ci\tFAILURE'
assert_rejected --approve --expected-head expected-head --required-check ci

reset_state
export GH_PR_AUTHOR=other-user
assert_rejected --approve --expected-head expected-head --required-check missing

reset_state
export GH_PR_AUTHOR=other-user
export GH_POLICY_REQUIRED=ci
assert_rejected --approve --expected-head expected-head --no-required-checks

reset_state
export GH_PR_AUTHOR=other-user
export GH_POLICY_REQUIRED=ci
export GH_CHECK_LINES='other\tSUCCESS\t'
assert_rejected --approve --expected-head expected-head --required-check other

reset_state
export GH_PR_AUTHOR=other-user
export GH_CLASSIC_REQUIRED='classic-ci\t321'
export GH_CHECK_LINES='classic-ci\tSUCCESS\t321'
assert_rejected --approve --expected-head expected-head --no-required-checks
"$SCRIPT" 42 "$REVIEW_FILE" --approve --expected-head expected-head \
  --required-check classic-ci@321

reset_state
export GH_PR_AUTHOR=other-user
export GH_CHANGE_HEAD_AFTER_REVIEW=true
assert_rejected --approve --expected-head expected-head --required-check ci
assert_log_contains "event=APPROVE"
assert_log_contains "commit_id=expected-head"

reset_state
export GH_PR_AUTHOR=other-user
export GH_CHANGE_HEAD_AFTER_REVIEW=true
assert_rejected --merge --expected-head expected-head --merge-method squash --required-check ci
assert_log_contains "event=APPROVE"
if grep -Fq "pr merge" "$CALL_LOG"; then
  echo "Head-change rejection must happen before merge." >&2
  exit 1
fi

reset_state
export GH_MERGED_AT=2026-07-26T00:00:00Z
"$SCRIPT" 42 "$REVIEW_FILE" --merge --expected-head expected-head \
  --merge-method rebase --allow-self-merge --required-check ci
assert_log_contains "pr merge 42 --rebase --match-head-commit expected-head"

reset_state
export GH_MERGE_STATE=BLOCKED
"$SCRIPT" 42 "$REVIEW_FILE" --merge --expected-head expected-head \
  --queue --allow-self-merge --required-check ci
assert_log_contains "pr merge 42 --match-head-commit expected-head"

reset_state
export GH_MERGE_STATE=BLOCKED
export GH_QUEUE_RULES=0
assert_rejected --merge --expected-head expected-head \
  --queue --allow-self-merge --required-check ci

reset_state
export GH_PR_AUTHOR=other-user
export GH_POLICY_REQUIRED='ci\t123'
export GH_CHECK_LINES='ci\tSUCCESS\t999'
assert_rejected --approve --expected-head expected-head --required-check ci@123

reset_state
export GH_PR_AUTHOR=other-user
export GH_PR_BASE=release/1
"$SCRIPT" 42 "$REVIEW_FILE" --approve --expected-head expected-head \
  --expected-base release/1 --required-check ci
assert_log_contains "event=APPROVE"

reset_state
assert_rejected --comment-only
assert_rejected --comment-only --approve --expected-head expected-head
assert_rejected --merge --expected-head expected-head
assert_rejected --merge --expected-head expected-head --queue --merge-method squash --required-check ci
assert_rejected --merge-method squash --expected-head expected-head
assert_rejected --delete-branch --expected-head expected-head
assert_rejected --queue --expected-head expected-head
assert_rejected --approve --expected-head expected-head --required-check ci --no-required-checks

echo "approve_or_merge_pr tests passed"
