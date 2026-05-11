---
name: user-story-implementer
description: Implement one specific user story or task from a GitHub Issue backlog, usually identified by a story ID such as USERST-001 or an issue number. Assigns the issue, implements the acceptance criteria, verifies the change, commits, pushes, and creates a PR. You MUST use this skill when asked to "implement USERST-001", "implement a user story", "run one iteration", "do the next task", or "complete a task from the backlog".
metadata:
  author: eho
  version: '2.0.1'
---

# Instructions

You are acting as an autonomous sub-agent to implement a user story or task managed via GitHub Issues.

Your objective is to complete exactly **one** user story or task from the GitHub repository, verify its acceptance criteria, push the changes to the appropriate feature branch, and create or update a Pull Request. For new implementation work, create a new branch and PR. For requested revisions to an existing PR, check out that PR branch, commit fixes there, and push to the same PR.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## Workflow

1. **Identify the Target Story**: Prefer the specific story ID or issue number supplied by the user.
   - If the user provides an issue number, run `gh issue view <issue-number> --json number,title,state,body,comments,labels,assignees,url`.
   - If the user provides a story ID such as `USERST-001`, search for the matching issue:
     ```bash
     gh issue list --state all --search "USERST-001" --json number,title,state,body,labels,assignees,url --limit 20
     ```
     Use the issue whose title or body clearly contains that exact story ID. If no issue or multiple plausible issues match, ask the user to identify the intended issue before writing code.
   - If the user explicitly asks for the next task within a feature prefix or label (e.g., `AUTH`), run `gh issue list --label "user-story" --label "<prefix>" --limit 10 --search "sort:created-asc" --json number,title,state,body,labels,assignees,url`.
   - If the user explicitly asks for the next task in a milestone, run `gh issue list --label "user-story" --milestone "<milestone-name>" --limit 10 --search "sort:created-asc" --json number,title,state,body,labels,assignees,url`.
   - If no story ID, issue number, prefix, label, or milestone is provided, ask the user to provide the target story ID or issue number. Avoid guessing across unrelated design docs.
   - Only check current-user PRs with changes requested when the user asks for an unspecified "next task" or "run one iteration". For a specific story ID or issue number, stay focused on that target unless its own PR already exists and needs revision.
2. **Validate Availability and Blockers**: Before editing files, make sure this issue is available to implement.
   - Stop if the issue is closed unless the user explicitly asked to revise a closed issue.
   - Skip or stop if the issue has a `blocked` label.
   - If the issue is assigned to someone other than the current GitHub user, stop and report who owns it.
   - Read both the issue body and comments for dependency markers such as `Depends on #123`, `Depends on: #123`, dependency task lists, or a `Dependencies` section. For each dependency, run `gh issue view <dependency-number> --json state -q '.state'`. If any dependency is still open, stop and report the blocker.
   - Check whether there is already an open PR for this issue or story ID using `gh pr list --state open --search "<story-id-or-issue-number>" --json number,title,headRefName,url --limit 20`. If a matching PR exists, check out that branch and continue there instead of creating a duplicate PR.
   - Once the target issue is validated, note the issue number, title, URL, body, and every Acceptance Criterion.
3. **State Management**: Before starting work, assign the issue to yourself (or the current user) using `gh issue edit <issue-number> --add-assignee "@me"`. This provides visibility and prevents conflicts.
4. **Branching**: Follow standard Git flow.
   - Run `git status --short` first. Do not overwrite unrelated local changes.
   - Base work on the repository's default branch unless continuing an existing PR branch.
   - Create and check out a branch based on the issue number and title, such as `feature/us-<issue-number>-short-title`.
   - If the branch already exists locally or remotely, resume it only when it clearly belongs to the same issue. Otherwise create a unique branch name.
5. **Reconnaissance**: Before making changes, inspect the codebase enough to understand the intended implementation.
   - Read the issue body, linked design doc, context paths, technical notes, and related files referenced by the issue.
   - Inspect existing tests, nearby code, package scripts, and project conventions before adding new abstractions or dependencies.
   - Identify the smallest coherent implementation that satisfies the acceptance criteria without widening scope.
