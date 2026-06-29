---
name: feature-delivery
description: 'Orchestrate end-to-end delivery of a complete feature from a revised design document: sync user stories to GitHub Issues with design-to-issues, deliver each story one at a time with user-story-delivery, and finish with post-implementation-reviewer. You MUST use this skill when asked to "deliver this design doc", "implement this feature from the design", "run the full feature delivery workflow", "turn this design into issues and ship it", or coordinate multiple user stories from a design document through implementation, review, and final audit.'
metadata:
  author: eho
  version: '1.0.0'
---

# Feature Delivery

You are acting as the top-level coordinator for a complete feature delivery lifecycle. Your job is to compose the existing specialist workflows:

- `design-to-issues`: publishes revised, agent-ready user stories from a design document into GitHub Issues.
- `user-story-delivery`: implements and reviews exactly one GitHub user story through a bounded implement-review loop.
- `post-implementation-reviewer`: audits the completed feature against the original design document, GitHub Issues, PRs, verification evidence, and documentation.

Keep this skill focused on orchestration. Do not duplicate the specialist skills' detailed implementation, issue creation, or audit workflows. The value of this skill is sequencing, state tracking, stop conditions, and a final feature-level delivery report.

**PREREQUISITES**:

- The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) because all downstream delivery steps rely on GitHub Issues and PRs.
- The `design-to-issues`, `user-story-delivery`, and `post-implementation-reviewer` skills MUST be available. Verify these skills are present before starting the workflow. If any required skill is missing, stop and report the missing prerequisite instead of attempting to recreate its behavior here.

## Delegation Requirement

This workflow is designed to use subagents so issue sync, per-story implementation/review, and final audit can stay independent. If the current runtime requires explicit user permission before starting subagents, and the user's request did not clearly ask for the full feature workflow, ask for confirmation before starting. A request such as "use the feature-delivery skill", "deliver this design doc", or "run the full feature delivery workflow" is enough to proceed.

## Workflow

1. **Resolve the Feature Scope**
   - Expect the user to supply a specific design document path or an unambiguous design document reference.
   - If no clear design document is specified, ask the user to confirm the exact design document before continuing. Do not auto-select a design document.
   - Read the design document enough to identify the feature name, story prefix, user story IDs, dependency notes, and expected milestone if present.
   - Confirm the document contains a `## User Stories` section with story IDs and acceptance criteria. If it does not, stop and route the user back to `design-doc`.

2. **Verify Required Skills**
   - Confirm the `design-to-issues`, `user-story-delivery`, and `post-implementation-reviewer` skills are available in the current environment.
   - If any required skill is unavailable, stop and tell the user exactly which skill is missing.
   - Do not inline or approximate a missing specialist workflow inside this skill.

3. **Check Design Readiness**
   - Validate that the design document status is `Revised`.
   - Prefer an explicit status field such as `**Status:** Revised`, `Status: Revised`, or equivalent frontmatter/metadata in the design document.
   - If the design document status is missing or is not `Revised`, stop before creating issues and ask the user to revise or confirm the design document.
   - Do not check a companion review file as part of this workflow.

4. **Sync Stories to GitHub Issues**
   - Run the `design-to-issues` workflow for the design document.
   - Require the issue-sync result to include a story-to-issue mapping:
     ```markdown
     ## Issue Sync Handoff
     - Design doc:
     - Milestone:
     - Story prefix:
     - Issues:
       - <Story ID>: #<issue-number> <url> (<Created|Existing>)
     - Dependencies linked: yes/no
     - Blocked: yes/no
     - Blocker:
     ```
   - If issue sync reports `Blocked: yes`, stop and report the blocker.
   - If the issue mapping is incomplete, ask the same worker for the missing mapping before continuing.

5. **Build the Delivery Queue**
   - Use the design document as the source of truth for story order and dependencies.
   - Use the GitHub issue mapping from `design-to-issues` to bind each story ID to an issue number or URL.
   - Deliver stories in dependency order. When the design document does not state dependencies, preserve the order in the `## User Stories` section.
   - Exclude stories only when the user explicitly marks them out of scope or deferred.
   - Before starting each story, check that all declared dependency stories have completed successfully. If a dependency is incomplete or blocked, stop instead of skipping ahead.

6. **Deliver One Story at a Time**
   - For each queued story, run the `user-story-delivery` workflow.
   - Pass the story ID, issue number or URL, design doc path, milestone when known, and any dependency context.
   - Once a story-delivery subagent starts, let it continue unless it returns a final handoff, reports a blocker, or at least 20 minutes have elapsed with no observable PR or branch movement.
   - Treat PR or branch movement as creation or update of the story branch, pushed commits, a PR being opened or updated, or a handoff/status message that names the active branch or PR.
   - Before spawning any recovery worker for a stalled story, ask the existing story-delivery subagent for status and wait for its response. Only start a recovery worker if the original subagent confirms it is blocked, fails to respond with useful status, or the status shows no safe path forward.
   - Require this final handoff for each story:
     ```markdown
     ## Story Delivery Handoff
     - Story ID:
     - Issue:
     - PR:
     - Final decision: Request changes | Approve | Comment only | Merge | Blocked
     - Review cycles:
     - Verification:
     - Known residual risk:
     - Blocked: yes/no
     - Blocker:
     ```
   - Treat `Merge`, `Approve`, and `Comment only` as story-complete only if the handoff explains why that decision satisfies the repository workflow.
   - Prefer merged PRs for completed stories. If a story is approved but not merged, record the reason and ask the user before continuing unless the repository workflow clearly leaves merging to a human.
   - If a story reports `Blocked: yes`, stop the feature workflow and report the blocker, completed stories, and remaining queue.
   - Do not start the next story until the current story has a concrete final status and verification evidence.

