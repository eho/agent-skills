---
name: design-to-issues
description: 'Reconcile every user story in a revised design document with canonical GitHub Issues and a milestone. Use for creating, syncing, refreshing, or resuming issues from a design doc, including goal-based feature delivery. This workflow is idempotent: it creates missing issues, updates changed open issues, reopens stale delivered issues when requirements changed, and repairs labels, milestone, and dependency metadata.'
metadata:
  author: eho
  version: '2.1.0'
---

# Design to Issues

Publish the current design contract into GitHub without losing traceability. “Sync” means reconcile desired state, not merely create anything missing.

## Prerequisites

- Authenticated GitHub CLI.
- An exact design document path.
- A `## User Stories` section with stable story IDs.
- Repository and scoped `AGENTS.md` plus project documentation read before GitHub mutations.

Require `Status: Revised` or equivalent unless the user explicitly accepts the risk of publishing an unrevised design.

## Canonical identity

Use repository-relative design identity plus story ID as the stable composite key. Story IDs must be unique within one design, but need not be globally unique across the repository. Every managed issue body must contain:

```markdown
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:story=<STORY-ID> -->
<!-- feature-delivery:design-revision=<DOCUMENT-REVISION> -->
<!-- feature-delivery:story-revision=<STORY-REVISION> -->
```

Resolve and invoke `scripts/story_contract.py` to compute identities. It normalizes CRLF to LF, removes trailing horizontal whitespace, trims leading and trailing blank lines, adds exactly one final newline, and computes:

- `DOCUMENT-REVISION`: SHA-256 of the complete normalized design document;
- `STORY-REVISION`: SHA-256 of the exact normalized story source slice.

Do not reimplement this normalization ad hoc. The document revision makes shared architecture and contract changes visible; the story revision distinguishes directly changed stories.

Search open and closed issues for the exact design-and-story marker pair first. Use exact `<STORY-ID>:` title only to discover legacy candidates, and require design path, milestone/label history, body equivalence, and discussion evidence before adoption. Apply the equivalence check to open and closed legacy issues. More than one canonical candidate is a blocker; do not guess.

## Reconciliation

1. Read the complete design document and run:

   ```bash
   python3 /absolute/path/to/scripts/story_contract.py \
     <design-doc> --repo-root <repository-root> --include-source \
     > <temporary-manifest.json>
   ```

   Treat its manifest as the identity and ordering source. Also extract:
   - feature name and story prefix;
   - every in-scope story in document order;
   - description, outcome, design references, implementation context, dependencies, out-of-scope boundaries, acceptance criteria, verification, and technical notes;
   - explicit milestone, or feature name as the default milestone.
2. Read the repository default branch and owner with `gh repo view`.
3. Ensure `user-story` and feature-prefix labels exist.
4. Do not paraphrase managed issue bodies. Build them with `scripts/render_issue_body.py` from the manifest's exact normalized story source, canonical issue-number map, and stable design URL. The design-document revision makes every shared architecture or contract change visible and reopens closed delivery by default; each self-contained story slice remains the executable issue contract.
5. Build the complete current issue map before mutating anything:
   - find exact current design-and-story marker pairs and conservative legacy exact-title matches;
   - enumerate every issue under the milestone and feature-prefix label;
   - inspect design identity markers to find previously managed stories no longer present in the design.
6. Create or reuse the milestone with `scripts/create_milestone.sh`. A closed historical milestone is a policy decision, not an automatic mutation: report it unless the user/repository explicitly authorizes invoking the script with `--reopen`.
7. Reconcile in two deterministic phases so forward dependencies are safe:
   - Phase A: adopt verified legacy candidates and use the renderer's `--allow-unresolved-dependencies` mode to create every missing issue with exact source, identity markers, and dependency story IDs. Do not finalize numbered dependency links until every canonical issue number exists.
   - Phase B: write the complete story-to-issue JSON map, rerun the renderer without the unresolved flag for every story, then reconcile content and metadata.
8. During Phase B:
   - both revisions and complete desired body identical: leave content unchanged, but repair title, labels, and milestone;
   - either revision changed and issue open: update title and complete body;
   - document revision changed and issue closed: update and reopen because shared design evidence changed. Issue reconciliation never creates or assumes carry-forward evidence; the feature coordinator may close it later only after the independent carry-forward transition defined in `feature-delivery/references/contracts.md`;
   - story revision changed and issue closed: update, reopen, and comment that the story contract invalidated prior completion evidence;
   - revisions match but managed body drifted: rewrite the complete desired body; if the issue is closed, reopen because acceptance evidence no longer matches the canonical contract;
   - verified markerless legacy issue: adopt it by writing the complete desired body and markers, preserving discussion history; reopen a closed candidate unless equivalence with the complete current contract is proven.
9. Put dependencies in a managed section of the issue body rather than appending repeated comments:

   ```markdown
   ## Dependencies
   - Depends on: #<issue-number> (`<STORY-ID>`)
   ```

   Rewriting the managed body makes repeat runs idempotent.
10. Attach every canonical issue to the milestone, then re-read every issue, including unchanged candidates, and verify complete desired body equality, all four markers, revisions, labels, milestone, state, dependencies, and acceptance criteria. Repair any mismatch and verify once more; if drift persists, report a blocker.

Do not silently close removed stories. Compare all issues with the same design identity marker against the desired story set. Report unresolved removed stories as orphans requiring an explicit scope decision.

After the user explicitly changes scope, persist one terminal orphan resolution:

- `removed`: add `<!-- feature-delivery:scope=removed;decided-at-revision=<REVISION> -->`, comment with the decision and reason, close the issue if open, and keep it as history;
- `deferred`: add `<!-- feature-delivery:scope=deferred;decided-at-revision=<REVISION> -->`, comment with the target/follow-up and reason, and apply repository-approved deferred state/label;
- `restored`: remove the terminal scope marker by rebuilding the canonical active body, reopen, and return it to normal reconciliation.

A terminal scope marker remains effective across later unrelated document revisions until an explicit restoration/supersession decision or the story reappears in the design. Report it with its deciding revision in `Orphan resolutions`; do not rediscover it as a blocker. Never infer one of these resolutions merely from story absence.

## Issue body

```markdown
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:story=<STORY-ID> -->
<!-- feature-delivery:design-revision=<DOCUMENT-REVISION> -->
<!-- feature-delivery:story-revision=<STORY-REVISION> -->

## Managed Story Contract
<exact normalized story source slice from the design document>

## Canonical Dependencies
<canonical numbered issue references or None>

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
  - <Story ID>: #<number> <url> (<Created|Updated|Reopened|Unchanged>; story revision: <SHA-256>)
- Dependencies reconciled: yes/no
- Stale delivered stories reopened:
- Orphaned issues:
- Orphan resolutions:
- Blocked: yes/no
- Blocker:
```

## Available scripts

- `scripts/create_issue.sh "<title>" "<labels>" "<body-file>"`
- `scripts/create_milestone.sh "<milestone-title>" [--reopen]`
- `scripts/story_contract.py "<design-doc>" --repo-root "<repository-root>"`
- `scripts/render_issue_body.py --manifest <manifest.json> --story-id <ID> --issue-map <map.json> --design-url <url> --output <body.md>`

Resolve scripts relative to this `SKILL.md`. Use temporary files for multiline bodies and preserve unrelated repository changes.
