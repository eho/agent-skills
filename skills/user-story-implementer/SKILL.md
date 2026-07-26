---
name: user-story-implementer
description: Implement or resume exactly one GitHub user story, safely basing new work on the synchronized default branch, verifying dependency merge commits, preserving unrelated changes, and creating or updating the story PR. Use when asked to implement a story ID or issue, run one backlog iteration, revise an existing story PR, or continue an in-progress story.
metadata:
  author: eho
  version: '2.1.0'
---

# User Story Implementer

Act as the implementation specialist for exactly one GitHub Issue. New work must start from a clean, current default branch containing every completed dependency. Revision work must continue on the existing PR head branch. Never review or approve your own implementation.

**Prerequisite:** `gh` must be installed and authenticated.

## Workflow

1. **Resolve one target**
   - Prefer the supplied issue number or exact story ID.
   - Search all issue states for a story ID and accept only a unique exact-ID match. If asked for “next,” use the supplied prefix, label, or milestone; do not guess across features.
   - Read `number,title,state,body,comments,labels,assignees,url`.

2. **Reconcile existing delivery state**
   - Search open and closed PRs using the issue number and story ID. Confirm matches through title, body, branch, commits, or closing issue references.
   - If a matching PR is merged, stop and return `State: completed` with its merge commit; do not reimplement it.
   - If exactly one matching PR is open, this is revision/resumption work. Use that PR even if the issue is closed, because GitHub PR state is stronger evidence than issue lifecycle alone.
   - If multiple plausible PRs exist, or a matching PR is closed without merge and intent is unclear, stop for reconciliation.
   - Without an existing open PR, stop if the issue is closed, blocked, or owned by someone else.

3. **Validate dependencies**
   - Parse dependency markers from the body and comments. Query every dependency issue and its associated PR.
   - A dependency is complete only when its intended PR is merged and its merge commit is reachable from the fetched remote default branch. A closed issue alone is insufficient.
   - Record dependency story IDs, issue numbers, PRs, and merge commit OIDs for the final handoff.

4. **Prepare the branch safely**
   - Run `git status --porcelain=v1 --untracked-files=all`. Stop on any output; do not stash, clean, reset, or overwrite user work.
   - **Existing open PR:** run `gh pr checkout <pr>`. Confirm the checked-out branch equals `headRefName`, the worktree remains clean, and its upstream is the PR branch. Fetch that branch and fast-forward it only; stop if the local branch is ahead, divergent, or cannot be safely updated. Do not create a new branch, rebase it onto default, or rewrite its history.
   - **New work:** resolve a branch name and invoke:
     ```bash
     "$SKILL_DIR/scripts/prepare_story_branch.sh" \
       "<new-branch>" "<dependency-merge-oid>"...
     ```
   - The script switches to the repository default branch, fetches it, refuses local-ahead/divergent state, fast-forwards only, verifies each dependency merge commit is an ancestor, and then creates the story branch. If default is checked out by another worktree or cannot be switched safely, stop; do not bypass the guardrail.

5. **Claim and inspect**
   - Assign the issue to `@me` only after branch preparation succeeds.
   - Read all acceptance criteria, design links, referenced files, nearby implementation, tests, commands, and repository instructions.

6. **Implement and verify**
   - Make the smallest coherent change satisfying every acceptance criterion.
   - Add focused tests for behavior changes, or document why tests are inappropriate and perform the strongest available verification.
   - For meaningful UI changes, verify behavior in a browser or platform runtime when practical.
   - Update user-facing documentation when commands, options, setup, UI, APIs, or workflows change.
   - Do not widen product scope or guess around missing decisions.

7. **Handle blockers**
   - For a genuine requirements or external blocker, comment on the issue and add the `blocked` label when available. Do not label temporary local dirtiness or branch divergence as a product blocker; report those as local safety blockers.
   - Stop without partial unrelated changes.

8. **Self-review, commit, and push**
   - Check each acceptance criterion individually, test depth, error paths, docs, and verification evidence.
   - Stage only specific files; never use `git commit -a` or `git add .`.
   - Commit and push the story branch.
   - On revision work, push to the same PR head and never create another PR.
   - On new work, create the PR with:
     ```bash
     "$SKILL_DIR/scripts/create_pr.sh" "<issue-number>" "<title>" "<summary>"
     ```

## Exact handoff

Always return:

```markdown
## Implementation Handoff
- Story ID:
- Issue:
- State: in_progress | completed | blocked
- Branch:
- PR:
- PR state: OPEN | MERGED | CLOSED | none
- Merge commit:
- Dependencies verified:
- Review findings addressed:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

Use `completed` only when an already-merged matching PR was discovered. A newly pushed open PR remains `in_progress` pending independent review.

## Safety rules

- New story: synchronized default branch, verified dependency commits, then a new branch.
- Existing PR: existing head branch, fast-forward only, same PR.
- Stop on dirty worktrees, local default commits, divergence, ambiguous PR identity, or missing dependency evidence.
- Never stash, reset, force-push, delete branches, or overwrite unrelated work.
- Issue closure is not proof of implementation; merged and reachable code is.

## Scripts

- `prepare_story_branch.sh "<branch>" [dependency-merge-oid...]`: safely synchronize the default base, verify dependencies, and create a new branch.
- `create_pr.sh "<issue-number>" "<title>" "<summary>"`: create a linked PR with a safe temporary body.
