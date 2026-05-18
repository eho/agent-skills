---
name: expo-scaffold
description: Create, bootstrap, initialize, or scaffold a brand-new React Native Expo app or Expo-centered monorepo with Expo Router, Expo SDK 55 by default, expo-dev-client, NativeWind, official gluestack setup via expo-gluestack-setup, starter gluestack components, EAS Build, and EAS Update. Use this skill only when the user is starting a new project/starter/scaffold or explicitly asks to use expo-scaffold. Do not use it for general Expo questions, code review, debugging, verification, postmortems, or existing-project changes unless the user explicitly requests a new scaffold or directly names this skill. For existing Expo apps, use a narrower skill only when the user explicitly asks to configure, set up, install, repair, or verify that specific system.
---

# Expo Scaffold

Use this skill to build a production-oriented Expo starter. Default to Expo SDK 55 and an `expo-dev-client` development-build workflow unless current official Expo docs show a newer stable SDK should replace SDK 55, or the user explicitly requests a different SDK or workflow. The volatile parts are NativeWind compatibility, gluestack setup, Expo SDK transition notes, and EAS defaults, so verify current tool output and official docs before locking versions.

This skill is the orchestrator. Delegate gluestack-specific installation, provider/component copying, CLI/manual branching, and gluestack verification to the `expo-gluestack-setup` skill when it is available. Keep this skill responsible for project shape, scaffold ordering, final integration, and final verification.

## Trigger Boundaries

Use this skill only when the user asks to create or scaffold a new Expo project, starter, app, or Expo-centered monorepo, or when the user explicitly names `expo-scaffold`.

Do not use this skill for:

- General Expo, EAS, NativeWind, or gluestack questions.
- Reviewing a failed scaffold report or explaining an error.
- Debugging or repairing an existing app.
- Adding a single feature to an existing app.
- Verifying an existing app, unless the user explicitly asks to run `expo-scaffold`.

For an existing app, do not infer this skill from related keywords such as Expo Router, EAS, NativeWind, gluestack, OTA updates, preview channels, or landing site. Use normal codebase work or a narrower explicitly requested skill instead.

## Initial Decisions

Before editing files, infer these from the user request. Ask a short preflight decision block for any missing choices that create sticky identifiers or materially change the scaffold:

- App display name and app slug.
- iOS bundle identifier and Android package name, or explicit approval to leave native identifiers unset or as placeholders.
- Package manager: use the repo/user's existing manager when present; otherwise prefer `bun` if the user commonly uses it, then `npm`.
- Target platforms: default to iOS and Android.
- Router: default to Expo Router unless the user asks for a single-file app.
- Development runtime: always install and configure `expo-dev-client`; do not target Expo Go.
- Project shape: ask whether the user wants mobile-only, backend/API support, landing-site support, or both. Read `references/project-structure.md` before choosing directories.
- Landing framework: ask when a landing site is requested and SEO/marketing requirements are unclear; default to a separate React/Vite app for simple marketing pages and Next.js only when SSR/SEO/routing needs justify it.
- Theme mode: default to following the system light/dark appearance. For gluestack, prefer provider `mode="system"` plus CSS-variable tokens over repeated `dark:` class pairs when the selected gluestack version supports that strategy.
- Launch experience: default to a static native splash screen; offer an optional React/Reanimated launch overlay when the user wants an animated splash.
- NativeWind version: prefer latest stable compatible NativeWind. If the latest compatible version appears to be preview, beta, canary, or unclear for the selected Expo SDK, ask the user before proceeding.
- EAS account metadata: configure local files; do not invent owner, project ID, bundle identifier, package name, ASC app ID, credentials, or secrets.
- Agent context: when `create-expo-app` generates Expo-specific agent files, merge the useful Expo context into the existing `AGENTS.md` created by `project-bootstrap` instead of replacing it.

## Workflow

1. Read `references/project-structure.md` to choose single-app or monorepo layout.
2. Read `references/scaffold-workflow.md` for the end-to-end sequence.
3. Use Expo SDK 55 unless official Expo docs now identify a newer stable default or the user requests differently. Check official Expo docs or `create-expo-app` output for the selected SDK's template syntax. Do not use `next`, beta, alpha, canary, or preview templates unless the user explicitly asks.
4. Read `references/package-installation.md` before installing dependencies or repairing missing-module errors.
5. Read `references/nativewind.md` before installing or configuring NativeWind.
6. Invoke or follow `expo-gluestack-setup` before installing gluestack packages, copying official provider/components, or running any gluestack CLI command. Pass the app root, package manager, Expo SDK, NativeWind status, route layout, UI component path, and requested gluestack major. Require the `## Gluestack Handoff` before wiring final starter screens.
7. Read `references/theme.md` before adding theme tokens, provider mode, status bar behavior, or light/dark styling.
8. Read `references/launch-experience.md` before configuring `expo-splash-screen` or adding an animated launch overlay.
9. Read `references/eas.md` before creating `eas.json`, build scripts, update scripts, or app config update settings.
10. Use the snippets in `examples/` as starting points for the standard starter files, then adapt to the actual project structure and selected package manager.
11. Finish by running the checks in `references/verification.md`.

## Implementation Standards

