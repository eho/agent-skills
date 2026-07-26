#!/bin/bash
# Usage:
#   prepare_story_branch.sh <branch> [--resume] [--worktree <path>] \
#     [--dependency-pr <number>]...

set -euo pipefail

BRANCH=${1:-}
if [[ -z "$BRANCH" ]]; then
  echo "Usage: $0 <branch> [--resume] [--worktree <path>] [--dependency-pr <number>]..." >&2
  exit 64
fi
shift

WORKTREE_PATH=""
RESUME=false
DEPENDENCY_PRS=()
DEPENDENCY_COUNT=0
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --resume)
      RESUME=true
      shift
      ;;
    --worktree)
      if [[ "$#" -lt 2 || -z "$2" ]]; then
        echo "Error: --worktree requires a path." >&2
        exit 64
      fi
      WORKTREE_PATH=$2
      shift 2
      ;;
    --dependency-pr)
      if [[ "$#" -lt 2 || ! "$2" =~ ^[0-9]+$ ]]; then
        echo "Error: --dependency-pr requires a numeric PR number." >&2
        exit 64
      fi
      DEPENDENCY_PRS+=("$2")
      DEPENDENCY_COUNT=$((DEPENDENCY_COUNT + 1))
      shift 2
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 64
      ;;
  esac
done

if ! git check-ref-format --branch "$BRANCH" > /dev/null 2>&1; then
  echo "Invalid branch name: $BRANCH" >&2
  exit 64
fi

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
REMOTE_REF="refs/remotes/origin/$DEFAULT_BRANCH"
git fetch origin "+refs/heads/$DEFAULT_BRANCH:$REMOTE_REF"

LOCAL_EXISTS=false
REMOTE_EXISTS=false
git show-ref --verify --quiet "refs/heads/$BRANCH" && LOCAL_EXISTS=true
set +e
git ls-remote --exit-code --heads origin "refs/heads/$BRANCH" > /dev/null 2>&1
remote_lookup_status=$?
set -e
if [[ "$remote_lookup_status" -eq 0 ]]; then
  REMOTE_EXISTS=true
  git fetch origin "+refs/heads/$BRANCH:refs/remotes/origin/$BRANCH"
elif [[ "$remote_lookup_status" -ne 2 ]]; then
  echo "Could not determine whether remote story branch exists: $BRANCH" >&2
  exit 3
fi

if [[ "$RESUME" == false ]] &&
   { [[ "$LOCAL_EXISTS" == true ]] || [[ "$REMOTE_EXISTS" == true ]]; }; then
  echo "Existing story branch found; resume it instead of creating a duplicate: $BRANCH" >&2
  exit 3
fi

if [[ "$RESUME" == true && "$LOCAL_EXISTS" == false && "$REMOTE_EXISTS" == false ]]; then
  echo "Cannot resume missing story branch: $BRANCH" >&2
  exit 3
fi

if [[ "$RESUME" == true && "$LOCAL_EXISTS" == true && "$REMOTE_EXISTS" == true ]]; then
  divergence=$(git rev-list --left-right --count \
    "refs/heads/$BRANCH...refs/remotes/origin/$BRANCH")
  IFS=$'\t' read -r ahead behind <<< "$divergence"
  if [[ "$behind" -gt 0 ]]; then
    echo "Preserving local/remote branch divergence for $BRANCH (ahead=$ahead behind=$behind); reconcile explicitly before resuming." >&2
    exit 5
  fi
fi

TARGET_REF="$REMOTE_REF"
if [[ "$RESUME" == true ]]; then
  if [[ "$LOCAL_EXISTS" == true ]]; then
    TARGET_REF="refs/heads/$BRANCH"
  else
    TARGET_REF="refs/remotes/origin/$BRANCH"
  fi
fi

