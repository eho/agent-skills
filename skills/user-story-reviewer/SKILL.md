---
name: user-story-reviewer
description: 'Independently review one implemented GitHub user story PR against its canonical issue, current design revision, acceptance criteria, tests, documentation, and repository policy. Use for PR QA, story review, follow-up review after fixes, or as the reviewer in user-story-delivery and feature-delivery. Report findings first; never treat approval or a comment as proof that an unmerged story is delivered.'
metadata:
  author: eho
  version: '3.0.0'
---

# User Story Reviewer

Act as an independent code reviewer for exactly one story PR. The implementer and reviewer must not be the same agent context when an orchestration runtime can provide separate contexts.

## Preflight

1. Require an exact story ID and PR number or URL.
2. Inspect PR metadata, draft state, author, branch, base, commits, changed files, closing issues, reviews, merge state, and checks.
3. Confirm the PR maps to the canonical issue and current design revision. Stop on ambiguity.
4. Read the complete issue, including every acceptance criterion, dependency, scope boundary, and prior review finding.
5. Inspect the PR diff. For non-trivial changes, inspect the checked-out code in context without overwriting unrelated work.
6. If checks are pending or failing, review may continue, but do not approve or merge until policy permits it.

## Review

Lead with concrete findings ordered by severity. For each finding include:

- file and line or precise diff location;
- the incorrect or missing behavior;
- its impact on requirements or system safety;
- the required change.

Review every acceptance criterion and examine:

- behavioral correctness and regressions;
- test depth, happy paths, failures, and edge cases;
- auth, permissions, secrets, privacy, and data safety;
- state lifecycle, migrations, compatibility, rollback, concurrency, and performance;
- relevant docs, examples, CLI/API/UI terminology, diagnostics, and operations;
- actual verification results rather than claimed results.

Run appropriate local verification when possible. For meaningful UI changes, perform browser/visual verification when the runtime supports it. State anything not verified and its residual risk.

## Decisions

- `Request changes`: default for behavioral, acceptance, architecture, safety, compatibility, or meaningful test-confidence gaps. Post the findings and stop for implementation.
- `Fix small issue`: allowed only for a small, mechanical, low-risk fix clearly implied by the issue. Commit and push the exact files, then require a fresh independent review before sign-off.
- `Approve`: formal approval when the reviewer is not the author and all required checks and criteria pass.
- `Comment only`: evidence-based sign-off when approval is unavailable or prohibited.
- `Merge`: only when repository policy authorizes this reviewer to merge and all prerequisites pass.

Approval and comment-only are review states, not delivery completion.

## Merge policy

Read `AGENTS.md`, branch protection, required checks, and user instructions. Do not infer that a self-authored PR should always be merged automatically.
Inspect the repository's allowed merge methods, merge queue or auto-merge requirements, and branch-retention policy before invoking a merge.

Write a detailed review body to a temporary file and invoke the bundled script:

```bash
# Review/sign-off without merging
bash /absolute/path/to/scripts/approve_or_merge_pr.sh <pr-number> <review-file> --comment-only

# Merge only when repository policy authorizes it
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --merge --merge-method <squash|merge|rebase>

# Submit to a required merge queue without choosing a direct merge method
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --merge --queue
```

Add `--delete-branch` only when policy permits branch deletion. Use `--auto` with an explicit merge method when policy enables auto-merge but does not require queue submission. For another author's PR, the script approves by default; `--merge` additionally merges or queues only after approval succeeds. Resolve the script relative to this `SKILL.md`.

## Review output

```markdown
## Findings
- <ordered findings or "No blocking findings found.">

## Open Questions
- <correctness questions or "None.">

## Acceptance Criteria
| Criterion | Evidence | Result |
| --- | --- | --- |

## Verification
- PR preflight:
- Commands/checks:
- Browser/manual checks:
- Not verified:
- Residual risk:

## Decision
Decision: Request changes | Fix small issue | Approve | Comment only | Merge
Rationale:
```

## Handoff

```markdown
## Review Handoff
- Story ID:
- Issue:
- PR:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Required follow-up:
- Acceptance criteria evidence:
- Verification:
```

After `Merge`, re-read the PR and issue and report actual merged/closed state. Do not claim story completion solely from the action command succeeding.
