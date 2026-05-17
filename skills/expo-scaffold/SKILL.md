---
name: expo-scaffold
description: Create, bootstrap, initialize, or broadly scaffold a new React Native Expo app or Expo-centered monorepo with Expo Router, Expo SDK 55 by default, expo-dev-client, NativeWind, official gluestack setup via expo-gluestack-setup, starter gluestack components, EAS Build, and EAS Update. Use this skill whenever the user asks to create a new Expo starter, reusable mobile app starter, or broad Expo project setup that should include NativeWind, gluestack, EAS Build, OTA updates, preview/production channels, API routes/backend support, or a landing site. For existing Expo apps where the requested change is only to add, repair, configure, or verify gluestack, use `expo-gluestack-setup` instead.
---

# Expo Scaffold

Use this skill to build a production-oriented Expo starter. Default to Expo SDK 55 and an `expo-dev-client` development-build workflow unless the user explicitly requests a different SDK or workflow. The volatile parts are NativeWind compatibility, gluestack setup, Expo SDK transition notes, and EAS defaults, so verify current tool output and official docs before locking versions.

This skill is the orchestrator. Delegate gluestack-specific installation, provider/component copying, CLI/manual branching, and gluestack verification to the `expo-gluestack-setup` skill when it is available. Keep this skill responsible for project shape, scaffold ordering, final integration, and final verification.

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
3. Use Expo SDK 55 unless the user requests differently. Check official Expo docs or `create-expo-app` output for current SDK 55 template syntax. Do not use `next`, beta, or canary templates unless the user explicitly asks.
4. Read `references/nativewind.md` before installing or configuring NativeWind.
5. Invoke or follow `expo-gluestack-setup` before installing gluestack packages, copying official provider/components, or running any gluestack CLI command. Pass the app root, package manager, Expo SDK, NativeWind status, route layout, UI component path, and requested gluestack major. Require the `## Gluestack Handoff` before wiring final starter screens.
6. Read `references/theme.md` before adding theme tokens, provider mode, status bar behavior, or light/dark styling.
7. Read `references/launch-experience.md` before configuring `expo-splash-screen` or adding an animated launch overlay.
8. Read `references/eas.md` before creating `eas.json`, build scripts, update scripts, or app config update settings.
9. Use the snippets in `examples/` as starting points, then adapt to the actual project structure.
10. Finish by running the checks in `references/verification.md`.

## Implementation Standards

- Treat gluestack setup as a hard gate for the default scaffold. If the gluestack handoff outcome is `interactive_cli_required` or `blocked`, stop before claiming the scaffold is complete. Continue with a non-official fallback only when the user explicitly approves and the handoff says `fallback_approved`.
- Do not duplicate gluestack version-specific setup rules here. For gluestack v3, the specialist skill owns package metadata resolution, manual source copying, CLI timeout handling, provider/component verification, and exact outcome labels. For future gluestack majors, update `expo-gluestack-setup` first and keep this orchestrator consuming the same handoff contract.
- Keep scaffolding idempotent where reasonable. If modifying an existing project, inspect current config before changing it.
- Scaffold into an empty temporary workspace when the target directory already contains repo files, then copy the finished scaffold into place without `.git` or accidental lockfiles.
- Do not overwrite user code blindly. Merge with existing `app.json` or `app.config.*`, `eas.json`, `babel.config.js`, `metro.config.js`, `tailwind.config.js`, and route files.
- Use `expo install` for Expo/RN packages where compatibility matters.
- In Bun workspaces, expect a root lockfile plus possible workspace-local `node_modules` link folders. Do not remove package-local link folders just because a root `bun.lock` exists; remove only generated dependency trees/caches that are explicitly excluded by the cleanup rules.
- Keep native prebuild output out of the starter unless the user asks for committed native directories. `expo run:ios` and `expo run:android` can generate native directories; include them as development-build convenience scripts only with a note about this behavior.
- Add scripts that make common workflows obvious: start, iOS, Android, web when supported, build profiles, and update channels.
- Keep `AGENTS.md` as the repository's project-rules source of truth. If Expo's scaffold generates `AGENTS.md`, `CLAUDE.md`, or `.claude/settings.json`, treat them as input material: extract Expo-specific SDK docs, commands, package-manager notes, and runtime constraints into the existing `AGENTS.md`, then remove duplicate generated agent files unless the user explicitly wants them kept.
- For EAS Update, explain that config changes, native dependency changes, and runtime version changes require a new build; OTA updates cover compatible JS and asset changes.
- When subagents are available, use them for parallel research or post-scaffold review, not for concurrent edits to the same package manifest, app config, route files, or styling setup. Keep the main agent responsible for the ordered scaffold sequence and final integration. If a subagent runs `expo-gluestack-setup`, give it ownership of gluestack files only and integrate its handoff in the main scaffold sequence.

## Expected Deliverables

At completion, the project should contain:

- An Expo SDK 55 app by default, normally with Expo Router.
- `expo-dev-client` installed and the project configured for development builds, not Expo Go.
- A project structure matching the user's answer: mobile-only, mobile plus backend/API package, mobile plus landing site, or full monorepo.
- NativeWind configured through Babel, Metro, Tailwind config, `global.css`, and TypeScript declarations.
- Official gluestack setup completed by `expo-gluestack-setup`, with an accepted handoff outcome and verified provider/components.
- Light/dark appearance following the system by default through gluestack provider mode and tokenized theme colors.
- Native splash screen configured with the `expo-splash-screen` config plugin, including dark-mode colors/assets where available.
- Optional animated launch overlay when requested, implemented as React UI after the static native splash.
- A starter set of official gluestack components confirmed by the gluestack handoff.
- A placeholder screen using only gluestack components that the gluestack handoff confirms exist in the selected UI path.
- EAS Build profiles for development, preview, and production.
- EAS Update prepared with preview and production channels locally; account-backed update URLs and project IDs are added only after authenticated EAS initialization.
- Updated existing living docs when the scaffold creates or changes project architecture, especially `docs/architecture/architecture.md`, `docs/architecture/tech-stack.md`, and relevant operational docs. If the repo has no docs convention, create lightweight seed docs only when that fits the project or report that no architecture docs were present.
- Existing `AGENTS.md` updated with merged Expo-generated agent context, when `create-expo-app` produced it.
- Verification results and any follow-up steps requiring the user's Expo account or app store credentials.

## Useful Official Docs

- Expo SDK: `https://expo.dev/sdk`
- Expo SDK reference: `https://docs.expo.dev/versions/latest/`
- EAS Build setup: `https://docs.expo.dev/build/setup/`
- EAS Update setup: `https://docs.expo.dev/eas-update/getting-started/`
- Expo splash screen: `https://docs.expo.dev/versions/latest/sdk/splash-screen/`
- NativeWind install: `https://www.nativewind.dev/docs/getting-started/installation`
- gluestack-ui install: `https://gluestack.io/ui/docs/home/getting-started/installation`
- gluestack-ui dark mode: `https://gluestack.io/ui/docs/home/theme-configuration/dark-mode`
