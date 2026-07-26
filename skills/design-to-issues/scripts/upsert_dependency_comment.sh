#!/bin/bash
# Usage: upsert_dependency_comment.sh "<issue-number>" "<body-file>"

set -euo pipefail

ISSUE_NUMBER=${1:-}
BODY_FILE=${2:-}
MARKER='<!-- agent-skills:dependencies -->'

if [[ -z "$ISSUE_NUMBER" || -z "$BODY_FILE" ]]; then
  echo "Usage: $0 <issue-number> <body-file>" >&2
  exit 2
fi
if [[ ! "$ISSUE_NUMBER" =~ ^[0-9]+$ || ! -f "$BODY_FILE" ]]; then
  echo "A numeric issue number and existing body file are required." >&2
  exit 2
fi
if ! grep -Fq "$MARKER" "$BODY_FILE"; then
  echo "Dependency body must contain marker: $MARKER" >&2
  exit 2
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
CURRENT_USER=$(gh api user -q .login)
COMMENT_IDS=$(
  gh api "repos/$REPO/issues/$ISSUE_NUMBER/comments?per_page=100" --paginate \
    --jq ".[] | select(.user.login == \"$CURRENT_USER\") | select(.body | contains(\"$MARKER\")) | .id"
)
COMMENT_COUNT=$(printf '%s\n' "$COMMENT_IDS" | awk 'NF { count++ } END { print count + 0 }')

if (( COMMENT_COUNT > 1 )); then
  echo "Multiple dependency marker comments exist on issue #$ISSUE_NUMBER; manual reconciliation required." >&2
  exit 1
fi
if (( COMMENT_COUNT == 0 )); then
  gh issue comment "$ISSUE_NUMBER" --body-file "$BODY_FILE" >/dev/null
  echo "Dependency Comment: Created"
  exit 0
fi

COMMENT_ID=$(printf '%s\n' "$COMMENT_IDS" | awk 'NF { print; exit }')
CURRENT_BODY=$(gh api "repos/$REPO/issues/comments/$COMMENT_ID" --jq .body)
DESIRED_BODY=$(<"$BODY_FILE")
if [[ "$CURRENT_BODY" == "$DESIRED_BODY" ]]; then
  echo "Dependency Comment: Unchanged"
  exit 0
fi

gh api --method PATCH "repos/$REPO/issues/comments/$COMMENT_ID" -F "body=@$BODY_FILE" >/dev/null
echo "Dependency Comment: Updated"
