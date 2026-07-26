#!/bin/bash
# Usage: create_milestone.sh "<milestone_title>" [--reopen]

set -euo pipefail

TITLE=${1:-}
REOPEN=false
if [[ "$#" -eq 2 && "$2" == "--reopen" ]]; then
  REOPEN=true
elif [[ "$#" -ne 1 ]]; then
  echo "Usage: $0 <milestone_title> [--reopen]" >&2
  exit 64
fi

if [[ -z "$TITLE" ]]; then
  echo "Usage: $0 <milestone_title> [--reopen]" >&2
  exit 64
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
TMP_LIST=$(mktemp)
trap 'rm -f "$TMP_LIST"' EXIT

load_milestones() {
  if ! gh api --paginate "repos/$REPO/milestones?state=all&per_page=100" \
    --jq '.[] | [.number, .state, .title] | @tsv' > "$TMP_LIST"; then
    echo "Failed to enumerate milestones; refusing to create after an unknown lookup state." >&2
    return 2
  fi
}

find_milestone() {
  while IFS=$'\t' read -r number state title; do
    if [[ "$title" == "$TITLE" ]]; then
      printf '%s\t%s\n' "$number" "$state"
      return 0
    fi
  done < "$TMP_LIST"
  return 1
}

ensure_existing() {
  local milestone number state
  if ! milestone=$(find_milestone); then
    return 1
  fi
  IFS=$'\t' read -r number state <<< "$milestone"
  if [[ "$state" == "closed" ]]; then
    if [[ "$REOPEN" != true ]]; then
      echo "Milestone '$TITLE' exists but is closed; pass --reopen only when repository policy authorizes reopening." >&2
      return 3
    fi
    if ! gh api --method PATCH "repos/$REPO/milestones/$number" -f state=open > /dev/null; then
      echo "Failed to reopen milestone: $TITLE" >&2
      return 2
    fi
  fi
  echo "Milestone ready: $TITLE"
  return 0
}

load_milestones || exit $?
if ensure_existing; then
  exit 0
else
  status=$?
  [[ "$status" -eq 1 ]] || exit "$status"
fi

if gh api "repos/$REPO/milestones" -f title="$TITLE" > /dev/null 2>&1; then
  echo "Milestone ready: $TITLE"
  exit 0
fi

# A concurrent creator may have won after our lookup. Re-query and apply the
# same open/closed policy instead of treating every create failure as success.
load_milestones || exit $?
if ensure_existing; then
  exit 0
else
  status=$?
  [[ "$status" -eq 1 ]] || exit "$status"
fi

echo "Failed to create milestone: $TITLE" >&2
exit 1
