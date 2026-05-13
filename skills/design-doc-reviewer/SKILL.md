---
name: design-doc-reviewer
description: "Review a design document for completeness, clarity, and quality — including user story readiness for agent implementation. Produces structured feedback with specific gaps, strengths, and a prioritized improvement checklist. Use when asked to review a design doc, critique a design, check a spec, review the PRD, or audit the requirements."
triggers:
  - review this design doc
  - review the design
  - critique this design
  - check this spec
  - review this spec
  - give feedback on this design
  - review the prd
  - audit the requirements
  - review the requirements
metadata:
  author: eho
  version: '2.0.0'
---

# Design Doc Reviewer

Produce structured, actionable review feedback on a design document. Reviews should be specific — not generic praise or criticism — and directly tied to content in the doc.

This is intentionally separate from the design-doc writer skill. Use this skill for independent critique and readiness assessment. Do not rewrite the design doc during review; produce a review artifact that the design-doc writer can later triage and apply.

---

## The Job

1. Identify which document to review (from the user's message, or ask)
2. Read the design doc in full
3. Read the design-doc skill/template if available so the review is aligned with the current design-doc contract
4. Read the vision doc (`docs/vision/vision.md`) for product alignment context if available
5. Evaluate the doc against the quality rubric below
6. Output the review in the structured format below

---

## Step 1: Locate the Document

If the user didn't specify a path, check `docs/design/` for recent files. Ask if ambiguous. Read the doc fully before evaluating.

Also read (if they exist):
- `skills/design-doc/SKILL.md` or equivalent design-doc writer instructions — to align the review rubric with the current expected document structure
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
| 14 | **Security, Privacy & Permissions** | Authentication, authorization, secrets, PII, data retention, auditability, and permission boundaries. If none apply, the doc should say why. |
| 15 | **Performance & Scalability** | Expected load, latency targets, data volume assumptions, caching/batching strategy, and known bottlenecks. |
| 16 | **Migration, Rollout & Rollback** | Schema migrations, backfills, feature flags, backward compatibility, rollout sequence, and rollback plan. |
| 17 | **Testing Strategy** | Not just "we'll write unit tests." Names specific test cases, edge cases, integration scenarios, and test files. |
| 18 | **Observability & Logging** | Specific operations, error paths, log levels, formats, and required context fields. |
| 19 | **Edge Cases & Failures** | What can go wrong? For each failure mode: how is it detected, and what's the mitigation? |
| 20 | **Risks** | Known technical or product risks, with likelihood, impact, and mitigation plan for each. |
| 21 | **Open Questions** | Does the doc itself include an explicit list of unresolved decisions or unknowns? Their presence signals intellectual honesty; their absence may mean the author hasn't surfaced real uncertainty. |
| 22 | **Context Required for Implementation** | Does the doc list exact file paths an implementer must read before starting? Missing = the implementer has to rediscover context. |
| 23 | **Implementation Plan** | Ordered implementation slices with story IDs, dependencies, purpose, and primary files. |
| 24 | **User Stories** | Are there well-formed user stories with acceptance criteria? See User Story Quality below. |
| 25 | **Future Extensions** | Ideas deferred with rationale. Shows the design is part of a roadmap, not a closed system. |

### Quality Signals (score holistically)

- **Principle-driven consistency**: Do implementation choices trace back to stated principles? Or do choices feel arbitrary?
- **State ownership clarity**: For every piece of mutable state, is it clear who creates/reads/modifies it?
- **Decision rationale**: For significant architectural choices, does the doc answer "why not the alternative"?
- **Concrete over abstract**: Does the doc use real examples (JSON, file paths, code, CLI output) or only prose?
- **Failure path coverage**: Does the doc only describe the happy path, or does it address what happens when things go wrong?
- **Security and data discipline**: Does the design explicitly handle authorization, sensitive data, retention, and permission boundaries where relevant?
- **Operational readiness**: Can the team roll the feature out, observe it, and roll it back without relying on unstated assumptions?
- **Product alignment**: Does the Vision Alignment section make a substantive argument, or is it hand-waving? Does it name specific vision goals?
- **Scope discipline**: Is the design appropriately scoped, or is it trying to solve everything at once?

### User Story Quality (evaluate each story)

Apply the **Agent-Ready Test** to every user story: could an AI agent implement this story without asking for more information? If "No" or "Maybe," the story needs more detail.

- **Self-contained**: Does each story include enough context (file paths, data contracts, relevant interfaces) that an agent doesn't need to read the full design doc?
- **Outcome-focused**: Does each story deliver one primary behavioral outcome rather than a loose bundle of tasks?
- **Design-traceable**: Does each story reference the relevant architecture, data contract, and integration point from the design sections?
- **Dependency-aware**: Does each story name prerequisite story IDs or explicitly state `None`?
- **Scoped**: Does each story include out-of-scope boundaries so the implementer knows what not to change?
- **Acceptance criteria are binary**: Every criterion must be verifiable — "works correctly" fails, "returns 404 when user ID doesn't exist" passes.
- **Verification is explicit**: Every story must include the exact typecheck, lint, test, or browser verification command/check needed to prove completion.
- **Testing requirements present**: Backend/logic stories must name test files and scenarios. UI stories must require browser verification for specific interactions or states.
- **Documentation decision present**: Stories that add user-facing functionality, CLI flags, API endpoints, or architectural changes must include AC to update the specific doc file. If no docs change is needed, the story must say `Documentation impact: None` and explain why.
- **Granularity**: Stories should be minimized in count but each small enough for an agent to complete in one focused session. Not over-fragmented, not combining unrelated tasks.
- **Likely files are named**: Does the story name files to read and files likely to change, using exact paths rather than guessed or vague locations?

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
| Security, Privacy & Permissions | ✅/⚠️/❌ | [specific observation] |
| Performance & Scalability | ✅/⚠️/❌ | [specific observation] |
| Migration, Rollout & Rollback | ✅/⚠️/❌ | [specific observation] |
| Testing Strategy | ✅/⚠️/❌ | [specific observation] |
| Observability & Logging | ✅/⚠️/❌ | [specific observation] |
| Edge Cases & Failures | ✅/⚠️/❌ | [specific observation] |
| Risks | ✅/⚠️/❌ | [specific observation] |
| Open Questions | ✅/⚠️/❌ | [specific observation] |
| Context Required for Implementation | ✅/⚠️/❌ | [specific observation] |
| Implementation Plan | ✅/⚠️/❌ | [specific observation] |
| User Stories | ✅/⚠️/❌ | [specific observation] |
| Future Extensions | ✅/⚠️/❌ | [specific observation] |

**Score:** X/25 elements present and strong

---

#### Strengths

List 2–4 specific strengths. Reference actual content from the doc (quote sections, describe specific design decisions). Don't be generic.

- **[Strength title]**: [specific observation with reference to doc content]

---

#### Critical Gaps (must fix before implementation)

Issues that could cause implementation problems, ambiguity, or rework. Be specific about what's missing and what the impact is.

- **[Gap title]**: [what's missing, why it matters, and a concrete suggestion for how to address it]

For user-story gaps, name the affected story IDs and explain whether the problem is missing context, unclear dependencies, oversized scope, weak acceptance criteria, missing verification, or missing documentation decision.

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
- **Review against the current design-doc contract.** If the design-doc writer skill/template is available, use it as the source of truth for expected sections and story shape. Do not penalize a doc for omitting Vision Alignment when no vision source exists.
- **Be skeptical about implementation readiness.** A design can read well and still be unready if stories lack dependencies, files, data contracts, verification commands, or out-of-scope boundaries.
- **Acknowledge what's strong.** A good review isn't only criticism. Noting what works well is as important as noting what doesn't — it tells the author what not to change.
- **Propose, don't just critique.** For every gap, suggest what's needed. "Add an edge cases table covering: DB lock failure, OS permission denial, and partial write crash" is more useful than "edge cases are missing."
- **Respect scope.** Don't ask the doc to solve everything. If something is intentionally deferred, acknowledge it — don't flag it as a gap.
