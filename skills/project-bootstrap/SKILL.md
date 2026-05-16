---
name: project-bootstrap
description: Initialize or update a repository so coding agents can work in it effectively. Use this skill whenever the user asks to bootstrap a new project, make a repo coding-agent friendly, create or update AGENTS.md, set project rules, add documentation conventions, initialize docs structure, or refresh package-manager/project-command guidance.
---

# Project Bootstrap

Use this skill to initialize or update lightweight project conventions for coding agents. The goal is not to teach agents generic software engineering. The goal is to capture the small set of project-specific facts that are easy to get wrong or expensive to rediscover.

This skill includes a reusable project-rules template at `templates/AGENTS.md`. Treat runtime, project-pattern, source-of-truth, testing, and safety sections as a menu, not a form to fill completely. Package manager rules and documentation conventions are baseline sections for this user's projects and should be included whenever a package manager and docs structure are known or being initialized.

## Core Principle

Keep `AGENTS.md` lean.

Only include rules that are specific to this repository or stack. If a capable coding agent can infer a rule from the codebase in under a minute, omit it unless the rule prevents a common mistake.

Good `AGENTS.md` content:

- Package manager and lockfile policy.
- Canonical project commands.
- Documentation source-of-truth locations.
- Documentation lifecycle rules for living docs, active specs, and archived design records.
- Runtime constraints that are easy to violate.
- Framework-specific install or code-generation rules.
- Project-specific naming, product, or domain conventions.
- Tooling commands that must be run through package scripts.
- Safety constraints for secrets, credentials, cloud resources, databases, and user data.

Avoid:

- Generic advice such as "write clean code", "add tests", "follow existing patterns", or "keep changes scoped".
- Long explanations of the architecture.
- Lists of every directory when the layout is obvious.
- Rules copied from other projects without evidence they apply here.
- Agent behavior rules that belong in global instructions rather than the repo.

## Workflow

### 1. Inspect the repository

Before editing, gather local evidence:

- `rg --files -g 'AGENTS.md' -g 'README.md' -g 'package.json' -g 'bun.lock' -g 'pnpm-lock.yaml' -g 'yarn.lock' -g 'package-lock.json' -g '.npmrc' -g '.nvmrc' -g '.node-version'`
- `find docs -maxdepth 3 -type f`, if `docs/` exists.
- `package.json` scripts and dependencies, if present.
- Existing framework config files such as `app.json`, `expo.json`, `next.config.*`, `vite.config.*`, `tsconfig.json`, `turbo.json`, or workspace files.
- Existing `.env.example` or documented environment setup.

Use this evidence to infer the minimum useful rules. Do not invent rules when the repo does not indicate them.

### 2. Decide initialize vs update mode

Use initialize mode when no `AGENTS.md` exists. Start from `templates/AGENTS.md`, then delete unused sections and replace placeholders with facts supported by repository evidence. Keep the package-manager section when a package manager is detected or chosen. Keep the documentation and documentation-conventions sections when docs exist or are initialized.

Use update mode when `AGENTS.md` already exists. Preserve project-specific rules. Refresh stale package-manager, command, and documentation sections when the repo clearly contradicts them. Do not remove existing rules unless they are obviously generic clutter or the user asks for cleanup.

### 3. Guided discovery for new projects

When initializing a new project that lacks source-of-truth docs, ask a small number of focused questions before writing `AGENTS.md` or docs. The goal is to capture enough context to seed durable docs, not to run a full product strategy workshop.

Ask only questions needed for missing context. Prefer one concise round with prompts like:

- What are you building, and who is it for?
- What is the project's purpose or north star?
- What kind of app/service/library is this, and what major capabilities should it have?
- What stack, framework, package manager, database, or hosting choices are already decided?
- Are there important constraints, integrations, compliance concerns, user-data rules, or naming conventions?
- Do you want lightweight source-of-truth docs created now, such as `docs/vision/vision.md`, `docs/architecture/architecture.md`, and `docs/architecture/tech-stack.md`?

