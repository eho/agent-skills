#!/bin/bash
set -euo pipefail

# scripts/create_pr.sh
# Usage: ./scripts/create_pr.sh "<issue_number>" "<pr_title>" "<delivery_body_file>" \
#   "<story_id>" "<design_identity>" "<design_revision>" "<story_revision>" \
#   "<delivery_id>" "<superseded_pr_number|none>"

if [ "$#" -ne 9 ]; then
    echo "Usage: $0 <issue_number> <pr_title> <delivery_body_file> <story_id> <design_identity> <design_revision> <story_revision> <delivery_id> <superseded_pr_number|none>" >&2
    exit 64
fi

ISSUE_NUMBER=$1
PR_TITLE=$2
DELIVERY_BODY_FILE=$3
STORY_ID=$4
DESIGN_IDENTITY=$5
DESIGN_REVISION=$6
STORY_REVISION=$7
DELIVERY_ID=$8
SUPERSEDES=$9

if [[ ! "$ISSUE_NUMBER" =~ ^[0-9]+$ ]]; then
    echo "Issue number must be numeric." >&2
    exit 64
fi

if [[ ! "$STORY_ID" =~ ^([A-Z][A-Z0-9]{1,9}-[0-9]{3,}|GAP-[0-9A-F]{12})$ ]]; then
    echo "Invalid story ID: $STORY_ID" >&2
    exit 64
fi

if [[ -z "$DESIGN_IDENTITY" || "$DESIGN_IDENTITY" == /* ||
      "$DESIGN_IDENTITY" == *$'\n'* ||
      "$DESIGN_IDENTITY" == *'<!--'* || "$DESIGN_IDENTITY" == *'-->'* ||
      "$DESIGN_IDENTITY" =~ (^|/)\.\.(/|$) ]]; then
    echo "Design identity must be a safe single-line repository-relative path." >&2
    exit 64
fi

if [[ ! "$DESIGN_REVISION" =~ ^[0-9a-f]{64}$ ||
      ! "$STORY_REVISION" =~ ^[0-9a-f]{64}$ ]]; then
    echo "Design and story revisions must be lowercase SHA-256 values." >&2
    exit 64
fi

if [[ ! "$DELIVERY_ID" =~ ^[a-z0-9][a-z0-9._-]{2,127}$ ]]; then
    echo "Invalid delivery ID: $DELIVERY_ID" >&2
    exit 64
fi

if [[ ! "$SUPERSEDES" =~ ^(none|[0-9]+)$ ]]; then
    echo "Superseded PR must be a number or 'none'." >&2
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
    printf '<!-- feature-delivery:design=%s -->\n' "$DESIGN_IDENTITY"
    printf '<!-- feature-delivery:story=%s -->\n' "$STORY_ID"
    printf '<!-- feature-delivery:design-revision=%s -->\n' "$DESIGN_REVISION"
    printf '<!-- feature-delivery:story-revision=%s -->\n' "$STORY_REVISION"
    printf '<!-- feature-delivery:delivery-id=%s -->\n' "$DELIVERY_ID"
    printf '<!-- feature-delivery:supersedes=%s -->\n\n' "$SUPERSEDES"
    cat "$DELIVERY_BODY_FILE"
    printf '\n'
} > "$TMP_BODY"

DEFAULT_BRANCH=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
HEAD_BRANCH=$(git branch --show-current)
if [[ -z "$HEAD_BRANCH" || "$HEAD_BRANCH" == "$DEFAULT_BRANCH" ]]; then
    echo "Create the PR from a focused non-default story branch." >&2
    exit 65
fi
if [[ "$HEAD_BRANCH" != "story/$DELIVERY_ID" ]]; then
    echo "Story branch must be exactly story/$DELIVERY_ID." >&2
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
    echo "Remote story branch does not match local HEAD; push and verify it before creating the PR." >&2
    exit 65
fi

gh pr create \
    --title "$PR_TITLE" \
    --body-file "$TMP_BODY" \
    --base "$DEFAULT_BRANCH" \
    --head "$HEAD_BRANCH"
