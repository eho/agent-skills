---
name: feature-delivery
description: 'Orchestrate fresh or resumed delivery of a revised multi-story feature: idempotently sync design stories to GitHub Issues, reconcile completed/in-progress/blocked/deferred/remaining work from live issue and PR state plus prior handoffs, deliver dependencies one at a time, and run a final release audit. Use for complete design-to-release delivery or continuing an interrupted feature run.'
metadata:
  author: eho
  version: '1.1.0'
---

# Feature Delivery

Act as the top-level coordinator. Compose, but do not duplicate, these specialists:

- `design-to-issues`: exact, idempotent requirements synchronization.
- `user-story-delivery`: independent implement-review delivery for one story.
- `post-implementation-reviewer`: report-first release audit.

The workflow must be safe both on a fresh run and after interruption. GitHub is the durable ledger; prior handoffs accelerate reconciliation but do not override live state.

**Prerequisites:** `gh` must be installed and authenticated, and all three specialist skills must be available.

## Workflow

1. **Resolve scope and readiness**
   - Require one exact design-document path. Never auto-select a design.
   - Require `## User Stories`, stable story IDs, acceptance criteria, and `Status: Revised` or equivalent explicit authorization.
   - Extract story order, dependencies, prefix, milestone, and explicit user deferrals.

2. **Synchronize issues**
   - Run `design-to-issues`.
   - Require its exact `Issue Sync Handoff`, including every current story, issue state, deferred stories, removed stories, dependency result, and blocker.
   - Stop on duplicate IDs, incomplete mapping, or blocked dependency synchronization.

3. **Collect durable evidence**
   - Gather any prior `Feature Delivery Status`, `Story Delivery Handoff`, implementation/review handoffs, or final-audit handoff available in the conversation or supplied artifacts.
   - Query live GitHub state for every mapped story:
     ```bash
     gh issue view <issue> --json number,title,state,body,comments,labels,assignees,closedAt,url
     gh pr list --state all --search "<story-id>" \
       --json number,title,state,isDraft,headRefName,baseRefName,body,mergedAt,closedAt,mergeCommit,reviewDecision,statusCheckRollup,mergeStateStatus,url --limit 50
     ```
   - Confirm PR identity through exact story ID, issue-closing references, body, branch, or commits. Stop on multiple plausible PRs.
   - Fetch the remote default branch before checking merge ancestry. Never infer freshness from a local branch alone.

4. **Reconcile every story**
   - Classify each in-scope story exactly once:
     - `completed`: its intended PR is merged and the merge commit is reachable from `origin/<default>`. An open issue may be ledger drift but does not invalidate merged code; record it.
     - `in_progress`: exactly one intended PR is open. Record branch, review state, checks, and whether changes are requested or human merge is pending.
     - `blocked`: a current blocked label/handoff, ambiguous PRs, a closed-unmerged PR without explicit replacement, failed state reconciliation, missing dependency evidence, or an issue closed without merged implementation evidence.
     - `deferred`: explicitly deferred by the user for this run. Do not infer this state from GitHub lifecycle and do not mutate the issue merely to reflect it.
     - `remaining`: an open, non-blocked issue with no intended PR.
   - Validate prior handoffs against these rules. Stale handoffs are history, not current state.
   - Never send `completed` or `deferred` stories to an implementer. Resume `in_progress` through its existing PR. Only `remaining` stories start new branches.

5. **Build the dependency queue**
   - Preserve design order among stories at the same dependency level.
   - A dependency is satisfied only by `completed` state. Pass its issue, PR, and reachable merge OID to the dependent story.
   - A deferred or blocked dependency blocks its dependents unless the user explicitly revises scope/dependencies.
   - A fresh run stays simple: when every story is `remaining`, this becomes the original dependency-ordered queue.

6. **Deliver and checkpoint one story**
   - Select the earliest eligible `in_progress` story before starting any `remaining` story; interrupted work should be resumed first.
   - Run `user-story-delivery` with story, issue, existing PR if any, design path, milestone, and dependency evidence.
   - Require its exact `Story Delivery Handoff`.
   - Requery GitHub after the handoff. Accept `completed` only when the PR is merged and reachable from remote default.
   - If `in_progress` is awaiting a required human merge, stop with a resumable checkpoint. If `blocked`, stop with the blocker.
   - Before the next story, fetch remote default and reconcile the entire matrix again. This catches external merges, closures, new PRs, or changed blockers and prevents duplicate work.

