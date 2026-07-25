---
name: post-implementation-reviewer
description: 'Run an independent, report-only final audit of a delivered design document or multi-story feature. Reconcile every current design story with canonical GitHub Issues, merged PRs, review and acceptance evidence, integration behavior, documentation, and verification, then decide Ready, Ready with follow-ups, or Not ready. Use for final audits, release-readiness checks, goal completion gates, and feature-delivery audit-remediation loops.'
metadata:
  author: eho
  version: '3.0.0'
---

# Post-Implementation Reviewer

Determine whether the current implementation satisfies the complete design. Remain report-only so the feature coordinator can route findings through implementation and independent story review.

Do not edit code, merge PRs, close issues, or create follow-up issues during this audit unless the user explicitly invokes this skill outside an orchestrated delivery workflow and requests those mutations.

## Audit

1. Read the exact design document in full. Extract every in-scope story, dependency, and acceptance criterion before querying GitHub.
2. Identify the design revision and canonical issue marker convention.
3. Build the complete traceability matrix:
   - current design story;
   - canonical issue and design revision;
   - intended delivery PRs;
   - review and merge evidence;
   - issue closure;
   - acceptance-criteria evidence.
4. Flag missing, duplicate, orphaned, or stale issues. A historical closed issue is insufficient when its design revision differs.
5. Verify each delivered story:
   - intended PR merged or a documented repository-policy exception exists;
   - independent review has no unresolved blocker;
   - required checks passed or an explicit exception exists;
   - every criterion has meaningful code, test, documentation, or manual evidence.
6. Inspect the current codebase, not only PR descriptions. Compare architecture, APIs, data contracts, state ownership, persistence, auth, permissions, failures, migrations, compatibility, rollout, and rollback with the design.
7. Test cross-story integration and critical user flows. Individual story success does not prove the assembled feature works.
8. Audit user-facing and operational documentation, examples, configuration, diagnostics, and terminology.
9. Discover repository verification commands and run the strongest relevant suite. Do not imply unrun checks passed.
10. Classify every finding:
    - blocking story gap;
    - blocking integration gap;
    - blocking documentation/operational gap;
    - product decision required;
    - genuinely non-blocking follow-up.

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
| Story | Design Revision | Issue | PR | Review | Merge/Closure | Acceptance Evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

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
- Decision: Ready | Ready with follow-ups | Not ready
- Blocking findings:
- Non-blocking follow-ups:
- Story completion:
- Design alignment:
- Documentation:
- Verification:
- Residual risk:
```
