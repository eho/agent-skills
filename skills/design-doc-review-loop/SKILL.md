---
name: design-doc-review-loop
description: 'Run the review-revision loop for an existing design doc: call design-doc-reviewer, address Critical Gaps and Minor Issues, repeat until clean, then mark the doc Revised for feature-delivery. Use when asked to review and revise, repeat until no gaps remain, prepare a design doc for feature delivery, or start a reviewer subagent and address feedback. Use design-doc-reviewer for one-time read-only critique.'
triggers:
  - review and revise this design doc
  - repeat design doc review until clean
  - get this design doc ready for feature delivery
  - address design doc reviewer feedback
  - no major or minor design doc gaps
  - mark the design doc revised after review
  - start a subagent to review the design doc and address feedback
metadata:
  author: eho
  version: '1.0.0'
---

# Design Doc Review Loop

You are acting as the coordinator for a complete design document review and revision cycle. Your job is to compose two specialist workflows:

- `design-doc-reviewer`: independently critiques the design doc and saves a review artifact. It does not edit the design doc.
- `design-doc`: revises the design doc by triaging review feedback, updating the design, adding `## Revision Notes`, and updating status when appropriate.

Keep review and revision responsibilities separate. The value of this skill is orchestration: independent review, disciplined feedback triage, repeated clean-up passes, and a final design status that `feature-delivery` can trust.

## Delegation Requirement

This workflow is designed to use subagents so the reviewer has a fresh, independent context. If the current runtime requires explicit user permission before starting subagents, and the user's request did not clearly ask for subagents, delegation, or a full review-revision loop, ask for confirmation before starting.

A request such as "use the design-doc-review-loop skill", "repeat review until no gaps remain", "get this design doc ready for feature delivery", or "start a subagent to review the design doc, address feedback, and repeat" is enough to proceed because this skill's purpose is delegation.

## Workflow

1. **Identify the Target Design Doc**
   - Prefer the exact path supplied by the user.
   - If no path is supplied, inspect `docs/design/` for recent design docs.
   - Exclude files named `review-*.md` when selecting the target design doc.
   - If multiple plausible design docs exist and the user did not provide a clear selection rule, ask which one to revise before starting.

2. **Check Prerequisites**
   - Confirm the `design-doc-reviewer` and `design-doc` skills are available in the current environment.
   - Read the target design doc status if present. Continue if the status is `Draft`, missing, or already `Revised`; an already revised doc can still be re-reviewed.
   - Do not start `feature-delivery` from this skill.

3. **Start Independent Review**
   - Start a reviewer subagent using the `design-doc-reviewer` skill.
   - Give it the target design doc path.
   - Tell it to save the normal review artifact as `docs/design/review-[original-filename].md`.
   - Require this final handoff format:
     ```markdown
     ## Design Review Handoff
     - Design doc:
     - Review file:
     - Score:
     - Critical gaps count:
     - Minor issues count:
     - Additional open questions count:
     - Ready for implementation: yes/no
     - Top findings:
     ```

4. **Decide Whether Revision Is Needed**
   - If `Critical gaps count` is `0` and `Minor issues count` is `0`, skip to final status preparation.
   - If there are Additional Open Questions that require product or architectural decisions the agent cannot infer safely, stop and ask the user for the missing decision.
   - Otherwise, revise the design doc using the review artifact.

5. **Revise the Design Doc**
   - Prefer applying the revision directly in the current agent context when the needed edits are clear.
   - Follow the `design-doc` skill's Revision Workflow:
     - triage every review item as `Accept`, `Accept (Alt)`, `Reject`, or `Defer`
     - update the relevant sections for accepted feedback
     - preserve strengths called out by the review
     - add or update `## Revision Notes`
     - move unresolved decision points to Open Questions
   - Do not set `Status: Revised` yet if a follow-up review is still required.
   - If the revision is large enough that a separate writer context would be safer, start a worker subagent using the `design-doc` skill and require this final handoff:
     ```markdown
     ## Design Revision Handoff
     - Design doc:
     - Review file addressed:
     - Accepted:
     - Accepted with alternative:
     - Rejected:
     - Deferred:
     - Verification:
     - Blocked: yes/no
     ```

6. **Repeat Review**
   - Re-run the reviewer on the revised design doc.
   - Repeat the review-revision cycle until the reviewer reports:
     - `Critical gaps count: 0`
     - `Minor issues count: 0`
   - Use a default maximum of 5 review passes. If major or minor gaps remain after 5 passes, stop and report the remaining findings rather than looping indefinitely.

7. **Prepare for Feature Delivery**
   - Once the latest review reports no Critical Gaps and no Minor Issues, update the design doc status to `Revised`.
   - Prefer an explicit status field such as `**Status:** Revised`, `Status: Revised`, or frontmatter equivalent, matching the file's existing convention.
   - Add or update a top-level changelog line using the current date, for example:
     ```markdown
     **Revised 2026-05-21:** Addressed review feedback and passed follow-up design review with no critical gaps or minor issues.
     ```
   - Ensure `## Revision Notes` exists and references the latest review artifact.
   - Do not create GitHub Issues and do not start implementation. Hand off to `feature-delivery` only by reporting that the design doc is ready.

## Subagent Prompts

Use concise prompts that include the handoff requirements. Adapt the target design doc path as needed.

### Review Prompt

```text
Use the design-doc-reviewer skill to review this design document:

Design doc: <design-doc-path>

Save the normal review artifact as docs/design/review-[original-filename].md. Complete the reviewer workflow as a read-only critique; do not edit the design document.

Return this final handoff:
## Design Review Handoff
- Design doc:
- Review file:
- Score:
- Critical gaps count:
- Minor issues count:
- Additional open questions count:
- Ready for implementation: yes/no
- Top findings:
```

### Revision Prompt

```text
Use the design-doc skill's Revision Workflow to revise this design document using the review artifact.

Design doc: <design-doc-path>
Review file: <review-file-path>

Triage every review item as Accept, Accept (Alt), Reject, or Defer. Update the design doc for accepted feedback, preserve review strengths, add or update ## Revision Notes, and keep unresolved decisions in Open Questions. Do not mark the design doc Revised unless this revision is being performed after a clean follow-up review with no Critical Gaps or Minor Issues.

Return this final handoff:
## Design Revision Handoff
- Design doc:
- Review file addressed:
- Accepted:
- Accepted with alternative:
- Rejected:
- Deferred:
- Verification:
- Blocked: yes/no
```

## Final Report

When the loop completes, report:

- Design doc path
- Latest review artifact path
- Number of review passes
- Final score
- Confirmation that `Status` is `Revised`
- Any deferred Open Questions or residual risks

If the loop stops because it is blocked or reached the pass limit, do not mark the design doc `Revised`. Report the remaining Critical Gaps, Minor Issues, or decisions needed from the user.

## Operating Principles

- **A clean review gates the status.** Only mark `Revised` after the latest review reports no Critical Gaps and no Minor Issues.
- **Reviewer independence matters.** Use a separate reviewer subagent for review passes so the critique is not biased by the revision work.
- **Do not rubber-stamp feedback.** Revision should triage reviewer findings against product intent, constraints, and the design-doc contract.
- **Bound the loop.** Aim for convergence, but stop after 5 review passes by default and surface remaining issues clearly.
- **Keep delivery separate.** This skill prepares a design doc for `feature-delivery`; it does not publish issues, implement stories, or review PRs.
