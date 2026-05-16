---
description: <project-name> project conventions
alwaysApply: true
---

# Project Rules

## Project Overview

<One or two sentences describing what this project is, the primary runtime, and the main product or system areas. Link to source-of-truth docs when they exist.>

## Package Manager

Use <Bun | pnpm | npm | Yarn | Poetry | other>.

- `<install command>` to install dependencies
- `<script command pattern>` to run package scripts
- `<tool command pattern>` to run one-off tools

<Add only real constraints, for example: Bun automatically loads `.env`; use `expo install` for Expo-compatible package versions; use Poetry from the repository root.>

## Commands

Use these commands from the repository root unless noted otherwise.

- Dev: `<command>`
- Test: `<command>`
- Typecheck: `<command>`
- Lint: `<command>`
- Build: `<command>`

Prefer these scripts over invoking underlying tools directly unless there is a specific reason.

## Runtime Rules

- <Runtime constraint that is easy to violate, such as using `expo-file-system` instead of `node:fs` in React Native app code.>
- <Framework-specific install, code generation, migration, or environment-variable rule.>

## Project Patterns

- <Non-obvious source boundary or architectural pattern, such as "route handlers stay thin; services own business logic".>
- <Project-specific state, navigation, data-access, or dependency-injection convention.>
- <Product, domain, naming, or tenant/user-isolation rule that agents must preserve.>

## Documentation

Project docs live under `docs/`.

- `docs/vision/` - strategic vision, product goals, and project direction
- `docs/architecture/` - current system architecture, data contracts, and technical decisions
- `docs/architecture/current-design/` - how the implemented system works now
- `docs/design/` - active feature specs and implementation plans
- `docs/design/archive/` - implemented, superseded, abandoned, or historical specs
- `docs/planning/` - roadmap, assessments, milestones, migrations, and ongoing planning notes
- `docs/testing/` - QA guides, testing strategy, manual validation, and verification checklists
- `docs/operational/` - runbooks, local setup, deployment, CLI usage, and troubleshooting

Keep `docs/README.md` as the documentation index. If the project uses design specs heavily, also keep `docs/design/README.md` as the active design index and `docs/design/archive/README.md` as the historical design index.

## Documentation Conventions

- `docs/vision/`, `docs/architecture/`, and `docs/architecture/current-design/` are living current-state docs.
- Put current implemented behavior under `docs/architecture/current-design/`; these docs should avoid user stories, rollout tasks, and workflow statuses.
- Use `docs/design/` for point-in-time specs and implementation plans that are still actionable.
- Use `docs/design/archive/` for shipped, superseded, abandoned, or historical records. Preserve historical context instead of rewriting archived specs as current-state docs.
- Use relative Markdown links inside repo docs; never use absolute filesystem paths.
- When behavior, architecture, commands, environment variables, or user-facing workflows change, update the relevant living docs and affected design-doc statuses in the same pass when feasible.
- When a design doc is replaced or archived, add a short banner linking readers to the current doc or replacement.

Design-doc statuses:

- `Draft` - new or in-progress proposal
- `Active` - approved current implementation plan
- `Revised` - updated proposal or plan that remains actionable
- `Implemented` - shipped and still useful as a recent implementation reference
- `Implemented (Historical)` - shipped and now mainly historical
- `Superseded` - replaced by a newer design
- `Abandoned` - explicitly not moving forward

## Current Source Of Truth

Include only entries that exist in this repository. Omit this section until source-of-truth docs exist.

- Product vision: `docs/vision/vision.md`
- System architecture: `docs/architecture/architecture.md`
- Tech stack and tooling: `docs/architecture/tech-stack.md`
- Current implemented design: `docs/architecture/current-design/`
- Operational runbooks: `docs/operational/`
- Documentation index: `docs/README.md`

## Testing Expectations

- Run `<test command>` for relevant code changes.
- Run `<build/typecheck command>` when touching shared types, build config, or release-sensitive code.
- If tests cannot run locally because of credentials, services, or device dependencies, document that in the final response.

## Safety

- Do not commit secrets, generated credentials, API keys, tokens, or personal data.
- Do not make destructive cloud, database, filesystem, or git operations unless explicitly requested.
- Do not overwrite user changes.
