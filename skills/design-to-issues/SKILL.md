---
name: design-to-issues
description: 'Reconcile every user story in a revised design document with canonical GitHub Issues and a milestone. Use for creating, syncing, refreshing, or resuming issues from a design doc, including goal-based feature delivery. This workflow is idempotent: it creates missing issues, updates changed open issues, reopens stale delivered issues when requirements changed, and repairs labels, milestone, and dependency metadata.'
metadata:
  author: eho
  version: '2.0.0'
---

# Design to Issues

Publish the current design contract into GitHub without losing traceability. “Sync” means reconcile desired state, not merely create anything missing.

## Prerequisites

- Authenticated GitHub CLI.
- An exact design document path.
- A `## User Stories` section with stable story IDs.

Require `Status: Revised` or equivalent unless the user explicitly accepts the risk of publishing an unrevised design.

## Canonical identity

Use the story ID as the stable key. Every managed issue body must contain:

```markdown
<!-- feature-delivery:story=<STORY-ID> -->
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:design-revision=<REVISION> -->
```

Compute `REVISION` deterministically from the exact story source slice: start at its story heading and end immediately before the next story heading of the same level or the next top-level section. Normalize CRLF to LF, remove trailing horizontal whitespace from each line, trim leading and trailing blank lines, add exactly one final newline, then compute SHA-256. Do not regenerate or summarize the story before hashing it.

Search open and closed issues for the exact marker first, then exact `<STORY-ID>:` title for legacy compatibility. More than one canonical candidate is a blocker; do not guess.

## Reconciliation

1. Read the complete design document and extract:
   - feature name and story prefix;
   - every in-scope story in document order;
   - description, outcome, design references, implementation context, dependencies, out-of-scope boundaries, acceptance criteria, verification, and technical notes;
   - explicit milestone, or feature name as the default milestone.
2. Read the repository default branch and owner with `gh repo view`.
3. Ensure `user-story` and feature-prefix labels exist.
4. Build the desired issue body for each story. Preserve all implementation-relevant detail so the issue remains sufficient after conversation compaction.
5. Build the complete current issue map before mutating anything:
   - find exact current story markers and legacy exact-title matches;
   - enumerate every issue under the milestone and feature-prefix label;
   - inspect design identity markers to find previously managed stories no longer present in the design.
6. Reconcile each story:
   - missing: create it with `scripts/create_issue.sh`;
   - same revision and identical desired body: leave content unchanged, but repair title, labels, and milestone;
   - same revision but body drifted: rewrite the complete desired body and repair metadata;
   - changed and open: update title and body with `gh issue edit --body-file`;
   - changed and closed: update the issue, reopen it, and comment that the design revision invalidated prior completion evidence;
   - unchanged and closed: preserve its closed state as historical delivered evidence.
   - markerless legacy and open: adopt it by writing the complete desired body and markers, preserving its discussion history;
   - markerless legacy and closed: compare its normalized managed story sections with the desired visible body. If equivalent, add markers without reopening. If equivalence cannot be established, update and reopen it conservatively because current acceptance evidence is unproven.
7. Put dependencies in a managed section of the issue body rather than appending repeated comments:

   ```markdown
   ## Dependencies
   - Depends on: #<issue-number> (`<STORY-ID>`)
   ```

   Rewriting the managed body makes repeat runs idempotent.
8. Create or reuse the milestone with `scripts/create_milestone.sh`, then attach every canonical issue.
9. Re-read every canonical issue, including unchanged candidates, and verify complete desired body equality, markers, revision, labels, milestone, state, dependencies, and acceptance criteria. Repair any mismatch and verify once more; if drift persists, report a blocker.

Do not silently close removed stories. Compare all issues with the same design identity marker against the desired story set. Report removed stories as orphans requiring an explicit scope decision.

## Issue body

```markdown
<!-- feature-delivery:story=<STORY-ID> -->
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:design-revision=<REVISION> -->

## Story
<description and outcome>

## Design References
<architecture, contracts, and integration points>

## Implementation Context
<files to read/change, boundaries, and technical notes>

## Dependencies
<canonical issue references or None>

## Acceptance Criteria
<exact binary criteria and verification requirements>

## Design Doc
[View in Design Doc](<repository blob URL>)
```

## Handoff

```markdown
## Issue Sync Handoff
- Design doc:
- Design revision:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<number> <url> (<Created|Updated|Reopened|Unchanged>)
- Dependencies reconciled: yes/no
- Stale delivered stories reopened:
- Orphaned issues:
- Blocked: yes/no
- Blocker:
```

## Available scripts

- `scripts/create_issue.sh "<title>" "<labels>" "<body-file>"`
- `scripts/create_milestone.sh "<milestone-title>"`

Resolve scripts relative to this `SKILL.md`. Use temporary files for multiline bodies and preserve unrelated repository changes.
