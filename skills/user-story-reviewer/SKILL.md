---
name: user-story-reviewer
description: Review an implemented user story or task (via GitHub Pull Request) for completeness, test coverage, and code quality. Use this when asked to QA, review a PR, verify implementation, review a user story like USERST-001, or as a follow-up to the user-story-implementer skill.
metadata:
  author: eho
  version: '2.3.1'
---

# User Story Reviewer

You are acting as an autonomous QA and code review sub-agent. Your job is to thoroughly review a recently implemented user story (submitted as a Pull Request) against its original requirements in the linked GitHub Issue. The user story identifier, such as `USERST-001`, is the primary input and traceability anchor.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) for this skill to function.

## The Objective

Too often, implementations miss subtle acceptance criteria, lack meaningful test coverage, or fail to update documentation. Your objective is to proactively identify such gaps. Review with the discipline of a code reviewer first: lead with concrete findings, ground them in evidence, and prioritize bugs, regressions, missing tests, security risks, data loss, and acceptance-criteria gaps. You will not approve a Pull Request until it fully passes all checks.

## Workflow

1. **Identify the Target PR**:
   - Require a user story identifier such as `USERST-001`. If the user did not provide one, ask for it before reviewing.
   - If the user also specified a PR number or URL, use it only after confirming the PR references the same story identifier in its title, body, branch name, linked issue, or commits.
   - Otherwise, find the PR by searching for the story identifier:
     ```bash
     gh pr list --state open --search "USERST-001" --json number,title,isDraft,headRefName,body,author,reviewDecision,statusCheckRollup,mergeStateStatus,url --limit 20
     ```
   - If no PR is found, or multiple plausible PRs are found, stop and ask the user to identify the intended PR. Do not fall back to the oldest open PR.
2. **Preflight the PR**:
   - Inspect PR metadata before reviewing:
     ```bash
     gh pr view <pr-number> --json number,title,body,author,isDraft,headRefName,baseRefName,files,commits,closingIssuesReferences,reviewDecision,statusCheckRollup,mergeStateStatus,url
     gh pr checks <pr-number>
     ```
   - Stop if the PR is a draft, does not reference the requested story identifier, or has no reliable requirements source. Report the blocker clearly.
   - If CI/checks are failing or pending, you may still review the code, but the Decision cannot be `Approve` or `Merge` until checks are passing or the user explicitly accepts the risk.
3. **Read the Requirements (The Issue)**:
   - Identify the linked issue using `closingIssuesReferences` first. Also check PR title, body, branch name, and commits for the story identifier. PR bodies may use `Closes`, `Fixes`, `Resolves`, full GitHub URLs, or multiple issue references.
   - If the PR metadata does not expose the linked issue, search issues for the story identifier:
     ```bash
     gh issue list --state all --search "USERST-001" --json number,title,state,body,url --limit 20
     ```
   - Run `gh issue view <issue-number>` to read the original user story description and **every single Acceptance Criterion**.
   - If multiple issues match, or no issue contains clear acceptance criteria, stop and ask for the intended issue or requirements source.
4. **Analyze the Implementation**: Review the code changes made in the Pull Request.
   - Run `gh pr diff <pr-number>` to view the changes.
   - For anything beyond a trivial documentation-only change, checkout the PR branch locally (`gh pr checkout <pr-number>`) so you can inspect changed files in context, nearby call sites, existing tests, configuration, migrations, generated types, and runtime behavior.
   - Do not rely on the diff alone when the change touches shared code, data models, auth, persistence, UI behavior, build configuration, or public APIs.
