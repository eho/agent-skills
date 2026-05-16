---
name: project-bootstrap
description: Initialize or update a repository so coding agents can work in it effectively. Use this skill whenever the user asks to bootstrap a new project, make a repo coding-agent friendly, create or update AGENTS.md, set project rules, add documentation conventions, initialize docs structure, or refresh package-manager/project-command guidance.
---

# Project Bootstrap

Use this skill to initialize or update lightweight project conventions for coding agents. The goal is not to teach agents generic software engineering. The goal is to capture the small set of project-specific facts that are easy to get wrong or expensive to rediscover.

## Core Principle

Keep `AGENTS.md` lean.

Only include rules that are specific to this repository or stack. If a capable coding agent can infer a rule from the codebase in under a minute, omit it unless the rule prevents a common mistake.

Good `AGENTS.md` content:

- Package manager and lockfile policy.
- Canonical project commands.
- Documentation source-of-truth locations.
- Runtime constraints that are easy to violate.
- Framework-specific install or code-generation rules.
- Project-specific naming, product, or domain conventions.
- Tooling commands that must be run through package scripts.

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

Use initialize mode when no `AGENTS.md` exists. Create a concise file from the evidence.

Use update mode when `AGENTS.md` already exists. Preserve project-specific rules. Refresh stale package-manager, command, and documentation sections when the repo clearly contradicts them. Do not remove existing rules unless they are obviously generic clutter or the user asks for cleanup.

### 3. Package manager rules

Detect the package manager from lockfiles and package manager metadata:

- `bun.lock` means Bun.
- `pnpm-lock.yaml` means pnpm.
- `yarn.lock` means Yarn.
- `package-lock.json` means npm.
- If multiple lockfiles exist, report the ambiguity and prefer the lockfile used by scripts/docs only when clear.

For Bun projects, prefer this concise section:

```md
## Package Manager

Use Bun.

- `bun install` instead of `npm install`, `yarn install`, or `pnpm install`
- `bun run <script>` instead of `npm run <script>`
- `bunx <tool>` instead of `npx <tool>`
```

Adapt the commands for pnpm, npm, or Yarn projects.

### 4. Canonical commands

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

Omit missing commands instead of adding placeholders.

### 5. Documentation structure

If the project has no docs structure, create a minimal one:

```text
docs/README.md
docs/architecture/README.md
docs/architecture/current-design/README.md
docs/design/README.md
docs/design/archive/README.md
docs/planning/README.md
docs/testing/README.md
```

Use this lean `AGENTS.md` section:

```md
## Documentation

Project docs live under `docs/`.

- `docs/architecture/` — current system architecture and technical decisions
- `docs/architecture/current-design/` — how the implemented system works now
- `docs/design/` — active feature specs and implementation plans
- `docs/design/archive/` — implemented, superseded, or historical specs
- `docs/planning/` — roadmap, launch, and planning notes
- `docs/testing/` — QA guides and manual validation notes

Keep `docs/README.md` as the documentation index.

When behavior, architecture, commands, environment variables, or user-facing workflows change, update the relevant docs in the same pass when feasible.
```

If the repo already has a different docs convention, preserve it and clarify the current source-of-truth instead of forcing this structure.

### 6. Runtime and framework rules

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

### 7. Source layout

Do not list the whole repository. Add source-layout guidance only for non-obvious boundaries that affect agent work.

Good:

- `services/` owns business logic; route handlers should stay thin.
- `packages/generated/` is generated and should not be edited.
- `apps/web/` and `apps/api/` have separate scripts and env files.

Avoid:

- `components/` contains components.
- `tests/` contains tests.
- `utils/` contains utilities.

### 8. Write docs indexes

When creating docs indexes, keep them lightweight and factual. Do not invent architecture. Use placeholder prompts only where the project is genuinely new.

`docs/README.md` should link to the main sections with one-line descriptions.

Subdirectory `README.md` files should explain what belongs there and link to existing docs, if any.

Use relative Markdown links.

### 9. Verification

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

