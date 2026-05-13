---
name: design-to-issues
description: Parses a design document to extract User Stories and creates corresponding GitHub Issues. It can optionally link them to a GitHub Milestone. This skill acts as a setup phase for GitHub-native issue tracking. Make sure to use this skill whenever the user asks to "send the design doc to GitHub", "create issues from the design doc", "setup the milestone", or mentions turning requirements into actionable GitHub issues.
metadata:
  author: eho
  version: '1.1.0'
---

# Instructions

You are acting as an autonomous sub-agent to publish reviewed, agent-ready user stories from a design document into GitHub Issues. The design document is expected to come from the `design-doc` skill and may have a companion review from `design-doc-reviewer`; treat GitHub issues as the implementation handoff, so preserve every detail an implementation agent needs without requiring it to reopen the full design doc.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## Workflow

1. **Resolve Inputs and Skill Directory**: Identify the design doc path from the user request. Resolve `SKILL_DIR` as the directory containing this `SKILL.md` from the base directory provided in the skill invocation. If no base directory is provided, locate it at `<git repo root>/.agents/skills/design-to-issues`.
2. **Check Design Readiness**: Before creating or editing GitHub issues, read the specified design doc and look for the companion review file at `docs/design/review-[original-filename].md`.
   - If a review file exists, read it and confirm the design doc has been revised after review. Strong signals include `**Status:** Revised`, a `## Revision Notes` section, or an explicit user instruction to publish despite outstanding review feedback.
   - If the review contains Critical Gaps and the design doc does not show revision notes addressing them, stop and tell the user the doc is not ready to publish to GitHub.
   - If no review file exists, warn the user that the expected `design-doc-reviewer` artifact is missing. Continue only if the user explicitly asked to publish anyway or the current request clearly says to proceed without review.
3. **Get Repository Metadata**: Run `gh repo view --json nameWithOwner,defaultBranchRef -q '{owner: .nameWithOwner, branch: .defaultBranchRef.name}'`. Use `owner` for issue URLs and `branch` for design-doc blob links. Do not assume the default branch is `main`.
4. **Parse User Stories**: Extract every story under `## User Stories` by story ID heading, e.g. `### PRI-001: Title`. Preserve each story's complete details from the design-doc contract:
   - Description and Outcome
   - Design References
   - Context, including files to read, relevant data contracts, files likely to change, dependencies, and out-of-scope boundaries
   - Acceptance Criteria, including verification commands, test requirements, browser checks, and documentation decisions
   - Any Technical Notes or other story-specific implementation context
5. **Setup Labels**: Before creating any issues, verify the `user-story` label exists and that a label for the specific feature prefix (e.g., `PRI`) exists. Prefer JSON output over text matching:
   ```bash
   gh label list --limit 1000 --json name -q '.[].name'
   gh label create "user-story" --color "0e8a16" --description "User story task"
   gh label create "<prefix>" --color "1d76db" --description "Feature prefix: <prefix>"
   ```
   Only create labels that are missing. If a create command reports that the label already exists, continue.
6. **Build an Issue Map for Idempotency**: Before creating issues, build a complete `story_id -> issue_number/url/title/status` map for all extracted stories. For each story ID, search open and closed issues using the story ID as the stable key, not only the title:
   ```bash
   gh issue list --state all --label "user-story" --search "<Story ID> in:title" --json number,title,url,state -q '.[]'
   ```
   Reuse an existing issue only when its title starts with `<Story ID>:`. If more than one matching issue exists, stop and ask the user to resolve the duplicate before publishing.
7. **Create Missing Issues**: Loop through the extracted stories. For each story missing from the issue map, construct a GitHub blob URL to the design doc using the repository's default branch, then create an issue whose body faithfully carries the full story content:
   ```
   ## Story
   <The complete story content from the design doc, normalized only enough to render cleanly in GitHub Markdown>

   ## Implementation Context
   <Files to read, relevant data contracts, files likely to change, dependencies, and out-of-scope boundaries>

   ## Acceptance Criteria
   <The exact checklist from the design doc, including verification, tests, browser checks, and documentation requirements>

   ## Design Doc
   [View in Design Doc](https://github.com/<owner>/<repo>/blob/<default-branch>/<design-doc-path>)
   ```
   The issue body may include additional sections such as `## Outcome`, `## Design References`, `## Dependencies`, or `## Technical Notes` when present in the story. Do not omit fields from the design-doc story contract.

   Run the bundled script to create the issue safely. Capture its output to extract the issue number and URL, then add the new issue to the same issue map used for existing issues.
   **Script location:** The script is at `SKILL_DIR/scripts/create_issue.sh`, where `SKILL_DIR` is the directory containing this SKILL.md file. Resolve it using the base directory provided at the top of the skill invocation (look for "Base directory for this skill:"). If not available, locate it at `<git repo root>/.agents/skills/design-to-issues/scripts/create_issue.sh`.
   ```bash
   # Use a temporary file for the body to keep the command clean and avoid shell escaping issues
   SKILL_DIR="<base directory from skill invocation>"
   cat <<'EOF' > issue_body.md
   ## Description
   ...
   EOF

   OUTPUT=$("$SKILL_DIR/scripts/create_issue.sh" "<Story ID>: <Title>" "user-story,<prefix>" issue_body.md)
   ISSUE_NUMBER=$(echo "$OUTPUT" | grep "Issue Number:" | awk '{print $3}')
   ISSUE_URL=$(echo "$OUTPUT" | grep "Created Issue:" | sed 's/^Created Issue: //')
   rm issue_body.md
   ```