7. **Bound monitoring and review**
   - Let the active story coordinator own its bounded five-cycle implement-review loop.
   - Do not replace an active specialist with a recovery worker. If there is no observable branch/PR movement for 20 minutes, request status from the same worker.
   - Keep implementer and reviewer roles independent.

8. **Run the final audit**
   - Start only when every in-scope, non-deferred story is live-verified `completed`; no `in_progress`, `remaining`, or `blocked` entries may remain.
   - Pass the design, milestone, complete issue/PR/merge-commit matrix, deferrals, ledger drift, verification, and residual risks to `post-implementation-reviewer`.
   - Require its exact `Final Audit Handoff`.

## Exact story handoff

`user-story-delivery` must return:

```markdown
## Story Delivery Handoff
- Story ID:
- Issue:
- State: completed | in_progress | blocked
- Branch:
- PR:
- PR state: OPEN | MERGED | CLOSED | none
- Merge commit:
- Final decision: Merge | Awaiting human merge | Blocked
- Review cycles:
- Dependencies verified:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

## Exact issue-sync handoff

`design-to-issues` must return:

```markdown
## Issue Sync Handoff
- Design doc:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<number> <url> (<Created|Updated|Unchanged>; issue <OPEN|CLOSED>)
- Deferred stories:
- Removed stories:
- Dependencies: Synchronized | Blocked
- Blocked: yes/no
- Blocker:
```

## Exact final-audit handoff

```markdown
## Final Audit Handoff
- Design doc:
- Decision: Ready | Ready with follow-ups | Not ready
- Remediation PR:
- Blocking findings:
- Follow-up issues:
- Verification:
- Residual risk:
- Blocked: yes/no
- Blocker:
```

## Specialist prompts

### Issue synchronization

```text
Use design-to-issues to synchronize this revised design with GitHub:
Design doc: <path>

Perform exact body/title reconciliation, marker-based dependency upserts, and safe removal/deferral reporting. Return the exact Issue Sync Handoff from that skill.
```

### Story delivery

```text
Use user-story-delivery for exactly one story.
Design doc: <path>
Story: <id>
Issue: <number-or-url>
Existing PR: <number-or-none>
Milestone: <milestone>
Completed dependencies: <story, issue, PR, reachable merge OID list>
Entry state: <remaining-or-in_progress>

Resume an existing PR when supplied; never create a duplicate. Return the exact Story Delivery Handoff.
```

### Final audit

```text
Use post-implementation-reviewer for a report-first final audit.
Design doc: <path>
Milestone: <milestone>
Story prefix: <prefix>
Reconciled story matrix: <story, issue, PR, merge OID, verification>
Deferred stories: <list>
Ledger drift and residual risks: <list>

Return the exact Final Audit Handoff. Do not edit the release branch directly.
```

## Final status report

```markdown
## Feature Delivery Status
- Design doc:
- Milestone:
- Story prefix:
- Final state: Ready | Ready with follow-ups | Not ready | Blocked

## Story State Matrix
| Story | Issue | State | Branch | PR | PR State | Merge Commit | Dependencies | Verification | Residual Risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Reconciliation
- Completed:
- In progress:
- Blocked:
- Deferred:
- Remaining:
- Removed from design:
- Ledger drift:

## Final Audit
- Decision:
- Remediation PR:
- Blocking findings:
- Follow-up issues:
- Verification:

## Next Action
- <exact resumable next action or "None">
```

Always emit this report when pausing or finishing. It is a checkpoint for the next run, but the next run must still validate it against GitHub.

## Operating rules

- Synchronize requirements before reconciling delivery state.
- Closed issue alone is never completion; approval alone is never completion.
- Merged and reachable code is completion even if issue closure bookkeeping lags.
- Resume open PRs before starting remaining stories.
- Reconcile the whole matrix after every story transition.
- Never skip blocked dependencies, duplicate a branch/PR, or run the final audit early.
- Keep specialist separation and bounded review loops intact.
