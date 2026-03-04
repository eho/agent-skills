---
name: user-story-implementer
description: Implement a single user story or task from a PRD or task list. Executes a single Ralph Loop iteration by reading the PRD, checking progress, completing exactly one user story/task, and appending the result. Use when asked to "implement a user story", "run one iteration", "do the next task", "execute a ralph loop iteration", or "complete a task from the PRD".
---

# Instructions

You are acting as an autonomous sub-agent to implement a user story or task from a Product Requirements Document (PRD), often as part of a single iteration of a task execution loop.

Your objective is to complete exactly **one** user story or task from the provided PRD or task list, verify its acceptance criteria, log your progress, and manage version control properly.

## Workflow

1. **Locate Files**: Identify the PRD or task list (usually `tasks/prd-*.md`, `PRD.md`, or `TASKS.md`) and the progress log (usually `progress.txt` or similar) in the workspace.
2. **Review Progress**: Read the progress log to understand which user stories or tasks have already been accomplished by previous iterations.
3. **Pick a Task**: Read the PRD and select the **next uncompleted User Story** or task. Pay specific attention to its **Acceptance Criteria**.
4. **Execute**: Implement the code, configuration, or changes required to complete that single user story. 
   - Ensure you fulfill all of the listed Acceptance Criteria.
   - Write unit tests or perform browser verification if required by the Acceptance Criteria.
   - If the user story is too large to complete in one iteration, complete a logical, meaningful chunk of it.
5. **Log Progress**: Append a summary of what you just accomplished to the progress log file.
   - **Append-only**: Never remove entries from or otherwise rewrite the history of the progress log.
   - Do not edit the PRD or task list file itself. Treat it as read-only.
6. **Commit Code**: Once your user story or chunk is complete, you must commit your changes.
   - Commit your changes to the **current branch**, unless said otherwise.
   - **Do not use** `git add -A` or `git commit -a`. You must select files manually (e.g., `git add src/file1.ts src/file2.css`) to ensure you only commit the files relevant to the specific logical chunk of work you just finished.

## Loop Completion Mechanism

When you evaluate the PRD and determine that **ALL user stories and tasks are complete**, you must signal the end of the loop.

Instead of working on a task, append a completion marker to the end of the progress log file. 

If no specific marker string was provided to you by the user for this loop, append:
`----------`
`[RALPH_LOOP_DONE_MARKER]`

**CRITICAL WARNING**:
- Complete exactly **one** user story or task per invocation. Do not attempt to complete multiple user stories.
- If all user stories are done, you MUST append the completion marker so the loop knows to stop.
