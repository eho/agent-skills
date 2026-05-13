#!/bin/bash
# scripts/create_milestone.sh
# Usage: ./scripts/create_milestone.sh "<milestone_title>"

set -euo pipefail

TITLE=${1:-}

if [[ -z "$TITLE" ]]; then
  echo "Usage: $0 <milestone_title>" >&2
  exit 2
fi

# Safely get the repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Create the milestone via the API. A 422 from GitHub means the milestone
# already exists; other failures should stop the workflow.
if gh api "repos/$REPO/milestones" -f title="$TITLE" > /dev/null 2>&1; then
  echo "Milestone ready: $TITLE"
  exit 0
fi

if gh api "repos/$REPO/milestones" --jq '.[].title' | grep -Fxq "$TITLE"; then
  echo "Milestone ready: $TITLE"
  exit 0
fi

echo "Failed to create milestone: $TITLE" >&2
exit 1
