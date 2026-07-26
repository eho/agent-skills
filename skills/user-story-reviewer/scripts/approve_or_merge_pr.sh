#!/bin/bash
# Usage: approve_or_merge_pr.sh "<pr-number>" "<review-file>" "<reviewed-head-oid>" [--comment-only]

set -euo pipefail

PR_NUMBER=${1:-}
REVIEW_BODY_FILE=${2:-}
REVIEWED_HEAD_OID=${3:-}
MODE=${4:-}

if [[ -z "$PR_NUMBER" || -z "$REVIEW_BODY_FILE" || -z "$REVIEWED_HEAD_OID" ]]; then
  echo "Usage: $0 <pr-number> <review-file> <reviewed-head-oid> [--comment-only]" >&2
  exit 2
fi
if [[ ! "$PR_NUMBER" =~ ^[0-9]+$ || ! -f "$REVIEW_BODY_FILE" || ! -s "$REVIEW_BODY_FILE" ]]; then
  echo "A numeric PR, non-empty review file, and reviewed head OID are required." >&2
  exit 2
fi
if [[ -n "$MODE" && "$MODE" != "--comment-only" ]]; then
  echo "Unknown option: $MODE" >&2
  exit 2
fi

PR_STATE=$(gh pr view "$PR_NUMBER" --json state -q .state)
IS_DRAFT=$(gh pr view "$PR_NUMBER" --json isDraft -q .isDraft)
HEAD_OID=$(gh pr view "$PR_NUMBER" --json headRefOid -q .headRefOid)
MERGEABLE=$(gh pr view "$PR_NUMBER" --json mergeable -q .mergeable)

if [[ "$PR_STATE" != "OPEN" || "$IS_DRAFT" != "false" ]]; then
  echo "PR #$PR_NUMBER is not an open, non-draft PR." >&2
  exit 1
fi
if [[ "$HEAD_OID" != "$REVIEWED_HEAD_OID" ]]; then
  echo "PR head changed after review; review the new head before acting." >&2
  exit 1
fi
if [[ "$MERGEABLE" != "MERGEABLE" ]]; then
  echo "PR #$PR_NUMBER is not currently mergeable: $MERGEABLE" >&2
  exit 1
fi

CHECK_PROBLEMS=$(gh pr view "$PR_NUMBER" --json statusCheckRollup --jq '
  [.statusCheckRollup[] |
    if has("status") and .status != "COMPLETED" then "pending"
    elif has("conclusion") and (.conclusion | IN("SUCCESS","NEUTRAL","SKIPPED") | not) then
      (.conclusion // "UNKNOWN")
    else empty end] | unique | join(",")
')
if [[ -n "$CHECK_PROBLEMS" ]]; then
  echo "PR checks are not ready: $CHECK_PROBLEMS" >&2
  exit 1
fi

PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)

if [[ "$PR_AUTHOR" == "$CURRENT_USER" ]]; then
  if [[ "$MODE" != "--comment-only" ]]; then
    MERGE_STATE=$(gh pr view "$PR_NUMBER" --json mergeStateStatus -q .mergeStateStatus)
    if [[ "$MERGE_STATE" != "CLEAN" && "$MERGE_STATE" != "HAS_HOOKS" ]]; then
      echo "PR #$PR_NUMBER is not merge-ready: $MERGE_STATE" >&2
      exit 1
    fi
  fi
  gh pr review "$PR_NUMBER" --comment --body-file "$REVIEW_BODY_FILE"
  if [[ "$MODE" != "--comment-only" ]]; then
    gh pr merge "$PR_NUMBER" --squash --delete-branch
  fi
else
  gh pr review "$PR_NUMBER" --approve --body-file "$REVIEW_BODY_FILE"
fi
