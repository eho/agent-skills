---
name: design-to-issues
description: Parses a revised design document and idempotently synchronizes its user stories, acceptance criteria, labels, dependencies, and milestone with GitHub Issues. Use whenever the user asks to send a design doc to GitHub, create or refresh issues from a design, set up a feature milestone, or reconcile revised requirements with an existing issue backlog.
metadata:
  author: eho
  version: '1.2.0'
---

# Design to Issues

Act as the requirements-publishing specialist. Convert every in-scope story in a revised design document into an exact, self-contained GitHub Issue. Reruns are synchronization runs: update changed canonical content, preserve unchanged content, and never duplicate issues or dependency comments.

**Prerequisite:** `gh` must be installed and authenticated.

## Workflow

1. **Resolve inputs and skill directory**
   - Require an unambiguous design-document path.
   - Resolve `SKILL_DIR` from the skill invocation or as the directory containing this file. Its scripts are authoritative; do not recreate their behavior with ad-hoc shell.

2. **Check design readiness**
   - Read the design and, when present, `docs/design/review-<filename>.md`.
   - Require evidence that review feedback was incorporated: `Status: Revised`, revision notes, or explicit user authorization to publish despite the review state.
   - If an existing review has unresolved critical gaps, stop. If no review exists, continue only when the request explicitly authorizes publication or the caller has already established readiness.

3. **Read repository metadata**
   - Run:
     ```bash
     gh repo view --json nameWithOwner,defaultBranchRef -q '{owner: .nameWithOwner, branch: .defaultBranchRef.name}'
     ```
   - Do not assume the default branch name. Use it for design-document links.

4. **Parse the complete story set**
   - Extract every story under `## User Stories` by its stable ID heading, such as `### PRI-001: Title`.
   - Preserve description, outcome, design references, implementation context, files, contracts, dependencies, out-of-scope boundaries, acceptance criteria, verification commands, tests, browser checks, documentation decisions, and technical notes.
   - Record explicit user deferrals separately. A story is not deferred merely because its issue is closed or absent.

5. **Ensure labels and milestone**
   - Read existing labels as JSON. Create only missing `user-story` and feature-prefix labels. Treat an already-existing response as success.
   - Resolve the milestone from the design or feature title, then run:
     ```bash
     "$SKILL_DIR/scripts/create_milestone.sh" "<milestone-title>"
     ```
   - Label and milestone setup must be safe on every rerun.

6. **Build a unique issue map**
   - Search open and closed issues by exact story ID:
     ```bash
     gh issue list --state all --label user-story --search "<story-id> in:title" \
       --json number,title,url,state,body,labels,milestone --limit 100
     ```
   - Reuse an issue only when its title begins with `<story-id>:`. Stop on duplicate matches; never guess which duplicate is canonical.
   - Also list all issues carrying both `user-story` and the feature-prefix label. Report any issue whose story ID is no longer in the design as `Removed from design`; do not close, delete, unlabel, or rewrite it without explicit user direction.

7. **Render and synchronize canonical issues**
   - Render each current story body deterministically with these sections when applicable:
     ```markdown
     ## Story
     <description, outcome, and design references>

     ## Implementation Context
     <files, contracts, dependencies, boundaries, and technical notes>

     ## Acceptance Criteria
     <the exact checklist and verification requirements>

     ## Design Doc
     [View in Design Doc](<blob-url>)
     ```
   - Use a temporary directory outside the worktree:
     ```bash
     TMP_DIR=$(mktemp -d)
     trap 'rm -rf "$TMP_DIR"' EXIT
     BODY_FILE="$TMP_DIR/<story-id>.md"
     ```
   - Do not use a fixed `issue_body.md` or another worktree file.
   - For each story, run:
     ```bash
     "$SKILL_DIR/scripts/sync_issue.sh" \
       "<existing-number-or-new>" "<story-id>: <title>" "user-story,<prefix>" "$BODY_FILE"
     ```
   - The script compares exact title and body content, updates only changed fields, adds only missing required labels, and creates the issue when `new` is supplied.
   - Attach every current mapped issue to the milestone. Do not reopen or close issues during requirements synchronization.

8. **Upsert dependency relationships**
   - Resolve every declared blocker through the complete issue map. Stop if any dependency is missing or ambiguous.
   - Render one canonical dependency comment per dependent issue:
     ```markdown
     <!-- agent-skills:dependencies -->
     Depends on: #42, #43
     ```
   - Sort blocker issue numbers and call:
     ```bash
     "$SKILL_DIR/scripts/upsert_dependency_comment.sh" "<issue-number>" "$DEPENDENCY_FILE"
     ```
   - The marker makes reruns idempotent. If multiple marker comments already exist, stop and report them instead of deleting history.
   - For a story whose dependencies were removed, upsert the canonical marker comment with `Depends on: None` so stale dependency state is not retained.

9. **Handle deferrals and removals safely**
   - Report explicit deferrals in the handoff, but do not close, delete, or alter their issues unless the user specifically requests that GitHub state change.
   - Report removed stories discovered by prefix-label reconciliation. Their existing issues remain untouched.

10. **Return the exact handoff**

## Exact handoff

```markdown
## Issue Sync Handoff
- Design doc:
- Milestone:
- Story prefix:
- Issues:
  - <Story ID>: #<number> <url> (<Created|Updated|Unchanged>; issue <OPEN|CLOSED>)
- Deferred stories:
- Removed stories:
- Dependencies: Synchronized | Blocked
- Blocked: yes/no
- Blocker:
```

Every current in-scope story must appear exactly once. `Updated` means title, body, labels, dependencies, or milestone changed; `Unchanged` means no synchronization mutation was needed.

## Operating rules

- The design document is the requirements source of truth; GitHub issue/PR state is the delivery ledger.
- Synchronize content, not lifecycle. Never infer that a revised design authorizes closing, reopening, or deleting an issue.
- Preserve full acceptance criteria exactly enough for an implementer to work from the issue alone.
- Use stable story IDs, exact body comparison, and marker comments; title-only heuristics and unconditional comments are not idempotent.
- Stop on duplicate IDs, missing dependency targets, or ambiguous scope.

## Scripts

- `sync_issue.sh "<issue-number|new>" "<title>" "<labels>" "<body-file>"`: create or exactly reconcile one issue.
- `upsert_dependency_comment.sh "<issue-number>" "<body-file>"`: create, update, or leave unchanged the single marker comment.
- `create_milestone.sh "<title>"`: ensure one milestone exists.
