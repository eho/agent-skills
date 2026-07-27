---
name: design-doc-review-loop
description: 'Coordinate independent review and focused revision of an existing design doc until mechanical validation passes and no blocking design findings remain, then exclusively promote it to Revised for feature-delivery. Use when asked to review and revise, repeat until ready, prepare a design for delivery, or start a reviewer worker and address feedback.'
triggers:
  - review and revise this design doc
  - repeat design doc review until clean
  - get this design doc ready for feature delivery
  - address design doc reviewer feedback
  - mark the design doc revised after review
  - start a subagent to review the design doc and address feedback
metadata:
  author: eho
  version: '2.0.0'
---

# Design Doc Review Loop

Coordinate independent review and revision without turning review history into
the implementation specification.

Read
[`../design-doc/references/design-contract.md`](../design-doc/references/design-contract.md),
the target design, and repository instructions. This skill owns normal
promotion to `Revised`; it does not synchronize issues or implement stories.

## Independence

Use a fresh reviewer subagent for each review pass and require it to follow
`design-doc-reviewer`. Reviewers remain read-only. The coordinator or a separate
writer applies revisions so the reviewer does not approve its own work.

If delegation requires permission, the user's request to use this loop, repeat
review, prepare for feature delivery, or start a reviewer is sufficient
authorization. Otherwise request permission before delegating.

## Workflow

1. **Select the design.** Use the supplied path. If discovery leaves multiple
   plausible non-review documents, ask the user to choose.
2. **Keep it Draft.** A document under review or revision remains `Draft`, even
   if it entered the loop as `Revised`.
3. **Run an initial review.** Ask a fresh reviewer to perform the full,
   repository-grounded review and author-mode mechanical validation. Save it to
   the next versioned review path.
4. **Handle the verdict.**
   - If validation passes and blocking findings are zero, continue to promotion.
   - If a blocker needs product authority or would expand scope, remove/defer a
     story, choose a destructive migration, or change an explicit user
     decision, pause for the user.
   - Otherwise revise against the evidence and required invariant.
5. **Revise economically.** Triage findings as accepted, addressed by a smaller
   alternative, rejected with evidence, or requiring user input. Do not blindly
   implement the reviewer's example solution. Update every affected canonical
   story when shared requirements change. Add only a one-line changelog entry
   to the design; keep detailed dispositions in the versioned review artifact
   or handoff.
6. **Run focused follow-up review.** A fresh reviewer verifies prior blockers,
   changed and affected surfaces, mechanical validation, and critical
   regressions. It widens to a full review when cross-cutting changes make that
   necessary.
7. **Converge or stop.** Repeat while progress is being made, with a default
   limit of five passes. Non-blocking suggestions may remain or be explicitly
   waived. They do not trigger another pass. At the limit, or when the same
   blocker cannot be resolved without user input, report it and leave `Draft`.
8. **Promote and prove readiness.** After the latest independent review says
   `Ready`, set the status to `Revised`, add a compact dated changelog line, and
   run:

   ```bash
   python3 <story-contract-script> <design-doc> \
     --repo-root <repository-root> --mode delivery
   ```

   If delivery-mode validation fails, restore `Draft`, fix the mechanical
   failure, and obtain another independent focused review before promotion.

An explicit user override may promote a mechanically valid document despite
semantic review findings, but state the exact risk and preserve the override in
the changelog. Mechanical failures must be fixed because downstream tooling
cannot consume them. Do not infer override authority from a normal loop request.

## Reviewer prompt

```text
Use the design-doc-reviewer skill for an independent <initial|follow-up> review.

Design: <path>
Prior review: <path or none>

Stay read-only. Save the next versioned review artifact. Run author-mode
story-contract validation. For a follow-up, verify prior blockers, changed and
affected surfaces, and critical regressions; widen only if cross-cutting changes
require it.

Return:
- Review artifact:
- Verdict: Ready | Not ready
- Mechanical validation: Pass | Fail
- Blocking findings:
- Non-blocking suggestions:
- User decisions required:
- Affected story IDs:
```

## Final report

Report the design path, latest versioned review artifact, pass count,
author-mode and delivery-mode validation results, final status, any waived
non-blocking suggestions, and remaining user decisions or risks. Do not start
`design-to-issues` or `feature-delivery`.
