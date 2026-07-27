# Design Contract

This is the shared contract between `design-doc`, `design-doc-reviewer`,
`design-doc-review-loop`, `design-to-issues`, and `feature-delivery`.

## Readiness

- `Draft` means the design is being authored or revised.
- `Revised` normally means the latest independent review found zero blocking
  findings and mechanical validation passed. Only `design-doc-review-loop`, or
  an explicit user override recorded in the changelog, may promote a document
  to `Revised`. An override may accept a semantic risk; it cannot make an
  invalid story contract consumable.
- Non-blocking suggestions may remain or be waived. They do not prevent
  readiness.
- An unresolved decision blocks readiness only when an in-scope story cannot be
  implemented safely and consistently without it.

Use `story_contract.py --mode author` while writing or reviewing. It accepts
`Draft` and `Revised`. `design-to-issues` and `feature-delivery` use
`--mode delivery`, which requires `Revised`.

Repositories may retain `Active`, `Implemented`, historical, superseded, or
abandoned statuses for their broader documentation lifecycle. Those are not
actionable inputs to this delivery pipeline. Move an implementation plan back
to `Draft`, revise and review it, then promote it to `Revised` before delivery.

## Evidence and authority

Distinguish verified current repository facts, proposed decisions, and
unresolved assumptions. Verify material integration points against current
code, tests, schemas, configuration, and repository guidance; do not turn
guessed paths or signatures into facts.

Preserve explicit user decisions and scope. Scope expansion, story removal or
deferral, destructive migration choices, and changes to explicit product
decisions require user authority. Prefer the smallest coherent contract that
addresses the demonstrated risk.

## Design content

A design is implementation-ready when it concisely establishes:

- the problem, goals, scope, and non-goals;
- the chosen approach and rationale;
- repository-grounded architecture, ownership, integration points, and
  contracts;
- relevant edge cases and failure behavior;
- security, privacy, data, migration, compatibility, performance, rollout,
  rollback, and operational behavior when those concerns materially apply;
- how the feature and its risky paths will be verified;
- no unresolved decision that prevents an in-scope story.

Use sections that help this design. Do not add placeholder sections, arbitrary
alternative counts, or generic operational detail merely to satisfy a
checklist.

## Canonical user stories

`design-to-issues` copies each story into its canonical GitHub Issue. Each story
must therefore be independently implementable and contain:

```markdown
### DEMO-001: Short outcome-oriented title

**Outcome:** One coherent behavioral result.

**Implementation Context:**
- Verified files and existing contracts the implementer must inspect.
- Proposed files or contracts likely to change.
- **Depends on:** None
- **Out of scope:** Explicit boundary for this slice.

**Acceptance Criteria:**
- [ ] Given a defined state, when an action occurs, then an observable result follows.

**Verification:**
- Run or perform the specific checks that prove the criteria.
```

Mechanical rules:

- Include exactly one `User Stories` section. Story headings are exactly one
  level below it and contain one unique ID matching
  `[A-Z][A-Z0-9]{1,9}-[0-9]{3,}`.
- Treat an assigned story ID as immutable. Never renumber existing stories or
  reuse a removed ID for a different outcome; append new IDs.
- Include exactly one `Depends on:` declaration per story. Its value is `None`
  or comma-separated story IDs, with no prose. Dependencies must exist, cannot
  reference the same story, and must be acyclic.
- Include non-empty `Outcome` and `Out of scope` fields, at least one binary
  acceptance-criteria checkbox, and at least one list item under
  `Verification`. Put Outcome and scope before Acceptance Criteria, followed by
  Verification. Items in later fields or headings do not satisfy an empty
  required section.
- Do not place `<!-- feature-delivery:` management markers in story source;
  issue synchronization owns those reserved markers.
- Keep each story to one focused, dependency-ordered implementation slice.
  Name relevant files and contracts when known, but do not invent them.

The story is the implementation contract, not merely a pointer to shared prose.
When a shared architecture, API, data, security, migration, compatibility, or
rollout requirement changes, update every affected story so issue
synchronization detects the changed contract and reopens completed work.
