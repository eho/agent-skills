---
name: design-to-issues
description: 'Synchronize every user story in a revised design document with one canonical GitHub Issue and milestone. Use for creating, updating, or resuming story issues from a design doc, including feature-delivery. Existing issues are updated in place and changed completed stories are reopened.'
metadata:
  author: eho
  version: '3.1.0'
---

# Design to Issues

Synchronize the current user stories into GitHub. The design document defines desired scope; GitHub Issues track delivery progress.

## Prerequisites

- Read repository instructions and the complete design document.
- Require an exact design path.
- Normal synchronization requires `Status: Revised`, meaning the latest
  independent review had zero blockers and mechanical validation passed. The
  user may explicitly override a semantic review risk, but delivery-mode
  mechanical validation still must pass.
- Use the authenticated GitHub CLI and repository policy.

## Canonical identity

Identify a managed issue by repository-relative design path plus story ID:

```markdown
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:story=<STORY-ID> -->
```

Resolve and run `scripts/story_contract.py` in delivery mode to validate status,
story structure, stable IDs, and dependencies. Use its normalized story source
as the managed issue contract. The script's hashes may help compare content,
but GitHub progress does not require a separate tracking system.

Each story is canonical and must contain every shared architecture, data,
security, migration, compatibility, or rollout requirement that affects its
implementation. When such a requirement changes, update every affected story;
the changed story body is what causes completed work to reopen.

Search open and closed issues for the exact marker pair. Use an exact story-ID title only to discover a legacy candidate, and adopt it only when its design path, content, and history make the match unambiguous. Stop on duplicate candidates.

## Synchronization

1. Run:

   ```bash
   python3 /absolute/path/to/scripts/story_contract.py \
     <design-doc> --repo-root <repository-root> --mode delivery \
     --include-source \
     > <temporary-manifest.json>
   ```

2. Determine the repository, default branch, milestone, labels, and stable design URL.
3. Build the complete current issue map before mutating anything.
4. Create or reuse the milestone. Do not reopen a closed milestone without user or repository-policy authority.
5. Create every missing story issue. Use the bundled renderer so issue bodies contain the exact normalized story source and canonical dependency links.
6. Update existing issues in place when the managed story body, title, dependencies, labels, or milestone differ.
7. Reopen a completed issue when its story contract changed. Leave an unchanged completed issue closed.
8. Re-read every canonical issue and verify its markers, managed body, dependencies, labels, milestone, and state.

Do not silently close stories removed from the design. Report their existing issues and ask whether they should be removed, deferred, or restored. Persist the user's decision on the issue so later runs do not ask again.

## Managed issue body

```markdown
<!-- feature-delivery:design=<REPO-RELATIVE-DESIGN-PATH> -->
<!-- feature-delivery:story=<STORY-ID> -->

## Managed Story Contract
<exact normalized story source>

## Canonical Dependencies
<canonical numbered issue references or None>

## Design Doc
[View in Design Doc](<repository blob URL>)
```

The manifest hashes may help synchronization compare content, but consumers should rely on the canonical issue body and current GitHub state rather than reproducing hash-transition rules.

## Result

```markdown
- Design:
- Milestone:
- Issues created:
- Issues updated:
- Changed completed issues reopened:
- Unchanged completed issues:
- Removed-story issues requiring a decision:
- Blocker:
```

## Scripts

- `scripts/create_issue.sh`
- `scripts/create_milestone.sh`
- `scripts/story_contract.py`
- `scripts/render_issue_body.py`

Resolve scripts relative to this skill. Use temporary files for multiline bodies and preserve unrelated repository changes.
