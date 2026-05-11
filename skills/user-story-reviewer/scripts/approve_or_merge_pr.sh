#!/bin/bash
# scripts/approve_or_merge_pr.sh
# Usage: ./scripts/approve_or_merge_pr.sh "<pr_number>" "review_comment_file" [--merge]

set -euo pipefail

PR_NUMBER=${1:-}
REVIEW_BODY_FILE=${2:-}
MERGE=false
TMP_BODY=""

cleanup() {
  if [ -n "$TMP_BODY" ]; then
    rm -f "$TMP_BODY"
  fi
}
trap cleanup EXIT

if [ "${2:-}" = "--merge" ] || [ "${3:-}" = "--merge" ]; then
  MERGE=true
fi

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: $0 <pr_number> <review_comment_file> [--merge]" >&2
  exit 1
fi

if [ -z "$REVIEW_BODY_FILE" ] || [ "$REVIEW_BODY_FILE" = "--merge" ] || [ ! -f "$REVIEW_BODY_FILE" ]; then
  echo "Error: review_comment_file is required and must exist." >&2
  exit 1
fi

# Safely extract author and current user
PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)

# Use a temporary file for the review body
TMP_BODY=$(mktemp)
cat "$REVIEW_BODY_FILE" > "$TMP_BODY"

# GitHub prevents users from approving their own PRs
if [ "$PR_AUTHOR" = "$CURRENT_USER" ]; then
  gh pr review "$PR_NUMBER" --comment --body-file "$TMP_BODY"
  if [ "$MERGE" = true ]; then
    gh pr merge "$PR_NUMBER" --squash --delete-branch
  fi
else
  gh pr review "$PR_NUMBER" --approve --body-file "$TMP_BODY"
fi
