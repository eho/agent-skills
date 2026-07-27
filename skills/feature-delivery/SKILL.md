---
name: feature-delivery
description: 'Fully deliver every in-scope user story from a revised design document through GitHub issue reconciliation, implementation, independent PR review, merge, and a final audit-remediation loop. This is a goal-aware, resumable workflow: use it for active goals or requests to deliver, ship, fully implement, resume, or finish a complete design doc or multi-story feature. Do not stop at issue creation, open or approved PRs, follow-up issues, or a Not ready audit.'
metadata:
  author: eho
  version: '2.2.0'
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

When a criterion requires iOS Simulator evidence, use `ios-simulator-automation`. Share its ledger and compatible infrastructure across the feature; independent reviewers still record fresh behavioral observations.

## Load the workflow contracts

Read these bundled references before starting:

- `references/state-machine.md` — canonical states, transitions, selection, and recovery.
- `references/contracts.md` — specialist handoffs and completion invariants.
- `references/goal-lifecycle.md` — portable goal behavior and terminal-state rules.

Resolve these paths relative to this `SKILL.md`.

## Entry and resumption

1. Read repository and scoped `AGENTS.md` files plus project documentation before any repository or GitHub action.
2. Resolve the exact design document. Do not guess when multiple documents are plausible.
3. Confirm it has a `## User Stories` section with stable story IDs, dependencies, and binary acceptance criteria.
4. Require `Status: Revised` or an equivalent explicit readiness marker. A direct user instruction to deliver a non-revised document is an explicit override; record the risk.
5. Inspect the active goal when the runtime exposes goal state. Reuse a matching active goal. Never create a goal unless the user explicitly requested goal creation.
6. Rehydrate delivery state before taking action:
   - parse every in-scope design story and dependency;
   - compute the whole-document and per-story revisions with the bundled `design-to-issues` contract script;
   - run `design-to-issues` to reconcile, not merely create, GitHub Issues;
   - inspect matching local/remote branches, worktrees, PRs, reviews, checks, merge state, and issue state;
   - classify each story using `references/state-machine.md`.
7. Establish one feature-wide verification policy before implementation:
   - map each acceptance criterion to automated, agent-manual, owner-manual, or not-applicable evidence;
   - record any user-authorized owner-manual deferral durably on the affected issue;
   - define the strongest broad gate, focused story gates, reusable exact-head evidence, and runtime retry budget;
   - run shared environment capability checks once before the first criterion that needs them.
8. Do not trust a prior prose handoff over current GitHub and repository state. Handoffs accelerate resumption; they are not the ledger.

## Delivery loop

Continue while any in-scope story is not `done`:

1. Select an actionable story whose dependencies are `done`.
   - For a reopened delivery whose story source is unchanged, the coordinator may first invoke the independent reviewer's carry-forward mode. Follow the ordered transition and exact comment schema in `references/contracts.md`; absent a valid `Carry forward` decision, continue normal implementation.
2. Invoke `user-story-implementer` for exactly that issue:
   - resume its existing PR when one exists;
   - resume its canonical local/remote branch when work exists but no PR does;
   - otherwise implement, verify, commit, push, and open one PR;
   - pass the feature verification policy and any reusable exact-head evidence;
   - require the Implementation Handoff from `references/contracts.md`.
3. Invoke a separate reviewer context with `user-story-reviewer`:
   - require an evidence-based review against every acceptance criterion;
   - require focused independent verification, but do not automatically duplicate a broad gate whose immutable exact-head result is reusable under the verification policy;
   - require the Review Handoff from `references/contracts.md`.
4. Handle the decision:
   - `Request changes`: send the concrete findings back through `user-story-implementer` on the same PR.
   - `Fix small issue`: verify the reviewer pushed the fix, then run a fresh review in a context independent of both the implementer and the reviewer who authored the fix.
   - `Approve` or `Comment only`: treat as reviewed but not done; merge only when repository policy permits.
   - `Merge`: re-read the PR and issue to verify the merge and closure actually occurred.
5. Repeat until the story meets every `done` invariant in `references/contracts.md`.
6. Rehydrate the completed story, its dependents, the default-branch head, and any volatile PR/check state before selecting the next story. Rehydrate the whole feature only on entry or resumption, after a design/scope change, when the incremental state is inconsistent, and before final audit. This preserves safety without repeatedly querying immutable history.

