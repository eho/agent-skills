#!/bin/bash
# Usage: create_milestone.sh "<milestone_title>"

set -euo pipefail

TITLE=${1:-}
if [[ -z "$TITLE" ]]; then
  echo "Usage: $0 <milestone_title>" >&2
  exit 2
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
if gh api "repos/$REPO/milestones?state=all&per_page=100" --paginate \
  --jq '.[].title' | grep -Fxq "$TITLE"; then
  echo "Milestone ready: $TITLE"
  exit 0
fi

if gh api "repos/$REPO/milestones" -f title="$TITLE" >/dev/null; then
  echo "Milestone created: $TITLE"
  exit 0
fi

# A concurrent run may have created it after the first read.
if gh api "repos/$REPO/milestones?state=all&per_page=100" --paginate \
  --jq '.[].title' | grep -Fxq "$TITLE"; then
  echo "Milestone ready: $TITLE"
  exit 0
fi

echo "Failed to ensure milestone: $TITLE" >&2
exit 1
