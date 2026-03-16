#!/bin/bash
# scripts/create_issue.sh
# Usage: ./scripts/create_issue.sh "<title>" "<labels>" "<body_file_path>"

TITLE=$1
LABELS=$2
BODY_FILE=$3

# Safely create the issue
ISSUE_URL=$(gh issue create --title "$TITLE" --label "$LABELS" --body-file "$BODY_FILE")

# Extract the issue number without triggering agent shell warnings
ISSUE_NUMBER=${ISSUE_URL##*/}

echo "Created Issue: $ISSUE_URL"
echo "Issue Number: $ISSUE_NUMBER"
