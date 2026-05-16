---
name: project-bootstrap
description: Initialize or update a repository so coding agents can work in it effectively. Use this skill whenever the user asks to bootstrap a new project, make a repo coding-agent friendly, create or update AGENTS.md, set project rules, add documentation conventions, initialize docs structure, or refresh package-manager/project-command guidance.
---

# Project Bootstrap

Use this skill to initialize or update lightweight project conventions for coding agents. The goal is not to teach agents generic software engineering. The goal is to capture the small set of project-specific facts that are easy to get wrong or expensive to rediscover.

This skill includes a reusable project-rules template at `templates/AGENTS.md`. The template is the standard baseline for this user's projects. Copy it first, then adapt repo-specific content. Do not rebuild `AGENTS.md` from memory.

## Core Principle

Keep `AGENTS.md` lean, but do not prune standard guardrails from the template.

Only include rules that are specific to this repository or stack. If a capable coding agent can infer a rule from the codebase in under a minute, omit it unless the rule prevents a common mistake.

The template's package-manager, documentation, documentation-conventions, testing-expectations, and safety sections are standard guardrails. Include them when initializing a project unless the user explicitly asks for a minimal file or a section truly cannot apply.

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
- `package.json` `packageManager`, workspaces, and monorepo package locations, if present.
- Existing framework config files such as `app.json`, `expo.json`, `next.config.*`, `vite.config.*`, `tsconfig.json`, `turbo.json`, or workspace files.
- Existing `.env.example` or documented environment setup.

Use this evidence to infer the minimum useful rules. Do not invent rules when the repo does not indicate them.

### 2. Choose the bootstrap path

Use this decision matrix before editing:

| Repository state | Action |
| --- | --- |
| `AGENTS.md` exists | Update mode. Use the existing file as the base, preserve project-specific rules, and patch in missing standard sections from `templates/AGENTS.md`. Do not wholesale rewrite unless the user asks. |
| No `AGENTS.md`, but code and package metadata exist | Initialize mode. Copy `templates/AGENTS.md`, then adapt it from repository evidence. Ask only about unresolved ambiguities. |
| Empty or barely scaffolded repository | Ask for the package manager, project purpose, app/service/library shape, and whether to initialize lightweight docs before writing files. |
| Multiple package-manager signals | Report the ambiguity and ask one focused question unless scripts/docs clearly identify the intended manager. |
| Existing docs use a different structure | Preserve the existing docs convention and document the actual source of truth. Do not force the default docs layout. |
| Monorepo or multi-app workspace | Capture root commands and package/app-specific commands separately only when agents need both. Do not flatten distinct package managers or runtime rules. |

### 3. Decide initialize vs update mode

Use initialize mode when no `AGENTS.md` exists. Copy `templates/AGENTS.md` as the starting point, then replace placeholders and adjust repo-specific content using repository evidence and user answers. Keep the standard package-manager, documentation, documentation-conventions, testing-expectations, and safety sections. Remove a standard section only when the user explicitly asks for a minimal file or the section truly cannot apply.

Use update mode when `AGENTS.md` already exists. Preserve project-specific rules. Add any missing standard sections from `templates/AGENTS.md`, especially package manager, documentation conventions, design-doc statuses, testing expectations, and safety. Refresh stale package-manager, command, and documentation sections when the repo clearly contradicts them. Do not remove existing rules unless they are obviously generic clutter or the user asks for cleanup.

Update mode merge rules:

- Treat the existing `AGENTS.md` as the base document.
- Patch in missing standard sections instead of replacing the whole file.
- Keep existing repo-specific safety, runtime, architecture, naming, deployment, and data-handling rules unless they are clearly stale.
- If an existing section conflicts with repository evidence, update the section and mention the evidence in the final response.
- If existing rules conflict with the template but the repository does not prove either rule correct, keep the existing rule and report the ambiguity.

### 4. Guided discovery for new projects

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

### 5. Apply the project-rules template

The template intentionally combines the best reusable pieces from mature project rule files:

- A short project overview with links to source-of-truth docs.
- Package-manager rules that prevent agents from mixing install tools.
- Canonical commands so agents run the project the same way maintainers do.
- Runtime/framework traps that are easy to violate.
- Non-obvious project patterns, especially boundaries for routing, services, state, navigation, data access, generated code, user isolation, and naming.
- Documentation structure and lifecycle rules that distinguish living current-state docs from point-in-time design records.
- Current source-of-truth paths for vision, architecture, current design, operations, and docs indexes.
- Focused testing expectations and safety constraints.

When adapting the copied template:

- Remove every placeholder that cannot be filled from repo evidence.
- Do not leave angle-bracket placeholders in the final file.
- Do not omit standard sections just because they are short. The default standard sections are `Package Manager`, `Documentation`, `Documentation Conventions`, `Testing Expectations`, and `Safety`.
- Omit optional sections that would only contain generic advice. Optional sections include `Runtime Rules`, `Project Patterns`, `Commands`, and `Current Source Of Truth` when there is no real content yet.
- Keep the standard documentation conventions, including design-doc statuses, unless the user explicitly asks for a minimal `AGENTS.md` without documentation lifecycle rules.
- Keep `Testing Expectations`; make the commands specific when known, or keep the generic template wording about relevant tests and documenting blockers.
- Keep `Safety`; use the template wording at minimum, and add repo-specific safety rules for credentials, cloud resources, databases, user data, destructive operations, or generated files when applicable.
- Keep examples concrete and runnable from the current repo layout.
- Prefer exact paths and commands over prose.
- Use relative Markdown links for documentation paths.

### 6. Standard sections

Use `templates/AGENTS.md` as the source of truth for standard section wording. Do not duplicate or retype those sections from memory.

