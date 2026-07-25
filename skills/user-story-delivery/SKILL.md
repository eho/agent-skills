---
name: user-story-delivery
description: 'Deliver one specific GitHub user story end to end through implementation, independent review, revision, and merge-policy completion. Use when asked to implement and review, finish, resume, or fully deliver one story or issue. This is the single-story facade for the same completion contract used by feature-delivery; approval or comment-only review is not completion while merge is still required.'
metadata:
  author: eho
  version: '2.0.0'
---

# User Story Delivery

Coordinate exactly one canonical GitHub Issue through implementation and independent review. For multi-story design documents, use `feature-delivery`.

## Shared contract

If `feature-delivery/references/contracts.md` is installed alongside this skill, read its handoff schemas and story `done` invariant. Otherwise apply the equivalent invariant below:

- the issue reflects current requirements;
- one intended PR is independently reviewed with no blocking findings;
- required checks and acceptance verification pass;
- the PR is merged and the issue is closed, unless repository policy records an explicit exception;
- relevant documentation is current.

An approval, comment-only sign-off, open PR, or follow-up issue is intermediate state.

## Workflow

1. Resolve the exact story ID and canonical issue. Do not select an unrelated “next” issue without an explicit selection rule.
2. Inspect issue state, dependencies, assignee, existing branch/PR, reviews, checks, and current worktree before acting.
3. Invoke `user-story-implementer` in a worker context:
   - create a branch and PR only when none exists;
   - otherwise resume the existing PR branch;
   - require an Implementation Handoff.
4. Invoke `user-story-reviewer` in a separate reviewer context and require a Review Handoff.
5. Handle review findings:
   - `Request changes`: send findings to the implementer on the same PR.
   - `Fix small issue`: verify the pushed fix and run a fresh review.
   - `Approve` or `Comment only`: apply repository merge policy; do not declare completion yet.
   - `Merge`: verify actual merged PR and closed issue state.
6. Repeat implementation and fresh review until the story meets the `done` invariant.
7. Re-read GitHub after every handoff. Current external state wins over prose.

Five review-fix cycles are an escalation checkpoint. Reassess unclear requirements or a flawed approach rather than declaring the story complete or abandoning it automatically.

## Blockers

Stop only when the story itself has no safe next action. Record the blocker on the issue and report the exact external decision, permission, credential, or dependency required. Do not create a second PR as a recovery mechanism.

## Handoffs

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

## Final report

```markdown
## Story Delivery Status
- Story:
- Issue:
- PR:
- State: Done | Blocked
- Review cycles:
- Acceptance criteria evidence:
- Verification:
- Residual risk or blocker:
```

Keep implementation and review independent. Follow repository `AGENTS.md`, branch, approval, and merge requirements.