6. **Execute**: Implement the code, configuration, or documentation changes required to complete that single user story.
   - Ensure you fulfill all of the listed Acceptance Criteria in the GitHub issue body.
   - Add or update focused tests for behavior changes. If tests are not appropriate for this story, state why in the PR and perform the strongest available verification.
   - For UI stories, run the app when practical and verify meaningful layout, navigation, form, or interaction changes in a browser.
   - Update relevant user-facing documentation when the story changes commands, options, UI behavior, APIs, or setup steps.
   - Add or preserve diagnostic logging only where the project already logs comparable operations or where failures would otherwise be hard to diagnose. Do not log secrets, tokens, personal data, or noisy high-volume client interactions.
   - If requirements are missing, product decisions are ambiguous, credentials or external services are unavailable, dependency issues block the work, or the scope cannot fit into one coherent issue, move to step 7 instead of guessing.
7. **Handling Blockers**: If you encounter missing requirements, ambiguity, or blockers that prevent completion, add a comment to the issue detailing the blocker using `gh issue comment <issue-number> --body "<Details>"`, add a `blocked` label using `gh issue edit <issue-number> --add-label "blocked"`, and stop work on this issue.
8. **Self-Review**: Before considering the task complete, perform this specific checklist:
   - [ ] For each Acceptance Criterion listed in the issue, is there code implementing it? (Check each one individually.)
   - [ ] Are focused tests added or updated for behavior changes, or is the reason for no tests documented?
   - [ ] Do the tests exercise the core feature rather than only superficial rendering or wiring?
   - [ ] Do tests or manual verification cover the happy path and relevant error or edge cases?
   - [ ] Were the appropriate verification commands run locally, and did they pass?
   - [ ] If diagnostics or docs were relevant, were they updated without adding noise or leaking sensitive data?
   - If all checkboxes pass, proceed to step 9. If any fail, return to step 6 to address gaps.
9. **Commit Code**: Once your user story or chunk is complete, you must commit your changes to your feature branch.
   - Do not use `git commit -a`. Select files manually.
10. **Pull Request & Linking**:
   - Push the branch: `git push -u origin HEAD`.
   - If this is revision work on an existing PR, do not create a second PR. Push the commit to the existing PR branch and report the existing PR URL.
   - If no matching PR exists yet, create a Pull Request using the bundled script to ensure clean formatting and avoid agent shell warnings.
     The `scripts/` directory is a sibling of this SKILL.md file. Resolve its absolute path and call:
     ```bash
     bash /absolute/path/to/scripts/create_pr.sh "<issue-number>" "feat: <issue-title>" "<Summary of work done>"
     ```
     Use the appropriate conventional commit prefix (`feat:`, `fix:`, `docs:`, etc.). The script automatically includes `Closes #<issue-number>` so merging the PR automatically closes the issue.

## Final Response and Handoffs

Always end with a concise implementation summary that includes the story, issue, branch, PR, verification performed, and any blocker or residual risk.

If the caller requests a specific handoff format, such as the `Implementation Handoff` used by the `user-story-delivery` coordinator, return that format exactly in the final response. The handoff is a reporting format only; it does not change this skill's implementation, verification, commit, push, or PR-linking requirements.

For revision work requested by a reviewer or coordinator, include the review findings addressed:

```markdown
## Implementation Handoff
- Story ID:
- Issue:
- Branch:
- PR:
- Review findings addressed:
- Verification:
- Known residual risk:
- Blocked: yes/no
```

## Available Scripts

This skill bundles the following scripts in the `scripts/` subdirectory relative to this SKILL.md file:

- `create_pr.sh "<issue_number>" "<issue_title>" "<summary_of_work>"`: Safely executes `gh pr create` with multi-line bodies to avoid shell escaping errors.

## Examples

**Example 1:**
*Input:* "Implement USERST-001"
*Action:*
1. Search for the matching issue: `gh issue list --state all --search "USERST-001" --json number,title,state,body,labels,assignees,url --limit 20`. Confirm the exact story ID appears in the title or body.
2. Read the issue body and comments, check dependencies, blocked labels, assignees, and existing PRs.
3. Assign: `gh issue edit 12 --add-assignee "@me"`.
4. Branch: `git checkout -b feature/us-12-add-priority-selector`.
5. Read referenced context, nearby implementation files, and existing tests.
6. Implement the feature and add focused tests or documented verification.
7. Review the code against every Acceptance Criterion in Issue #12.
8. Commit: `git add src/components/TaskEdit.tsx src/components/TaskEdit.test.tsx` and `git commit -m "feat: add priority selector (USERST-001)"`.
9. Push: `git push -u origin HEAD`.
10. Create PR (resolve absolute path to `scripts/` sibling of this SKILL.md, e.g. `/path/to/skills/user-story-implementer/scripts/create_pr.sh`):
   ```bash
   bash /path/to/skills/user-story-implementer/scripts/create_pr.sh "12" "feat: Add priority selector" "Added priority selector to task edit."
   ```
