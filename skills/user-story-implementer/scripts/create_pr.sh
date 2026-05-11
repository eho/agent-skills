#!/bin/bash
set -euo pipefail

# scripts/create_pr.sh
# Usage: ./scripts/create_pr.sh "<issue_number>" "<issue_title>" "<summary_of_work>"

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <issue_number> <issue_title> <summary_of_work>" >&2
    exit 64
fi

ISSUE_NUMBER=$1
PR_TITLE=$2
SUMMARY=$3

# Use a temporary file to safely handle multi-line formatting
TMP_BODY=$(mktemp)
trap 'rm -f "$TMP_BODY"' EXIT

cat <<EOF > "$TMP_BODY"
Closes #$ISSUE_NUMBER

### Summary
$SUMMARY
EOF

# Safely create the pull request
gh pr create --title "$PR_TITLE" --body-file "$TMP_BODY"