if [[ "$DEPENDENCY_COUNT" -gt 0 ]]; then
  for pr_number in "${DEPENDENCY_PRS[@]}"; do
    dependency=$(
      gh pr view "$pr_number" \
        --json state,mergedAt,mergeCommit,baseRefName \
        --jq '[.state, (.mergedAt // ""), (.mergeCommit.oid // ""), .baseRefName] | @tsv'
    )
    IFS=$'\t' read -r state merged_at merge_sha base_branch <<< "$dependency"
    if [[ "$state" != "MERGED" || -z "$merged_at" || -z "$merge_sha" ]]; then
      echo "Dependency PR #$pr_number is not verifiably merged." >&2
      exit 4
    fi
    if [[ "$base_branch" != "$DEFAULT_BRANCH" ]]; then
      echo "Dependency PR #$pr_number did not merge to $DEFAULT_BRANCH." >&2
      exit 4
    fi
    if ! git merge-base --is-ancestor "$merge_sha" "$TARGET_REF"; then
      echo "Dependency merge $merge_sha from PR #$pr_number is absent from $TARGET_REF." >&2
      exit 4
    fi
    if ! git merge-base --is-ancestor "$merge_sha" "$REMOTE_REF"; then
      echo "Dependency merge $merge_sha from PR #$pr_number is absent from current $DEFAULT_BRANCH." >&2
      exit 4
    fi
    echo "Dependency PR #$pr_number merge SHA: $merge_sha"
  done
fi

BASE_SHA=$(git rev-parse "$REMOTE_REF")
BRANCH_WORKTREE=""
current_worktree=""
while IFS=' ' read -r key value; do
  case "$key" in
    worktree) current_worktree=$value ;;
    branch)
      if [[ "$value" == "refs/heads/$BRANCH" ]]; then
        BRANCH_WORKTREE=$current_worktree
      fi
      ;;
  esac
done < <(git worktree list --porcelain)

if [[ "$RESUME" == true && -n "$BRANCH_WORKTREE" ]]; then
  echo "Story branch is already owned by worktree: $BRANCH_WORKTREE"
elif [[ -n "$WORKTREE_PATH" ]]; then
  if [[ -e "$WORKTREE_PATH" ]]; then
    echo "Refusing to overwrite existing worktree path: $WORKTREE_PATH" >&2
    exit 5
  fi
  if [[ "$RESUME" == true && "$LOCAL_EXISTS" == true ]]; then
    git worktree add "$WORKTREE_PATH" "$BRANCH"
  elif [[ "$RESUME" == true ]]; then
    git worktree add --track -b "$BRANCH" "$WORKTREE_PATH" "refs/remotes/origin/$BRANCH"
  else
    git worktree add -b "$BRANCH" "$WORKTREE_PATH" "$REMOTE_REF"
  fi
  echo "Prepared story worktree: $WORKTREE_PATH"
else
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Refusing to change branches in a dirty worktree; use --worktree with a new path." >&2
    exit 5
  fi
  CURRENT_BRANCH=$(git branch --show-current)
  if [[ -z "$CURRENT_BRANCH" ]]; then
    echo "Refusing to leave detached HEAD; use --worktree with a new path." >&2
    exit 5
  fi
  if [[ "$CURRENT_BRANCH" != "$DEFAULT_BRANCH" && "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    echo "Refusing to leave active branch $CURRENT_BRANCH; use --worktree with a new path." >&2
    exit 5
  fi
  if [[ "$RESUME" == false ]]; then
    git switch --create "$BRANCH" --no-track "$REMOTE_REF"
  elif [[ "$CURRENT_BRANCH" != "$BRANCH" && "$LOCAL_EXISTS" == true ]]; then
    git switch "$BRANCH"
  elif [[ "$CURRENT_BRANCH" != "$BRANCH" ]]; then
    git switch --track -c "$BRANCH" "refs/remotes/origin/$BRANCH"
  fi
fi

if [[ "$RESUME" == true ]]; then
  echo "Mode: Resumed"
else
  echo "Mode: Created"
fi
echo "Branch: $BRANCH"
echo "Base branch: $DEFAULT_BRANCH"
echo "Current default SHA: $BASE_SHA"
if [[ "$RESUME" == true ]]; then
  echo "Start SHA: recover from the durable branch-preparation issue record"
else
  echo "Start SHA: $BASE_SHA"
fi
echo "Branch SHA: $(git rev-parse "$TARGET_REF")"
