---
name: user-story-implementer
description: 'Implement or revise exactly one canonical GitHub user story, including acceptance-criteria verification, focused tests, documentation, commit, push, and creation or resumption of one PR. Use for a specific story ID or issue, for requested changes on an existing story PR, or as the implementation worker in user-story-delivery and feature-delivery.'
metadata:
  author: eho
  version: '3.2.0'
---

# User Story Implementer

Own the implementation phase for exactly one GitHub Issue. Do not review or merge your own work as the independent reviewer.

## Resolve current state

1. Read repository and scoped `AGENTS.md`, verification commands, and branch/merge conventions before acting.
2. Resolve the exact issue from a supplied issue number or exact design-story ID. A final-audit gap is also valid only when it has a canonical `GAP-<12 uppercase hex>` ID and the complete audit-gap markers/payload defined by `feature-delivery/references/contracts.md`.
3. Read the issue body and comments, including every acceptance criterion, design identity, document and story revision markers, dependency, blocker, and scope boundary.
4. Stop on ambiguous duplicate issues. Do not guess.
5. Verify dependencies are delivered, not merely closed:
   - inspect the dependency issue;
   - confirm its intended PR merged or a repository-policy exception exists.
6. Find existing work through the canonical story branch, closing references, exact issue number, and the complete marker tuple. Search local branches, remote branches, and `git worktree list --porcelain` before searching PRs. Resume work that belongs to this issue; never open a duplicate delivery branch or PR.
   - Prefer PRs carrying design identity, story, document-revision, story-revision, immutable delivery-ID, and supersedes markers. Build the attempt graph and select its unique non-superseded current leaf.
   - Treat PRs for older document or story revisions as historical delivery, not as the current implementation PR.
   - For a markerless legacy open PR, adopt it only when it is the sole unambiguous candidate and its issue, branch, commits, and diff align with the current story. Add the complete current marker tuple to its body with `gh pr edit --body-file` before resuming it.
   - If a markerless PR may have been built for older requirements, or more than one candidate exists, stop and request disambiguation rather than stamping it with the current revision.
7. Inspect `git status --short`. Preserve unrelated changes and coordinate rather than overwriting them.

## Choose mode

- `Created`: no delivery branch or PR exists. Use the bundled branch-preparation script to fetch the remote default branch, verify dependency merge ancestry, create a focused branch, and open one PR.
- `Resumed`: an existing branch or PR has unfinished implementation. Check out and continue it.
- `Revised`: reviewer or final-audit findings require changes on the existing PR, or a stale delivered story was reopened and needs a new traceable delivery PR.

When a previously delivered issue was reopened because its document revision, story revision, or managed delivery contract changed, do not mutate the old merged PR. Create a new delivery attempt linked to the reopened canonical issue and mark the prior leaf as superseded.

When an existing unmerged PR crosses a design revision, revision work must stay on that branch and PR. Keep its immutable delivery ID, comment with the old revision tuple, update the PR's revision markers only after issue/diff equivalence is verified, and require fresh verification and independent review. Never stamp uncertain work as current.

## Prepare a new branch safely

Enumerate delivery IDs across every open, closed, and merged PR for the composite story identity, then choose the next ID with the bundled script:

```bash
python3 /absolute/path/to/scripts/next_delivery_id.py \
  --design-identity "<repo-relative-design-path>" \
  --story-id "<STORY-ID>" \
  --existing-ids-json '<JSON-array>'
```

Use `story/<delivery-id>` as the canonical branch. Invoke:

```bash
bash /absolute/path/to/scripts/prepare_story_branch.sh \
  "story/<delivery-id>" \
  --dependency-pr <merged-dependency-pr-number>
```

Repeat `--dependency-pr` for every direct dependency. Use `--worktree <new-path>` when the current checkout is dirty, on another active branch, or shared with another worker. The script refuses dirty/divergent branch switching, duplicate local/remote branches, unknown remote lookup state, unmerged dependencies, and dependency merge SHAs absent from either the fetched remote default branch or the resumed branch. On creation, record its `Start SHA` in the durable issue record and handoff. On resumption, recover that immutable start SHA from the issue record; the script reports the current default SHA separately and deliberately does not invent the historical start SHA.

For a discovered branch-only interruption, invoke the same command with `--resume`. Add `--worktree <new-path>` to track a remote-only or unowned local branch without disturbing the current checkout. If another worktree already owns the branch, resume that worker/worktree rather than creating a replacement.

Immediately after branch preparation, comment on the canonical issue with delivery ID, canonical branch, base SHA, dependency merge SHAs, and worktree/worker ownership. On resumption, verify that record against the branch commits and diff before treating name equivalence as proof.

## Implement

1. Assign the issue to the current user if repository policy permits.
2. Read the linked design context and inspect exact nearby code, tests, contracts, and documentation before editing.
3. Implement the smallest coherent change satisfying the complete current issue.
4. Read the feature verification policy when supplied. Reuse valid exact-head evidence, inherit consumed runtime attempts, and do not retry owner-manual criteria.
5. For each acceptance criterion, record its evidence:
   - code path;
   - focused automated test;
   - manual or browser verification where appropriate;
   - documentation or operational change.
6. Add meaningful happy-path and relevant error/edge coverage. UI behavior requires visual/browser verification when the verification policy assigns it to the agent and the shared runtime budget remains.
7. Run focused verification for the changed risk. Run a broader gate when repository policy requires it or no reusable exact-head result covers the current head; do not repeat an unchanged broad gate merely to populate a handoff.
8. Self-review the diff for regressions, security, permissions, data safety, migrations, concurrency, compatibility, diagnostics, and documentation.

If correctness depends on a missing product decision, credential, external service, or undelivered dependency, record a specific blocker on the issue and stop. Add a `blocked` label only when it exists or repository policy permits creating it.

## Commit and PR

- Stage only intended files; do not use `git add .` or `git commit -a`.
- Use repository commit conventions and include the story ID when helpful.
- Push the story branch.
- For a new PR, write a delivery body file containing `### Summary`, `### Acceptance Criteria Evidence`, `### Verification`, and `### Not Verified`, then resolve and invoke `scripts/create_pr.sh` relative to this skill:

  ```bash
  bash /absolute/path/to/scripts/create_pr.sh \
    "<issue-number>" "<pr-title>" "<delivery-body-file>" \
    "<story-id>" "<design-identity>" "<design-revision>" "<story-revision>" \
    "<delivery-id>" "<superseded-pr-number|none>"
  ```

- The PR body must link the canonical issue, carry the complete marker tuple, describe implementation and verification, and identify anything not verified. Delivery ID and supersedes markers are immutable; revision markers may change only on an unmerged PR through the recorded revalidation transition above.
- For revision work, push to the same open PR. Create a new PR only when the previous PR is already merged/closed and the canonical issue was legitimately reopened.

## Handoff

```markdown
## Implementation Handoff
- Story ID:
- Issue:
- Design doc:
- Design revision:
- Story revision:
- Delivery ID:
- Supersedes PR:
- Branch:
- Base branch and start SHA:
- Dependency merge SHAs:
- PR:
- Head SHA:
- Mode: Created | Resumed | Revised
- Review or audit findings addressed:
- Acceptance criteria evidence:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

Do not claim completion, approval, or release readiness. The coordinator and an independent reviewer determine those states.

Keep the handoff compact. Put detailed criterion evidence and command output on the PR once, then reference it. For a revision of the same delivery tuple, report the changed head, addressed finding IDs, verification delta, and residual risk without restating unchanged design or issue prose.
