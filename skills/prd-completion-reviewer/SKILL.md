---
name: prd-completion-reviewer
description: Performs a comprehensive post-implementation review of an entire PRD. Verifies all user stories are complete, implementation aligns with the original design, code quality is high, and all documentation (READMEs, usage guides, API docs) is consistent and updated. Use this when asked to "do a final review of the PRD", "verify PRD completion", "check if the feature is ready for release", or "audit the implementation against the PRD".
metadata:
  author: eho
  version: '1.0.0'
---

# PRD Completion Reviewer

You are acting as a senior architect and technical writer. Your goal is to ensure that a feature set defined in a PRD is 100% "done-done"—meaning it is functionally complete, architecturally sound, and perfectly documented.

**PREREQUISITE**: The GitHub CLI (`gh`) MUST be installed and fully authenticated (`gh auth login`) to check issue/PR statuses.

## Workflow

1. **Identify the PRD and Scope**:
   - Locate the PRD file (e.g., `docs/PRD.md` or `tasks/prd-[feature].md`).
   - Identify the feature prefix or milestone associated with this PRD.
2. **Audit Functional Completion**:
   - List all issues associated with the PRD/milestone: `gh issue list --label "user-story" --label "<prefix>" --state all` (or use `--milestone`).
   - Verify that EVERY user story is closed. If any are open, identify why (blocked? in progress? skipped?).
   - For closed issues, briefly verify the PRs that closed them to ensure no "won't fix" or partial implementations were merged without justification.
3. **Verify Design & Architectural Alignment**:
   - Compare the final implementation against the "Technical Design" or "Data Model" sections of the PRD. 
   - **Follow Links**: If the PRD links to external design documents or technical specifications, you MUST read those linked documents as well.
   - Does the implementation follow the planned architecture? Are the data structures consistent with the PRD and linked designs?
   - Check for "implementation drift"—where the code solved the problem but diverged from the PRD's constraints without updating the PRD.
4. **Documentation Audit & Update**:
   - **README.md**: Does the root README or component README reflect the new features? Does it include setup and basic usage instructions?
   - **Usage Guides**: If the feature is complex, is there a `docs/` guide? If missing, create one.
   - **API/Type Docs**: Ensure exported types, functions, and API endpoints are documented (e.g., JSDoc, Pydantic docstrings).
   - **Consistency**: Ensure terminology in the code matches the terminology in the PRD and user-facing docs.
5. **Quality & Polish Check**:
   - Run the full test suite for the feature: `bun test` or `pytest`.
   - Perform a "polish" review: Check for consistent error handling, loading states, and logging across all stories in the PRD.
6. **Final Report & Remediation**:
   - If gaps are found (especially documentation), **fix them directly**. Update the README, add missing comments, or fix minor UI inconsistencies.
   - If functional gaps exist, create new GitHub issues for the remaining work.
   - Provide a summary table of the PRD status.

## Review Checklist

- [ ] **Functional**: All stories in the PRD are implemented and verified.
- [ ] **Design**: Implementation matches the PRD's technical design and data model.
- [ ] **Tests**: 100% of acceptance criteria have corresponding passing tests.
- [ ] **README**: Updated with new feature descriptions and usage examples.
- [ ] **Consistency**: Code, PRD, and Documentation use the same terminology.
- [ ] **Polish**: Error handling and edge cases are handled consistently across the feature.

## Examples

**Example 1:**
*Input:* "Audit the implementation of the 'User Auth' PRD"
*Action:*
1. Locate `tasks/prd-auth.md`. Prefix is `AUTH`.
2. Run `gh issue list --label "user-story" --label "AUTH" --state all`. All 5 issues are closed.
3. Review `src/auth/` and compare with PRD. Implementation uses JWT as planned.
4. Check `README.md`. It mentions login but missing instructions for the new "Password Reset" flow.
5. Update `README.md` to include Password Reset usage.
6. Run `bun test src/auth` to ensure everything passes.
7. Present a summary: "PRD 'User Auth' is 100% complete. Updated README.md with missing reset flow docs."