8. **Link Dependencies**: After the issue map contains both existing and newly created issues, add dependency comments to dependent issues listing their blockers. Use story IDs from the design doc to look up issue numbers in the map:
   ```bash
   gh issue comment <dependent-issue-number> --body "Depends on: #<blocker-issue-number>"
   ```
   For example: `gh issue comment 43 --body "Depends on: #42"`. If a dependency points to a story ID that was not extracted or mapped, stop and report the missing dependency instead of creating partial links.
9. **Create & Link to Milestone**:
   - Determine the milestone name: Check if the design doc explicitly organizes stories by milestone. If yes, use that name. Otherwise, use the feature name from the doc title.
   - Create the milestone first (ensures it exists): `"$SKILL_DIR/scripts/create_milestone.sh" "<Milestone Title>"` (where `SKILL_DIR` is the base directory from the skill invocation; if not available, locate it at `<git repo root>/.agents/skills/design-to-issues/scripts/create_milestone.sh`).
   - Link all mapped issues, existing and newly created, to the milestone: `gh issue edit <issue-number> --milestone "<Milestone Title>"`.
10. **Output Mapping**: Generate a markdown table and present to user:
   ```
   | Story ID | Title | Issue # | Status | URL |
   |----------|-------|---------|--------|-----|
   | PRI-001 | User Login | #12 | Existing | https://github.com/.../issues/12 |
   | PRI-002 | User Logout | #13 | Created | https://github.com/.../issues/13 |
   ```
   Include the milestone name and note whether dependencies were linked.

## Available Scripts

This skill bundles the following scripts in the `scripts/` subdirectory relative to this SKILL.md file:

- `create_issue.sh "<title>" "<labels>" "<body_file_path>"`: Safely executes `gh issue create` and extracts the issue number.
- `create_milestone.sh "<milestone_title>"`: Safely executes `gh api` to create a new milestone.

## Examples

**Example 1:**
*Input:* "Create issues from docs/design/login.md and add them to the 'v1.0' milestone"
*Action:*
1. Read `docs/design/login.md` and `docs/design/review-login.md`. Continue only if the review is absent by explicit user instruction, or if review feedback has been addressed in the design doc.
2. Get repo info: `gh repo view --json nameWithOwner,defaultBranchRef -q '{owner: .nameWithOwner, branch: .defaultBranchRef.name}'` → returns owner `myorg/myapp` and branch `trunk`.
3. Setup labels from `gh label list --limit 1000 --json name -q '.[].name'`. Ensure `user-story` and `LOGIN` exist.
4. Extract LOGIN-001 (Login), LOGIN-002 (Logout) with dependencies: LOGIN-002 depends on LOGIN-001.
5. Search for existing issues by story ID: `gh issue list --state all --label "user-story" --search "LOGIN-001 in:title" --json number,title,url,state`.
6. Create any missing issue, preserving the full story content:
   ```bash
   cat <<'EOF' > issue_body.md
   ## Story
   **Description:** As a user, I want to log in so that I can access my account.

   **Outcome:** Authenticated users receive an active session.

   **Design References:**
   - Architecture Overview: Login form posts credentials to the auth endpoint.
   - API & Data Contracts: `LoginRequest`, `LoginResponse`
   - Integration Points: `src/auth/login.ts`, `src/auth/session.ts`

   ## Implementation Context
   - Files to read: `src/auth/login.ts`, `src/auth/session.ts`
   - Relevant data contracts: `LoginRequest`, `LoginResponse`
   - Files likely to change: `src/auth/login.ts`
   - Depends on: None
   - Out of scope: Password reset

   ## Acceptance Criteria
   - [ ] Form validates email in `src/auth/login.ts`
   - [ ] Form validates password in `src/auth/login.ts`
   - [ ] Typecheck passes using `bun run build`
   - [ ] Unit tests cover invalid email and invalid password in `src/auth/login.test.ts`
   - [ ] Documentation impact: None, because this changes internal validation only

   ## Design Doc
   [View in Design Doc](https://github.com/myorg/myapp/blob/trunk/docs/design/login.md)
   EOF

   OUTPUT=$("$SKILL_DIR/scripts/create_issue.sh" "LOGIN-001: User Login" "user-story,LOGIN" issue_body.md)
   ISSUE_NUMBER=$(echo "$OUTPUT" | grep "Issue Number:" | awk '{print $3}')
   ISSUE_URL=$(echo "$OUTPUT" | grep "Created Issue:" | sed 's/^Created Issue: //')
   rm issue_body.md
   ```
7. Add every existing and created issue to the issue map, then comment on LOGIN-002: `gh issue comment 43 --body "Depends on: #42"`.
8. Create milestone `v1.0` and link both issues, including any that already existed.
9. Output summary:
   ```
   | Story ID | Title | Issue # | Status | URL |
   |----------|-------|---------|--------|-----|
   | LOGIN-001 | User Login | #42 | Existing | https://github.com/myorg/myapp/issues/42 |
   | LOGIN-002 | User Logout | #43 | Created | https://github.com/myorg/myapp/issues/43 |
   ```
