#!/bin/bash
set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SCRIPT_DIR/scripts/create_pr.sh"
FAKE_BIN="$TEST_DIR/bin"
CALL_LOG="$TEST_DIR/gh-calls.log"
CAPTURED_BODY="$TEST_DIR/pr-body.md"
DELIVERY_BODY="$TEST_DIR/delivery.md"

mkdir -p "$FAKE_BIN"
cat > "$DELIVERY_BODY" <<'EOF'
### Summary
Implemented the story.

### Acceptance Criteria Evidence
- Criterion one: covered.

### Verification
- Tests passed.

### Not Verified
- None.
EOF

cat > "$FAKE_BIN/git" <<'EOF'
#!/bin/sh
if [ "$1" = "branch" ] && [ "$2" = "--show-current" ]; then
  printf '%s\n' "${GIT_BRANCH:-story/demo-demo-001-a1}"
  exit 0
fi
if [ "$1" = "rev-parse" ] && [ "$2" = "HEAD" ]; then
  printf '%s\n' "${GIT_LOCAL_HEAD:-1111111111111111111111111111111111111111}"
  exit 0
fi
if [ "$1" = "ls-remote" ]; then
  if [ "${GIT_REMOTE_MISSING:-false}" = "true" ]; then
    exit 2
  fi
  printf '%s\t%s\n' \
    "${GIT_REMOTE_HEAD:-1111111111111111111111111111111111111111}" \
    "refs/heads/${GIT_BRANCH:-story/demo-demo-001-a1}"
  exit 0
fi
echo "Unexpected git invocation: $*" >&2
exit 1
EOF

cat > "$FAKE_BIN/gh" <<'EOF'
#!/bin/sh
set -eu
if [ "$1" = "repo" ] && [ "$2" = "view" ]; then
  printf '%s\n' "main"
  exit 0
fi
if [ "$1" = "pr" ] && [ "$2" = "create" ]; then
  previous=""
  for argument in "$@"; do
    if [ "$previous" = "--body-file" ]; then
      cp "$argument" "$GH_CAPTURED_BODY"
    fi
    previous=$argument
  done
  printf '%s\n' "$*" > "$GH_CALL_LOG"
  printf '%s\n' "https://github.example/pull/42"
  exit 0
fi
echo "Unexpected gh invocation: $*" >&2
exit 1
EOF
chmod +x "$FAKE_BIN/git" "$FAKE_BIN/gh"

export GH_CALL_LOG="$CALL_LOG"
export GH_CAPTURED_BODY="$CAPTURED_BODY"
export PATH="$FAKE_BIN:$PATH"

DOCUMENT_SHA=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
STORY_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
"$SCRIPT" 17 "DEMO-001: Deliver" "$DELIVERY_BODY" \
  DEMO-001 docs/design/demo.md "$DOCUMENT_SHA" "$STORY_SHA" \
  demo-demo-001-a1 none >/dev/null

grep -Fq -- "--base main --head story/demo-demo-001-a1" "$CALL_LOG"
grep -Fq "<!-- feature-delivery:design=docs/design/demo.md -->" "$CAPTURED_BODY"
grep -Fq "<!-- feature-delivery:story=DEMO-001 -->" "$CAPTURED_BODY"
grep -Fq "<!-- feature-delivery:design-revision=$DOCUMENT_SHA -->" "$CAPTURED_BODY"
grep -Fq "<!-- feature-delivery:story-revision=$STORY_SHA -->" "$CAPTURED_BODY"
grep -Fq "<!-- feature-delivery:delivery-id=demo-demo-001-a1 -->" "$CAPTURED_BODY"
grep -Fq "<!-- feature-delivery:supersedes=none -->" "$CAPTURED_BODY"
grep -Fq "### Verification" "$CAPTURED_BODY"

export GIT_REMOTE_HEAD=2222222222222222222222222222222222222222
if "$SCRIPT" 17 "DEMO-001" "$DELIVERY_BODY" \
  DEMO-001 docs/design/demo.md "$DOCUMENT_SHA" "$STORY_SHA" \
  demo-demo-001-a1 none >/dev/null 2>&1; then
  echo "Expected a stale remote story branch to be rejected." >&2
  exit 1
fi
unset GIT_REMOTE_HEAD

export GIT_BRANCH=story/prefix-demo-demo-001-a1-suffix
if "$SCRIPT" 17 "DEMO-001" "$DELIVERY_BODY" \
  DEMO-001 docs/design/demo.md "$DOCUMENT_SHA" "$STORY_SHA" \
  demo-demo-001-a1 none >/dev/null 2>&1; then
  echo "Expected a non-canonical branch name to be rejected." >&2
  exit 1
fi
unset GIT_BRANCH

if "$SCRIPT" 17 "DEMO-001" "summary" >/dev/null 2>&1; then
  echo "Expected markerless legacy invocation to be rejected." >&2
  exit 1
fi

printf '%s\n' '<!-- feature-delivery:story=EVIL-001 -->' >> "$DELIVERY_BODY"
if "$SCRIPT" 17 "DEMO-001" "$DELIVERY_BODY" \
  DEMO-001 docs/design/demo.md "$DOCUMENT_SHA" "$STORY_SHA" \
  demo-demo-001-a2 42 >/dev/null 2>&1; then
  echo "Expected conflicting body markers to be rejected." >&2
  exit 1
fi

echo "create_pr tests passed"
