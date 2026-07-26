#!/bin/bash
set -euo pipefail

TEST_DIR=$(mktemp -d)
trap 'rm -rf "$TEST_DIR"' EXIT

ORIGIN="$TEST_DIR/origin.git"
SEED="$TEST_DIR/seed"
WORK="$TEST_DIR/work"
FAKE_BIN="$TEST_DIR/bin"
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
SCRIPT="$SCRIPT_DIR/scripts/prepare_story_branch.sh"
REAL_GIT=$(command -v git)

git init --bare "$ORIGIN" >/dev/null
git init -b main "$SEED" >/dev/null
git -C "$SEED" config user.name "Test User"
git -C "$SEED" config user.email "test@example.com"
printf '%s\n' "base" > "$SEED/base.txt"
git -C "$SEED" add base.txt
git -C "$SEED" commit -m "base" >/dev/null
git -C "$SEED" remote add origin "$ORIGIN"
git -C "$SEED" push -u origin main >/dev/null
git --git-dir "$ORIGIN" symbolic-ref HEAD refs/heads/main
git clone "$ORIGIN" "$WORK" >/dev/null

mkdir -p "$FAKE_BIN"
cat > "$FAKE_BIN/gh" <<'EOF'
#!/bin/sh
if [ "$1" = "repo" ] && [ "$2" = "view" ]; then
  printf '%s\n' "main"
  exit 0
fi
if [ "$1" = "pr" ] && [ "$2" = "view" ]; then
  printf 'MERGED\t2026-07-26T00:00:00Z\t%s\tmain\n' "$GH_DEPENDENCY_SHA"
  exit 0
fi
echo "Unexpected gh invocation: $*" >&2
exit 1
EOF
chmod +x "$FAKE_BIN/gh"

cat > "$FAKE_BIN/git" <<'EOF'
#!/bin/sh
if [ "${GIT_LS_REMOTE_FAILURE:-false}" = "true" ] &&
   [ "$1" = "ls-remote" ]; then
  exit 128
fi
exec "$REAL_GIT" "$@"
EOF
chmod +x "$FAKE_BIN/git"

export GH_DEPENDENCY_SHA
export REAL_GIT
GH_DEPENDENCY_SHA=$(git -C "$WORK" rev-parse refs/remotes/origin/main)

(
  cd "$WORK"
  PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-001 --dependency-pr 7 >/dev/null
  test "$(git branch --show-current)" = "story/demo-001"
  test "$(git rev-parse HEAD)" = "$(git rev-parse refs/remotes/origin/main)"
)

git -C "$WORK" switch main >/dev/null
git -C "$SEED" push origin main:refs/heads/story/demo-remote >/dev/null
if (
  cd "$WORK"
  PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-remote >/dev/null 2>&1
); then
  echo "Expected an existing remote story branch to be rejected." >&2
  exit 1
fi

(
  cd "$WORK"
  output=$(PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-remote \
    --resume --worktree "$TEST_DIR/resumed")
  test "$(git -C "$TEST_DIR/resumed" branch --show-current)" = "story/demo-remote"
  printf '%s\n' "$output" | grep -Fq "Current default SHA:"
  printf '%s\n' "$output" | grep -Fq "Start SHA: recover from"
)

printf '%s\n' "remote update" >> "$SEED/base.txt"
git -C "$SEED" add base.txt
git -C "$SEED" commit -m "remote story update" >/dev/null
git -C "$SEED" push origin HEAD:refs/heads/story/demo-remote >/dev/null
if (
  cd "$WORK"
  PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-remote --resume >/dev/null 2>&1
); then
  echo "Expected behind/divergent local story branch to be preserved and rejected." >&2
  exit 1
fi

git -C "$WORK" checkout --detach main >/dev/null
if (
  cd "$WORK"
  PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-detached >/dev/null 2>&1
); then
  echo "Expected detached HEAD to be rejected." >&2
  exit 1
fi
git -C "$WORK" switch main >/dev/null

if (
  cd "$WORK"
  GIT_LS_REMOTE_FAILURE=true PATH="$FAKE_BIN:$PATH" \
    "$SCRIPT" story/lookup-unknown >/dev/null 2>&1
); then
  echo "Expected a remote lookup failure to fail closed." >&2
  exit 1
fi

printf '%s\n' "dirty" > "$WORK/dirty.txt"
if (
  cd "$WORK"
  PATH="$FAKE_BIN:$PATH" "$SCRIPT" story/demo-002 >/dev/null 2>&1
); then
  echo "Expected dirty worktree to be rejected." >&2
  exit 1
fi

echo "prepare_story_branch tests passed"
