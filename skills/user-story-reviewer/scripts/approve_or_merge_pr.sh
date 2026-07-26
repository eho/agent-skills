#!/bin/bash
# Usage:
#   approve_or_merge_pr.sh <pr> <review-file> <review-mode> \
#     --expected-head <sha> [--expected-base <branch>] [merge options]
#
# Review modes: --comment-only | --request-changes | --approve | --merge
# Merge options:
#   --merge-method <squash|merge|rebase> [--delete-branch]
#   --queue
#   --allow-self-merge  # only when repository policy explicitly permits it
# Approval and merge require repeated --required-check <name>, or an explicit
# --no-required-checks after repository policy is inspected.

set -euo pipefail

PR_NUMBER=${1:-}
REVIEW_BODY_FILE=${2:-}
MODE=""
EXPECTED_HEAD=""
EXPECTED_BASE=""
MERGE_METHOD=""
DELETE_BRANCH=false
QUEUE_MERGE=false
ALLOW_SELF_MERGE=false
NO_REQUIRED_CHECKS=false
REQUIRED_CHECKS=()
REQUIRED_CHECK_COUNT=0
TMP_BODY=""
TMP_CHECKS=""
TMP_POLICY=""
TMP_CLASSIC_POLICY=""
TMP_CLASSIC_ERROR=""

cleanup() {
  if [[ -n "$TMP_BODY" ]]; then
    rm -f "$TMP_BODY"
  fi
  if [[ -n "$TMP_CHECKS" ]]; then
    rm -f "$TMP_CHECKS"
  fi
  if [[ -n "$TMP_POLICY" ]]; then
    rm -f "$TMP_POLICY"
  fi
  if [[ -n "$TMP_CLASSIC_POLICY" ]]; then
    rm -f "$TMP_CLASSIC_POLICY"
  fi
  if [[ -n "$TMP_CLASSIC_ERROR" ]]; then
    rm -f "$TMP_CLASSIC_ERROR"
  fi
}
trap cleanup EXIT

usage() {
  echo "Usage: $0 <pr> <review-file> <--comment-only|--request-changes|--approve|--merge> --expected-head <sha> [options]" >&2
  exit 64
}

if [[ -z "$PR_NUMBER" || -z "$REVIEW_BODY_FILE" || ! -f "$REVIEW_BODY_FILE" ]]; then
  usage
fi

set_mode() {
  if [[ -n "$MODE" ]]; then
    echo "Error: choose exactly one review mode." >&2
    exit 64
  fi
  MODE=$1
}

shift 2
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --comment-only)
      set_mode comment
      shift
      ;;
    --request-changes)
      set_mode request
      shift
      ;;
    --approve)
      set_mode approve
      shift
      ;;
    --merge)
      set_mode merge
      shift
      ;;
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
    --delete-branch)
      DELETE_BRANCH=true
      shift
      ;;
    --queue)
      QUEUE_MERGE=true
      shift
      ;;
    --allow-self-merge)
      ALLOW_SELF_MERGE=true
      shift
      ;;
    --required-check)
      [[ "$#" -ge 2 && -n "$2" ]] || usage
      REQUIRED_CHECKS+=("$2")
      REQUIRED_CHECK_COUNT=$((REQUIRED_CHECK_COUNT + 1))
      shift 2
      ;;
    --no-required-checks)
      NO_REQUIRED_CHECKS=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 64
      ;;
  esac
done

[[ -n "$MODE" && -n "$EXPECTED_HEAD" ]] || usage

case "$MERGE_METHOD" in
  ""|squash|merge|rebase) ;;
  *)
    echo "Invalid merge method: $MERGE_METHOD" >&2
    exit 64
    ;;
esac

if [[ "$MODE" != "merge" ]] &&
   { [[ -n "$MERGE_METHOD" ]] || [[ "$DELETE_BRANCH" == true ]] ||
     [[ "$QUEUE_MERGE" == true ]] ||
     [[ "$ALLOW_SELF_MERGE" == true ]]; }; then
  echo "Error: merge options require --merge." >&2
  exit 64
fi

if [[ "$MODE" == "merge" && "$QUEUE_MERGE" == false && -z "$MERGE_METHOD" ]]; then
  echo "Error: direct --merge requires an explicit --merge-method; use --queue for a required merge queue." >&2
  exit 64
fi

if [[ "$QUEUE_MERGE" == true ]] &&
   { [[ -n "$MERGE_METHOD" ]] || [[ "$DELETE_BRANCH" == true ]]; }; then
  echo "Error: --queue cannot be combined with direct merge options." >&2
  exit 64
fi

if [[ "$NO_REQUIRED_CHECKS" == true && "$REQUIRED_CHECK_COUNT" -gt 0 ]]; then
  echo "Error: choose required check names or --no-required-checks, not both." >&2
  exit 64
fi

if [[ "$MODE" == "approve" || "$MODE" == "merge" ]]; then
  if [[ "$NO_REQUIRED_CHECKS" != true && "$REQUIRED_CHECK_COUNT" -eq 0 ]]; then
    echo "Error: approval/merge requires --required-check <name> or explicit --no-required-checks." >&2
    exit 64
  fi
