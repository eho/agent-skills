#!/bin/bash
# Usage: sync_issue.sh "<issue-number|new>" "<title>" "<labels>" "<body-file>"

set -euo pipefail

TARGET=${1:-}
TITLE=${2:-}
LABELS=${3:-}
BODY_FILE=${4:-}

if [[ -z "$TARGET" || -z "$TITLE" || -z "$LABELS" || -z "$BODY_FILE" ]]; then
  echo "Usage: $0 <issue-number|new> <title> <labels> <body-file>" >&2
  exit 2
fi
if [[ ! -f "$BODY_FILE" ]]; then
  echo "Issue body file not found: $BODY_FILE" >&2
  exit 2
fi

if [[ "$TARGET" == "new" ]]; then
  ISSUE_URL=$(gh issue create --title "$TITLE" --label "$LABELS" --body-file "$BODY_FILE")
  echo "Sync Result: Created"
  echo "Issue Number: ${ISSUE_URL##*/}"
  echo "Issue URL: $ISSUE_URL"
  exit 0
fi
if [[ ! "$TARGET" =~ ^[0-9]+$ ]]; then
  echo "Issue target must be 'new' or a positive issue number." >&2
  exit 2
fi

CURRENT_TITLE=$(gh issue view "$TARGET" --json title -q .title)
CURRENT_BODY=$(gh issue view "$TARGET" --json body -q .body)
DESIRED_BODY=$(<"$BODY_FILE")
CHANGED=false

if [[ "$CURRENT_TITLE" != "$TITLE" || "$CURRENT_BODY" != "$DESIRED_BODY" ]]; then
  gh issue edit "$TARGET" --title "$TITLE" --body-file "$BODY_FILE" >/dev/null
  CHANGED=true
fi

CURRENT_LABELS=$(gh issue view "$TARGET" --json labels -q '.labels[].name')
IFS=',' read -r -a REQUIRED_LABELS <<<"$LABELS"
for LABEL in "${REQUIRED_LABELS[@]}"; do
  if ! grep -Fxq "$LABEL" <<<"$CURRENT_LABELS"; then
    gh issue edit "$TARGET" --add-label "$LABEL" >/dev/null
    CHANGED=true
  fi
done

ISSUE_URL=$(gh issue view "$TARGET" --json url -q .url)
if [[ "$CHANGED" == true ]]; then
  echo "Sync Result: Updated"
else
  echo "Sync Result: Unchanged"
fi
echo "Issue Number: $TARGET"
echo "Issue URL: $ISSUE_URL"
