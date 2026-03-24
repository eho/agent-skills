---
name: design-doc
description: "Synthesize design discussions into a complete, structured design document. Use when asked to write a design doc, produce a design document, or turn a discussion into a spec."
triggers:
  - write a design doc
  - produce a design doc
  - create a design document
  - turn this into a design doc
  - write up the design
  - produce the spec
metadata:
  author: eho
  version: '1.1.0'
---

# Design Doc Writer

Synthesize a design discussion into a complete, structured design document. The goal is to capture the full intent of the design — including decisions made, rationale behind them, and outstanding questions — in a format that is ready for review and implementation by both humans and downstream AI agents.

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

## Implementation Plan

[A breakdown of the work into discrete, atomic tasks. Each task must be small enough for an AI agent to execute and validate independently. Specify exact file paths.]

**Phase 1: [Phase Name]**
- [ ] **Task 1: [Action]**
  - **Files:** `path/to/file.ts`
  - **Details:** [What specifically needs to be done, e.g., add `functionName` that implements X]
  - **Validation:** [How to verify this specific change, e.g., run `bun test path/to/file.test.ts`]
- [ ] **Task 2: [Action]**
  - ...

**Phase 2 (if applicable):**
- [ ] ...

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

## Writing Principles

- **Synthesize, don't transcribe.** The doc should read as a coherent design artifact, not a transcript of a conversation.
- **Concrete over abstract.** Use real names, precise file paths, strict data contracts, and code snippets from the discussion/codebase wherever possible.
- **Surface decisions.** Every significant choice should include a brief rationale. "We chose X because Y" is a design doc. "We chose X" is a changelog.
- **Respect what was deferred.** If the user explicitly said something is out of scope, put it in Non-Goals or Future Extensions — don't silently drop it or re-raise it.
- **Own the gaps.** If a required section has nothing from the conversation and couldn't be found in the codebase, write a placeholder that names what's needed. Don't fabricate details.
- **Align with the vision.** If `docs/vision/vision.md` exists, read it first and ensure the design fits the stated product direction. Note any tension in the Open Questions section.
