---
name: user-story-implementer
description: 'Implement or revise exactly one canonical GitHub user story, including acceptance-criteria verification, focused tests, documentation, commit, push, and creation or resumption of one PR. Use for a specific story ID or issue, for requested changes on an existing story PR, or as the implementation worker in user-story-delivery and feature-delivery.'
metadata:
  author: eho
  version: '3.0.0'
---

# User Story Implementer

Own the implementation phase for exactly one GitHub Issue. Do not review or merge your own work as the independent reviewer.

## Resolve current state

1. Resolve the exact issue from a supplied issue number or exact story ID.
2. Read the issue body and comments, including every acceptance criterion, design revision marker, dependency, blocker, and scope boundary.
3. Stop on ambiguous duplicate issues. Do not guess.
4. Verify dependencies are delivered, not merely closed:
   - inspect the dependency issue;
   - confirm its intended PR merged or a repository-policy exception exists.
5. Find an existing PR through closing references, exact issue number, and story ID. Resume it when it belongs to this issue; never open a duplicate delivery PR.
   - Prefer PRs carrying both `<!-- feature-delivery:story=<STORY-ID> -->` and `<!-- feature-delivery:design-revision=<REVISION> -->`.
   - Treat PRs for older design revisions as historical delivery, not as the current implementation PR.
   - For a markerless legacy open PR, adopt it only when it is the sole unambiguous candidate and its issue, branch, commits, and diff align with the current story. Add the current story and design-revision markers to its body with `gh pr edit --body-file` before resuming it.
   - If a markerless PR may have been built for older requirements, or more than one candidate exists, stop and request disambiguation rather than stamping it with the current revision.
6. Read `AGENTS.md`, repository verification commands, and branch/merge conventions.
7. Inspect `git status --short`. Preserve unrelated changes and coordinate rather than overwriting them.

## Choose mode

- `Created`: no delivery PR exists. Start from the repository default branch, create a focused branch, and open one PR.
- `Resumed`: an existing branch or PR has unfinished implementation. Check out and continue it.
- `Revised`: reviewer or final-audit findings require changes on the existing PR, or a stale delivered story was reopened and needs a new traceable delivery PR.

When a previously delivered issue was reopened because its design revision changed, do not mutate the old merged PR. Create a new PR linked to the reopened canonical issue.

## Implement

1. Assign the issue to the current user if repository policy permits.
2. Read the linked design context and inspect exact nearby code, tests, contracts, and documentation before editing.
3. Implement the smallest coherent change satisfying the complete current issue.
4. For each acceptance criterion, record its evidence:
   - code path;
   - focused automated test;
   - manual or browser verification where appropriate;
   - documentation or operational change.
5. Add meaningful happy-path and relevant error/edge coverage. UI behavior requires visual/browser verification when the runtime supports it.
6. Run the strongest relevant targeted verification, then broader typecheck, lint, build, or tests required by the repository.
7. Self-review the diff for regressions, security, permissions, data safety, migrations, concurrency, compatibility, diagnostics, and documentation.

If correctness depends on a missing product decision, credential, external service, or undelivered dependency, record a specific blocker on the issue and stop. Add a `blocked` label only when it exists or repository policy permits creating it.

## Commit and PR

- Stage only intended files; do not use `git add .` or `git commit -a`.
- Use repository commit conventions and include the story ID when helpful.
- Push the story branch.
- For a new PR, resolve and invoke `scripts/create_pr.sh` relative to this skill:

  ```bash
  bash /absolute/path/to/scripts/create_pr.sh \
    "<issue-number>" "<pr-title>" "<summary>" "<story-id>" "<design-revision>"
  ```

- The PR body must link the canonical issue, carry immutable story and design-revision markers, describe implementation and verification, and identify anything not verified.
- For revision work, push to the same open PR. Create a new PR only when the previous PR is already merged/closed and the canonical issue was legitimately reopened.

## Handoff

```markdown
## Implementation Handoff
- Story ID:
- Issue:
- Branch:
- PR:
- Mode: Created | Resumed | Revised
- Review or audit findings addressed:
- Acceptance criteria evidence:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

Do not claim completion, approval, or release readiness. The coordinator and an independent reviewer determine those states.
