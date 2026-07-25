#!/bin/bash
# scripts/approve_or_merge_pr.sh
# Usage:
#   ./scripts/approve_or_merge_pr.sh "<pr_number>" "review_comment_file" [--comment-only]
#   ./scripts/approve_or_merge_pr.sh "<pr_number>" "review_comment_file" --merge \
#     --merge-method <squash|merge|rebase> [--delete-branch] [--auto]
#   ./scripts/approve_or_merge_pr.sh "<pr_number>" "review_comment_file" --merge --queue

set -euo pipefail

PR_NUMBER=${1:-}
REVIEW_BODY_FILE=${2:-}
MODE="review"
MODE_SET=false
MERGE_METHOD=""
DELETE_BRANCH=false
AUTO_MERGE=false
QUEUE_MERGE=false
TMP_BODY=""

cleanup() {
  if [ -n "$TMP_BODY" ]; then
    rm -f "$TMP_BODY"
  fi
}
trap cleanup EXIT

if [ -z "$PR_NUMBER" ]; then
  echo "Usage: $0 <pr_number> <review_comment_file> [--comment-only|--merge]" >&2
  exit 1
fi

if [ -z "$REVIEW_BODY_FILE" ] || [ "$REVIEW_BODY_FILE" = "--comment-only" ] || [ "$REVIEW_BODY_FILE" = "--merge" ] || [ ! -f "$REVIEW_BODY_FILE" ]; then
  echo "Error: review_comment_file is required and must exist." >&2
  exit 1
fi

shift 2
while [ "$#" -gt 0 ]; do
  case "$1" in
    --comment-only)
      if [ "$MODE_SET" = true ]; then
        echo "Error: choose exactly one of --comment-only or --merge." >&2
        exit 1
      fi
      MODE="comment"
      MODE_SET=true
      shift
      ;;
    --merge)
      if [ "$MODE_SET" = true ]; then
        echo "Error: choose exactly one of --comment-only or --merge." >&2
        exit 1
      fi
      MODE="merge"
      MODE_SET=true
      shift
      ;;
    --merge-method)
      MERGE_METHOD=${2:-}
      shift 2
      ;;
    --delete-branch)
      DELETE_BRANCH=true
      shift
      ;;
    --auto)
      AUTO_MERGE=true
      shift
      ;;
    --queue)
      QUEUE_MERGE=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

case "$MERGE_METHOD" in
  ""|squash|merge|rebase)
    ;;
  *)
    echo "Invalid merge method: $MERGE_METHOD" >&2
    exit 1
    ;;
esac

if [ "$MODE" != "merge" ] && { [ -n "$MERGE_METHOD" ] || [ "$DELETE_BRANCH" = true ] || [ "$AUTO_MERGE" = true ] || [ "$QUEUE_MERGE" = true ]; }; then
  echo "Error: merge options require --merge." >&2
  exit 1
fi

if [ "$MODE" = "merge" ] && [ "$QUEUE_MERGE" = false ] && [ -z "$MERGE_METHOD" ]; then
  echo "Error: direct --merge requires --merge-method squash, merge, or rebase; use --queue for a required merge queue." >&2
  exit 1
fi

if [ "$QUEUE_MERGE" = true ] && { [ -n "$MERGE_METHOD" ] || [ "$AUTO_MERGE" = true ] || [ "$DELETE_BRANCH" = true ]; }; then
  echo "Error: --queue cannot be combined with direct merge options." >&2
  exit 1
fi

merge_pr() {
  if [ "$QUEUE_MERGE" = true ]; then
    gh pr merge "$PR_NUMBER"
    return
  fi
  set -- "$PR_NUMBER" "--$MERGE_METHOD"
  if [ "$DELETE_BRANCH" = true ]; then
    set -- "$@" --delete-branch
  fi
  if [ "$AUTO_MERGE" = true ]; then
    set -- "$@" --auto
  fi
  gh pr merge "$@"
}

# Safely extract author and current user
PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)

# Use a temporary file for the review body
TMP_BODY=$(mktemp)
cat "$REVIEW_BODY_FILE" > "$TMP_BODY"

# GitHub prevents users from approving their own PRs. Comment by default for
# self-authored PRs; merging always requires the explicit --merge option.
if [ "$PR_AUTHOR" = "$CURRENT_USER" ]; then
  gh pr review "$PR_NUMBER" --comment --body-file "$TMP_BODY"
  if [ "$MODE" = "merge" ]; then
    merge_pr
  fi
else
  if [ "$MODE" = "comment" ]; then
    gh pr review "$PR_NUMBER" --comment --body-file "$TMP_BODY"
  else
    gh pr review "$PR_NUMBER" --approve --body-file "$TMP_BODY"
    if [ "$MODE" = "merge" ]; then
      merge_pr
    fi
  fi
fi
