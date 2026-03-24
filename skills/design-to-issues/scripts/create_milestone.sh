#!/bin/bash
# scripts/create_milestone.sh
# Usage: ./scripts/create_milestone.sh "<milestone_title>"

TITLE=$1

# Safely get the repository name
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

# Create the milestone via the API (ignore 422 if it already exists)
gh api "repos/$REPO/milestones" -f title="$TITLE" > /dev/null 2>&1 || true

echo "Milestone ready: $TITLE"
