---
name: prd-to-github-milestone
description: Parses a design document to extract User Stories and creates corresponding GitHub Issues. It can optionally link them to a GitHub Milestone. This skill acts as a setup phase for GitHub-native issue tracking. Make sure to use this skill whenever the user asks to "send the design doc to GitHub", "create issues from the design doc", "send the PRD to GitHub", "create issues from the PRD", "setup the milestone", or mentions turning requirements into actionable GitHub issues.
metadata:
  author: eho
  version: '1.0.0'
---

# Instructions

You are acting as an autonomous sub-agent to parse a design document (which contains user stories) and scaffold a GitHub milestone by creating GitHub Issues for each user story.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## Workflow

1. **Setup Labels**: Before creating any issues, verify the `user-story` label exists and that a label for the specific feature prefix (e.g., `PRI`) exists. Run `gh label list --limit 1000 | grep "user-story"`. If not found, create it: `gh label create "user-story" --color "0e8a16" --description "User story task"`. Repeat this check and creation process for the PRD's specific prefix if applicable: `gh label create "<prefix>" --color "1d76db"`.
2. **Parse Design Doc**: Read the specified design document (e.g., `docs/design/[feature].md`). Extract all User Stories and their complete details, including Titles, Descriptions, Acceptance Criteria, Context (file paths, data contracts), Technical Notes, dependencies, the feature prefix, and any other relevant context.
3. **Identify Dependencies**: If the PRD outlines dependencies between user stories, note them. You will add these as comments or task lists in the issues.
4. **Idempotency Check**: Before creating an issue, check if an issue already exists for a given user story using `gh issue list --search "in:title <User Story Title>"`. This prevents creating duplicate issues if the skill is run multiple times.
5. **Create Issues**: Loop through the extracted stories. For each uncreated story, construct a GitHub blob URL to the design doc. Get the repo info with `gh repo view --json nameWithOwner -q` (format: `owner/repo`), then format the issue body:
   ```
   ## Description
   <User Story Description>

   ## Context
   <Files to read and relevant data contracts from the story's Context section>

   ## Acceptance Criteria
   - [ ] <Criterion 1>
   - [ ] <Criterion 2>
   ...

   ## Technical Notes
   <Any technical details>

   ## Design Doc
   [View in Design Doc](https://github.com/<owner>/<repo>/blob/main/<design-doc-path>)
   ```
   Example: `https://github.com/eho/test-example/blob/main/docs/design/auth-token-refresh.md`

   Run the bundled script to create the issue safely. Capture its output to extract the issue number for dependency linking in Step 6.
   **Script location:** The script is at `SKILL_DIR/scripts/create_issue.sh`, where `SKILL_DIR` is the directory containing this SKILL.md file. Resolve it using the base directory provided at the top of the skill invocation (look for "Base directory for this skill:"). If not available, locate it at `<git repo root>/.agents/skills/prd-to-github-milestone/scripts/create_issue.sh`.
   ```bash
   # Use a temporary file for the body to keep the command clean and avoid shell escaping issues
   SKILL_DIR="<base directory from skill invocation>"
   cat <<'EOF' > issue_body.md
   ## Description
   ...
   EOF

   OUTPUT=$("$SKILL_DIR/scripts/create_issue.sh" "<Story ID>: <Title>" "user-story,<prefix>" issue_body.md)
   ISSUE_NUMBER=$(echo "$OUTPUT" | grep "Issue Number:" | awk '{print $3}')
   rm issue_body.md
   ```
   If there are dependencies noted from Step 3, add them to the issue body as a "Dependencies" section, or add a comment later once all issues are created.
6. **Link Dependencies**: After creating all issues, if there are dependencies between user stories, add comments to dependent issues listing their blockers. Use the captured issue numbers from Step 5:
   ```bash
   gh issue comment <dependent-issue-number> --body "Depends on: #<blocker-issue-number>"
   ```
   For example: `gh issue comment 43 --body "Depends on: #42"`
7. **Create & Link to Milestone**:
   - Determine the milestone name: Check if the design doc explicitly organizes stories by milestone. If yes, use that name. Otherwise, use the feature name from the doc title.
   - Create the milestone first (ensures it exists): `"$SKILL_DIR/scripts/create_milestone.sh" "<Milestone Title>"` (where `SKILL_DIR` is the base directory from the skill invocation; if not available, locate it at `<git repo root>/.agents/skills/prd-to-github-milestone/scripts/create_milestone.sh`).
   - Link all created issues to the milestone: `gh issue edit <issue-number> --milestone "<Milestone Title>"`.
8. **Output Mapping**: Generate a markdown table and present to user:
   ```
   | Story ID | Title | Issue # | URL |
   |----------|-------|---------|-----|
   | PRI-001 | User Login | #12 | https://github.com/.../issues/12 |
   | PRI-002 | User Logout | #13 | https://github.com/.../issues/13 |
   ```

## Available Scripts

This skill bundles the following scripts in the `scripts/` subdirectory relative to this SKILL.md file:

- `create_issue.sh "<title>" "<labels>" "<body_file_path>"`: Safely executes `gh issue create` and extracts the issue number.
- `create_milestone.sh "<milestone_title>"`: Safely executes `gh api` to create a new milestone.

## Examples

**Example 1:**
*Input:* "Create issues from docs/design/login.md and add them to the 'v1.0' milestone"
*Action:*
1. Setup labels: `gh label list --limit 1000 | grep "user-story"`. If not found, run `gh label create "user-story" --color "0e8a16"`. Extract the prefix (`LOGIN` from `docs/design/login.md`), then check and create it: `gh label create "LOGIN" --color "1d76db"`.
2. Read `docs/design/login.md`.
3. Extract LOGIN-001 (Login), LOGIN-002 (Logout) with dependencies: LOGIN-002 depends on LOGIN-001.
4. Get repo info: `gh repo view --json nameWithOwner -q` → returns `myorg/myapp`.
5. Create issue for LOGIN-001:
   ```bash
   cat <<'EOF' > issue_body.md
   ## Description
   User should be able to log in...

   ## Acceptance Criteria
   - [ ] Form validates email
   - [ ] Form validates password

   ## Design Doc
   [View in Design Doc](https://github.com/myorg/myapp/blob/main/docs/design/login.md)
   EOF

   OUTPUT=$("$SKILL_DIR/scripts/create_issue.sh" "LOGIN-001: User Login" "user-story,LOGIN" issue_body.md)
   # Extract the ISSUE_NUMBER output by the script for dependency linking
   ISSUE_NUMBER=$(echo "$OUTPUT" | grep "Issue Number:" | awk '{print $3}')
   rm issue_body.md
   ```
6. Create issue for LOGIN-002 (with dependency noted):
   ```bash
   cat <<'EOF' > issue_body.md
   ## Description
   User should be able to log out...

   ## Dependencies
   - Depends on #42 (User Login)

   ## Design Doc
   [View in Design Doc](https://github.com/myorg/myapp/blob/main/docs/design/login.md)
   EOF

   "$SKILL_DIR/scripts/create_issue.sh" "LOGIN-002: User Logout" "user-story,LOGIN" issue_body.md
   rm issue_body.md
   ```
7. Create milestone `v1.0` and link both issues.
8. Output summary:
   ```
   | Story ID | Title | Issue # | URL |
   |----------|-------|---------|-----|
   | LOGIN-001 | User Login | #42 | https://github.com/myorg/myapp/issues/42 |
   | LOGIN-002 | User Logout | #43 | https://github.com/myorg/myapp/issues/43 |
   ```