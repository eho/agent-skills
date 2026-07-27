---
name: design-doc
description: "Create or update a concise, repository-grounded design document with canonical user stories ready for independent review and feature delivery. Use when asked to write a design doc, PRD, implementation plan, feature spec, requirements, or to turn a technical discussion into an implementable design."
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
  version: '3.0.0'
---

# Design Doc Writer

Turn product and technical context into the smallest design that a capable
implementation agent can execute safely.

Read [the shared design contract](references/design-contract.md) completely
before writing. It defines readiness, evidence, authority, story syntax, and
the downstream `feature-delivery` contract.

## Workflow

1. **Mine the conversation.** Extract the problem, goals, constraints,
   non-goals, decisions and rationale, rejected directions, and unresolved
   decisions. Preserve explicit user choices.
2. **Ground the design.** Read repository instructions and relevant vision,
   architecture, code, tests, schemas, and configuration. Use search before
   guessing. Verify important paths, current signatures, ownership, and
   integration points.
3. **Clarify only material gaps.** Ask a concise, batched question only when an
   answer would materially change scope, architecture, compatibility, safety,
   or story boundaries and cannot be discovered or safely inferred. Otherwise
   state the assumption.
4. **Synthesize the design.** Explain the chosen behavior and contracts, not
   the discovery transcript. Prefer an existing repository pattern unless the
   design gives a reason to depart from it.
5. **Write canonical stories.** Use stable IDs and make every story independently
   implementable from its copied issue body. Minimize story count while keeping
   each story to one coherent, dependency-ordered outcome.
6. **Validate.** Resolve `design-to-issues/scripts/story_contract.py` from the
   installed or repository skill set and run:

   ```bash
   python3 <story-contract-script> <design-doc> \
     --repo-root <repository-root> --mode author
   ```

   Fix every validation failure before reporting completion.
7. **Save as Draft.** Write `docs/design/<short-kebab-case-name>.md` unless the
   user or repository specifies another path. New and revised content remains
   `Draft`; this skill never promotes it to `Revised`.

## Adaptive document shape

Use only sections that carry useful design information. A typical document is:

```markdown
# Feature name

**Status:** Draft

## Problem and Goals
## Scope and Non-Goals
## Decisions and Rationale
## Architecture and Contracts
## Integration and Behavior
## Risks and Verification
## Open Questions
## User Stories
## Changelog
```

Adapt or combine headings to fit the feature. Include security, privacy, data
ownership, migration, compatibility, performance, observability, rollout, and
rollback where material. Include alternatives when they explain a consequential
decision. Omit irrelevant sections instead of filling them with boilerplate.

Use exact examples, data shapes, sequences, or diagrams only when they remove
implementation ambiguity. Mark proposed interfaces as proposed; do not present
them as current repository facts.

## Story guidance

Follow the exact story shape and dependency syntax in the shared contract.
Additionally:

- Put behavioral results in Acceptance Criteria and implementation guidance in
  Implementation Context.
- Make criteria binary and observable. Do not use file placement, lint success,
  or vague statements such as “works correctly” as behavioral acceptance
  criteria.
- In Verification, name the tests, commands, browser/device checks, migrations,
  or operational evidence appropriate to the story. Do not require every
  verification mode for every story.
- Include documentation or operational work only when the story changes those
  surfaces.
- When revising shared architecture or contract prose, update every affected
  story. Story content is what issue synchronization hashes and delivers.
- Preserve existing IDs across revisions. Adding, removing, deferring, or
  materially rescoping stories must respect the authority rules in the shared
  contract.

## Revision behavior

When asked to address a review artifact, evaluate each blocking finding against
the evidence and original intent. Satisfy the required invariant with the
smallest coherent change; a reviewer suggestion is not automatically the
solution. Apply worthwhile non-blocking suggestions only when requested or
clearly beneficial.

Keep detailed finding dispositions in the review artifact or coordinator
handoff. Add only a compact changelog line to the design, for example:

```markdown
- 2026-07-28: Addressed review pass 2; clarified token ownership and updated AUTH-002.
```

Leave the document `Draft` for independent follow-up review.

## Report

Return the design path, a brief summary of the decisions and story order, the
validation result, and any user decision still required. Do not start issue
synchronization or implementation.
