#!/bin/bash
set -euo pipefail

# Usage:
#   create_pr.sh <issue-number> <title> <body-file> <story-id-or-none> <design-path-or-none>

if [ "$#" -ne 5 ]; then
  echo "Usage: $0 <issue-number> <title> <body-file> <story-id-or-none> <design-path-or-none>" >&2
  exit 64
fi

ISSUE_NUMBER=$1
PR_TITLE=$2
DELIVERY_BODY_FILE=$3
STORY_ID=$4
DESIGN_IDENTITY=$5

if [[ ! "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
  echo "Issue number must be numeric." >&2
  exit 64
fi
if [[ "$STORY_ID" != "none" &&
      ! "$STORY_ID" =~ ^[A-Z][A-Z0-9]{1,20}-[0-9]{1,}$ ]]; then
  echo "Invalid story ID: $STORY_ID" >&2
  exit 64
fi
if [[ "$DESIGN_IDENTITY" != "none" ]] &&
   { [[ -z "$DESIGN_IDENTITY" || "$DESIGN_IDENTITY" == /* ||
        "$DESIGN_IDENTITY" == *$'\n'* ||
        "$DESIGN_IDENTITY" == *'<!--'* || "$DESIGN_IDENTITY" == *'-->'* ||
        "$DESIGN_IDENTITY" =~ (^|/)\.\.(/|$) ]]; }; then
  echo "Design identity must be 'none' or a safe repository-relative path." >&2
  exit 64
fi
if [[ ! -f "$DELIVERY_BODY_FILE" ]]; then
  echo "Delivery body file not found: $DELIVERY_BODY_FILE" >&2
  exit 64
fi
if grep -Fq '<!-- feature-delivery:' "$DELIVERY_BODY_FILE"; then
  echo "Delivery body must not contain reserved feature-delivery markers." >&2
  exit 64
fi

TMP_BODY=$(mktemp)
trap 'rm -f "$TMP_BODY"' EXIT
{
  printf 'Closes #%s\n\n' "$ISSUE_NUMBER"
  if [[ "$DESIGN_IDENTITY" != "none" ]]; then
    printf '<!-- feature-delivery:design=%s -->\n' "$DESIGN_IDENTITY"
  fi
  if [[ "$STORY_ID" != "none" ]]; then
    printf '<!-- feature-delivery:story=%s -->\n' "$STORY_ID"
  fi
  printf '\n'
  cat "$DELIVERY_BODY_FILE"
  printf '\n'
} > "$TMP_BODY"

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
HEAD_BRANCH=$(git branch --show-current)
if [[ -z "$HEAD_BRANCH" || "$HEAD_BRANCH" == "$DEFAULT_BRANCH" ]]; then
  echo "Create the PR from a focused non-default story branch." >&2
  exit 65
fi

LOCAL_HEAD=$(git rev-parse HEAD)
set +e
REMOTE_LINE=$(git ls-remote --exit-code --heads origin "refs/heads/$HEAD_BRANCH" 2>/dev/null)
REMOTE_STATUS=$?
set -e
if [[ "$REMOTE_STATUS" -ne 0 ]]; then
  echo "Remote story branch is missing or could not be verified: $HEAD_BRANCH" >&2
  exit 65
fi
REMOTE_HEAD=${REMOTE_LINE%%[[:space:]]*}
if [[ -z "$REMOTE_HEAD" || "$REMOTE_HEAD" != "$LOCAL_HEAD" ]]; then
  echo "Remote story branch does not match local HEAD; push it before creating the PR." >&2
  exit 65
fi

gh pr create \
  --title "$PR_TITLE" \
  --body-file "$TMP_BODY" \
  --base "$DEFAULT_BRANCH" \
  --head "$HEAD_BRANCH"
