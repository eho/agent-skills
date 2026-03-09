---
name: prd-to-github-milestone
description: Parses a Product Requirements Document (PRD) to extract User Stories and creates corresponding GitHub Issues. It can optionally link them to a GitHub Milestone. This skill acts as a setup phase to move from markdown-based tracking to GitHub-native issue tracking.
metadata:
  author: eho
  version: '1.0.0'
---

# Instructions

You are acting as an autonomous sub-agent to parse a Product Requirements Document (PRD) and scaffold a GitHub milestone by creating GitHub Issues for each user story.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## Workflow

1. **Parse PRD**: Read the specified PRD file (e.g., `docs/PRD.md` or `tasks/prd-[feature].md`). Extract all User Stories and their complete details, including Titles, Descriptions, Acceptance Criteria, Technical Notes, Data Models, dependencies, and any other relevant context.
2. **Identify Dependencies**: If the PRD outlines dependencies between user stories, note them. You will add these as comments or task lists in the issues.
3. **Idempotency Check**: Before creating an issue, check if an issue already exists for a given user story using `gh issue list --search "in:title <User Story Title>"`. This prevents creating duplicate issues if the skill is run multiple times.
4. **Create Issues**: Loop through the extracted stories. For each uncreated story, run `gh issue create --title "<Title>" --body "<Full Details>"` and assign the appropriate labels. **Crucially, ensure the entire context for the user story from the PRD is included in the body, and append a link/reference to the PRD file (e.g., `[Original PRD](docs/PRD.md)`) so agents can easily navigate back to the full PRD.**
5. **Link Dependencies**: If there are dependencies, update the newly created issues to link them (e.g., add a comment or update the body to say "Depends on #<IssueNumber>").
6. **Link to Milestone**: Check if the user stories in the PRD are organized by milestone. If so, use that milestone name for those user stories. Otherwise, use the PRD feature name as the milestone name. The `gh issue create` command supports passing a milestone using the `--milestone "<Milestone Title>"` flag. However, the milestone must exist first. If it does not exist, you can create it using the GitHub API: `gh api repos/{owner}/{repo}/milestones -f title="<Milestone Title>"`. Note that you will need to determine the `{owner}` and `{repo}` from the context or the `gh repo view` command. Alternatively, after creating issues, you can edit them to add the milestone: `gh issue edit <issue-number> --milestone "<Milestone Title>"`.
7. **Output Mapping**: Generate a final summary mapping the PRD's User Story IDs/Titles to their new GitHub Issue Numbers and URLs. Present this to the user as an immediate reference.

## Examples

**Example 1:**
*Input:* "Create issues from tasks/prd-login.md and add them to the 'v1.0' milestone"
*Action:*
1. Read `tasks/prd-login.md`.
2. Extract US-001, US-002 with their full details.
3. Check if the milestone exists or use `gh issue create` with `--milestone "v1.0"`.
4. Check `gh issue list --search "in:title US-001"`. If it doesn't exist, run `gh issue create --title "US-001: User Login" --body "Description...<br>Acceptance Criteria...<br>[Original PRD](tasks/prd-login.md)" --label "user-story" --milestone "v1.0"`.
5. Output summary: "US-001 created as #12 (URL). US-002 created as #13 (URL)."