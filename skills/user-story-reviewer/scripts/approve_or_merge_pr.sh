#!/bin/bash
set -euo pipefail

# Commit-bound review and merge helper.
#
# Usage:
#   approve_or_merge_pr.sh <pr> <review-file> <mode> --expected-head <sha> [options]
#
# Modes:
#   --comment-only | --request-changes | --approve | --merge
#
# Merge options:
#   --merge-method <squash|merge|rebase>
#   --queue
#   --delete-branch
#   --allow-self-merge
#   --expected-base <branch>

usage() {
  sed -n '3,16p' "$0" >&2
  exit "${1:-64}"
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage 0
fi

PR_NUMBER=${1:-}
REVIEW_BODY_FILE=${2:-}
MODE=""
EXPECTED_HEAD=""
EXPECTED_BASE=""
MERGE_METHOD=""
QUEUE_MERGE=false
DELETE_BRANCH=false
ALLOW_SELF_MERGE=false

[[ "$PR_NUMBER" =~ ^[0-9]+$ ]] || usage
[[ -s "$REVIEW_BODY_FILE" ]] || usage

set_mode() {
  [[ -z "$MODE" ]] || {
    echo "Choose exactly one review mode." >&2
    exit 64
  }
  MODE=$1
}

shift 2
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --comment-only) set_mode comment; shift ;;
    --request-changes) set_mode request; shift ;;
    --approve) set_mode approve; shift ;;
    --merge) set_mode merge; shift ;;
    --expected-head)
      [[ "$#" -ge 2 && -n "$2" ]] || usage
      EXPECTED_HEAD=$2
      shift 2
      ;;
    --expected-base)
      [[ "$#" -ge 2 && -n "$2" ]] || usage
      EXPECTED_BASE=$2
      shift 2
      ;;
    --merge-method)
      [[ "$#" -ge 2 ]] || usage
      MERGE_METHOD=$2
      shift 2
      ;;
    --queue) QUEUE_MERGE=true; shift ;;
    --delete-branch) DELETE_BRANCH=true; shift ;;
    --allow-self-merge) ALLOW_SELF_MERGE=true; shift ;;
    *)
      echo "Unknown option: $1" >&2
      exit 64
      ;;
  esac
done

[[ -n "$MODE" && -n "$EXPECTED_HEAD" ]] || usage
case "$MERGE_METHOD" in
  ""|squash|merge|rebase) ;;
  *) echo "Invalid merge method: $MERGE_METHOD" >&2; exit 64 ;;
esac

if [[ "$MODE" != "merge" ]] &&
   { [[ -n "$MERGE_METHOD" ]] || [[ "$QUEUE_MERGE" == true ]] ||
     [[ "$DELETE_BRANCH" == true ]] || [[ "$ALLOW_SELF_MERGE" == true ]]; }; then
  echo "Merge options require --merge." >&2
  exit 64
fi
if [[ "$MODE" == "merge" && "$QUEUE_MERGE" == false && -z "$MERGE_METHOD" ]]; then
  echo "Direct merge requires --merge-method; use --queue for a merge queue." >&2
  exit 64
fi
if [[ "$QUEUE_MERGE" == true ]] &&
   { [[ -n "$MERGE_METHOD" ]] || [[ "$DELETE_BRANCH" == true ]]; }; then
  echo "--queue cannot be combined with direct merge options." >&2
  exit 64
fi

if [[ -z "$EXPECTED_BASE" ]]; then
  EXPECTED_BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
fi
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
REPO_OWNER=${REPO%%/*}
REPO_NAME=${REPO#*/}

pr_field() {
  gh pr view "$PR_NUMBER" --json "$1" -q ".$1"
}

assert_identity() {
  local state draft head base
  state=$(pr_field state)
  draft=$(pr_field isDraft)
  head=$(pr_field headRefOid)
  base=$(pr_field baseRefName)
  [[ "$state" == "OPEN" ]] || {
    echo "Refusing review: PR state is $state." >&2
    exit 2
  }
  [[ "$head" == "$EXPECTED_HEAD" ]] || {
    echo "Refusing review: head changed from $EXPECTED_HEAD to $head." >&2
    exit 2
  }
  [[ "$base" == "$EXPECTED_BASE" ]] || {
    echo "Refusing review: expected base $EXPECTED_BASE, found $base." >&2
    exit 2
  }
  if [[ "$MODE" == "approve" || "$MODE" == "merge" ]]; then
    [[ "$draft" == "false" ]] || {
      echo "Refusing approval or merge: PR is a draft." >&2
      exit 2
    }
  fi
}

