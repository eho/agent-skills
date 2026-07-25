# Feature Delivery Contracts

Use these handoffs between coordinator and specialists. Validate handoffs against current GitHub state before transitioning.

## Issue Sync Handoff

```markdown
## Issue Sync Handoff
- Design doc:
- Design revision:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<number> <url> (<Created|Updated|Reopened|Unchanged>)
- Dependencies reconciled: yes/no
- Stale delivered stories reopened:
- Blocked: yes/no
- Blocker:
```

## Implementation Handoff

```markdown
## Implementation Handoff
- Story ID:
- Issue:
- Branch:
- PR:
- Mode: Created | Resumed | Revised
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
- PR:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Required follow-up:
- Acceptance criteria evidence:
- Verification:
```

## Final Audit Handoff

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

## Story `done` invariant

A story is `done` only when all applicable conditions hold:

1. Its canonical issue matches the current design revision.
2. The current design revision has exactly one intended delivery chain, identified by story and design-revision markers. Older-revision PRs remain valid history but do not prove current completion.
3. The current delivery chain's intended PR is merged, or an explicit repository-policy exception is recorded.
4. The merged PR closes the canonical issue, or issue closure is independently verified and explained.
5. Independent review found no unresolved blocking findings.
6. Required checks passed, or a user-authorized exception is recorded with residual risk.
7. Every acceptance criterion has direct code, test, documentation, or manual-verification evidence.
8. Relevant user-facing documentation is current.
9. No later dependency merge or design revision invalidated the evidence.

`Approve`, `Comment only`, an open PR, a closed issue without merge evidence, or a newly created follow-up issue does not satisfy this invariant.

## Feature completion invariant

The feature is complete only when:

- all in-scope stories are `done`;
- all blocking integration and audit gaps have passed through implementation and independent review;
- the latest full-feature audit reports the threshold required by the goal;
- strongest relevant repository verification passes;
- no known blocking risk is merely deferred.
