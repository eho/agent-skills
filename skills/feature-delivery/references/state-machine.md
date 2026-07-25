# Feature Delivery State Machine

Reconstruct these states from the design document, GitHub, and repository on every initial or resumed run.

## Story states

| State | Evidence | Next transition |
| --- | --- | --- |
| `unsynced` | No canonical issue | Reconcile with `design-to-issues` |
| `ready` | Canonical open issue, dependencies done, no blocker | Implement |
| `waiting` | One or more dependencies not done | Revisit after dependency progress |
| `implementing` | Branch or open draft PR exists | Resume implementer |
| `reviewable` | Non-draft PR exists and implementation verification is recorded | Review |
| `changes-requested` | Blocking review findings exist | Revise same PR |
| `reviewed` | Approve or comment-only sign-off exists, PR not merged | Apply merge policy |
| `blocked` | Concrete external/product/technical blocker is recorded | Continue independent work; revisit |
| `done` | Every completion invariant holds | Unlock dependents |
| `stale` | Design hash differs from the canonical issue or delivered implementation | Reconcile and reopen delivery |

An open PR takes precedence over an older implementation handoff. A merged PR does not imply `done` when the issue remains open, required checks failed, acceptance evidence is missing, or the design changed.

## Selection

1. Prefer `changes-requested`, then `implementing`, then `reviewable`, so in-flight work is completed before new branches are opened.
2. Otherwise choose `ready` stories in dependency order.
3. Preserve design-document order as the tie-breaker.
4. Skip `waiting` and `blocked` stories only temporarily; do not remove them from scope.
5. If nothing is actionable, perform one fresh rehydration and blocker audit before concluding that external input is required.

## Recovery

On resumption:

1. Fetch the repository default branch and current GitHub state.
2. Re-run issue reconciliation.
3. Search open and merged PRs by canonical issue, story marker, and design-revision marker. Classify older revisions as history and identify one current-revision delivery chain.
   - A sole markerless legacy open PR may be migrated only after its issue, branch, commits, and diff are verified against the current story.
   - Add current markers to that PR before treating it as the current delivery chain. Block on uncertain equivalence or multiple candidates.
4. Verify the current checkout before changing branches.
5. Resume the existing branch/PR rather than creating a duplicate.
6. Re-run verification whose result may have become stale after rebases, merges, dependency changes, or reviewer fixes.

## Audit findings

Classify final-audit findings as:

- `story-gap`: belongs to an existing story; reopen or revise that story's delivery.
- `integration-gap`: emerges only from stories working together; create one delivery-gap issue.
- `documentation-gap`: attach to the closest story or create one focused gap issue.
- `product-decision`: no safe implementation is possible without authority; record and request the decision.
- `non-blocking-follow-up`: optional improvement that does not violate the explicit goal.

All blocking classes re-enter the delivery loop.
