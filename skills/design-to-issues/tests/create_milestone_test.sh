#!/bin/bash
set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SCRIPT_DIR/scripts/create_milestone.sh"
FAKE_BIN="$TEST_DIR/bin"
CALL_LOG="$TEST_DIR/gh-calls.log"

mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/gh" <<'EOF'
#!/bin/sh
set -eu
printf '%s\n' "$*" >> "$GH_CALL_LOG"
if [ "$1" = "repo" ] && [ "$2" = "view" ]; then
  printf '%s\n' "owner/repo"
  exit 0
fi
if [ "$1" = "api" ] && [ "$2" = "--paginate" ]; then
  if [ "${GH_LOOKUP_FAILURE:-false}" = "true" ]; then
    exit 1
  fi
  if [ "${GH_EXISTING_MILESTONE:-false}" = "true" ]; then
    printf '37\tclosed\tRelease 1\n'
  fi
  exit 0
fi
if [ "$1" = "api" ] && [ "$2" = "--method" ] && [ "$3" = "PATCH" ]; then
  exit 0
fi
if [ "$1" = "api" ] && [ "$2" = "repos/owner/repo/milestones" ]; then
  exit 0
fi
echo "Unexpected gh invocation: $*" >&2
exit 1
EOF
chmod +x "$FAKE_BIN/gh"

export GH_CALL_LOG="$CALL_LOG"
export PATH="$FAKE_BIN:$PATH"

export GH_EXISTING_MILESTONE=true
if "$SCRIPT" "Release 1" >/dev/null 2>&1; then
  echo "Expected closed milestone to require explicit reopen policy." >&2
  exit 1
fi
"$SCRIPT" "Release 1" --reopen >/dev/null
grep -Fq -- "api --paginate repos/owner/repo/milestones?state=all&per_page=100" "$CALL_LOG"
grep -Fq -- "api --method PATCH repos/owner/repo/milestones/37 -f state=open" "$CALL_LOG"

: > "$CALL_LOG"
export GH_EXISTING_MILESTONE=false
"$SCRIPT" "Release 2" >/dev/null
grep -Fq -- "api repos/owner/repo/milestones -f title=Release 2" "$CALL_LOG"

export GH_LOOKUP_FAILURE=true
if "$SCRIPT" "Release 3" >/dev/null 2>&1; then
  echo "Expected milestone lookup failure to stop before creation." >&2
  exit 1
fi
if grep -Fq "title=Release 3" "$CALL_LOG"; then
  echo "Lookup failure must not fall through to creation." >&2
  exit 1
fi

echo "create_milestone tests passed"
