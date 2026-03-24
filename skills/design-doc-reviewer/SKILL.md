---
name: design-doc-reviewer
description: "Review a design document for completeness, clarity, and quality. Produces structured feedback with specific gaps, strengths, and a prioritized improvement checklist. Use when asked to review a design doc, critique a design, or check a spec."
triggers:
  - review this design doc
  - review the design
  - critique this design
  - check this spec
  - review this spec
  - give feedback on this design
metadata:
  author: eho
  version: '1.0.0'
---

# Design Doc Reviewer

Produce structured, actionable review feedback on a design document. Reviews should be specific — not generic praise or criticism — and directly tied to content in the doc.

---

## The Job

1. Identify which document to review (from the user's message, or ask)
2. Read the design doc in full
3. Read the vision doc (`docs/vision/vision.md`) for product alignment context
4. Evaluate the doc against the quality rubric below
5. Output the review in the structured format below

---

## Step 1: Locate the Document

If the user didn't specify a path, check `docs/design/` for recent files. Ask if ambiguous. Read the doc fully before evaluating.

Also read (if they exist):
- `docs/vision/vision.md` or equivalent product vision doc — to check product alignment
- Any directly related existing designs or architecture docs if referenced

---

## Step 2: Evaluate Against the Rubric

Score each element as: ✅ Present & Strong / ⚠️ Partial or Unclear / ❌ Missing

### Required Elements

| # | Element | What to look for |
|---|---------|-----------------|
| 1 | **Problem Statement** | Concrete pain or gap — not "we want to add X." Should answer: what breaks today without this? |
| 2 | **Goals** | Numbered, specific, and measurable. Can you tell when a goal is met? |
| 3 | **Success Metrics** | How will success be measured post-implementation? Quantifiable where possible (latency, error rate, adoption). |
| 4 | **Non-Goals** | Explicit list of what's out of scope and why. Missing = the doc hasn't thought about scope. |
| 5 | **Alternatives Considered** | At least 2 alternative approaches with rationale for rejection. Missing = the chosen approach feels arbitrary. |
| 6 | **Design Principles** | Named principles (not just description of approach). Serve as tie-breakers for ambiguous choices. |
| 7 | **Vision Alignment** | If a vision doc exists: does the design explicitly connect its choices to the product vision? Does it justify any tension? Not just "this aligns" — it should name specific vision goals it advances. Omitted is fine only if no vision doc exists. |
| 8 | **Architecture Overview** | Diagram or component list. Reader should understand the system model without reading all prose. |
| 9 | **API & Data Contracts** | Exact interfaces, schemas, or payloads — not just descriptions. What gets stored, where, in what format. Strict enough for an implementer to code against. |
| 10 | **Integration Points** | Which existing files, APIs, events, or hooks are modified. Specific — file names and function names. |
| 11 | **Sequence / Flow Walkthrough** | Step-by-step for the critical path. ASCII diagram or numbered sequence for complex async flows. |
| 12 | **Example Output** | What does the user actually see? JSON response, CLI output, UI state, or file content example. |
| 13 | **Configuration** | Env vars, feature flags, or tunables — with defaults, types, and descriptions. |
| 14 | **Testing Strategy** | Not just "we'll write unit tests." Names specific test cases, edge cases, and integration scenarios. |
| 15 | **Edge Cases & Failures** | What can go wrong? For each failure mode: how is it detected, and what's the mitigation? |
| 16 | **Risks** | Known technical or product risks, with likelihood, impact, and mitigation plan for each. |
| 17 | **Open Questions** | Does the doc itself include an explicit list of unresolved decisions or unknowns? Their presence signals intellectual honesty; their absence may mean the author hasn't surfaced real uncertainty. |
| 18 | **Context Required for Implementation** | Does the doc list exact file paths an implementer must read before starting? Missing = the implementer has to rediscover context. |
| 19 | **Implementation Plan** | Concrete list of files to change, functions to add, and phases if multi-step. Tasks should be atomic with per-task validation. |
| 20 | **Future Extensions** | Ideas deferred with rationale. Shows the design is part of a roadmap, not a closed system. |

### Quality Signals (score holistically)

- **Principle-driven consistency**: Do implementation choices trace back to stated principles? Or do choices feel arbitrary?
- **State ownership clarity**: For every piece of mutable state, is it clear who creates/reads/modifies it?
- **Decision rationale**: For significant architectural choices, does the doc answer "why not the alternative"?
- **Concrete over abstract**: Does the doc use real examples (JSON, file paths, code, CLI output) or only prose?
- **Failure path coverage**: Does the doc only describe the happy path, or does it address what happens when things go wrong?
- **Product alignment**: Does the Vision Alignment section make a substantive argument, or is it hand-waving? Does it name specific vision goals?
- **Scope discipline**: Is the design appropriately scoped, or is it trying to solve everything at once?

---

## Step 3: Output the Review

Use this exact structure:

---

### Design Doc Review: [Document Title]

**File:** `docs/design/[filename].md`
**Reviewed:** [today's date]
**Overall Assessment:** [1–2 sentences. What's the doc's current state? Is it ready to implement, needs revision, or needs substantial work?]

---

#### Scorecard

| Element | Status | Notes |
|---------|--------|-------|
| Problem Statement | ✅/⚠️/❌ | [specific observation] |
| Goals | ✅/⚠️/❌ | [specific observation] |
| Success Metrics | ✅/⚠️/❌ | [specific observation] |
| Non-Goals | ✅/⚠️/❌ | [specific observation] |
| Alternatives Considered | ✅/⚠️/❌ | [specific observation] |
| Design Principles | ✅/⚠️/❌ | [specific observation] |
| Vision Alignment | ✅/⚠️/❌ | [specific observation] |
| Architecture Overview | ✅/⚠️/❌ | [specific observation] |
| API & Data Contracts | ✅/⚠️/❌ | [specific observation] |
| Integration Points | ✅/⚠️/❌ | [specific observation] |
| Sequence / Flow | ✅/⚠️/❌ | [specific observation] |
| Example Output | ✅/⚠️/❌ | [specific observation] |
| Configuration | ✅/⚠️/❌ | [specific observation] |
| Testing Strategy | ✅/⚠️/❌ | [specific observation] |
| Edge Cases & Failures | ✅/⚠️/❌ | [specific observation] |
| Risks | ✅/⚠️/❌ | [specific observation] |
| Open Questions | ✅/⚠️/❌ | [specific observation] |
| Context Required for Implementation | ✅/⚠️/❌ | [specific observation] |
| Implementation Plan | ✅/⚠️/❌ | [specific observation] |
| Future Extensions | ✅/⚠️/❌ | [specific observation] |

**Score:** X/20 elements present and strong

---

#### Strengths

List 2–4 specific strengths. Reference actual content from the doc (quote sections, describe specific design decisions). Don't be generic.

- **[Strength title]**: [specific observation with reference to doc content]

---

#### Critical Gaps (must fix before implementation)

Issues that could cause implementation problems, ambiguity, or rework. Be specific about what's missing and what the impact is.

- **[Gap title]**: [what's missing, why it matters, and a concrete suggestion for how to address it]

---

#### Minor Issues (should fix, but not blocking)

- **[Issue title]**: [what's unclear or incomplete, and how to improve it]

---

#### Additional Open Questions

Questions the doc hasn't answered that an implementer would need to resolve — beyond any already listed in the doc itself:

1. [Question]
2. [Question]

---

#### Recommended Next Steps

Prioritized list of what the author should do before this doc is ready to implement:

1. [Highest priority action]
2. [Next action]
3. ...

---

## Output

Save the review as `docs/design/review-[original-filename].md` (e.g., reviewing `docs/design/auth-redesign.md` → save to `docs/design/review-auth-redesign.md`). Then tell the user the file was saved and summarize the score and top 2–3 critical gaps in a short message.

---

## Review Principles

- **Be specific, not generic.** "The testing strategy is weak" is not useful. "The testing strategy lists unit tests but doesn't name a single test case or edge case" is useful.
- **Quote the doc.** Reference actual sections, headings, or excerpts. This proves you read it and helps the author find exactly what to fix.
- **Separate blockers from polish.** Critical gaps block implementation. Minor issues are improvements. Don't conflate them.
- **Acknowledge what's strong.** A good review isn't only criticism. Noting what works well is as important as noting what doesn't — it tells the author what not to change.
- **Propose, don't just critique.** For every gap, suggest what's needed. "Add an edge cases table covering: DB lock failure, OS permission denial, and partial write crash" is more useful than "edge cases are missing."
- **Respect scope.** Don't ask the doc to solve everything. If something is intentionally deferred, acknowledge it — don't flag it as a gap.
