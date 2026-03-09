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
4. **Create Issues**: Loop through the extracted stories. For each uncreated story, format the issue body as follows:
   ```
   ## Description
   <User Story Description>

   ## Acceptance Criteria
   - [ ] <Criterion 1>
   - [ ] <Criterion 2>
   ...

   ## Technical Notes
   <Any technical details>

   ## Original PRD
   [Link to PRD](docs/PRD.md)
   ```
   Run `gh issue create --title "<Story ID>: <Title>" --body "<Formatted Body>"` and assign the label `user-story`. If there are dependencies noted from Step 2, also add them to the issue body as a "Dependencies" section.
5. **Link Dependencies**: After creating all issues, if there are dependencies between user stories, add a comment to dependent issues listing their blockers: `gh issue comment <issue-number> --body "Depends on: #<blocker-issue-number>"`.
6. **Create & Link to Milestone**:
   - Determine the milestone name: Check if the PRD explicitly organizes stories by milestone. If yes, use that name. Otherwise, use the PRD feature name.
   - Create the milestone first (ensures it exists): `gh api repos/$(gh repo view --json nameWithOwner -q) milestones -f title="<Milestone Title>"`.
   - Link all created issues to the milestone: `gh issue edit <issue-number> --milestone "<Milestone Title>"`.
7. **Output Mapping**: Generate a markdown table and present to user:
   ```
   | Story ID | Title | Issue # | URL |
   |----------|-------|---------|-----|
   | US-001 | User Login | #12 | https://github.com/.../issues/12 |
   | US-002 | User Logout | #13 | https://github.com/.../issues/13 |
   ```

## Examples

**Example 1:**
*Input:* "Create issues from tasks/prd-login.md and add them to the 'v1.0' milestone"
*Action:*
1. Read `tasks/prd-login.md`.
2. Extract US-001, US-002 with their full details.
3. Check if the milestone exists or use `gh issue create` with `--milestone "v1.0"`.
4. Check `gh issue list --search "in:title US-001"`. If it doesn't exist, run `gh issue create --title "US-001: User Login" --body "Description...<br>Acceptance Criteria...<br>[Original PRD](tasks/prd-login.md)" --label "user-story" --milestone "v1.0"`.
5. Output summary: "US-001 created as #12 (URL). US-002 created as #13 (URL)."