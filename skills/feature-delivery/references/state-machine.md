# Feature Delivery State Machine

Reconstruct these states from the design document, GitHub, and repository on every initial or resumed run.

## Ordered story classifier

Apply the first matching rule only. Current-head evidence means evidence explicitly bound to the current delivery leaf's present head SHA; historical reviews and findings never classify a later head.

| Order | State | Evidence | Next transition |
| --- | --- | --- | --- |
| 1 | `unsynced` | No unique canonical issue | Reconcile with `design-to-issues` |
| 2 | `stale` | Issue/body/revision tuple, scope state, attempt graph, or delivered implementation differs from the current contract | Reconcile before any delivery action |
| 3 | `done` | Every completion invariant holds | Unlock dependents |
| 4 | `blocked` | A concrete external/product/technical blocker prevents this story independent of dependencies | Continue independent work; revisit |
| 5 | `waiting` | One or more dependencies are not `done` | Revisit after dependency progress |
| 6 | `changes-requested` | Unresolved blocking findings are bound to the current delivery leaf and current head | Revise the same PR |
| 7 | `implementing` | A current branch exists without a PR, or the current delivery-leaf PR is draft | Resume implementer |
| 8 | `reviewable` | Current leaf is non-draft, implementation verification covers its current head, and no current-head sign-off exists | Review |
| 9 | `reviewed` | Current-head approval or comment-only sign-off exists, PR remains unmerged | Apply merge policy |
| 10 | `ready` | Canonical issue is open, dependencies are done, no blocker exists, and no current delivery attempt/branch/PR exists | Implement |

An open PR takes precedence over an older implementation handoff. A merged PR does not imply `done` when the issue remains open, required checks failed, acceptance evidence is missing, or the design changed.

## Selection

1. Reconcile every `stale` story before implementation or review.
2. Prefer `changes-requested`, then `implementing`, then `reviewable`, then `reviewed`, so in-flight work is completed before new branches are opened.
3. Otherwise choose `ready` stories in dependency order.
4. Preserve design-document order as the tie-breaker.
5. Skip `waiting` and `blocked` stories only temporarily; do not remove them from scope.
6. If nothing is actionable, perform one fresh rehydration and blocker audit before concluding that external input is required.

## Recovery

On resumption:

1. Fetch the repository default branch and current GitHub state without moving or rewriting a dirty/divergent worktree.
2. Re-run issue reconciliation.
3. Search open and merged PRs by canonical issue, complete revision tuple, delivery ID, and supersedes marker. Build the attempt graph, classify older/superseded revisions as history, and identify exactly one current leaf or a valid carry-forward record.
   - A sole markerless legacy open PR may be migrated only after its issue, branch, commits, and diff are verified against the current story.
   - Add the complete current marker tuple to that PR before treating it as the current delivery chain. Block on uncertain equivalence or multiple candidates.
4. Search local branches, remote branches, and `git worktree list --porcelain` for the canonical story branch even when no PR exists. A pushed or worktree-owned branch is in-progress work, not permission to create a replacement.
5. Verify the current checkout before changing branches. Never switch, reset, rebase, or delete a dirty, divergent, or separately owned worktree as recovery.
6. Resume the existing branch/PR rather than creating a duplicate.
7. For a new branch, start at the fetched remote default-branch SHA and prove every completed dependency merge SHA is its ancestor.
8. Re-run verification whose result may have become stale after rebases, merges, dependency changes, or reviewer fixes.

Use the immutable delivery ID as the canonical branch suffix, for example `story/<design-slug>-<story-id-lowercase>-a1`. Record any repository-specific alternative on the issue and PR so branch-only interruption remains discoverable.

## Audit findings

Classify final-audit findings as:

- `story-gap`: belongs to an existing story; reopen or revise that story's delivery.
- `integration-gap`: emerges only from stories working together; normalize and reconcile one canonical audit-gap issue.
- `documentation-gap`: attach to the closest story or normalize and reconcile one canonical audit-gap issue.
- `product-decision`: no safe implementation is possible without authority; record and request the decision.
- `non-blocking-follow-up`: optional improvement that does not violate the explicit goal.

All blocking classes re-enter the delivery loop. New gap issues use the audit-gap identity/revision contract and ordinary delivery-attempt state machine from `contracts.md`.