assert_checks_passed() {
  local checks status name bucket
  set +e
  checks=$(
    gh pr checks "$PR_NUMBER" --required --json name,bucket --jq \
      '.[] | [.name, .bucket] | @tsv'
  )
  status=$?
  set -e
  if [[ "$status" -ne 0 && "$status" -ne 8 ]]; then
    echo "Could not read PR checks." >&2
    exit 2
  fi
  while IFS=$'\t' read -r name bucket; do
    [[ -n "$name" ]] || continue
    case "$bucket" in
      pass|skipping) ;;
      *)
        echo "Refusing approval or merge: required check '$name' is $bucket." >&2
        exit 2
        ;;
    esac
  done <<< "$checks"
}

assert_mergeable() {
  local mergeable merge_state
  mergeable=$(pr_field mergeable)
  merge_state=$(pr_field mergeStateStatus)
  [[ "$mergeable" == "MERGEABLE" ]] || {
    echo "Refusing merge: mergeability is $mergeable." >&2
    exit 2
  }
  case "$merge_state" in
    CLEAN|HAS_HOOKS) ;;
    BLOCKED)
      [[ "$QUEUE_MERGE" == true ]] || {
        echo "Refusing direct merge: merge state is BLOCKED." >&2
        exit 2
      }
      ;;
    *)
      echo "Refusing merge: merge state is $merge_state." >&2
      exit 2
      ;;
  esac
}

assert_merge_method_allowed() {
  local field allowed
  case "$MERGE_METHOD" in
    squash) field=squashMergeAllowed ;;
    merge) field=mergeCommitAllowed ;;
    rebase) field=rebaseMergeAllowed ;;
    "") return ;;
  esac
  allowed=$(gh repo view --json "$field" -q ".$field")
  [[ "$allowed" == "true" ]] || {
    echo "Repository does not allow $MERGE_METHOD merges." >&2
    exit 2
  }
}

submit_review() {
  gh api --method POST "repos/$REPO/pulls/$PR_NUMBER/reviews" \
    -f event="$1" -f commit_id="$EXPECTED_HEAD" -F body=@"$REVIEW_BODY_FILE"
}

verify_result() {
  local merged_at queue_state
  merged_at=$(gh pr view "$PR_NUMBER" --json mergedAt -q '.mergedAt // ""')
  if [[ -n "$merged_at" ]]; then
    echo "Merge result: merged at $merged_at"
    return
  fi
  if [[ "$QUEUE_MERGE" == true ]]; then
    queue_state=$(
      gh api graphql \
        -F owner="$REPO_OWNER" -F name="$REPO_NAME" -F number="$PR_NUMBER" \
        -f query='query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){mergeQueueEntry{state}}}}' \
        --jq '.data.repository.pullRequest.mergeQueueEntry.state // ""'
    )
    case "$queue_state" in
      QUEUED|AWAITING_CHECKS|MERGEABLE|LOCKED)
        echo "Merge result: queue state $queue_state"
        return
        ;;
    esac
  fi
  echo "Merge command succeeded but final merged or queued state was not verified." >&2
  exit 2
}

assert_identity
PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)
[[ -n "$PR_AUTHOR" && -n "$CURRENT_USER" ]] || {
  echo "Could not resolve PR author or current user." >&2
  exit 2
}

case "$MODE" in
  comment) submit_review COMMENT ;;
  request)
    if [[ "$PR_AUTHOR" == "$CURRENT_USER" ]]; then
      submit_review COMMENT
    else
      submit_review REQUEST_CHANGES
    fi
    ;;
  approve|merge)
    assert_checks_passed
    if [[ "$PR_AUTHOR" == "$CURRENT_USER" ]]; then
      if [[ "$MODE" == "approve" ]]; then
        echo "Cannot approve a self-authored PR; use --comment-only." >&2
        exit 2
      fi
      [[ "$ALLOW_SELF_MERGE" == true ]] || {
        echo "Self-authored merge requires --allow-self-merge and explicit authority." >&2
        exit 2
      }
      submit_review COMMENT
    else
      submit_review APPROVE
    fi
    ;;
esac

echo "Reviewed head SHA: $EXPECTED_HEAD"
[[ "$MODE" == "merge" ]] || {
  assert_identity
  [[ "$MODE" != "approve" ]] || assert_checks_passed
  exit 0
}

# Re-read volatile state and pass the same head to GitHub so a concurrent push
# cannot be merged under stale review evidence.
assert_identity
assert_checks_passed
assert_mergeable
assert_merge_method_allowed
if [[ "$PR_AUTHOR" != "$CURRENT_USER" ]]; then
  decision=$(pr_field reviewDecision)
  [[ "$decision" == "APPROVED" ]] || {
    echo "Refusing merge: review decision is $decision." >&2
    exit 2
  }
fi

if [[ "$QUEUE_MERGE" == true ]]; then
  gh pr merge "$PR_NUMBER" --match-head-commit "$EXPECTED_HEAD"
else
  merge_args=("$PR_NUMBER" "--$MERGE_METHOD" --match-head-commit "$EXPECTED_HEAD")
  [[ "$DELETE_BRANCH" == true ]] && merge_args+=(--delete-branch)
  gh pr merge "${merge_args[@]}"
fi
verify_result