5. **Conduct the Review**: Evaluate the implementation across the key dimensions (see Review Dimensions below). Produce the Review Output before taking action. Findings come first, ordered by severity, and each finding should be grounded in a file/line reference or diff hunk when code evidence exists.
6. **Report & Fix**:
   - If there are NO gaps, proceed to step 7.
   - If there ARE gaps:
     - First record the issue as a review finding.
     - **Request changes by default** if the gap affects acceptance criteria, behavior, architecture, data safety, security, compatibility, or test confidence. Write the detailed review to a file and run `gh pr review <pr-number> --request-changes --body-file <file>`.
     - **Fix yourself only after choosing the `Fix small issue` Decision** and only if the gap is small, mechanical, low-risk, and clearly within the reviewer workflow (e.g., missing focused test, typo in comment, adding 1-2 obvious lines of code). Checkout the PR branch with `gh pr checkout <pr-number>`, make the fix, commit with `git add <specific-files>` (not `git add .`), and push. Call out the fix commit in the review.
   - If you request changes, stop after posting the review and final response. Do not continue toward approval until a follow-up review is requested.
7. **Sign off (Approve or Merge)**: Determine if you are the author of the PR. GitHub prevents users from approving their own PRs, so self-authored PRs should be handled by leaving a comment review and then merging once there are no blocking findings and CI/checks are passing. If you are not the author, formally approve the PR. The bundled script handles this logic automatically: current-user PRs are comment-and-merge by default, while non-current-user PRs receive an approval review.

   **Review comment**: Before approving or merging, write a specific, self-documenting review comment. Do NOT use generic statements like "All acceptance criteria met." Instead:
   - Summarize what was verified — list the key acceptance criteria checked and confirm each passed.
   - Call out any fixes made — if you fixed a gap, describe what was wrong and how you resolved it (include the commit hash).
   - Note anything worth flagging — edge cases covered, design decisions observed, minor concerns that don't block approval, residual risks, or anything not verified.

   **Script usage**: Write your detailed review comment to a temporary text file (e.g., `review_comment.txt`). Then, call the bundled script passing the PR number and the path to your comment file.

   The `scripts/` directory is a sibling of this SKILL.md file. Resolve its absolute path and call:
   ```bash
   echo "My detailed review comment..." > review_comment.txt
   bash /absolute/path/to/scripts/approve_or_merge_pr.sh <pr-number> review_comment.txt
   rm review_comment.txt
   ```

   To leave a comment-only sign-off without merging a current-user PR, pass `--comment-only`:
   ```bash
   bash /absolute/path/to/scripts/approve_or_merge_pr.sh <pr-number> review_comment.txt --comment-only
   ```

## Review Output

Before approving, requesting changes, fixing, or merging, produce this structure. Keep it concise, but make the judgment auditable.

### Findings
- Lead with findings, ordered by severity.
- Prioritize bugs, behavioral regressions, acceptance-criteria gaps, missing tests, security risks, data loss, permission/auth mistakes, lifecycle/state issues, migrations, concurrency, and performance risks.
- For each code finding, include:
  - File path and line number, or a precise diff hunk reference if line numbers are unavailable.
  - What is wrong.
  - Why it matters to the user story, existing behavior, or system safety.
  - What should change.
- If there are no blocking findings, say: `No blocking findings found.`

### Open Questions
- Include only questions that affect correctness, acceptance, or approval.
- If there are none, say: `None.`

### Verification
- List the acceptance criteria checked and whether each passed.
- List commands, tests, type checks, lint checks, browser checks, or manual inspections performed.
- State anything not verified and the residual risk. Do not imply unrun tests passed.
- Include PR preflight status: story identifier matched, linked issue found, draft status, CI/check status, and whether the PR branch was checked out locally.

### Decision
- Choose one: `Request changes`, `Fix small issue`, `Approve`, `Comment only`, or `Merge`.
- Explain the decision in one or two sentences.

## Final Response and Handoffs

The Review Output is always required before approving, requesting changes, fixing, or merging. After completing the selected review action, end with a concise final response that includes the PR, final decision, blocking findings count, verification performed, and any required follow-up.

If the caller requests a specific handoff format, such as the `Review Handoff` used by the `user-story-delivery` coordinator, return that format exactly in the final response after the review action is complete. The handoff is a reporting format only; it does not replace the Review Output or change the review, approval, request-changes, or merge rules.

Use `Decision` in the handoff to report the final state after the review action:

- `Request changes`: blocking findings were posted and follow-up implementation is required.
- `Fix small issue`: the reviewer pushed a small fix, but did not approve, comment-only sign off, or merge in this run.
- `Approve`: the PR was approved.
- `Comment only`: a non-approval sign-off comment was left.
- `Merge`: the PR was merged.

