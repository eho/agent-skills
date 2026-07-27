---
name: design-doc-reviewer
description: "Independently and read-only review a design doc, PRD, spec, or requirements for repository accuracy, material risks, and canonical story readiness. Produces a binary readiness verdict with evidence-backed blocking findings and optional non-blocking suggestions. Use design-doc-review-loop when revisions or feature-delivery readiness are requested."
triggers:
  - review this design doc
  - review the design
  - critique this design
  - check this spec
  - review this spec
  - give feedback on this design
  - review the prd
  - audit the requirements
  - review the requirements
  - one-time design review
  - read-only design review
metadata:
  author: eho
  version: '3.0.0'
---

# Design Doc Reviewer

Independently determine whether a design is a sound, economical implementation
contract. Stay read-only: save a review artifact, but do not revise the design
or change its status.

Read the complete target document and
[`../design-doc/references/design-contract.md`](../design-doc/references/design-contract.md).
Do not load the writer prompt; the shared contract is the review boundary.

## Ground the review

Read repository instructions and relevant vision or architecture documents.
Independently inspect the highest-risk code, tests, schemas, configuration, and
call sites behind material claims. Distinguish in the review:

- verified current repository facts;
- proposed design decisions;
- unresolved assumptions.

Use risk-proportionate exploration rather than reproducing the writer's entire
discovery pass. A precise-looking path or signature is not evidence until
verified.

Resolve `design-to-issues/scripts/story_contract.py` and run:

```bash
python3 <story-contract-script> <design-doc> \
  --repo-root <repository-root> --mode author
```

Mechanical validation failure is blocking. The script judges syntax and
structure, not semantic quality.

## Review modes

### Initial review

Read the whole design and inspect all material implementation boundaries. Ask:

- Does the design solve the stated product problem within its authorized scope?
- Are architecture, ownership, state/data contracts, integration behavior, and
  failure paths consistent with the repository and with one another?
- Where relevant, are security, privacy, permissions, migration, compatibility,
  rollout, rollback, performance, and operations safe enough to implement?
- Can the risky behavior be verified without relying on circular, unavailable,
  or post-hoc evidence?
- Does each canonical story describe one coherent outcome, include all shared
  requirements that affect it, use valid dependencies, and provide binary
  criteria and realistic verification?
- Is any detail speculative, duplicated, or disproportionate to the feature?
  Prefer simplification or existing mechanisms when they satisfy the invariant.

Treat a concern as blocking only when it could plausibly cause incompatible or
unsafe implementations, incorrect behavior, data/security/migration/
compatibility failure, an impossible criterion, or an unresolved decision
needed for an in-scope story. Missing polish or a possible enhancement is
non-blocking.

### Follow-up review

When given a prior review, verify:

1. each prior blocking finding;
2. changed sections and every story or dependency surface they affect;
3. mechanical validation;
4. critical regressions introduced by the revision.

Do not regenerate a full checklist or reopen waived suggestions. Widen to a
full review when changes alter cross-cutting architecture, security boundaries,
data contracts, migration, compatibility, rollout, or story sequencing enough
that a focused review would be unsafe.

## Findings

Every blocking finding contains:

- **Evidence:** exact design location plus verified repository evidence or a
  concrete internal contradiction;
- **Impact:** how implementation or delivery could fail;
- **Required invariant:** the condition a revision must satisfy.

Do not prescribe a new subsystem when several solutions could satisfy the
invariant. Offer an example only when it materially clarifies the gap.

Non-blocking suggestions must be worthwhile and concise. They may remain or be
waived and never prevent a `Ready` verdict. Do not require strengths, generic
section commentary, numeric scores, or arbitrary issue counts.

## Output

Use the next unused versioned path:
`docs/design/reviews/<design-slug>/review-<NN>.md`. If repository conventions
require another durable path, preserve every pass rather than overwriting the
previous artifact.

```markdown
# Design Review: [title]

- Design: `docs/design/<file>.md`
- Reviewed: YYYY-MM-DD
- Mode: Initial | Follow-up
- Verdict: Ready | Not ready
- Mechanical validation: Pass | Fail
- Blocking findings: N
- Non-blocking suggestions: N

## Blocking Findings

### B1: [short title]
- Evidence:
- Impact:
- Required invariant:

## Non-Blocking Suggestions
- N1: [concise optional improvement]

## Prior Findings
- B1: Resolved | Unresolved | Regressed — [evidence]

## Handoff
- User decisions required:
- Affected story IDs:
- Recommended next action:
```

Omit empty finding sections or state `None`. `Ready` means author-mode
mechanical validation passed, no blocking finding remains, and no unresolved
decision prevents an in-scope story. A one-time reviewer reports this verdict
but never promotes the design to `Revised`.