elif [[ "$NO_REQUIRED_CHECKS" == true || "$REQUIRED_CHECK_COUNT" -gt 0 ]]; then
  echo "Error: required-check policy options apply only to approval or merge." >&2
  exit 64
fi

if [[ -z "$EXPECTED_BASE" ]]; then
  EXPECTED_BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
fi
REPO_NAME_WITH_OWNER=$(gh repo view --json nameWithOwner -q .nameWithOwner)
REPO_OWNER=${REPO_NAME_WITH_OWNER%%/*}
REPO_NAME=${REPO_NAME_WITH_OWNER#*/}
BRANCH_PATH=$(jq -rn --arg branch "$EXPECTED_BASE" '$branch | @uri')

pr_field() {
  gh pr view "$PR_NUMBER" --json "$1" -q ".$1"
}

assert_identity_preflight() {
  local state draft head base
  state=$(pr_field state)
  draft=$(pr_field isDraft)
  head=$(pr_field headRefOid)
  base=$(pr_field baseRefName)

  [[ "$state" == "OPEN" ]] || {
    echo "Refusing review: PR is not open (state=$state)." >&2
    exit 2
  }
  if [[ "$MODE" == "approve" || "$MODE" == "merge" ]]; then
    [[ "$draft" == "false" ]] || {
      echo "Refusing approval or merge: PR is still a draft." >&2
      exit 2
    }
  fi
  [[ "$head" == "$EXPECTED_HEAD" ]] || {
    echo "Refusing review: head changed from $EXPECTED_HEAD to $head." >&2
    exit 2
  }
  [[ "$base" == "$EXPECTED_BASE" ]] || {
    echo "Refusing review: expected base $EXPECTED_BASE, found $base." >&2
    exit 2
  }
}

