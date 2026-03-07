---
name: user-story-implementer
description: Implement a single user story or task from a PRD or task list. Executes a single Ralph Loop iteration by reading the PRD, checking progress, completing exactly one user story/task, and appending the result. You MUST use this skill when asked to "implement a user story", "run one iteration", "do the next task", "execute a ralph loop iteration", or "complete a task from the PRD".
metadata:
  author: eho
  version: '1.0.4'
---

# Instructions

You are acting as an autonomous sub-agent to implement a user story or task from a Product Requirements Document (PRD), often as part of a single iteration of a task execution loop.

Your objective is to complete exactly **one** user story or task from the provided PRD or task list, verify its acceptance criteria, log your progress, and manage version control properly.

## Workflow

1. **Identify Scope**: Determine which feature or PRD you are working on. If multiple PRDs exist in `tasks/` (e.g., `tasks/prd-feature-a.md` and `tasks/prd-feature-b.md`), identify the correct one based on user instructions or recent context.
2. **Locate Files**: 
   - **PRD**: Identify the specific PRD (e.g., `tasks/prd-[feature-name].md`).
   - **Progress Log**: Use a feature-specific progress log (e.g., `tasks/progress-[feature-name].md`). If it doesn't exist, create it in the `tasks/` directory.
3. **Review Progress**: Read the progress log to understand which user stories or tasks have already been accomplished by previous iterations.
4. **Pick a Task**: Read the PRD and select the **next uncompleted User Story** or task. Pay specific attention to its **Acceptance Criteria**.
4. **Execute**: Implement the code, configuration, or changes required to complete that single user story. 
   - Ensure you fulfill all of the listed Acceptance Criteria.
   - Write unit tests or perform browser verification if required by the Acceptance Criteria.
   - Update any relevant documentation (e.g., design docs, architecture diagrams, CLI usage guides) as features are added, updated, or deleted.
   - If the user story is too large to complete in one iteration, complete a logical, meaningful chunk of it.
5. **Self-Review**: Before considering the task complete, perform a thorough self-review:
   - **Requirements**: Verify that the implemented solution aligns exactly with the user story.
   - **Acceptance Criteria**: Check that every single acceptance criterion is fully met.
   - **Test Coverage**: Ensure all significant logic and edge cases are covered by tests.
   - **Documentation**: Verify that design docs, architecture diagrams, or CLI usage instructions were updated if necessary.
   - **Code Quality**: Review the code changes for correctness, styling, and potential bugs.
   If anything is missing or incorrect, return to the Execution step to address it before proceeding.
6. **Log Progress**: Append a summary of what you just accomplished to the progress log file.
   - **Append-only**: Never remove entries from or otherwise rewrite the history of the progress log. **Why?** Re-writing the file risks losing historical context of what previous iterations accomplished and can cause conflicts.
   - Do not edit the PRD or task list file itself. Treat it as read-only.
7. **Commit Code**: Once your user story or chunk is complete, you must commit your changes.
   - Commit your changes to the **current branch**, unless said otherwise.
   - **Do not use** `git add -A` or `git commit -a`. You must select files manually (e.g., `git add src/file1.ts src/file2.css`) to ensure you only commit the files relevant to the specific logical chunk of work you just finished. **Why?** Blind commits might accidentally include unrelated changes or broken code left over from exploration.

## Loop Completion Mechanism

When you evaluate the PRD and determine that **ALL user stories and tasks are complete**, you must signal the end of the loop.

Instead of working on a task, append a completion marker to the end of the progress log file. 

If no specific marker string was provided to you by the user for this loop, append:
`----------`
`[RALPH_LOOP_DONE_MARKER]`

**CRITICAL WARNING**:
- Complete exactly **one** user story or task per invocation. Do not attempt to complete multiple user stories.
- If all user stories are done, you MUST append the completion marker so the loop knows to stop.

## Examples

**Example 1:**
*Input:* "Implement the next task for the Task Priority feature"
*Action:*
1. Locate files: `tasks/prd-task-priority.md` and `tasks/progress-task-priority.md`.
2. Read `tasks/prd-task-priority.md` and find the first User Story without a `[x]`. Let's say it's "US-002: Add priority selector".
3. Read `tasks/progress-task-priority.md` to see what was done previously.
4. Implement the feature.
5. Write tests to verify the Acceptance Criteria in US-002.
6. Review the user story, acceptance criteria, test coverage, and code to ensure everything is complete.
7. Append `Completed US-002: Add priority selector to task edit` to `tasks/progress-task-priority.md`.
8. Run `git add src/components/TaskEdit.tsx` and `git commit -m "feat: add priority selector (US-002)"`.
