---
name: expo-scaffold
description: Scaffold or set up a React Native Expo app or Expo-centered monorepo with Expo Router, Expo SDK 55 by default, expo-dev-client, NativeWind, gluestack-ui v3, starter gluestack components, EAS Build, and EAS Update. Use this skill whenever the user asks to create, bootstrap, initialize, scaffold, or configure an Expo React Native project that should include NativeWind, gluestack, EAS Build, OTA updates, preview/production channels, API routes/backend support, a landing site, or a reusable mobile app starter.
---

# Expo Gluestack Scaffold

Use this skill to build a production-oriented Expo starter. Default to Expo SDK 55 and an `expo-dev-client` development-build workflow unless the user explicitly requests a different SDK or workflow. The volatile parts are NativeWind compatibility, gluestack CLI behavior, Expo SDK transition notes, and EAS defaults, so verify current tool output and official docs before locking versions.

## Initial Decisions

Before editing files, infer these from the user request or ask only for missing choices that affect generated identifiers:

- App display name and app slug.
- Package manager: use the repo/user's existing manager when present; otherwise prefer `bun` if the user commonly uses it, then `npm`.
- Target platforms: default to iOS and Android.
- Router: default to Expo Router unless the user asks for a single-file app.
- Development runtime: always install and configure `expo-dev-client`; do not target Expo Go.
- Project shape: ask whether the user wants mobile-only, backend/API support, landing-site support, or both. Read `references/project-structure.md` before choosing directories.
- NativeWind version: prefer latest stable compatible NativeWind. If the latest compatible version appears to be preview, beta, canary, or unclear for the selected Expo SDK, ask the user before proceeding.
- EAS account metadata: configure local files; do not invent owner, project ID, bundle identifier, package name, ASC app ID, credentials, or secrets.

## Workflow

1. Read `references/project-structure.md` to choose single-app or monorepo layout.
2. Read `references/scaffold-workflow.md` for the end-to-end sequence.
3. Use Expo SDK 55 unless the user requests differently. Check official Expo docs or `create-expo-app` output for current SDK 55 template syntax. Do not use `next`, beta, or canary templates unless the user explicitly asks.
4. Read `references/nativewind.md` before installing or configuring NativeWind.
5. Read `references/gluestack.md` before running gluestack commands or adding components.
6. Read `references/eas.md` before creating `eas.json`, build scripts, update scripts, or app config update settings.
7. Use the snippets in `examples/` as starting points, then adapt to the actual project structure.
8. Finish by running the checks in `references/verification.md`.

## Implementation Standards

- Prefer CLI-generated project files over hand-written approximations when the official CLI supports the setup.
- Keep scaffolding idempotent where reasonable. If modifying an existing project, inspect current config before changing it.
- Scaffold into an empty temporary workspace when the target directory already contains repo files, then copy the finished scaffold into place without `.git` or accidental lockfiles.
- Do not overwrite user code blindly. Merge with existing `app.json` or `app.config.*`, `eas.json`, `babel.config.js`, `metro.config.js`, `tailwind.config.js`, and route files.
- Use `expo install` for Expo/RN packages where compatibility matters.
- Keep native prebuild output out of the starter unless the user asks for committed native directories. `expo run:ios` and `expo run:android` can generate native directories; include them as development-build convenience scripts only with a note about this behavior.
- Add scripts that make common workflows obvious: start, iOS, Android, web when supported, build profiles, and update channels.
- For EAS Update, explain that config changes, native dependency changes, and runtime version changes require a new build; OTA updates cover compatible JS and asset changes.

## Expected Deliverables

At completion, the project should contain:

- An Expo SDK 55 app by default, normally with Expo Router.
- `expo-dev-client` installed and the project configured for development builds, not Expo Go.
- A project structure matching the user's answer: mobile-only, mobile plus backend/API package, mobile plus landing site, or full monorepo.
- NativeWind configured through Babel, Metro, Tailwind config, `global.css`, and TypeScript declarations.
- gluestack-ui v3 initialized.
- A starter set of gluestack components installed.
- A placeholder screen using gluestack layout, typography, form, feedback, and action components.
- EAS Build profiles for development, preview, and production.
- EAS Update configured with preview and production channels.
- Verification results and any follow-up steps requiring the user's Expo account or app store credentials.

## Useful Official Docs

- Expo SDK: `https://expo.dev/sdk`
- Expo SDK reference: `https://docs.expo.dev/versions/latest/`
- EAS Build setup: `https://docs.expo.dev/build/setup/`
- EAS Update setup: `https://docs.expo.dev/eas-update/getting-started/`
- NativeWind install: `https://www.nativewind.dev/docs/getting-started/installation`
- gluestack-ui install: `https://gluestack.io/ui/docs/home/getting-started/installation`
