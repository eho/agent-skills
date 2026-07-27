---
name: post-implementation-reviewer
description: 'Run an independent, report-only overall audit of a delivered design document or multi-story feature. Verify story completion, assembled behavior, design alignment, documentation, and relevant tests, then report whether blocking findings remain.'
metadata:
  author: eho
  version: '4.0.0'
---

# Post-Implementation Reviewer

Audit the complete implemented feature against its design document. Remain report-only: do not edit code, push commits, merge PRs, change issues, or create remediation issues.

## Audit

1. Read repository instructions and the complete design document.
2. Extract every current story, dependency, and acceptance criterion.
3. Map each story to its canonical GitHub Issue and delivered Pull Request. Flag missing, duplicate, open, unmerged, unreviewed, or stale work.
4. Verify that every acceptance criterion has meaningful implementation and evidence.
5. Inspect the current codebase rather than relying only on issue or PR descriptions.
6. Test important cross-story integration and critical user flows.
7. Check architecture, APIs, data contracts, state ownership, security, permissions, failures, compatibility, migrations, rollout, and rollback where relevant.
8. Audit user-facing and operational documentation, examples, configuration, diagnostics, and terminology.
9. Run the strongest relevant repository verification that is not already covered by trustworthy exact-head evidence. Do not imply unrun checks passed.
10. Complete the entire audit even after finding a blocker so remediation receives one complete finding set.

Classify findings as:

- an existing story gap;
- a cross-story integration or documentation gap;
- a product decision requiring user authority; or
- a genuinely non-blocking follow-up.

Report `Ready` only when no blocking finding remains. Creating a follow-up issue does not make a blocking finding non-blocking.

## Report

```markdown
## Findings
- Blocking findings first.
- If none: No blocking findings found.

## Story Completion
| Story | Issue | PR | Acceptance Evidence | Status |
| --- | --- | --- | --- | --- |

## Integration and Design Alignment
- Critical flows:
- Design or implementation drift:

## Documentation and Operations
- Current:
- Missing or stale:

## Verification
- Commands/checks:
- Not verified:
- Residual risk:

## Required Remediation
- Existing story gaps:
- Cross-story gaps:
- Product decisions:
- Non-blocking follow-ups:

## Release Readiness
Decision: Ready | Not ready
```
