---
name: user-story-delivery
description: 'Deliver one specific GitHub Issue end to end through implementation, acceptance-criteria verification, independent review, revision, merge, and issue closure. Use when asked to implement and review, finish, resume, or fully deliver one story or issue, or when feature-delivery delegates a story.'
metadata:
  author: eho
  version: '3.1.0'
---

# User Story Delivery

Coordinate one canonical GitHub Issue through implementation and independent review. GitHub is the durable progress record.

Use `user-story-implementer` for implementation and `user-story-reviewer` in a separate context for review and merge.

## Workflow

1. Read repository instructions and the complete issue, including dependencies, scope, acceptance criteria, comments, and linked work.
2. Resolve any existing local or remote branch and Pull Request for the issue. Resume them instead of creating duplicates. Stop on ambiguous candidates.
3. Confirm dependencies are delivered and the issue has testable acceptance criteria.
4. For a new story, invoke `user-story-implementer` in a fresh, clearly named
   context; do not repurpose a worker from another story. Resume an existing
   same-story worker only when its ownership and state are unambiguous.
   Require evidence for every acceptance criterion and focused verification of
   the changed behavior.
5. Wait for a complete implementation handoff. Do not start review from a
   partial head, and do not repeat unchanged progress reports while the worker
   is active.
6. Verify the implementer's reported PR and head SHA against GitHub.
7. Invoke `user-story-reviewer` in an independent context. The reviewer checks the implementation against every acceptance criterion, runs risk-relevant verification, and either requests changes or signs off and merges when repository policy permits.
8. When review finds blocking problems, send the complete finding set to the
   same implementer and wait for a complete revised handoff on the same PR.
   Review that head in a fresh independent reviewer context.
9. Repeat until no blocking findings remain, required checks pass, and the PR is merged according to repository policy.
10. Re-read the PR and issue. Finish only after the reviewed head is merged and the canonical issue is closed.

If the same blocking behavior survives revision, pause automatic cycling, diagnose the cause, and continue only with a materially different safe approach; otherwise report the decision or change needed.

If correctness requires a product decision, credential, permission, external service, or unfinished dependency, record the concrete blocker on the issue and report the exact action required. A retry limit is not completion.

## Compact handoff

Handoffs between specialist contexts and the coordinator should contain only:

```markdown
- Issue:
- PR:
- Head SHA:
- Result:
- Acceptance-criteria evidence:
- Verification:
- Blocking findings:
- Blocker:
```

Detailed evidence belongs on the issue, PR, review, or check run rather than being repeated in conversation.

## Completion

An approval, comment-only review, open PR, closed issue without merge evidence, or follow-up issue is intermediate state. Report `Done` only when all acceptance criteria are evidenced, independent review has no unresolved blocker, the reviewed head is merged, required checks pass, and the issue is closed.
