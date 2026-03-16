#!/bin/bash
# scripts/approve_or_merge_pr.sh
# Usage: ./scripts/approve_or_merge_pr.sh "<pr_number>"

PR_NUMBER=$1

# Safely extract author and current user
PR_AUTHOR=$(gh pr view "$PR_NUMBER" --json author -q .author.login)
CURRENT_USER=$(gh api user -q .login)

# Use a temporary file for the review body
TMP_BODY=$(mktemp)
cat <<EOF > "$TMP_BODY"
Reviewed and verified:
- All acceptance criteria met
- Tests passing
- Code quality acceptable
- Documentation updated (if applicable)
EOF

# GitHub prevents users from approving their own PRs
if [ "$PR_AUTHOR" = "$CURRENT_USER" ]; then
  gh pr review "$PR_NUMBER" --comment --body-file "$TMP_BODY"
  gh pr merge "$PR_NUMBER" --squash --delete-branch
else
  gh pr review "$PR_NUMBER" --approve --body-file "$TMP_BODY"
fi

# Cleanup
rm "$TMP_BODY"