7. **Handle Story Failures**
   - If `user-story-delivery` ends with unresolved blocking findings, do not continue to later stories by default.
   - If the user explicitly chooses to defer a blocked story, update the delivery queue and mark dependent stories blocked unless their dependencies still hold.
   - If the failure is caused by ambiguous requirements, route back to `design-doc` or ask for the missing product decision.
   - If the failure is caused by issue sync mistakes, re-run the relevant `design-to-issues` step or repair the GitHub issue state before continuing.

8. **Run Final Feature Audit**
   - After all in-scope stories are complete, run `post-implementation-reviewer` against the original design document.
   - Pass the design doc path, milestone, story prefix, completed issue mapping, PR list, and any known residual risks from story delivery.
   - Require the final audit to make a release-readiness decision:
     ```markdown
     ## Final Audit Handoff
     - Design doc:
     - Decision: Ready | Ready with follow-ups | Not ready
     - Blocking findings:
     - Follow-up issues:
     - Verification:
     - Residual risk:
     ```
   - If the final audit reports `Not ready`, lead the final report with the blocking findings and exact next actions.

## Subagent Prompts

Use concise prompts that invoke the specialist skill explicitly and require the handoff needed by this workflow. Adapt details to the repository and feature.

### Issue sync prompt

```text
Use the design-to-issues skill to sync this revised design document to GitHub Issues:

Design doc: <path>

Preserve every user story and acceptance criterion. Create or reuse issues idempotently, link dependencies, and attach the milestone according to the design-to-issues workflow.

Return this final handoff:
## Issue Sync Handoff
- Design doc:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<issue-number> <url> (<Created|Existing>)
- Dependencies linked: yes/no
- Blocked: yes/no
- Blocker:
```

### Story delivery prompt

```text
Use the user-story-delivery skill to deliver exactly one story from this feature.

Design doc: <path>
Story: <story-id>
Issue: <issue-number-or-url>
Milestone: <milestone-or-none>
Dependencies already completed: <story-id-list-or-none>

You are part of a larger feature delivery workflow. Do not pick a different story. Follow the user-story-delivery workflow through implementation, review, and bounded review-fix loops.

Return this final handoff:
## Story Delivery Handoff
- Story ID:
- Issue:
- PR:
- Final decision: Request changes | Approve | Comment only | Merge | Blocked
- Review cycles:
- Verification:
- Known residual risk:
- Blocked: yes/no
- Blocker:
```

### Final audit prompt

```text
Use the post-implementation-reviewer skill to audit this completed feature against the original design document.

Design doc: <path>
Milestone: <milestone-or-none>
Story prefix: <prefix>
Completed issues and PRs:
<mapping>
Known residual risks:
<risks-or-none>

Run the full post-implementation review workflow and make a release-readiness decision.

Return this final handoff:
## Final Audit Handoff
- Design doc:
- Decision: Ready | Ready with follow-ups | Not ready
- Blocking findings:
- Follow-up issues:
- Verification:
- Residual risk:
```

## Final Feature Delivery Report

When the workflow stops, report:

```markdown
## Feature Delivery Status
- Design doc:
- Milestone:
- Story prefix:
- Final state: Ready | Ready with follow-ups | Not ready | Blocked

## Story Delivery Matrix
| Story | Issue | PR | Final Decision | Verification | Residual Risk |
| --- | --- | --- | --- | --- | --- |

## Final Audit
- Decision:
- Blocking findings:
- Follow-up issues:
- Verification:

## Remaining Work
- Completed:
- Deferred:
- Blocked:
- Next action:
```

If the workflow stops early, still include the matrix for completed and attempted stories, then lead with the blocker and next action. If the feature is ready, say `No blocking findings found.` and include the verification evidence from the final audit.

## Operating Rules

- Treat the design document as the source of truth for story scope and acceptance criteria until the user explicitly changes scope.
- Use GitHub Issues as the delivery ledger once issue sync succeeds.
- Deliver one story at a time. Do not batch multiple implementation stories into one worker unless the user explicitly overrides the workflow.
- Keep implementation and review independent by relying on `user-story-delivery` rather than calling implementer and reviewer directly from this skill.
- Do not interrupt or replace an active story-delivery subagent until 20 minutes have elapsed with no PR or branch movement. Ask that subagent for status before spawning any recovery worker.
- Do not continue past a blocked story when later stories depend on it.
- Do not run the final audit until all in-scope stories have a final delivery handoff.
- Do not silently skip issue sync. If the user wants local-only delivery, state that this skill is optimized for GitHub-tracked delivery and ask for explicit confirmation.
- Keep the user informed when the workflow changes state: scope resolved, issues synced, queue built, each story started, each story completed, final audit started, and final status.
- If any specialist handoff is missing required fields, ask the same specialist for the missing fields before moving forward.