After the user answers:

- Create only docs that are applicable and useful now.
- Keep seed docs short, explicit, and labeled as current starting points rather than final architecture.
- Use `docs/vision/vision.md` for purpose, audience, goals, and product direction.
- Use `docs/architecture/architecture.md` for high-level system shape, major components, data flow, and integration boundaries.
- Use `docs/architecture/tech-stack.md` for chosen technologies, package manager, runtime, tooling, and deployment assumptions.
- Use `docs/architecture/current-design/` only for implemented behavior; for an empty project, create an index that says current design docs should be added as features are implemented.
- Add `Current Source Of Truth` entries to `AGENTS.md` only for files or directories that now exist.
- If the user does not want docs initialized, omit source-of-truth entries that would point to nonexistent files.

Never leave placeholders in committed project docs or `AGENTS.md`.

### 4. Apply the project-rules template

The template intentionally combines the best reusable pieces from mature project rule files:

- A short project overview with links to source-of-truth docs.
- Package-manager rules that prevent agents from mixing install tools.
- Canonical commands so agents run the project the same way maintainers do.
- Runtime/framework traps that are easy to violate.
- Non-obvious project patterns, especially boundaries for routing, services, state, navigation, data access, generated code, user isolation, and naming.
- Documentation structure and lifecycle rules that distinguish living current-state docs from point-in-time design records.
- Current source-of-truth paths for vision, architecture, current design, operations, and docs indexes.
- Focused testing expectations and safety constraints.

When adapting the template:

- Remove every placeholder that cannot be filled from repo evidence.
- Omit optional sections that would only contain generic advice.
- Keep the standard documentation conventions unless the user explicitly asks for a minimal `AGENTS.md` without documentation lifecycle rules.
- Keep examples concrete and runnable from the current repo layout.
- Prefer exact paths and commands over prose.
- Use relative Markdown links for documentation paths.

### 5. Package manager rules

Detect the package manager from lockfiles and package manager metadata:

- `bun.lock` means Bun.
- `pnpm-lock.yaml` means pnpm.
- `yarn.lock` means Yarn.
- `package-lock.json` means npm.
- If multiple lockfiles exist, report the ambiguity and prefer the lockfile used by scripts/docs only when clear.

Always include a package-manager section when the package manager is known. It must tell agents which commands to use and which equivalent commands not to use. For Bun projects, prefer this section:

```md
## Package Manager

Use Bun.

- `bun install` instead of `npm install`, `yarn install`, or `pnpm install`
- `bun run <script>` instead of `npm run <script>`
- `bunx <tool>` instead of `npx <tool>`
- Do not add or update `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`
```

For Expo projects using Bun, add:

```md
- Use `expo install <package>` when Expo SDK compatibility matters
- Bun automatically loads `.env`; do not add `dotenv` just to load local environment variables
```

Adapt the commands and lockfile prohibition for pnpm, npm, Yarn, Poetry, or other package managers.

If no package manager exists yet, ask which one to standardize on before writing `AGENTS.md`. Do not leave the package manager unspecified.

### 6. Canonical commands

Read package scripts and include only commands agents will commonly need:

- Dev/start server.
- Test.
- Typecheck.
- Lint.
- Build.
- Deploy only when the repo has a clear deploy script.

Prefer package scripts over underlying tools. If a test or typecheck must not be invoked directly, state that.

Use this shape:

```md
## Commands

- Dev: `<command>`
- Test: `<command>`
- Typecheck: `<command>`
- Lint: `<command>`
- Build: `<command>`

Use these package scripts rather than invoking underlying tools directly unless there is a specific reason.
```

Omit missing commands instead of adding placeholders or instructions like "add commands here later." If the repo has not been scaffolded yet, either ask whether to scaffold first or omit the commands section until scripts exist.

### 7. Documentation structure

If the project has no docs structure, create a minimal one:

```text
docs/README.md
docs/vision/README.md
docs/architecture/README.md
docs/architecture/current-design/README.md
docs/design/README.md
docs/design/archive/README.md
docs/operational/README.md
docs/planning/README.md
docs/testing/README.md
```

