---
name: user-story-delivery
description: Orchestrate independent implementation and review for exactly one GitHub user story, including safe resumption of an existing PR and bounded review-fix cycles until merged, awaiting human merge, or blocked. Use when asked to deliver a story end to end, implement and review an issue, resume an interrupted story delivery, or run the complete workflow for one story.
metadata:
  author: eho
  version: '1.1.0'
---

# User Story Delivery

Coordinate exactly one story through two independent specialists:

- `user-story-implementer` owns code, verification, commits, pushes, and revisions.
- `user-story-reviewer` independently evaluates the PR and owns review actions.

Do not perform either specialist's work in this coordinator. Reuse the same implementer for revisions when practical, but never use that implementer as reviewer.

**Prerequisite:** `gh` must be installed and authenticated, and both specialist skills must be available.

## Workflow

1. **Resolve and reconcile the story**
   - Require an exact story ID and issue number/URL, or an unambiguous selection rule.
   - Inspect the issue plus matching PRs in all states before starting a worker.
   - Validate any prior `Story Delivery Handoff` against live GitHub state. Prior handoffs help identify the branch/PR but never override GitHub.
   - Classify the entry state:
     - `completed`: a matching PR is merged and its merge commit is reachable from the fetched remote default branch.
     - `in_progress`: exactly one matching open PR exists.
     - `blocked`: blocked label/handoff remains current, a matching PR was closed without merge, state is ambiguous, or dependency evidence is incomplete.
     - `remaining`: the issue is open with no matching PR.
   - If already `completed`, return the final handoff immediately without creating workers or branches.

2. **Start or resume implementation**
   - For `remaining`, invoke `user-story-implementer` with dependency issue/PR/merge-commit evidence from the feature coordinator.
   - For `in_progress`, inspect the PR:
     - If it has unresolved requested changes, invoke the implementer to revise the existing PR head.
     - Otherwise skip implementation and send the existing PR directly to review.
   - Require the exact implementation handoff below. Stop if it reports blocked or omits branch/PR identity.

3. **Run independent review**
   - Start a separate reviewer using `user-story-reviewer`.
   - Pass the story, issue, exact PR, current review cycle, and prior review findings if any.
   - Require the exact review handoff below.

4. **Handle the decision**
   - `Request changes`: send findings to the implementer for the same PR branch, then review again.
   - `Fix small issue`: verify the reviewer pushed the named commit, then run another independent review; the fix itself is not final sign-off.
   - `Merge`: verify live GitHub state is `MERGED`, capture `mergedAt` and `mergeCommit`, fetch the remote default branch, and verify the commit is reachable. Only then mark `completed`.
   - `Approve` or `Comment only`: inspect repository policy. If a human must merge, return `in_progress` with `Awaiting human merge`; otherwise ask the reviewer to complete the permitted merge action. Approval alone is not completed delivery.
   - Any discrepancy between a handoff and GitHub state is `blocked` pending reconciliation.

5. **Bound the loop**
   - Count every completed review action as one cycle, including reviewer-fixed cycles.
   - Stop after five review cycles by default. Return remaining findings and the exact next action; do not silently start a sixth cycle.
   - Never create a second PR for revision work.

## Specialist handoffs

### Implementation

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

### Review

```markdown
## Review Handoff
- Story ID:
- Issue:
- State: in_progress | completed | blocked
- Branch:
- PR:
- PR state: OPEN | MERGED | CLOSED
- Merge commit:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge | Blocked
- Blocking findings:
- Reviewer-fixed commits:
- Required follow-up:
- Verification:
- Blocked: yes/no
- Blocker:
```

If a worker omits fields, ask that same worker to complete its handoff before continuing.

## Exact final handoff

```markdown
## Story Delivery Handoff
- Story ID:
- Issue:
- State: completed | in_progress | blocked
- Branch:
- PR:
- PR state: OPEN | MERGED | CLOSED | none
- Merge commit:
- Final decision: Merge | Awaiting human merge | Blocked
- Review cycles:
- Dependencies verified:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

`completed` requires a merged, reachable PR. `in_progress` is reserved for a valid open PR awaiting review or required human merge. Do not use approval, comment-only sign-off, issue closure, or a stale handoff as a synonym for completion.

## Prompt templates

### Implement or revise

```text
Use user-story-implementer for exactly this story.
Story: <id>
Issue: <number-or-url>
Existing PR: <number-or-none>
Dependencies verified by coordinator: <issue, PR, merge OID list>
Review findings to address: <findings-or-none>

For a new story, synchronize the default branch and verify dependency OIDs before branching.
For an existing PR, continue only on its current head branch and update the same PR.
Return the exact Implementation Handoff required by user-story-delivery.
```

### Review

```text
Use user-story-reviewer to independently review this story.
Story: <id>
Issue: <number-or-url>
PR: <number-or-url>
Review cycle: <n-of-5>

Return the exact Review Handoff required by user-story-delivery.
```

## Operating rules

- GitHub issue/PR state is the durable ledger; prior handoffs are resumable hints that must be revalidated.
- Preserve implementer/reviewer independence on every cycle.
- Keep revision work on the existing PR branch.
- A merged PR must be reachable from remote default before dependent work can begin.
- Stop on ambiguous identity, state conflicts, dirty/divergent branch reports, blockers, or the review cap.
