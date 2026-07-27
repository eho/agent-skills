---
name: post-implementation-reviewer
description: 'Run an independent, report-only final audit of a delivered design document or multi-story feature. Reconcile every current design story with canonical GitHub Issues, merged PRs, review and acceptance evidence, integration behavior, documentation, and verification, then decide Ready, Ready with follow-ups, or Not ready. Use for final audits, release-readiness checks, goal completion gates, and feature-delivery audit-remediation loops.'
metadata:
  author: eho
  version: '3.2.0'
---

# Post-Implementation Reviewer

Determine whether the current implementation satisfies the complete design. Remain report-only so the feature coordinator can route findings through implementation and independent story review.

This skill is always report-first and report-only. Do not edit code, push commits, merge PRs, change issues, create follow-up issues, or otherwise remediate during the audit. If the user also requests fixes, finish and hand off the complete audit first; remediation must run through the normal implementation and independent-review workflow in a separate phase.

## Audit

1. Read repository and scoped `AGENTS.md` files plus project documentation before inspecting implementation state.
2. Read the exact design document in full. Extract every in-scope story, dependency, and acceptance criterion before querying GitHub.
3. Compute the whole-document and per-story revisions with the installed `design-to-issues/scripts/story_contract.py` when available; otherwise apply its exact normalization contract. Identify the complete composite marker convention.
4. Build the complete traceability matrix:
   - current design story;
   - canonical issue, design identity, document revision, and story revision;
   - delivery IDs, supersession graph, unique current leaf, and any carry-forward record;
   - review and merge evidence;
   - issue closure;
   - acceptance-criteria evidence.
   Also enumerate every canonical audit-gap issue under the feature milestone. A gap remains in scope across audit passes until its current gap revision satisfies the ordinary delivery invariant or a user-authorized terminal scope decision exists.
5. Flag missing, duplicate, unresolved orphaned, or stale issues. Treat a terminal `scope=removed|deferred;decided-at-revision=<REVISION>` marker as resolved scope history across unrelated later revisions until an explicit restoration/supersession decision or the story reappears. A historical closed issue without that durable scope decision is insufficient when either revision differs or its managed delivery contract drifted.
6. Verify each delivered story:
   - current delivery-leaf PR merged, a documented repository-policy exception exists, or an independently reviewed current-revision carry-forward record proves the historical merged head;
   - independent review covers the delivered head SHA and has no unresolved blocker;
   - required checks passed or an explicit exception exists;
   - every criterion has meaningful code, test, documentation, or manual evidence.
7. Inspect the current codebase, not only PR descriptions. Compare architecture, APIs, data contracts, state ownership, persistence, auth, permissions, failures, migrations, compatibility, rollout, and rollback with the design.
8. Test cross-story integration and critical user flows. Individual story success does not prove the assembled feature works.
9. Audit user-facing and operational documentation, examples, configuration, diagnostics, and terminology.
10. Discover repository verification commands and run the strongest relevant suite. Do not imply unrun checks passed.
11. Classify every finding:
    - blocking story gap;
    - blocking integration gap;
    - blocking documentation/operational gap;
    - product decision required;
    - genuinely non-blocking follow-up.
12. Complete every audit category even after discovering a blocker. Return one exhaustive finding set so remediation does not require another full pass merely to discover a pre-existing documentation or operational gap.

Reuse immutable story/PR/review evidence from a prior audit pass when its identity and ancestry remain valid. Recompute the current default-branch head, changed delivery leaves, affected integrations, documentation, and strongest-gate validity. Evidence reuse reduces repeated history traversal; it never permits a partial audit or hides newly introduced drift.

## Decision

- `Ready`: no blocking findings; all story and feature completion evidence is current.
- `Ready with follow-ups`: only non-blocking improvements remain. Explain why each cannot affect correctness, safety, compatibility, operations, or explicit acceptance criteria.
- `Not ready`: any story is incomplete/stale, required verification fails, documentation required for correct use is absent, or blocking integration/design drift remains.

Creating a follow-up issue would not make a blocking finding non-blocking. Report the work required; the coordinator owns remediation and reruns this entire audit afterward.

## Report

```markdown
## Findings
- Blocking findings first with story/issue/PR and code evidence.
- If none: No blocking findings found.

## Story Completion Matrix
| Story | Document Revision | Story Revision | Delivery Leaf | Issue | PR | Reviewed Head | Merge/Closure | Acceptance Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Integration and Design Alignment
- Critical flows:
- Architecture/API/data contracts:
- Security/data safety/compatibility:
- Drift:

## Documentation and Operations
- Current:
- Missing or stale:
- Observability/rollout/rollback:

## Verification
- Commands/checks run:
- CI reviewed:
- Manual/browser checks:
- Not verified:
- Residual risk:

## Required Remediation
- Existing story gaps:
- New integration gaps:
- Product decisions:
- Non-blocking follow-ups:

## Release Readiness
Decision: Ready | Ready with follow-ups | Not ready
Rationale:
```

## Handoff

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