Use this baseline `AGENTS.md` section:

```md
## Documentation

Project docs live under `docs/`.

- `docs/vision/` — strategic vision, product goals, and project direction
- `docs/architecture/` — current system architecture and technical decisions
- `docs/architecture/current-design/` — how the implemented system works now
- `docs/design/` — active feature specs and implementation plans
- `docs/design/archive/` — implemented, superseded, or historical specs
- `docs/operational/` — runbooks, local setup, deployment, and troubleshooting
- `docs/planning/` — roadmap, launch, and planning notes
- `docs/testing/` — QA guides and manual validation notes

Keep `docs/README.md` as the documentation index.

When behavior, architecture, commands, environment variables, or user-facing workflows change, update the relevant docs in the same pass when feasible.

## Documentation Conventions

- `docs/vision/`, `docs/architecture/`, and `docs/architecture/current-design/` are living current-state docs.
- Put current implemented behavior under `docs/architecture/current-design/`; these docs should avoid user stories, rollout tasks, and workflow statuses.
- Use `docs/design/` for point-in-time specs and implementation plans that are still actionable.
- Use `docs/design/archive/` for shipped, superseded, abandoned, or historical records. Preserve historical context instead of rewriting archived specs as current-state docs.
- Use relative Markdown links inside repo docs; never use absolute filesystem paths.
- When behavior, architecture, commands, environment variables, or user-facing workflows change, update the relevant living docs and affected design-doc statuses in the same pass when feasible.
- When a design doc is replaced or archived, add a short banner linking readers to the current doc or replacement.
```

If the repo already has a different docs convention, preserve it and clarify the current source-of-truth instead of forcing this structure.

If docs exist or are initialized, include both `Documentation` and `Documentation Conventions` in `AGENTS.md`. Do not drop documentation conventions just because the project is new or the docs are sparse.

For projects with heavier design history, include the fuller lifecycle from `templates/AGENTS.md`, including design-doc statuses and archive/index rules.

### 8. Runtime and framework rules

Add a runtime/framework section only when the repo evidence shows a real trap. Keep it short.

Examples:

- React Native or Expo app code cannot use Node-only APIs.
- Expo packages should be installed with `expo install` when version compatibility matters.
- App router/navigation conventions are project-specific.
- Generated files should not be edited manually.
- Database migrations must be created through a specific script.
- Environment variables are loaded by a specific runtime or must be mirrored in a typed env file.

Use this shape:

```md
## Runtime Rules

- Use `<preferred API>` for `<task>`; do not use `<forbidden API>` in `<runtime>`.
- Use `<framework command>` when adding `<kind of dependency>`.
```

Omit this section if there are no clear project-specific runtime rules.

### 9. Source layout

Do not list the whole repository. Add source-layout guidance only for non-obvious boundaries that affect agent work.

Good:

- `services/` owns business logic; route handlers should stay thin.
- `packages/generated/` is generated and should not be edited.
- `apps/web/` and `apps/api/` have separate scripts and env files.

Avoid:

- `components/` contains components.
- `tests/` contains tests.
- `utils/` contains utilities.

### 10. Write docs indexes

When creating docs indexes, keep them lightweight and factual. Do not invent architecture. Use placeholder prompts only where the project is genuinely new.

`docs/README.md` should link to the main sections with one-line descriptions.

Subdirectory `README.md` files should explain what belongs there and link to existing docs, if any.

Use relative Markdown links.

### 11. Verification

After editing:

- Re-read `AGENTS.md` and check that every rule is project-specific.
- Confirm all links in new docs are relative and point to files/directories that exist.
- Run a lightweight file listing to verify the scaffold.
- Do not run full test/build commands unless the user asked or the edits touched executable code.

## Output

Finish with a concise summary:

- Files created or updated.
- Package manager and command assumptions.
- Any ambiguities the user should resolve.
- Whether tests/builds were skipped because the change was documentation-only.