assert_checks_passed() {
  local check_name check_state check_app required required_name required_app found
  if [[ -n "$TMP_CHECKS" ]]; then
    rm -f "$TMP_CHECKS"
  fi
  TMP_CHECKS=$(mktemp)
  if ! gh pr view "$PR_NUMBER" --json statusCheckRollup --jq \
    '.statusCheckRollup[]? |
      [(.name // .context // ""), ((.conclusion // .state // "") | ascii_upcase),
       ((.app.databaseId // "") | tostring)] |
      @tsv' > "$TMP_CHECKS"; then
    echo "Could not read PR checks." >&2
    exit 2
  fi

  while IFS=$'\t' read -r check_name check_state check_app; do
    [[ -n "$check_name" ]] || continue
    case "$check_state" in
      SUCCESS|NEUTRAL|SKIPPED) ;;
      *)
        echo "Refusing approval or merge: check '$check_name' is $check_state." >&2
        exit 2
        ;;
    esac
  done < "$TMP_CHECKS"

  if [[ "$REQUIRED_CHECK_COUNT" -gt 0 ]]; then
    for required in "${REQUIRED_CHECKS[@]}"; do
      required_name=${required%@*}
      required_app=""
      if [[ "$required" == *@* ]]; then
        required_app=${required##*@}
      fi
      found=false
      while IFS=$'\t' read -r check_name check_state check_app; do
        if [[ "$check_name" == "$required_name" &&
              ( -z "$required_app" || "$check_app" == "$required_app" ) ]]; then
          found=true
          case "$check_state" in
            SUCCESS|NEUTRAL|SKIPPED) ;;
            *)
              echo "Required check '$required' is $check_state." >&2
              exit 2
              ;;
          esac
        fi
      done < "$TMP_CHECKS"
      [[ "$found" == true ]] || {
        echo "Required check is missing from the PR with the expected app identity: $required" >&2
        exit 2
      }
    done
  fi
}

assert_required_check_policy() {
  local policy_check policy_app policy_identity declared required
  if [[ -n "$TMP_POLICY" ]]; then
    rm -f "$TMP_POLICY"
  fi
  TMP_POLICY=$(mktemp)
  TMP_CLASSIC_POLICY=$(mktemp)
  TMP_CLASSIC_ERROR=$(mktemp)
  if ! gh api "repos/$REPO_NAME_WITH_OWNER/rules/branches/$BRANCH_PATH" \
    --jq '.[] | select(.type == "required_status_checks") |
      .parameters.required_status_checks[]? |
      [.context, ((.integration_id // "") | tostring)] | @tsv' > "$TMP_POLICY"; then
    echo "Could not verify required-check rules for $EXPECTED_BASE." >&2
    exit 2
  fi
  if ! gh api \
    "repos/$REPO_NAME_WITH_OWNER/branches/$BRANCH_PATH/protection/required_status_checks" \
    --jq 'if (.checks | type) == "array" then
      .checks[]? | [.context, ((.app_id // "") | tostring)] | @tsv
    else
      .contexts[]? | [., ""] | @tsv
    end' > "$TMP_CLASSIC_POLICY" 2> "$TMP_CLASSIC_ERROR"; then
    if ! grep -Eq 'HTTP 404|Not Found' "$TMP_CLASSIC_ERROR"; then
      echo "Could not verify classic branch-protection checks for $EXPECTED_BASE." >&2
      exit 2
    fi
    : > "$TMP_CLASSIC_POLICY"
  fi
  cat "$TMP_CLASSIC_POLICY" >> "$TMP_POLICY"
  sort -u "$TMP_POLICY" -o "$TMP_POLICY"

  while IFS=$'\t' read -r policy_check policy_app; do
    [[ -n "$policy_check" ]] || continue
    policy_identity=$policy_check
    if [[ -n "$policy_app" ]]; then
      policy_identity="$policy_check@$policy_app"
    fi
    if [[ "$NO_REQUIRED_CHECKS" == true ]]; then
      echo "Repository policy requires '$policy_identity'; --no-required-checks is invalid." >&2
      exit 2
    fi
    declared=false
    if [[ "$REQUIRED_CHECK_COUNT" -gt 0 ]]; then
      for required in "${REQUIRED_CHECKS[@]}"; do
        [[ "$required" == "$policy_identity" ]] && declared=true
      done
    fi
    [[ "$declared" == true ]] || {
      echo "Repository policy requires an undeclared check: $policy_identity" >&2
      exit 2
    }
  done < "$TMP_POLICY"
}

assert_queue_required() {
  local queue_rules
  if ! queue_rules=$(
    gh api "repos/$REPO_NAME_WITH_OWNER/rules/branches/$BRANCH_PATH" \
      --jq '[.[] | select(.type == "merge_queue")] | length'
  ); then
    echo "Could not verify merge-queue policy for $EXPECTED_BASE." >&2
    exit 2
  fi
  [[ "$queue_rules" =~ ^[1-9][0-9]*$ ]] || {
    echo "Refusing methodless queue submission: $EXPECTED_BASE has no verified merge-queue rule." >&2
    exit 2
  }
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
      if [[ "$QUEUE_MERGE" != true ]]; then
        echo "Refusing direct merge: merge state is BLOCKED." >&2
        exit 2
      fi
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
    echo "Refusing merge: repository does not allow $MERGE_METHOD merges." >&2
    exit 2
  }
}

verify_merge_or_queue_result() {
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
      QUEUED|AWAITING_CHECKS|MERGEABLE|LOCKED) ;;
      *)
        echo "Merge command succeeded but queue state is not active: ${queue_state:-missing}." >&2
        exit 2
        ;;
    esac
    echo "Merge result: queue state $queue_state"
    return
  fi

  echo "Direct merge command succeeded but merged state could not be verified." >&2
  exit 2
}

assert_identity_preflight

PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)
if [[ -z "$PR_AUTHOR" || -z "$CURRENT_USER" ]]; then
  echo "Could not resolve PR author or current user." >&2
  exit 2
fi

TMP_BODY=$(mktemp)
cp "$REVIEW_BODY_FILE" "$TMP_BODY"

submit_commit_bound_review() {
  local event=$1
  gh api --method POST \
    "repos/$REPO_NAME_WITH_OWNER/pulls/$PR_NUMBER/reviews" \
    -f event="$event" \
    -f commit_id="$EXPECTED_HEAD" \
    -F body=@"$TMP_BODY"
}

case "$MODE" in
  comment)
    submit_commit_bound_review COMMENT
    ;;
  request)
    if [[ "$PR_AUTHOR" == "$CURRENT_USER" ]]; then
      submit_commit_bound_review COMMENT
    else
      submit_commit_bound_review REQUEST_CHANGES
    fi
    ;;
  approve|merge)
    assert_required_check_policy
    assert_checks_passed
    if [[ "$PR_AUTHOR" == "$CURRENT_USER" ]]; then
      if [[ "$MODE" == "approve" ]]; then
        echo "Cannot formally approve a self-authored PR; use --comment-only." >&2
        exit 2
      fi
      if [[ "$MODE" == "merge" && "$ALLOW_SELF_MERGE" != true ]]; then
        echo "Refusing self-authored merge without --allow-self-merge and explicit repository-policy authority." >&2
        exit 2
      fi
      submit_commit_bound_review COMMENT
    else
      submit_commit_bound_review APPROVE
    fi
    ;;
esac

echo "Reviewed head SHA: $EXPECTED_HEAD"

if [[ "$MODE" == "approve" ]]; then
  assert_identity_preflight
  assert_required_check_policy
  assert_checks_passed
fi

if [[ "$MODE" != "merge" ]]; then
  exit 0
fi

# Re-read all volatile state after posting the review. The head lock is also
# passed to GitHub so a concurrent push cannot be merged under stale evidence.
assert_identity_preflight
assert_required_check_policy
assert_checks_passed
assert_mergeable
assert_merge_method_allowed
if [[ "$QUEUE_MERGE" == true ]]; then
  assert_queue_required
fi

if [[ "$PR_AUTHOR" != "$CURRENT_USER" ]]; then
  REVIEW_DECISION=$(pr_field reviewDecision)
  [[ "$REVIEW_DECISION" == "APPROVED" ]] || {
    echo "Refusing merge: repository review decision is $REVIEW_DECISION." >&2
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

verify_merge_or_queue_result