```markdown
## Review Handoff
- Story ID:
- PR:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Required follow-up:
- Verification:
```

## Review Dimensions

### 1. Requirements & Implementation Alignment
- Does the implementation fully solve the problem outlined in the user story description?
- Walk through **each individual Acceptance Criterion**. Does the codebase strictly satisfy every single one?
- Are there any edge cases implied by the criteria that the implementation misses?
- Does the implementation preserve existing behavior outside the story's scope?

### 2. Test Coverage & Quality
- Are there newly added unit, integration, or browser tests?
- Do the tests *actually* exercise the core logic of the new feature, or are they superficial?
- Do the tests cover both the "happy path" and relevant error/edge cases?
- Run the tests locally to ensure they actually pass.
- **UI stories**: If the change affects meaningful UI behavior, layout, navigation, forms, visual state, or interaction, spin up the local dev server and use the available browser tool to visually verify the behavior. Do not skip this — automated tests alone are insufficient for visual QA.
- If no tests were added, explicitly judge whether that is acceptable and state the residual risk.

### 3. Documentation & Code Quality
- **Documentation**: Check if the project has a README, API docs, or user guide. If this feature adds user-facing functionality (new command, option, UI element, etc.), those docs MUST be updated. If it's an internal refactor or non-user-facing change, documentation updates are optional.
- Is the code clean, readable, and following the project's established style guidelines?
- Did the implementation introduce any obvious security or performance issues?
- Are there data loss, permission, auth, state lifecycle, migration, concurrency, or rollback risks?

## Available Scripts

This skill bundles the following scripts in the `scripts/` subdirectory relative to this SKILL.md file:

- `approve_or_merge_pr.sh "<pr-number>" "<review-comment-file>" [--comment-only]`: Safely extracts author information and determines whether to comment-and-merge (if the PR belongs to the current user) or approve the PR, avoiding agent shell parsing errors. Pass `--comment-only` to skip merging a current-user PR. A real review comment file is required; the script will not post a generic approval body.

## Examples

**Example 1:**
*Input:* "Review USERST-001."
*Action:*
1. Run `gh pr list --state open --search "USERST-001" --json number,title,isDraft,headRefName,body,author,reviewDecision,statusCheckRollup,mergeStateStatus,url --limit 20`. Returns PR #13: "USERST-001: Add priority selector".
2. Run `gh pr view 13 --json number,title,body,author,isDraft,headRefName,baseRefName,files,commits,closingIssuesReferences,reviewDecision,statusCheckRollup,mergeStateStatus,url` and `gh pr checks 13`.
3. Read the linked issue from `closingIssuesReferences`, or search issues for `USERST-001` if needed.
4. Run `gh issue view 12` and note the acceptance criteria: Dropdown in modal, shows current priority, saves immediately, type-checks pass.
5. Run `gh pr diff 13`, then `gh pr checkout 13` to inspect `TaskEdit.tsx` and `TaskEdit.test.tsx` in context.
6. Produce the Review Output. Notice that changes were made to save immediately, but no tests verify the immediate save functionality. Record the missing test as a finding with a file/line or diff hunk reference.
7. Choose `Fix small issue` only if the reviewer workflow allows it. Write the missing test in `TaskEdit.test.tsx` and update the README if needed.
8. Commit and push: `git add TaskEdit.test.tsx README.md && git commit -m "test: add immediate save test"` and `git push`.
9. Approve, comment, or merge the PR as appropriate (resolve absolute path to `scripts/` sibling of this SKILL.md):
   ```bash
   echo "Verified:
   - Priority selector dropdown works in modal
   - Shows current priority correctly
   - Saves immediately
   - Fixed missing test for immediate save in TaskEdit.test.tsx (see commit <hash>)
   - Residual risk: none beyond existing coverage limits
   " > review_comment.txt
   bash /path/to/skills/user-story-reviewer/scripts/approve_or_merge_pr.sh 13 review_comment.txt
   rm review_comment.txt
   ```
