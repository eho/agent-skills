---
name: user-story-reviewer
description: 'Independently review one implemented GitHub user story or audit-gap PR, or revalidate a historical merged delivery for carry-forward, against its canonical issue, current design revision, criteria, tests, documentation, and repository policy. Use for PR QA, story review, carry-forward review, or as the reviewer in feature delivery.'
metadata:
  author: eho
  version: '3.2.0'
---

# User Story Reviewer

Act as an independent code reviewer for exactly one story/audit-gap PR, or for one explicit carry-forward candidate. The implementer and reviewer must not be the same agent context when an orchestration runtime can provide separate contexts.

## Preflight

1. Read repository and scoped `AGENTS.md` files, project documentation, branch protection, and merge conventions.
2. Require an exact story or audit-gap ID and PR number or URL. For carry-forward mode, require both the canonical issue and exact historical merged PR.
3. Inspect PR metadata, draft state, author, branch, base, head SHA, delivery ID, supersedes marker, commits, changed files, closing issues, reviews and their commit SHAs, merge state, and checks.
4. Confirm the PR is the unique current delivery leaf and maps to the canonical issue through the complete marker tuple. Stop on ambiguity.
5. Read the complete issue, including every acceptance criterion, dependency, scope boundary, and prior review finding.
6. Inspect the PR diff. For non-trivial changes, inspect the checked-out code in context without overwriting unrelated work.
7. If checks are pending or failing, review may continue and findings may be posted, but do not approve or merge. Record the exact reviewed head SHA; any later head change invalidates sign-off and requires a fresh independent review.

## Carry-forward mode

Carry-forward is independent revalidation, not PR approval or revision-marker editing. Use it only after reconciliation reopened a delivered issue and the coordinator supplies the current tuple plus one historical merged delivery candidate.

1. Read the complete current design, canonical issue, current criteria, shared contracts, and every dependency.
2. Verify the historical PR's immutable delivery ID, historical tuple, reviewed head, merge SHA, and current-default ancestry. Inspect that exact delivered code in the current default branch, including subsequent changes that could invalidate it.
3. Re-run every verification needed to prove the historical delivery satisfies the current issue and shared contracts. Absence of a direct story-source change is not proof.
4. Decide `Carry forward` only with criterion-by-criterion and shared-contract evidence and no blocking finding. Otherwise decide `Reopen delivery`.
5. Return the exact handoff below. Do not edit or comment on the historical PR, close the issue, or create the durable record; the coordinator owns that transition.

```markdown
## Carry-Forward Review Handoff
- Story ID:
- Issue:
- Design doc:
- Current design revision:
- Current story revision:
- Historical PR:
- Historical delivery ID:
- Historical design revision:
- Historical story revision:
- Historical reviewed and merged head SHA:
- Reviewer:
- Current acceptance criteria evidence:
- Current shared-contract evidence:
- Verification:
- Decision: Carry forward | Reopen delivery
- Blocking findings:
```

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

Run focused independent verification for the changed behavior and highest risks. Reuse a valid immutable exact-head broad-gate result when the feature verification policy permits; rerun it when repository policy, changed configuration, suspicious evidence, or risk requires it. For meaningful UI changes, perform browser/visual verification only when the policy assigns it to the agent and the feature-wide runtime budget remains. Preserve authorized owner-manual criteria as pending rather than retrying them or calling them passed.

## Decisions

- `Request changes`: default for behavioral, acceptance, architecture, safety, compatibility, or meaningful test-confidence gaps. Post the findings and stop for implementation.
- `Fix small issue`: allowed only for a small, mechanical, low-risk fix clearly implied by the issue. Commit and push the exact files, then hand off to a fresh reviewer context independent of both the implementer and the reviewer who authored the fix.
- `Approve`: formal approval when the reviewer is not the author and all required checks and criteria pass.
- `Comment only`: evidence-based sign-off when approval is unavailable or prohibited.
- `Merge`: only when repository policy authorizes this reviewer to merge and all prerequisites pass.

Approval and comment-only are review states, not delivery completion.

## Merge policy

Read `AGENTS.md`, branch protection, required checks, and user instructions. Do not infer that a self-authored PR should always be merged automatically.
Inspect the repository's allowed merge methods, merge queue or auto-merge requirements, and branch-retention policy before invoking a merge.

Immediately before approval and again before merge, fail closed unless:

- the PR is open and non-draft;
- its base is the expected repository-policy branch;
- its head SHA exactly matches the SHA reviewed;
- all required and reported checks are successful, neutral, or skipped as policy permits;
- the PR is mergeable and its merge-state status is compatible with the chosen direct or queue path;
- the current repository review decision satisfies policy;
- the selected merge method is enabled, or queue submission is required.

Write a detailed review body to a temporary file and invoke the bundled script:

```bash
# Review/sign-off without merging
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --comment-only --expected-head <reviewed-head-sha>

# Formal approval without merging
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --approve --expected-head <reviewed-head-sha> \
  --required-check "<required-context>"

# Merge only when repository policy authorizes it
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --merge --expected-head <reviewed-head-sha> \
  --merge-method <squash|merge|rebase> --required-check "<required-context>"

# Submit to a required merge queue without choosing a direct merge method
bash /absolute/path/to/scripts/approve_or_merge_pr.sh \
  <pr-number> <review-file> --merge --expected-head <reviewed-head-sha> \
  --queue --required-check "<required-context>"
```

Repeat `--required-check` for every context discovered from branch/ruleset and repository policy. Use `<context>@<integration-id>` when policy binds a check to a GitHub App. If policy has no required checks, pass `--no-required-checks` explicitly; an empty check rollup alone is not proof. Use `--request-changes --expected-head <sha>` to post a formal request when the GitHub identity is not the author; the script falls back to a commit-bound comment for self-authored PRs. Add `--delete-branch` only when policy permits branch deletion. Do not enable asynchronous auto-merge: exact-head independent review must be re-established after any later push.

For another author's PR, `--approve` and `--merge` create a review bound to the exact reviewed commit ID. For a self-authored PR, merging requires both repository-policy authority and the explicit `--allow-self-merge` flag; otherwise the script refuses. The script passes `--match-head-commit`, rechecks volatile PR state after review, reconciles required check names and app identities with applicable rules, verifies a merge-queue rule before methodless queue submission, and confirms merged or active queue state. Resolve it relative to this `SKILL.md`.

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
- Design doc:
- Design revision:
- Story revision:
- Delivery ID:
- PR:
- Reviewed head SHA:
- Base branch:
- Draft state:
- Required checks:
- Mergeability:
- Merge policy:
- Review epoch:
- Review cycle:
- Strategy:
- Blocking finding IDs:
- Decision: Request changes | Fix small issue | Approve | Comment only | Merge
- Blocking findings:
- Reviewer-fixed commits:
- Resulting head SHA:
- Merge or queue result:
- Required follow-up:
- Acceptance criteria evidence:
- Verification:
```

After `Merge`, re-read the PR and issue and report actual merged/closed state. Do not claim story completion solely from the action command succeeding.

Keep review output concise. Findings and changed evidence belong in the review body; the handoff should reference that body and contain only the current identity, decision, finding IDs, verification delta, and merge result.
