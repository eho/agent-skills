---
name: design-doc
description: "Synthesize design discussions into a complete design document with agent-ready user stories. Use when asked to write a design doc, produce a design document, create a PRD, plan a feature, or turn a discussion into a spec."
triggers:
  - write a design doc
  - produce a design doc
  - create a design document
  - turn this into a design doc
  - write up the design
  - produce the spec
  - create a prd
  - write prd for
  - plan this feature
  - requirements for
  - spec out
metadata:
  author: eho
  version: '2.0.0'
---

# Design Doc Writer

Synthesize a design discussion into a complete, structured design document with agent-ready user stories. The design sections capture the technical context — architecture, data contracts, integration points. The user stories are the primary deliverable: each one is grounded in the design work and precise enough for an AI agent to implement without asking follow-up questions.

---

## The Job

1. Review the conversation history for all design discussion
2. Actively search the codebase (using glob/grep) to find relevant existing files, architectural patterns, and verify integration points. Do not guess file paths.
3. Identify gaps — things not yet discussed that a complete design doc needs
4. Ask targeted clarifying questions for only the genuinely unresolved gaps
5. Write the design doc following the structure below
6. Save it and tell the user

---

## Step 1: Extract & Explore

Before asking anything, mine the conversation for:

- The problem being solved and why it matters
- Goals that were stated or implied
- Constraints and non-goals that came up
- Alternatives that were discussed and reasons they were rejected
- Key decisions and their rationale
- Any open questions or unresolved tradeoffs the user explicitly flagged

**Crucially, explore the codebase:**
- Read `docs/vision/vision.md` (or equivalent) if it exists — this is the lens through which all design choices should be evaluated. If the design conflicts with the vision, surface it in Open Questions.
- Locate the exact file paths where changes will be made.
- Identify existing data models, API conventions, and utility functions that should be reused.
- Verify that the proposed integration points actually exist and note their current signatures.

If the conversation and your codebase exploration cover most elements, proceed to writing. Only ask about genuinely unresolved gaps.

---

## Step 2: Clarifying Questions (only if needed)

Ask only what is truly missing and necessary to write a complete doc. Batch questions into a single message. Don't ask about things that can be reasonably inferred from the conversation or discovered via codebase search.

Good candidates for questions:
- Success metrics (if none were mentioned)
- Concrete example of expected output or behavior
- Deployment or configuration details not discussed
- Whether there's a vision doc or related prior art to align with

Bad candidates (skip these — infer from context):
- Restating what was already discussed
- Generic questions that apply to any design
- Asking the user to repeat themselves
- Details that can be found by reading the codebase

If you have 3 or fewer questions, ask them directly. If more, prioritize the most blocking ones.

### Format Questions Like This:

Provide lettered options so the user can respond quickly (e.g., "1A, 2C, 3B"):

```
1. What is the primary goal?
   A. Improve user onboarding experience
   B. Increase user retention
   C. Reduce support burden
   D. Other: [please specify]

2. What is the scope?
   A. Minimal viable version
   B. Full-featured implementation
   C. Just the backend/API
   D. Just the UI
```

---

## Step 3: Write the Design Doc

Use the structure below. Every section is required. If a section genuinely doesn't apply, include it with a one-line explanation of why it was omitted rather than silently skipping it.

Write concretely — use real names, exact file paths, strict data structures, and examples from the discussion and codebase. Avoid abstract prose when specifics are available. This document must be highly actionable for an AI agent to implement.

---

### Design Doc Structure

