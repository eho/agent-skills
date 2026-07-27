---
name: feature-delivery
description: 'Deliver every user story in a revised design document through GitHub issue synchronization, single-story implementation and independent review, merge, and an overall feature audit. Use when asked to deliver, ship, resume, finish, or fully implement a complete design doc or multi-story feature.'
metadata:
  author: eho
  version: '3.0.0'
---

# Feature Delivery

Deliver the feature described by one design document. The design document defines scope. GitHub Issues track story progress, and Pull Requests track implementation, review, verification, and merge history.

Use these specialists:

- `design-to-issues` to synchronize stories with GitHub;
- `user-story-delivery` to deliver one issue at a time;
- `post-implementation-reviewer` for the final feature audit.

If a required specialist is unavailable, report that prerequisite instead of silently combining implementation and independent review in one context.

## Workflow

1. Read repository instructions and the complete design document.
2. Confirm the document is ready for implementation and contains stable story IDs, dependencies, and testable acceptance criteria. Proceed with an unrevised document only when the user explicitly requests it.
3. Run `design-to-issues` to create or update one canonical GitHub Issue for every current story. Use the issue state, body, comments, linked PRs, and dependencies as the durable progress record.
4. Inspect all canonical story issues:
   - a closed issue with a merged, reviewed PR is complete;
   - an open issue is remaining work;
   - resume an existing branch or PR rather than creating a duplicate;
   - work only on stories whose dependencies are complete.
5. Invoke `user-story-delivery` for one dependency-ready open issue. Require it to implement every acceptance criterion, obtain independent review, address blocking findings, merge according to repository policy, and verify issue closure.
6. Re-read the issue and PR after the handoff. Continue until every in-scope story issue is complete. If one story is blocked, continue unrelated dependency-ready stories.
7. Invoke `post-implementation-reviewer` with the original design document. The auditor must inspect the assembled implementation, story completion, cross-story behavior, documentation, and relevant verification.
8. Handle audit results:
   - attach a story-specific blocking finding to its canonical issue, reopen it if necessary, and deliver it again through `user-story-delivery`;
   - create one ordinary GitHub Issue for a blocking integration or documentation gap that does not belong to an existing story, give it concrete acceptance criteria, and deliver it through `user-story-delivery`;
   - request the user's decision when remediation would expand the approved design scope;
   - rerun the overall audit after blocking remediation.
9. Finish only when every in-scope story is complete and the latest overall audit reports no blocking findings.

## Completion rules

A story is complete only when:

- its canonical issue reflects the current story requirements;
- every acceptance criterion has implementation and verification evidence;
- an independent reviewer found no unresolved blocking issue;
- required checks and repository merge policy passed;
- the reviewed PR head was merged; and
- the canonical issue is closed.

The feature is complete only when all current stories satisfy those rules and the overall audit has no blocking findings. Issue creation, an open or approved PR, a review checkpoint, or a newly filed follow-up issue is not completion.

## Safety and authorization

- Current repository and GitHub state outrank conversation handoffs.
- Resolve ambiguous duplicate issues or PRs before proceeding.
- Preserve unrelated and dirty worktree changes.
- Never replace active work merely because a worker is slow or interrupted.
- Do not remove or defer a design story without explicit user authority.
- Do not treat unperformed manual verification as passed.
- Follow repository-specific branch, review, check, merge, and branch-retention policy.
- Never create or complete a runtime goal unless the user authorized that goal and this feature satisfies it.

## Final report

```markdown
## Feature Delivery Status
- Design:
- Final audit: Ready | Not ready

| Story | Issue | PR | Status | Verification |
| --- | --- | --- | --- | --- |

## Audit
- Blocking findings remediated:
- Remaining non-blocking follow-ups:

## Remaining Work
- None | exact blocker and required action
```