Use review epochs of at most five review-fix cycles. Write blocking findings as a JSON array with exactly `stable_key`, `severity`, `location`, `behavior`, `impact`, and `required_change`, then run `scripts/fingerprint_findings.py` to assign stable IDs to each finding. After every review, post the exact `feature-delivery:review-ledger` issue-comment schema from `references/contracts.md`; include the IDs in the Review Handoff. Reconstruct counters only from ledger comments matching the current delivery ID and head SHA after interruption. At an epoch boundary, stop automatic retry, rehydrate state, summarize repeated finding IDs, and start a new implementation strategy and fresh independent reviewer context only when evidence supports a materially different safe approach. If the same blocking finding ID survives two epochs, record it as a concrete story blocker and request the missing product or architecture decision. A review limit is never completion.

Keep handoffs compact. Put durable criterion detail, commands, and evidence links on the canonical issue or PR once; return identifiers, head SHAs, decisions, finding IDs, evidence references, and deltas rather than repeating issue/design prose. A coordinator status request asks only for the next safe-boundary delta. Do not request another full handoff when the prior identity tuple remains current.

When the runtime supports controlling inherited context, start specialists with the smallest useful context rather than copying the full feature transcript. Send the task-packet fields from `references/contracts.md`; the specialist reads canonical repository and GitHub state directly. Final auditors need the full design scope, not the coordinator's historical narration.

Runtime retry budgets apply across all agents, not per context. A replacement worker inherits prior attempts and may continue only with a materially different diagnosed strategy. Once the durable policy marks a criterion owner-manual, later implementers, reviewers, and auditors must preserve that status rather than retrying or converting it into a pass.

## Blockers and partial progress

- A blocked story does not automatically block the feature.
- Record the blocker on its GitHub Issue, then continue stories that neither depend on it nor conflict with its work.
- Do not defer or remove a story from scope unless the user explicitly changes the design scope.
- When scope changes, require `design-to-issues` to record a durable `deferred` or `removed` orphan resolution with the deciding revision and reason; do not rediscover the same unresolved orphan on every pass.
- Continue safe diagnostics, issue repair, verification, and independent stories while useful work remains.
- Treat the overall workflow as blocked only when no meaningful in-scope progress remains and the goal runtime's blocked policy is satisfied.
- Permission, usage, and token-budget pauses are runtime states, not evidence that the feature is complete.

## Final audit-remediation loop

When all stories appear `done`:

1. Invoke `post-implementation-reviewer` in report-only mode using the original design document and current GitHub/repository state.
2. Require the Final Audit Handoff from `references/contracts.md`.
3. If the decision is `Not ready`:
   - map each blocking finding to the affected existing story where possible;
   - when that story's prior PR is already merged, reopen the canonical issue with an audit-gap comment, retain the current design/story identity, and create exactly one new delivery attempt whose PR explicitly supersedes the prior leaf rather than attempting to revise merged history;
   - otherwise normalize the finding with `scripts/audit_gap_contract.py`, reconcile exactly one canonical audit-gap issue under the same milestone using the audit-gap contract in `references/contracts.md`, and run its gap ID through the ordinary attempt/branch/implementation/review lifecycle;
   - run that issue through implementation and independent review;
   - rerun the complete final audit.
4. If the decision is `Ready with follow-ups`, verify every follow-up is genuinely non-blocking. The default full-delivery goal remains active unless its objective explicitly permits non-blocking follow-ups.
   - If a follow-up remains within the design or goal scope, deliver it through the same implementation-review loop and rerun the audit.
   - If it would expand scope beyond the design, request an explicit choice to expand the goal or accept `Ready with follow-ups`; do not repeat an unchanged audit indefinitely.
5. Finish only when the audit reports `Ready`, or when the adopted goal explicitly allows `Ready with follow-ups`.

The auditor identifies gaps; the coordinator owns remediation. Creating a follow-up issue is never remediation by itself.

Before the first audit, finalize lifecycle/index/acceptance-ledger documentation that could not truthfully describe the last story's merge from inside that story's own PR. Route any required mutation through the normal reviewed delivery path.

## Completion

Before reporting success, independently re-check:

- every in-scope design story has one canonical GitHub Issue;
- every story satisfies the `done` invariant;
- no dependency or blocking audit-gap issue remains open;
- required CI and repository verification pass;
- user-facing and operational documentation is current;
- the latest full-feature audit satisfies the goal's release-readiness threshold.

Only then mark the matching goal adopted during entry complete, when the runtime supports it. Never update an unrelated active goal. Never mark a goal complete merely because the current turn, token budget, review limit, or planned queue ended.

## Final report

```markdown
## Feature Delivery Status
- Design doc:
- Design revision:
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
- Use the runtime's wait mechanism for active specialists. Do not poll with repeated prompts or restate unchanged status; request one compact delta only when a worker exceeds a meaningful expected boundary.
- Reuse immutable exact-head evidence and deterministic artifacts; rerun work when the head, environment contract, risk, or repository policy invalidates it.
