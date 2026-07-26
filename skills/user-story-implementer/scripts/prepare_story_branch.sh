#!/bin/bash
# Usage: prepare_story_branch.sh "<new-branch>" [dependency-merge-oid...]

set -euo pipefail

NEW_BRANCH=${1:-}
if [[ -z "$NEW_BRANCH" ]]; then
  echo "Usage: $0 <new-branch> [dependency-merge-oid...]" >&2
  exit 2
fi
shift

if [[ -n "$(git status --porcelain=v1 --untracked-files=all)" ]]; then
  echo "Worktree is dirty; refusing to switch or create branches." >&2
  exit 1
fi

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
if [[ -z "$DEFAULT_BRANCH" ]]; then
  echo "Could not resolve the repository default branch." >&2
  exit 1
fi

git switch "$DEFAULT_BRANCH"
git fetch origin "$DEFAULT_BRANCH"

COUNTS=$(git rev-list --left-right --count "$DEFAULT_BRANCH...origin/$DEFAULT_BRANCH")
LOCAL_AHEAD=${COUNTS%%[[:space:]]*}
REMOTE_AHEAD=${COUNTS##*[[:space:]]}
if [[ "$LOCAL_AHEAD" != "0" ]]; then
  echo "Local $DEFAULT_BRANCH is ahead or divergent; refusing to rewrite it." >&2
  exit 1
fi
if [[ "$REMOTE_AHEAD" != "0" ]]; then
  git merge --ff-only "origin/$DEFAULT_BRANCH"
fi
if [[ "$(git rev-parse "$DEFAULT_BRANCH")" != "$(git rev-parse "origin/$DEFAULT_BRANCH")" ]]; then
  echo "Default branch did not synchronize exactly with origin/$DEFAULT_BRANCH." >&2
  exit 1
fi

for DEPENDENCY_OID in "$@"; do
  if ! git cat-file -e "$DEPENDENCY_OID^{commit}" 2>/dev/null; then
    echo "Dependency commit is unavailable locally: $DEPENDENCY_OID" >&2
    exit 1
  fi
  if ! git merge-base --is-ancestor "$DEPENDENCY_OID" "$DEFAULT_BRANCH"; then
    echo "Dependency commit is not present on $DEFAULT_BRANCH: $DEPENDENCY_OID" >&2
    exit 1
  fi
done

if git show-ref --verify --quiet "refs/heads/$NEW_BRANCH" ||
   git show-ref --verify --quiet "refs/remotes/origin/$NEW_BRANCH"; then
  echo "Branch already exists; reconcile the matching PR instead: $NEW_BRANCH" >&2
  exit 1
fi

git switch -c "$NEW_BRANCH"
echo "Default Branch: $DEFAULT_BRANCH"
echo "Base Commit: $(git rev-parse HEAD)"
echo "Created Branch: $NEW_BRANCH"