- Treat gluestack setup as a hard gate for the default scaffold. If the gluestack handoff outcome is `interactive_cli_required` or `blocked`, stop before claiming the scaffold is complete. Continue with a non-official fallback only when the user explicitly approves and the handoff says `fallback_approved`.
- Do not duplicate gluestack version-specific setup rules here. For gluestack v3, the specialist skill owns package metadata resolution, manual source copying, CLI timeout handling, provider/component verification, and exact outcome labels. For future gluestack majors, update `expo-gluestack-setup` first and keep this orchestrator consuming the same handoff contract.
- Keep scaffolding idempotent where reasonable. If modifying an existing project, inspect current config before changing it.
- Scaffold into an empty temporary workspace when the target directory already contains repo files, then copy the finished scaffold into place without `.git` or accidental lockfiles.
- Do not overwrite user code blindly. Merge with existing `app.json` or `app.config.*`, `eas.json`, `babel.config.js`, `metro.config.js`, `tailwind.config.js`, and route files.
- Follow `references/package-installation.md`: use `expo install` for Expo/RN packages where compatibility matters, use the selected package manager for ordinary JS/tooling packages, and do not manually list transitive dependencies unless there is a documented peer/direct requirement or a verified undeclared runtime import workaround.
- In Bun workspaces, expect a root lockfile plus possible workspace-local `node_modules` link folders. Do not remove package-local link folders just because a root `bun.lock` exists; remove only generated dependency trees/caches that are explicitly excluded by the cleanup rules.
- Keep native prebuild output out of the starter unless the user asks for committed native directories. `expo run:ios` and `expo run:android` can generate native directories; include them as development-build convenience scripts only with a note about this behavior.
- Add scripts that make common workflows obvious: start, iOS, Android, web when supported, build profiles, and update channels.
- Keep `AGENTS.md` as the repository's project-rules source of truth. If Expo's scaffold generates `AGENTS.md`, `CLAUDE.md`, or `.claude/settings.json`, treat them as input material: extract Expo-specific SDK docs, commands, package-manager notes, and runtime constraints into the existing `AGENTS.md`, then remove duplicate generated agent files unless the user explicitly wants them kept.
- For EAS Update, explain that config changes, native dependency changes, and runtime version changes require a new build; OTA updates cover compatible JS and asset changes.
- End every scaffold with post-scaffold operations that remain outside local file generation, especially EAS login/init/update configuration, first development build/install, credentials, secrets, store submission, backend/landing deployment, and native rebuild triggers.
- When the runtime policy and user request permit subagents, use them for parallel research or post-scaffold review, not for concurrent edits to the same package manifest, app config, route files, or styling setup. Keep the main agent responsible for the ordered scaffold sequence and final integration. If a permitted subagent runs `expo-gluestack-setup`, give it ownership of gluestack files only and integrate its handoff in the main scaffold sequence.

## Expected Deliverables

At completion, the project should contain:

- An Expo SDK 55 app by default, normally with Expo Router.
- `expo-dev-client` installed and the project configured for development builds, not Expo Go.
- A project structure matching the user's answer: mobile-only, mobile plus backend/API package, mobile plus landing site, or full monorepo.
- NativeWind configured through Babel, Metro, Tailwind config, `global.css`, and TypeScript declarations.
- Standard starter config files adapted from `examples/`: app config, Babel, Metro, Tailwind, TypeScript, `.gitignore`, package scripts, and monorepo package configuration when relevant.
- Official gluestack setup completed by `expo-gluestack-setup`, with an accepted handoff outcome and verified provider/components.
- Light/dark appearance following the system by default through gluestack provider mode and tokenized theme colors.
- Native splash screen configured with the `expo-splash-screen` config plugin, including dark-mode colors/assets where available.
- Optional animated launch overlay when requested, implemented as React UI after the static native splash.
- A starter set of official gluestack components confirmed by the gluestack handoff.
- A placeholder screen using only gluestack components that the gluestack handoff confirms exist in the selected UI path.
- Package manifests containing direct runtime/tooling dependencies in the owning package, with any known undeclared runtime import workaround documented and verified.
- EAS Build profiles for development, preview, and production.
- EAS Update prepared with preview and production channels locally; account-backed update URLs and project IDs are added only after authenticated EAS initialization.
- Updated existing living docs when the scaffold creates or changes project architecture, especially `docs/architecture/architecture.md`, `docs/architecture/tech-stack.md`, and relevant operational docs. If the repo has no docs convention, create lightweight seed docs only when that fits the project or report that no architecture docs were present.
- Existing `AGENTS.md` updated with merged Expo-generated agent context, when `create-expo-app` produced it.
- Verification results and any follow-up steps requiring the user's Expo account or app store credentials.
- A `Post-scaffold operations` section with exact commands and required/optional/conditional account, device, credential, deployment, and update steps that still need user action.

## Useful Official Docs

- Expo SDK: `https://expo.dev/sdk`
- Expo SDK reference: `https://docs.expo.dev/versions/latest/`
- EAS Build setup: `https://docs.expo.dev/build/setup/`
- EAS Update setup: `https://docs.expo.dev/eas-update/getting-started/`
- Expo splash screen: `https://docs.expo.dev/versions/latest/sdk/splash-screen/`
- NativeWind install: `https://www.nativewind.dev/docs/getting-started/installation`
- gluestack-ui install: `https://gluestack.io/ui/docs/home/getting-started/installation`
- gluestack-ui dark mode: `https://gluestack.io/ui/docs/home/theme-configuration/dark-mode`
