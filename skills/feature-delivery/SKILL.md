---
name: feature-delivery
description: 'Fully deliver every in-scope user story from a revised design document through GitHub issue reconciliation, implementation, independent PR review, merge, and a final audit-remediation loop. This is a goal-aware, resumable workflow: use it for active goals or requests to deliver, ship, fully implement, resume, or finish a complete design doc or multi-story feature. Do not stop at issue creation, open or approved PRs, follow-up issues, or a Not ready audit.'
metadata:
  author: eho
  version: '2.0.0'
---

# Feature Delivery

Coordinate a complete feature to verified release readiness. Treat a long-running goal as the durable completion contract, the design document as the scope contract, and GitHub Issues and Pull Requests as the recoverable execution ledger.

This skill owns orchestration and recovery. Specialist skills own issue reconciliation, implementation, review, and final audit.

## Required specialists

- `design-to-issues`
- `user-story-implementer`
- `user-story-reviewer`
- `post-implementation-reviewer`

If a specialist is unavailable, report the exact missing prerequisite. Do not silently approximate a review or implementation workflow that depends on independence.

## Load the workflow contracts

Read these bundled references before starting:

- `references/state-machine.md` — canonical states, transitions, selection, and recovery.
- `references/contracts.md` — specialist handoffs and completion invariants.
- `references/goal-lifecycle.md` — portable goal behavior and terminal-state rules.

Resolve these paths relative to this `SKILL.md`.

## Entry and resumption

1. Resolve the exact design document. Do not guess when multiple documents are plausible.
2. Confirm it has a `## User Stories` section with stable story IDs, dependencies, and binary acceptance criteria.
3. Require `Status: Revised` or an equivalent explicit readiness marker. A direct user instruction to deliver a non-revised document is an explicit override; record the risk.
4. Inspect the active goal when the runtime exposes goal state. Reuse a matching active goal. Never create a goal unless the user explicitly requested goal creation.
5. Rehydrate delivery state before taking action:
   - parse every in-scope design story and dependency;
   - run `design-to-issues` to reconcile, not merely create, GitHub Issues;
   - inspect matching PRs, reviews, checks, merge state, and issue state;
   - classify each story using `references/state-machine.md`.
6. Do not trust a prior prose handoff over current GitHub and repository state. Handoffs accelerate resumption; they are not the ledger.

## Delivery loop

Continue while any in-scope story is not `done`:

1. Select an actionable story whose dependencies are `done`.
2. Invoke `user-story-implementer` for exactly that issue:
   - resume its existing PR when one exists;
   - otherwise implement, verify, commit, push, and open one PR;
   - require the Implementation Handoff from `references/contracts.md`.
3. Invoke a separate reviewer context with `user-story-reviewer`:
   - require an evidence-based review against every acceptance criterion;
   - require the Review Handoff from `references/contracts.md`.
4. Handle the decision:
   - `Request changes`: send the concrete findings back through `user-story-implementer` on the same PR.
   - `Fix small issue`: verify the reviewer pushed the fix, then run a fresh review.
   - `Approve` or `Comment only`: treat as reviewed but not done; merge only when repository policy permits.
   - `Merge`: re-read the PR and issue to verify the merge and closure actually occurred.
5. Repeat until the story meets every `done` invariant in `references/contracts.md`.
6. Rehydrate the whole feature state before selecting the next story. This catches merges, user changes, stale branches, and newly surfaced blockers.

Use five review-fix cycles as an escalation checkpoint, not a completion condition. At the checkpoint, reassess scope, requirements, and implementation strategy. Continue when a safe path remains; request a product decision only when correctness genuinely depends on one.

## Blockers and partial progress

- A blocked story does not automatically block the feature.
- Record the blocker on its GitHub Issue, then continue stories that neither depend on it nor conflict with its work.
- Do not defer or remove a story from scope unless the user explicitly changes the design scope.
- Continue safe diagnostics, issue repair, verification, and independent stories while useful work remains.
- Treat the overall workflow as blocked only when no meaningful in-scope progress remains and the goal runtime's blocked policy is satisfied.
- Permission, usage, and token-budget pauses are runtime states, not evidence that the feature is complete.

## Final audit-remediation loop

When all stories appear `done`:

1. Invoke `post-implementation-reviewer` in report-only mode using the original design document and current GitHub/repository state.
2. Require the Final Audit Handoff from `references/contracts.md`.
3. If the decision is `Not ready`:
   - map each blocking finding to the affected existing story where possible;
   - otherwise create a clearly traceable delivery-gap issue under the same milestone;
   - run that issue through implementation and independent review;
   - rerun the complete final audit.
4. If the decision is `Ready with follow-ups`, verify every follow-up is genuinely non-blocking. The default full-delivery goal remains active unless its objective explicitly permits non-blocking follow-ups.
   - If a follow-up remains within the design or goal scope, deliver it through the same implementation-review loop and rerun the audit.
   - If it would expand scope beyond the design, request an explicit choice to expand the goal or accept `Ready with follow-ups`; do not repeat an unchanged audit indefinitely.
5. Finish only when the audit reports `Ready`, or when the adopted goal explicitly allows `Ready with follow-ups`.

The auditor identifies gaps; the coordinator owns remediation. Creating a follow-up issue is never remediation by itself.

## Completion

Before reporting success, independently re-check:

- every in-scope design story has one canonical GitHub Issue;
- every story satisfies the `done` invariant;
- no dependency or blocking-delivery-gap issue remains open;
- required CI and repository verification pass;
- user-facing and operational documentation is current;
- the latest full-feature audit satisfies the goal's release-readiness threshold.

Only then mark the matching goal adopted during entry complete, when the runtime supports it. Never update an unrelated active goal. Never mark a goal complete merely because the current turn, token budget, review limit, or planned queue ended.

## Final report

```markdown
## Feature Delivery Status
- Design doc:
- Goal:
- Milestone:
- Final state: Ready | Ready with follow-ups | Blocked

## Story Delivery Matrix
| Story | Issue | PR | State | Review | Verification | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- |

## Audit-Remediation
- Audit passes:
- Blocking findings remediated:
- Follow-up issues:
- Latest decision:

## Verification
- Commands and checks:
- CI:
- Not verified:

## Remaining Work
- None | exact blocker, owner, and required decision/action
```

If blocked, report completed work and all remaining stories. If ready, say `No blocking findings found.`

## Operating principles

- Preserve independent implementation and review contexts.
- Prefer sequential story delivery unless the runtime provides isolated worktrees and the dependency graph and file ownership make parallel work demonstrably safe.
- Do not replace or duplicate an active worker. Ask it for status when needed.
- Do not overwrite unrelated worktree changes.
- Follow repository-specific branch, review, and merge policy from `AGENTS.md` and project documentation.
- Keep user updates tied to meaningful state transitions rather than every low-level action.
