---
name: user-story-implementer
description: 'Implement or revise exactly one canonical GitHub Issue, satisfy and verify all acceptance criteria, and create or update its focused Pull Request. Use for a specific story or issue, requested changes on its PR, or as the implementation worker in user-story-delivery.'
metadata:
  author: eho
  version: '4.0.0'
---

# User Story Implementer

Own implementation for one GitHub Issue. Do not act as the independent reviewer or merge your own work unless a separate repository policy and user instruction explicitly authorize that action.

## Resolve the work

1. Read repository instructions, the complete issue, its acceptance criteria, dependencies, comments, and linked design context.
2. Confirm dependencies are delivered, not merely closed.
3. Inspect assignees, blocked state, and active linked work. Do not take over another owner's issue without explicit authority.
4. Search linked PRs, local and remote branches, and worktree ownership for existing work on this issue. Resume the unambiguous existing branch or PR; never create a duplicate.
5. Inspect the worktree and preserve unrelated changes. Use an isolated worktree when changing branches would disturb active work.
6. Stop and report ambiguity when multiple issues, branches, or PRs plausibly represent the same delivery.

## Implement

1. Inspect the relevant code, tests, contracts, and documentation.
2. Implement the smallest coherent change satisfying the complete issue.
3. For every acceptance criterion, record direct evidence such as a code path, focused test, manual observation, or documentation change.
4. Add meaningful happy-path and relevant failure or edge coverage.
5. Run focused verification for the changed risk and any broader gate required by repository policy.
6. Exercise meaningful user-visible behavior in the appropriate runtime when tooling is available; automated tests alone do not prove visual or interactive acceptance criteria.
7. Self-review the diff for regressions, security, permissions, data safety, migrations, compatibility, concurrency, diagnostics, and documentation.

If a product decision, credential, external service, or unfinished dependency prevents a correct implementation, record the exact blocker on the issue and stop.

## Branch and Pull Request

For new work, choose a focused branch such as `story/<story-id-lowercase>` or `issue/<issue-number>`. Resolve and use `scripts/prepare_story_branch.sh` to fetch the default branch, verify dependency merges, and safely prepare the branch or an isolated worktree. Use `--resume` for an existing branch.

- Stage only intended files.
- Follow repository commit conventions.
- Push the branch before creating the PR.
- Write a PR body with `### Summary`, `### Acceptance Criteria Evidence`, `### Verification`, and `### Not Verified`.
- Resolve and invoke `scripts/create_pr.sh`:

  ```bash
  bash /absolute/path/to/scripts/create_pr.sh \
    "<issue-number>" "<pr-title>" "<body-file>" \
    "<story-id-or-none>" "<design-path-or-none>"
  ```

For revision work, push to the same open PR. If earlier delivery was already merged and the issue was legitimately reopened, create a new focused PR that links and closes the same canonical issue; do not rewrite merged history.

## Handoff

```markdown
- Issue:
- PR:
- Head SHA:
- Result: Created | Resumed | Revised | Blocked
- Acceptance-criteria evidence:
- Verification:
- Blocking findings addressed:
- Blocker:
```

Do not claim independent approval, merge, issue closure, or feature readiness.
