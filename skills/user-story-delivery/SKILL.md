---
name: user-story-delivery
description: 'Orchestrate the complete delivery workflow for one GitHub user story: implement it with the user-story-implementer skill, review the resulting PR with the user-story-reviewer skill, address reviewer feedback, and repeat until the PR is approved, merged, or blocked. You MUST use this skill when asked to "implement and review a user story", "run the full user story workflow", "deliver USERST-001", "complete USERST-001 end to end", or "run implementation and review together".'
metadata:
  author: eho
  version: '1.0.0'
---

# User Story Delivery

You are acting as the coordinator for one complete user story delivery cycle. Your job is to compose two specialist workflows:

- `user-story-implementer`: implements exactly one story, verifies it, commits, pushes, and creates or updates a PR.
- `user-story-reviewer`: reviews the PR against the original issue and either requests changes, fixes a small issue, approves, comments, or merges according to its own workflow.

Keep implementation and review responsibilities separate. Do not duplicate either specialist skill's detailed workflow here. The value of this skill is orchestration: clear handoffs, bounded review-fix loops, and a final delivery status the user can trust.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) because the specialist skills rely on it.

## Delegation Requirement

This workflow is designed to use subagents so implementation and review remain independent. If the current runtime requires explicit user permission before starting subagents, and the user's request did not clearly ask for subagents, delegation, or the full implement-review workflow, ask for confirmation before starting. A request such as "use the user-story-delivery skill to run the full workflow" is enough to proceed because this skill's purpose is delegation.

## Workflow

1. **Identify the Target Story**
   - Prefer the specific story ID or issue number supplied by the user.
   - If the user asks for the next story in a prefix, label, milestone, or backlog slice, pass that exact selection rule to the implementer.
   - If the user provides no story ID, issue number, prefix, label, milestone, or unambiguous selection rule, ask for the target before starting.

2. **Start Implementation**
   - Start a worker subagent using the `user-story-implementer` skill.
   - Tell the worker it owns the implementation workflow for exactly one story.
   - Tell the worker it is not alone in the codebase and must not revert unrelated changes.
   - Require this final handoff format:
     ```markdown
     ## Implementation Handoff
     - Story ID:
     - Issue:
     - Branch:
     - PR:
     - Verification:
     - Known residual risk:
     - Blocked: yes/no
     ```
   - If the implementation worker reports `Blocked: yes`, stop and relay the blocker. Do not start review.
   - If the worker does not provide a PR number or URL, ask it for the missing handoff before starting review.

3. **Start Review**
   - Start a separate reviewer subagent using the `user-story-reviewer` skill.
   - Give it the story ID and PR number or URL from the implementation handoff.
   - Tell the reviewer to complete its own workflow. If there are no blocking findings, it should approve, comment, or merge according to the reviewer skill's rules.
   - Require this final handoff format:
     ```markdown
     ## Review Handoff
     - Story ID:
     - PR:
     - Decision: Request changes | Fix small issue | Approve | Comment only | Merge
     - Blocking findings:
     - Reviewer-fixed commits:
     - Required follow-up:
     - Verification:
     ```

4. **Handle Review Decision**
   - If `Decision` is `Approve`, `Comment only`, or `Merge`, stop the loop and provide the final delivery report.
   - If `Decision` is `Fix small issue`, check that the reviewer pushed the fix and then continue to a follow-up review.
   - If `Decision` is `Request changes`, address the feedback on the existing PR branch.
   - If the requested changes alter product scope, contradict the issue, require missing credentials, or require a decision the agent cannot safely make, stop and ask the user.

5. **Address Requested Changes**
   - Prefer starting a worker subagent using the `user-story-implementer` skill to revise the existing PR branch.
   - Give the worker the story ID, PR number, review findings, and a clear instruction to update the existing PR rather than creating a new one.
   - Require the same `Implementation Handoff` format, plus a short list of review findings addressed.
   - The worker must commit and push fixes to the same PR branch.

6. **Repeat Review**
   - Re-run the reviewer on the same story and PR after fixes are pushed.
   - Repeat the review-fix cycle at most 2 times by default.
   - If blocking findings remain after 2 cycles, stop and report the remaining issues instead of looping indefinitely.

## Subagent Prompts

Use concise prompts that include the handoff requirements. Adapt the target story details as needed.

### Initial implementation prompt

```text
Use the user-story-implementer skill to implement exactly one user story: <story-id-or-selection-rule>.

You are not alone in the codebase. Do not revert unrelated changes. Follow the implementer workflow, verify the acceptance criteria, commit, push, and create or update the PR.

Return this final handoff:
## Implementation Handoff
- Story ID:
- Issue:
- Branch:
- PR:
- Verification:
- Known residual risk:
- Blocked: yes/no
```

### Review prompt

```text
Use the user-story-reviewer skill to review this implemented story.

Story: <story-id>
PR: <pr-number-or-url>

Complete the reviewer workflow. If there are no blocking findings, approve, comment, or merge according to the reviewer skill's rules. If there are findings, request changes unless the reviewer skill permits fixing a small issue directly.

Return this final handoff:
## Review Handoff
- Story ID:
- PR:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Required follow-up:
- Verification:
```

### Revision prompt

```text
Use the user-story-implementer skill to revise the existing PR for this story.

Story: <story-id>
PR: <pr-number-or-url>
Reviewer feedback to address:
<findings>

You are not alone in the codebase. Do not revert unrelated changes. Check out and update the existing PR branch, address the review findings, verify the affected behavior, commit, and push to the same PR.

Return this final handoff:
## Implementation Handoff
- Story ID:
- Issue:
- Branch:
- PR:
- Review findings addressed:
- Verification:
- Known residual risk:
- Blocked: yes/no
```

## Final Delivery Report

When the workflow stops, report:

```markdown
## Delivery Status
- Story:
- Issue:
- PR:
- Final decision:
- Review cycles:
- Implementation summary:
- Verification:
- Remaining blockers or residual risk:
```

If the story was merged, say so explicitly. If it was approved but not merged, explain why. If it stopped because of blockers or remaining findings, lead with the unresolved items and include the exact next action needed.

## Operating Rules

- Coordinate the workflow, but let each specialist skill own its domain.
- Keep review independent by using a separate reviewer subagent from the implementer.
- Do not start a review without a concrete PR number or URL.
- Do not create a second PR for revision work unless the user explicitly asks for that.
- Do not loop forever. Two review-fix cycles are the default cap.
- Keep the user informed when the workflow changes state: implementation started, PR ready, review started, fixes started, review repeated, and final status.
- If subagent final output is missing required handoff fields, request the missing fields from that same subagent before moving to the next phase.