Keep these standard sections in initialized projects unless the user explicitly asks for a minimal file or the section truly cannot apply:

- `Package Manager`
- `Documentation`
- `Documentation Conventions`, including `Design-doc statuses`
- `Testing Expectations`
- `Safety`

When updating an existing `AGENTS.md`, add missing standard sections from the template rather than recreating abbreviated versions.

### 7. Package manager rules

Detect the package manager from lockfiles and package-manager metadata. Prefer explicit metadata, then lockfiles, then documented commands:

| Signal | Package manager |
| --- | --- |
| `package.json` `packageManager: "bun@..."` or `bun.lock` | Bun |
| `package.json` `packageManager: "pnpm@..."` or `pnpm-lock.yaml` | pnpm |
| `package.json` `packageManager: "yarn@..."` or `yarn.lock` | Yarn |
| `package.json` `packageManager: "npm@..."` or `package-lock.json` | npm |
| `pyproject.toml` with Poetry config or `poetry.lock` | Poetry |

If multiple package-manager signals exist, report the ambiguity and prefer the one used by scripts/docs only when clear. If no package manager exists yet, ask which one to standardize on before writing `AGENTS.md`. Do not leave the package manager unspecified.

Adapt the template's package-manager section to the detected or chosen tool. It must tell agents which commands to use and which equivalent commands or lockfiles not to use.

Use concrete wording like:

```md
## Package Manager

Use Bun.

- `bun install` to install dependencies
- `bun run <script>` to run package scripts
- `bunx <tool>` to run one-off tools
- Do not use `npm install`, `yarn install`, or `pnpm install`
- Do not create or update `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`
```

Adapt the command names and forbidden lockfiles for pnpm, npm, Yarn, Poetry, or other package managers. For example, pnpm projects should prefer `pnpm install`, `pnpm run <script>`, and `pnpm dlx <tool>` and should not create `bun.lock`, `package-lock.json`, or `yarn.lock`.

Add stack-specific package rules when evidence supports them:

- Expo: use `expo install <package>` when Expo SDK compatibility matters.
- Bun: Bun automatically loads `.env`; do not add `dotenv` only to load local environment variables.
- Monorepo: run dependency changes from the workspace root unless package docs say otherwise.
- Python/Poetry: run commands from the directory that owns `pyproject.toml` and `poetry.lock`.

### 8. Canonical commands

Read package scripts and include only commands agents will commonly need:

- Dev/start server.
- Test.
- Typecheck.
- Lint.
- Build.
- Deploy only when the repo has a clear deploy script.

Prefer package scripts over underlying tools. If a test or typecheck must not be invoked directly, state that.

Omit missing commands instead of adding placeholders or instructions like "add commands here later." If the repo has not been scaffolded yet, either ask whether to scaffold first or omit the commands section until scripts exist.

### 9. Documentation structure

If the project has no docs structure and the user wants docs initialized, create this standard scaffold. Keep indexes lightweight and factual:

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

Create richer seed docs only when the user provides enough context:

```text
docs/vision/vision.md
docs/architecture/architecture.md
docs/architecture/tech-stack.md
```

For an empty project, do not invent architecture. It is acceptable for the indexes to say what belongs in each directory and point to seed docs that actually exist.

If the repo already has a different docs convention, preserve it and clarify the current source of truth instead of forcing the template's structure. Still include the standard documentation lifecycle rules unless the user explicitly opts out.

When docs exist or are initialized, include both `Documentation` and `Documentation Conventions` from the template. Do not drop the `Design-doc statuses` list just because the project is new or sparse.

### 10. Testing expectations

Always include the `Testing Expectations` section from `templates/AGENTS.md`. Make commands concrete when known; otherwise keep the generic template wording and do not invent commands.

### 11. Safety

Always include the `Safety` section from `templates/AGENTS.md`. Add repo-specific safety constraints when applicable, such as production account names, protected data stores, generated credential locations, or commands that mutate external services.

### 12. Runtime and framework rules

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

### 13. Source layout

Do not list the whole repository. Add source-layout guidance only for non-obvious boundaries that affect agent work.

Good:

- `services/` owns business logic; route handlers should stay thin.
- `packages/generated/` is generated and should not be edited.
- `apps/web/` and `apps/api/` have separate scripts and env files.

Avoid:

- `components/` contains components.
- `tests/` contains tests.
- `utils/` contains utilities.

### 14. Write docs indexes

When creating docs indexes, keep them lightweight and factual. Do not invent architecture. For genuinely new projects, describe what belongs in each docs area instead of leaving placeholder prompts.

`docs/README.md` should link to the main sections with one-line descriptions.

Subdirectory `README.md` files should explain what belongs there and link to existing docs, if any.

Use relative Markdown links.

### 15. Verification

After editing:

- Re-read `AGENTS.md` and check that every repo-specific addition is supported by repository evidence or user answers. Standard guardrail sections may remain even when generic.
- Confirm that standard package-manager rules, documentation conventions, design-doc statuses, testing expectations, and safety are present when those sections apply.
- Confirm that optional sections omitted from the template were intentionally omitted because they had no real content or the user asked for a minimal file.
- Confirm all links in new docs are relative and point to files/directories that exist.
- Run a lightweight file listing to verify the scaffold.
- Search for leftover placeholders with a command like `rg '<[^>]+>|add this later|TODO' AGENTS.md docs`, adjusting paths if docs were not created.
- Do not run full test/build commands unless the user asked or the edits touched executable code.

## Output

Finish with a concise summary:

- Files created or updated.
- Package manager and command assumptions.
- Any ambiguities the user should resolve.
- Whether tests/builds were skipped because the change was documentation-only.
