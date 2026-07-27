# Feature Delivery Contracts

Use these handoffs between coordinator and specialists. Validate handoffs against current GitHub state before transitioning.

## Minimal specialist task packet

When the runtime can limit inherited context, pass this packet instead of the complete coordinator transcript:

```markdown
- Role: issue sync | implement | review | final audit
- Design doc and revision:
- Story/gap ID and canonical issue:
- Delivery ID, PR, and expected head:
- Dependency merge SHAs:
- Finding IDs to address:
- Verification-policy comment:
- Runtime ledger, selected criteria, and attempts consumed:
- Reusable evidence references:
- Required handoff:
```

Omit fields irrelevant to the role. Repository files and GitHub remain the source of truth; conversation history is not a substitute for either.

## Verification efficiency contract

Create one policy for the feature and pass it by reference to every specialist. This prevents each context from rediscovering evidence requirements, retrying the same broken runtime path, or rerunning broad gates without new information.

For each criterion, record one mode:

- `automated`: a command or deterministic artifact can verify it;
- `agent-manual`: supported interactive tooling can verify it within the shared runtime budget;
- `owner-manual`: the user explicitly accepted verification after delivery;
- `not-applicable`: the criterion does not apply, with a reason;
- `unverified-blocking`: required evidence is unavailable and no exception exists.

An owner-manual entry is an authorized pending verification, not a pass. It is valid only when the durable record names the criterion, user authority, owner, residual risk, and goal threshold that permits completion with it pending. Persist this compact issue comment on every affected canonical issue:

```markdown
<!-- feature-delivery:verification-policy -->
- Design revision: <SHA-256>
- Story revision: <SHA-256>
- Criteria: <criterion=mode; ...>
- Owner: <agent|user|role>
- Runtime budget: <attempt/time boundary or none>
- Authority: <user instruction reference or none>
- Residual risk: <concise risk or none>
```

Treat retry state as feature-wide. One primary attempt, one diagnosed fallback, and one environment repair are the default ceiling for an interactive criterion unless the user or repository policy requires more. A new agent inherits consumed attempts.

Reusable evidence must be bound to:

- the exact head SHA or immutable artifact;
- the command or observation;
- the relevant environment/configuration fingerprint without secret values;
- the result and evidence location.

Reuse it when those bindings remain valid. Reviewers rerun focused risk-relevant checks independently, but need not duplicate a broad exact-head gate solely for ceremony. Repository policy, changed code/configuration, suspicious output, or a high-risk finding overrides reuse.

Keep handoffs terse: identity fields are hashes and references; criterion detail and command output live once on the PR/issue or in an artifact. On revision cycles, report only changed head, addressed finding IDs, verification delta, and residual risk while retaining the full schema.

## Issue Sync Handoff

```markdown
## Issue Sync Handoff
- Design doc:
- Design revision:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<number> <url> (<Created|Updated|Reopened|Unchanged>; story revision: <SHA-256>)
- Dependencies reconciled: yes/no
- Stale delivered stories reopened:
- Orphaned issues:
- Orphan resolutions:
- Blocked: yes/no
- Blocker:
```

## Implementation Handoff

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

## Review Handoff

```markdown
## Review Handoff
- Story ID:
- Issue:
- Design doc:
- Design revision:
- Story revision:
- Delivery ID:
- PR:
- Reviewed head SHA:
- Base branch:
- Draft state:
- Required checks:
- Mergeability:
- Merge policy:
- Review epoch:
- Review cycle:
- Strategy:
- Blocking finding IDs:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Resulting head SHA:
- Merge or queue result:
- Required follow-up:
- Acceptance criteria evidence:
- Verification:
```

After each PR review, persist this exact machine-readable issue comment:

```markdown
<!-- feature-delivery:review-ledger -->
- Delivery ID: <ID>
- Reviewed head SHA: <git SHA>
- Review epoch: <positive integer>
- Review cycle: <1-5>
- Strategy: <stable strategy ID>
- Blocking finding IDs: <comma-separated SHA-256 IDs or none>
```

Only a ledger entry matching the current delivery ID and head SHA affects classification. Generate per-finding IDs from a JSON array with `scripts/fingerprint_findings.py`; each finding must have exactly `stable_key`, `severity`, `location`, `behavior`, `impact`, and `required_change`. Keep `stable_key` semantic and stable across wording or line-number changes (for example, `path:symbol:contract-name`).

## Carry-Forward Review Handoff

```markdown
## Carry-Forward Review Handoff
- Story ID:
- Issue:
- Design doc:
- Current design revision:
- Current story revision:
- Historical PR:
- Historical delivery ID:
- Historical design revision:
- Historical story revision:
- Historical reviewed and merged head SHA:
- Reviewer:
- Current acceptance criteria evidence:
- Current shared-contract evidence:
- Verification:
- Decision: Carry forward | Reopen delivery
- Blocking findings:
```

## Final Audit Handoff

```markdown
## Final Audit Handoff
- Design doc:
- Design revision:
- Audited default-branch SHA:
- Decision: Ready | Ready with follow-ups | Not ready
- Blocking findings:
- Non-blocking follow-ups:
- Story completion:
- Design alignment:
- Documentation:
- Verification:
- Residual risk:
```

## Story `done` invariant

A story is `done` only when all applicable conditions hold:

1. Its canonical issue matches the current design and story revisions.
2. Exactly one current completion proof exists: either (a) one intended delivery leaf identified by the complete current revision tuple, immutable delivery ID, and explicit `supersedes` marker, or (b) one valid current-revision carry-forward record. Older or superseded PRs remain history and are not a second proof.
3. For a delivery leaf, its intended PR is merged or an explicit repository-policy exception is recorded. For carry-forward, the exact historical PR and reviewed/merged head have been independently revalidated against every current criterion and shared contract.
4. The merged PR closes the canonical issue, or issue closure is independently verified and explained.
5. Independent review found no unresolved blocking findings.
6. Required checks passed, or a user-authorized exception is recorded with residual risk.
7. Every acceptance criterion has direct code, test, documentation, or completed manual-verification evidence, or a durable owner-manual policy explicitly permits completion with that criterion pending.
8. Relevant user-facing documentation is current.
9. The reviewed head SHA is the delivered head, and no later dependency merge or design revision invalidated the evidence.

`Approve`, `Comment only`, an open PR, a closed issue without merge evidence, or a newly created follow-up issue does not satisfy this invariant.

## Delivery attempts and carry-forward

- Give every delivery PR an immutable ID such as `<design-slug>-<story-id-lowercase>-a<N>`, choosing the next unused monotonically increasing attempt after enumerating open, closed, and merged PRs for the composite story identity.
- Add `<!-- feature-delivery:delivery-id=<ID> -->` and `<!-- feature-delivery:supersedes=<PR-NUMBER|none> -->` to every PR. The unique current leaf is the non-superseded attempt for the current revision tuple.
- When an unmerged PR crosses a design revision, keep its delivery ID, branch, and PR. After verifying its issue, diff, and scope against the revised contract, comment with the old tuple and update only its revision markers. Then require fresh implementation verification and independent review.
- Never rewrite markers on merged PRs. A replacement PR gets a new delivery ID and supersedes the prior leaf.
- Carry-forward is not marker rewriting. Record a durable issue comment containing design revision, story revision, historical PR, reviewed head SHA, reviewer, criterion evidence, and `<!-- feature-delivery:carry-forward -->`. It is valid only for that exact current revision tuple and requires independent review.

Carry-forward is an explicit alternative transition, not a shortcut inside issue synchronization:

1. Reconcile the canonical issue to the new design/story tuple and reopen it.
2. Give an independent `user-story-reviewer` the Carry-Forward Review Handoff inputs. The reviewer inspects the current issue/design and the historical merged head on the current default branch.
3. On `Reopen delivery`, leave the issue open and enter normal implementation.
4. On `Carry forward`, the coordinator posts this exact durable issue-comment schema and only then closes the issue:

```markdown
<!-- feature-delivery:carry-forward -->
- Current design revision: <SHA-256>
- Current story revision: <SHA-256>
- Historical PR: #<number>
- Historical delivery ID: <ID>
- Historical design revision: <SHA-256>
- Historical story revision: <SHA-256>
- Historical reviewed and merged head SHA: <git SHA>
- Reviewer: <identity/context>
- Current acceptance criteria evidence: <evidence>
- Current shared-contract evidence: <evidence>
- Verification: <commands/checks>
```

The record is invalid after a new design/story revision, a change to the historical delivered code, an unresolved blocker, or missing independent-review evidence. Never rewrite historical PR markers.

## Audit gap contract

A blocking final-audit integration or documentation finding that cannot be assigned to an existing design story becomes one canonical audit gap:

- Normalize it with `scripts/audit_gap_contract.py`; do not invent an identity manually. Give the finding a durable semantic `stable_key` such as `integration:event-forwarding` so wording and line shifts do not create duplicates.
- Its ID is `GAP-<first 12 uppercase hex characters of SHA-256(stable_key)>`.
- Its gap revision is SHA-256 of the canonical JSON payload containing stable key, design identity/revision, category, affected stories, evidence, required remediation, binary acceptance criteria, verification, and dependency IDs.
- Its canonical issue carries the normal design, design-revision, story, and story-revision markers, using the gap ID as `story` and the full gap revision as `story-revision`, plus `<!-- feature-delivery:audit-gap=<FULL-GAP-REVISION> -->`.
- Reconcile by exact design identity plus gap ID across open and closed issues. The same stable finding reuses its issue; changed evidence/remediation/criteria updates its gap revision and reopens stale delivery rather than creating a duplicate.
- Gap dependencies must be `done` before implementation. Delivery IDs, branches, PR markers, review epochs, supersession, merge, closure, and acceptance evidence follow the same rules as design stories.

An audit gap is in feature scope until delivered or explicitly resolved by a user-authorized scope decision. Creating or closing its issue without a reviewed delivery does not satisfy feature completion.

Its managed issue body is deterministic:

```markdown
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:story=<GAP-ID> -->
<!-- feature-delivery:design-revision=<DOCUMENT-REVISION> -->
<!-- feature-delivery:story-revision=<GAP-REVISION> -->
<!-- feature-delivery:audit-gap=<GAP-REVISION> -->

## Managed Audit Gap Contract
<canonical_payload emitted by audit_gap_contract.py in a fenced json block>

## Canonical Dependencies
<canonical numbered issue references or None>
```

## Feature completion invariant

The feature is complete only when:

- all in-scope stories are `done`;
- all blocking integration and audit gaps have passed through implementation and independent review;
- the latest full-feature audit reports the threshold required by the goal;
- strongest relevant repository verification passes;
- no known blocking risk is merely deferred; authorized owner-manual criteria remain disclosed as pending rather than reported as passed.
