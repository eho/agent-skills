---
name: user-story-implementer
description: Implement a single user story or task from a GitHub Issue backlog. Executes a single iteration by fetching the next open issue, assigning it, implementing the code, creating a branch and PR, and moving on. You MUST use this skill when asked to "implement a user story", "run one iteration", "do the next task", or "complete a task from the backlog".
metadata:
  author: eho
  version: '2.0.0'
---

# Instructions

You are acting as an autonomous sub-agent to implement a user story or task managed via GitHub Issues.

Your objective is to complete exactly **one** user story or task from the GitHub repository, verify its acceptance criteria, push the changes in a new branch, and create a Pull Request.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## Workflow

1. **Identify the Next Task**: Check if the user specified a specific feature prefix, label, milestone, or issue number.
   - If a specific issue number is provided, use `gh issue view <issue-number>`.
   - If a specific feature prefix or label is provided (e.g., `PRI`), run `gh issue list --label "user-story" --label "<prefix>" --limit 1 --search "sort:created-asc"`.
   - If a milestone is provided, use `gh issue list --label "user-story" --milestone "<milestone-name>" --limit 1 --search "sort:created-asc"`.
   - If no specific scope is provided, you MUST ask the user to clarify which feature prefix, milestone, or issue number they want to work on to avoid picking up tasks from unrelated PRDs.
   - Once the next available issue is identified, note the issue number, title, and body (which contains the Acceptance Criteria).
2. **State Management**: Before starting work, assign the issue to yourself (or the current user) using `gh issue edit <issue-number> --add-assignee "@me"`. This provides visibility and prevents conflicts.
3. **Branching**: Follow standard Git flow. Create and checkout a new branch based on the issue number: `git checkout -b feature/us-<issue-number>`.
4. **Execute**: Implement the code, configuration, or changes required to complete that single user story.
   - Ensure you fulfill all of the listed Acceptance Criteria in the GitHub issue body.
   - Write unit tests or perform browser verification if required.
   - Update any relevant documentation.
   - **Important**: If you cannot complete the entire story within ~2 hours of effort, or if you identify missing requirements or technical blockers during implementation, do NOT continue. Move to step 5 (Handling Blockers) instead.
5. **Handling Blockers**: If you encounter missing requirements, ambiguity, or blockers that prevent completion, add a comment to the issue detailing the blocker using `gh issue comment <issue-number> --body "<Details>"`, add a `blocked` label using `gh issue edit <issue-number> --add-label "blocked"`, and stop work on this issue.
6. **Self-Review**: Before considering the task complete, perform this specific checklist:
   - [ ] For each Acceptance Criterion listed in the issue, is there code implementing it? (Check each one individually.)
   - [ ] Are there new tests? Run them locally to verify they pass.
   - [ ] Do the tests exercise the core feature (not just superficial checks)?
   - [ ] Do the tests cover the happy path AND relevant error cases?
   - If all checkboxes pass, proceed to step 7. If any fail, return to step 4 to address gaps.
7. **Commit Code**: Once your user story or chunk is complete, you must commit your changes to your feature branch.
   - Do not use `git commit -a`. Select files manually.
8. **Pull Request & Linking**:
   - Push the branch: `git push -u origin HEAD`.
   - Create a Pull Request using the bundled script to ensure clean formatting and avoid agent shell warnings.
     **Script location:** The script is at `SKILL_DIR/scripts/create_pr.sh`, where `SKILL_DIR` is the directory containing this SKILL.md file. Resolve it using the base directory provided at the top of the skill invocation (look for "Base directory for this skill:"). Example:
     ```bash
     SKILL_DIR="<base directory from skill invocation>"
     "$SKILL_DIR/scripts/create_pr.sh" "<issue-number>" "feat: <issue-title>" "<Summary of work done>"
     ```
     If the base directory is not available, locate the script at `<git repo root>/.agents/skills/user-story-implementer/scripts/create_pr.sh`.
     Use the appropriate conventional commit prefix (`feat:`, `fix:`, `docs:`, etc.). The script automatically includes `Closes #<issue-number>` so merging the PR automatically closes the issue.

## Available Scripts

This skill bundles the following scripts in the `scripts/` subdirectory relative to this SKILL.md file:

- `create_pr.sh "<issue_number>" "<issue_title>" "<summary_of_work>"`: Safely executes `gh pr create` with multi-line bodies to avoid shell escaping errors.

## Examples

**Example 1:**
*Input:* "Implement the next task for the PRI feature"
*Action:*
1. The user specified the "PRI" feature prefix. Run `gh issue list --label "user-story" --label "PRI" --limit 1 --search "sort:created-asc"`. Returns Issue #12: "Add priority selector".
2. Assign: `gh issue edit 12 --add-assignee "@me"`.
3. Branch: `git checkout -b feature/us-12`.
4. Implement the feature and write tests.
5. Review the code to ensure it meets Acceptance Criteria in Issue #12.
6. Commit: `git add src/components/TaskEdit.tsx` and `git commit -m "feat: add priority selector (US-002)"`.
7. Push: `git push -u origin HEAD`.
8. Create PR (using SKILL_DIR from "Base directory for this skill:" header):
   ```bash
   "$SKILL_DIR/scripts/create_pr.sh" "12" "feat: Add priority selector" "Added priority selector to task edit."
   ```