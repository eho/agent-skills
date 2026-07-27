---
name: user-story-reviewer
description: 'Independently review one GitHub story PR against its canonical issue and every acceptance criterion, run risk-relevant verification, request changes or sign off, and merge when repository policy permits. Use for PR QA or as the reviewer in user-story-delivery.'
metadata:
  author: eho
  version: '4.0.0'
---

# User Story Reviewer

Review exactly one story PR independently from its implementer. Review only; send all code changes back to the implementer so the next review remains independent.

## Review

1. Read repository instructions, the complete issue, acceptance criteria, dependencies, prior findings, and repository merge policy.
2. Inspect the PR metadata, base, current head SHA, draft state, commits, changed files, checks, mergeability, linked issue, and existing reviews.
3. Read the diff and relevant surrounding code.
4. Check every acceptance criterion against concrete implementation and verification evidence.
5. Review correctness, regressions, tests, failure paths, security, permissions, data safety, compatibility, migrations, concurrency, performance, diagnostics, operations, and documentation where relevant.
6. Run focused independent verification for the changed behavior and highest risks. Reuse a trustworthy broad test result bound to the exact current head unless repository policy or risk requires rerunning it.
7. Exercise meaningful user-visible behavior in the appropriate runtime when tooling is available; automated tests alone do not prove visual or interactive acceptance criteria.
8. Report blocking findings with a precise location, incorrect behavior, impact, and required change.

Any pushed commit invalidates sign-off. Review the new head in a fresh independent context.

## Decision and merge

- `Request changes` when any acceptance, correctness, safety, compatibility, or meaningful test-confidence problem remains.
- `Approve` when all criteria and required checks pass and formal approval is allowed.
- `Comment only` when the implementation is sound but the current GitHub identity cannot formally approve.
- `Merge` only when repository policy authorizes it and all prerequisites pass.

Immediately before approval or merge, verify that the PR remains open, non-draft, based on the expected branch, at the exact reviewed head, mergeable, and compliant with required checks and review policy.

Resolve and use `scripts/approve_or_merge_pr.sh` for commit-bound approval or merge. Inspect its `--help` and pass the expected head and the repository-authorized direct merge method or queue mode. Do not enable asynchronous auto-merge.

After merging, re-read the PR and issue. Report actual merge and closure state rather than assuming the command succeeded.

## Review record and handoff

Post the detailed review on the PR:

```markdown
## Findings
- <blocking findings or "No blocking findings found.">

## Acceptance Criteria
| Criterion | Evidence | Result |
| --- | --- | --- |

## Verification
- Commands/checks:
- Not verified:
- Residual risk:

## Decision
Decision: Request changes | Approve | Comment only | Merge
```

After taking the review action, return only this compact handoff to the coordinator:

```markdown
- Issue:
- PR:
- Head SHA:
- Result:
- Acceptance-criteria evidence:
- Verification:
- Blocking findings:
- Merge result:
```