```markdown
# [Feature / System Name]

**Author:** [from context or leave blank]
**Date:** [today's date]
**Status:** Draft

---

## Problem Statement

[What's broken, missing, or painful today? Concrete — not "we want to add X." Answer: what happens without this?]

---

## Goals

1. [Specific, measurable goal]
2. ...

---

## Non-Goals

- [Explicit out-of-scope items and why]

---

## Success Metrics

[How will we know this succeeded? Quantifiable where possible: latency targets, error rate reduction, adoption numbers.]

---

## Design Principles

[Named principles that guided decisions and can serve as tie-breakers for future ambiguity. e.g., "Fail fast over silent degradation."]

---

## Vision Alignment

[If a vision doc exists: 2–4 sentences explaining how this design advances the product vision. Name the specific vision goals or principles it supports. If any aspect of the design is in tension with the vision, state it explicitly and explain why the tradeoff is justified. If no vision doc exists, omit this section.]

---

## Alternatives Considered

### [Option A]
[Description] — **Rejected because:** [reason]

### [Option B]
[Description] — **Rejected because:** [reason]

---

## Architecture Overview

[Component diagram (ASCII) or component list. Reader should understand the system model without reading all prose.]

---

## API & Data Contracts

[Exact TypeScript interfaces, Pydantic models, GraphQL schemas, or REST JSON payloads. Downstream agents need strict contracts, not just descriptions. What gets stored, where, in what format?]

---

## Integration Points

[Which existing files, APIs, events, or hooks are modified. Be extremely specific — provide exact file paths and function signatures.]

---

## Sequence / Flow Walkthrough

[Step-by-step for the critical path. ASCII or numbered sequence for async flows.]

---

## Example Output

[What does the user actually see? JSON response, CLI output, UI state, or file content. Use a real example.]

---

## Configuration

[Env vars, feature flags, or tunables — with defaults, types, and descriptions.]

---

## Testing Strategy

[Not just "we'll write unit tests." Name specific test cases, edge cases, and integration scenarios, including which test files to create or modify.]

---

## Edge Cases & Failures

[For each failure mode: how is it detected, and what's the mitigation?]

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| ...     | ...       | ...        |

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ...  | ...        | ...    | ...        |

---

## Open Questions

[Unresolved decisions or unknowns. Their presence signals intellectual honesty.]

1. [Question + context on what's blocking resolution]

---

## Context Required for Implementation

[A bulleted list of exact file paths that an implementing agent must read to understand the existing system and constraints before making changes.]
- `src/example/file.ts`
- ...

---

## User Stories

[PREFIX] is a short 3-10 letter abbreviation derived from the feature name.

Minimize the number of user stories while ensuring each story is small enough for an AI agent to complete in one focused session. Avoid over-fragmenting into tiny stories, but do not combine unrelated complex tasks.

Each story must be grounded in the design sections above — reference exact file paths, data contracts, and integration points. An implementing agent should be able to complete the story without reading the rest of this document.

**Important — Documentation Requirements:**
- For structural/architectural changes: require updating design docs to reflect added, updated, or deleted features.
- For CLI tools: require documenting CLI usage (flags, commands, help text).
- For user-facing features: require updating README or usage guides.
- For API changes: require updating API docs or type documentation.

### [PREFIX]-001: [Title]
**Description:** As a [user], I want [feature] so that [benefit].

**Context:**
- Files to read: `path/to/relevant/file.ts`
- Relevant data contracts: [reference the specific interface/schema from API & Data Contracts section]

**Acceptance Criteria:**
- [ ] [Specific, verifiable criterion referencing exact file paths and function names]
- [ ] [Another criterion]
- [ ] Typecheck/lint passes
- [ ] **[Logic/Backend]** Write unit tests covering [specific scenarios]
- [ ] **[UI stories only]** Verify in browser using dev-browser skill
- [ ] **[Documentation]** Update [specific doc — name the file] if applicable

### [PREFIX]-002: [Title]
...

---

## Future Extensions

[Ideas deferred from this design, with rationale for deferral. Shows this is part of a roadmap.]
```

---

## Step 4: Save and Report

Save the design doc as `docs/design/[slug].md` where the slug is a short kebab-case name for the feature (e.g., `docs/design/auth-token-refresh.md`). If `docs/design/` doesn't exist, create it.

After saving, tell the user:
- The file path
- A 2–3 sentence summary of what was captured
- Any open questions remaining that they should resolve before the doc is ready for review

---

## Revision Workflow

If a review file exists (e.g., `docs/design/review-[slug].md` produced by the design-doc-reviewer skill), use it to revise the design doc:

1. Read the review file in full.
2. Address every **Critical Gap** — these are blockers. For each one, update the relevant section of the design doc with the suggested fix or a substantive alternative.
3. Address **Minor Issues** where the fix is clear. If a minor issue requires a judgment call, add it to Open Questions instead of guessing.
4. Do NOT remove or weaken sections the review marked as **Strengths**.
5. After revisions, update the doc's **Status** from `Draft` to `Revised` and add a one-line changelog entry at the top (e.g., `**Revised [date]:** Addressed review feedback — added edge case table, clarified auth flow.`).
6. Tell the user what was changed and what was deferred to Open Questions.

---

## Writing Principles

- **Synthesize, don't transcribe.** The doc should read as a coherent design artifact, not a transcript of a conversation.
- **Concrete over abstract.** Use real names, precise file paths, strict data contracts, and code snippets from the discussion/codebase wherever possible.
- **Surface decisions.** Every significant choice should include a brief rationale. "We chose X because Y" is a design doc. "We chose X" is a changelog.
- **Respect what was deferred.** If the user explicitly said something is out of scope, put it in Non-Goals or Future Extensions — don't silently drop it or re-raise it.
- **Own the gaps.** If a required section has nothing from the conversation and couldn't be found in the codebase, write a placeholder that names what's needed. Don't fabricate details.
- **Align with the vision.** If `docs/vision/vision.md` exists, read it first and ensure the design fits the stated product direction. Note any tension in the Open Questions section.
- **User stories are the deliverable.** The design sections are context. The user stories are what gets sent to GitHub issues for agents to implement. Every story must be self-contained: an agent reading only that story should know exactly what to do, which files to touch, and how to verify it's done.
- **Acceptance criteria must be binary.** "Works correctly" is not a criterion. "Returns 404 when user ID doesn't exist" is. Each criterion should be verifiable by running a test or checking a specific behavior.
- **Every story needs testing.** Backend/logic changes require unit tests. UI changes require browser verification. No exceptions.
- **Every story needs documentation.** If a story adds user-facing functionality, a CLI flag, an API endpoint, or changes architecture, its acceptance criteria must require updating the relevant docs. Name the specific file to update — don't say "update docs if applicable."
