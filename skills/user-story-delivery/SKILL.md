---
name: user-story-delivery
description: 'Deliver one specific GitHub user story end to end through implementation, independent review, revision, and merge-policy completion. Use when asked to implement and review, finish, resume, or fully deliver one story or issue. This is the single-story facade for the same completion contract used by feature-delivery; approval or comment-only review is not completion while merge is still required.'
metadata:
  author: eho
  version: '2.1.0'
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

1. Read repository and scoped `AGENTS.md` files plus project documentation.
2. Resolve the exact story ID and canonical issue. Do not select an unrelated “next” issue without an explicit selection rule.
3. Inspect issue state, complete revision marker tuple, dependencies, assignee, local/remote branches, worktree ownership, PRs, reviewed head SHAs, checks, and current worktree before acting.
4. Invoke `user-story-implementer` in a worker context:
   - create a branch and PR only when no canonical local/remote branch or PR exists;
   - for a new branch, use the fetched remote default tip and verify every dependency merge SHA is its ancestor;
   - otherwise resume the existing PR branch;
   - require an Implementation Handoff.
5. Invoke `user-story-reviewer` in a separate reviewer context and require a Review Handoff.
6. Handle review findings:
   - `Request changes`: send findings to the implementer on the same PR.
   - `Fix small issue`: verify the pushed fix and run a fresh review in a context independent of the fix author.
   - `Approve` or `Comment only`: apply repository merge policy; do not declare completion yet.
   - `Merge`: verify actual merged PR and closed issue state.
7. Repeat implementation and fresh review until the story meets the `done` invariant.
8. Re-read GitHub after every handoff. Current external state wins over prose.

Use review epochs of at most five review-fix cycles. Generate stable per-finding IDs with the structured `feature-delivery/scripts/fingerprint_findings.py` contract and persist the exact `feature-delivery:review-ledger` comment from the shared contracts after every review. Reconstruct only entries matching the current delivery ID and head SHA. At the boundary, rehydrate and stop automatic retry. Continue only with a materially different safe strategy and a fresh reviewer. If the same finding ID survives two epochs, record the exact blocker and request the missing product or architecture decision; never declare completion from the limit.

## Blockers

Stop only when the story itself has no safe next action. Record the blocker on the issue and report the exact external decision, permission, credential, or dependency required. Do not create a second PR as a recovery mechanism.

## Handoffs

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
