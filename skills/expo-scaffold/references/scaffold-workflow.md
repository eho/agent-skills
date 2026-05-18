# Scaffold Workflow

Follow this sequence for a new project. For an existing project, start at step 2 and merge changes instead of replacing files.

## Subagent Use

When the runtime policy and user request permit subagents, use them only where parallelism reduces risk:

- Ask one subagent to check current official Expo, NativeWind, gluestack, or EAS docs and report exact commands or version constraints.
- Ask one subagent to inspect the generated project shape after `create-expo-app` and summarize routes, config files, package versions, and template artifacts.
- Ask one subagent to review the completed scaffold or verification output.

Keep package installation, app config edits, route edits, and final integration in the main agent's control. Do not let multiple agents edit the same scaffold files concurrently. If a subagent runs `expo-gluestack-setup`, give it a bounded ownership set for gluestack files only and require its `## Gluestack Handoff` before the main agent wires final screens or reports success.

## 1. Choose And Prepare The Workspace

Read `project-structure.md` first. If the target directory is not empty, do not run `create-expo-app` directly in it. `create-expo-app .` refuses directories containing files such as `.agents`, `AGENTS.md`, `skills-lock.json`, existing lockfiles, or app code.

Before any scaffold command, resolve sticky naming inputs:

- Display name.
- Slug.
- iOS bundle identifier and Android package name, or explicit approval to leave them unset or as placeholders.
- Mobile-only, mobile plus backend/API, mobile plus landing, or full monorepo shape.
- Landing framework preference when a landing site is requested and SEO/SSR requirements are unclear.

Ask for these in one concise preflight block when they are not present in the user request. Do not silently invent native identifiers because they are painful to change later.

Recommended flow for non-empty targets:

1. Scaffold into `/private/tmp/<slug>-expo-scaffold`.
2. Complete package installation and official gluestack setup there.
3. Copy the generated files into the target location or into `apps/mobile` for a monorepo.
4. Prefer copying source and configuration files only, then run the chosen package manager install in the final target.
5. Exclude `.git`, `node_modules`, `.expo`, `.expo-shared`, generated native folders unless requested, `ios/Pods`, `dist`, `build`, `.turbo`, package-manager caches, and lockfiles from package managers the project is not using.
6. Do not blindly copy generated agent files over an existing `AGENTS.md`. Keep generated `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json` in the temporary scaffold until the agent-context merge step below, then copy only the final intended agent files.

For a monorepo, create the root workspace first, then scaffold the Expo app into `apps/mobile`. After copying from a temporary scaffold, run the selected package manager install from the final workspace root. With Bun, allow that install to recreate package-local `node_modules` link folders inside apps/packages if local scripts need them.

## 2. Create The Expo App

Use Expo SDK 55 unless official Expo docs now identify a newer stable default or the user asks for a different SDK. Verify the current official template syntax for the selected SDK first, then create the project with the pinned stable template:

```sh
npx create-expo-app@latest <app-slug> --template default@sdk-55
```

Prefer the default TypeScript + Expo Router template unless the user asks for a different template. Expo SDK 55 defaults to a `src/app` Expo Router layout; keep that structure unless the selected template generates root-level `app/` or the user asks for it. Avoid templates that include `@next`, canary, beta, or preview SDKs.

If official Expo docs show that latest stable has moved past SDK 55, pause before using the older default unless the user explicitly requested SDK 55. Report the newer stable SDK, the template syntax, and any material migration implications for NativeWind, gluestack, EAS, or route layout.

If the user requests a different stable SDK, use the SDK-pinned stable template syntax when available:

```sh
npx create-expo-app@latest <app-slug> --template default@sdk-<stable>
```

Use that only for stable SDK identifiers from official Expo docs.

After creation:

- Confirm `expo`, `react`, `react-native`, and `expo-router` versions are stable.
- Inspect generated agent files such as `AGENTS.md`, `CLAUDE.md`, and `.claude/settings.json`; current `create-expo-app` templates may create them by default.
- Run the package manager install if the CLI did not do so.
- Install `expo-dev-client` before adding development-build scripts:

```sh
npx expo install expo-dev-client
```

- If the package manager should be Bun, normalize scripts to work with `bun run` but keep commands portable inside scripts.
- After any third-party CLI runs, delete accidental lockfiles from other package managers such as `package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml` when Bun is the chosen package manager.

## 2a. Normalize The Generated Template

SDK 55's default template may generate starter UI, nested routes, and web-specific CSS module files. Normalize the template before adding scaffold-specific UI:

- Confirm whether Expo Router is rooted at `src/app` or `app`; keep the generated root unless the user asked for a different shape.
- Replace the default welcome route with the scaffold placeholder route intentionally.
- Keep or remove generated demo components intentionally instead of leaving unused template code.
- For a minimal starter, remove unreferenced demo routes such as `src/app/(tabs)/`, sample modal/explore routes, and route-specific demo CSS modules after replacing the starter route.
- Remove unreferenced template components such as `HelloWave`, `ParallaxScrollView`, `ThemedText`, `ThemedView`, `Collapsible`, `ExternalLink`, demo haptic tab helpers, demo icon wrappers, and demo-only constants such as `Colors`.
- Remove React-logo/sample image assets such as `react-logo*.png` after confirming no route, component, or config imports them. Keep real app icon, splash, adaptive icon, favicon, and any files referenced by `app.json`, `app.config.*`, route files, or imports.
- If generated `.module.css` imports remain, add a TypeScript declaration such as `src/types/css.d.ts`:

```ts
declare module "*.module.css" {
  const classes: { readonly [key: string]: string };
  export default classes;
}
```

- Verify generated web/CSS files are either still referenced and typed or removed with their imports.

## 2b. Merge Expo Agent Context

If `create-expo-app` generated `AGENTS.md`, `CLAUDE.md`, or `.claude/settings.json`, merge the useful Expo-specific context into the repository's existing `AGENTS.md` rather than replacing project-bootstrap content.

Use this process:

1. Read the existing target `AGENTS.md`, if present. Treat it as the base document because `project-bootstrap` owns the repository rules and docs conventions.
2. Read Expo's generated agent files from the temporary scaffold or generated app root.
3. Extract only durable Expo-specific guidance, such as:
   - Versioned Expo docs or SDK reference paths generated for the selected SDK.
   - Canonical Expo commands that match the selected package manager.
   - `expo install` guidance for SDK-compatible packages.
   - Expo Router route root and file-based routing conventions.
   - Continuous Native Generation notes: native `ios/` and `android/` directories are generated on demand and should not be committed unless requested.
   - Development-build workflow notes for `expo-dev-client`, especially that this scaffold does not target Expo Go.
   - EAS Build/Update boundaries already configured by this scaffold.
4. Preserve existing project-bootstrap sections for package manager, docs conventions, testing expectations, safety, and current source-of-truth docs.
5. Add a concise Expo-specific section or merge bullets into existing runtime/commands sections. Do not paste the entire generated file if it duplicates existing rules or conflicts with this scaffold.
6. If there is no existing `AGENTS.md`, keep the generated Expo `AGENTS.md` only after removing template clutter, or run/use the `project-bootstrap` skill first when available and merge the Expo context into that output.
7. Remove generated `CLAUDE.md` and `.claude/settings.json` from the final scaffold unless the user explicitly wants Claude-specific files. If kept, make sure they do not contradict `AGENTS.md`.

The final report should state whether Expo-generated agent context was merged, skipped because no generated agent files were present, or left for follow-up because the repository had no agent-rules convention.

## 3. Add Baseline App Metadata

Update `app.json` or `app.config.*` conservatively:

- `name`: display name from the user.
- `slug`: URL/package-safe slug.
- `scheme`: lower-case slug by default.
- `userInterfaceStyle`: `automatic`.
- `orientation`: `portrait` unless the user requests otherwise.
- `ios.bundleIdentifier` and `android.package`: use the user-provided values, or leave unset/placeholders only after explicit approval.
- `plugins`: include `expo-splash-screen` with config-plugin options when splash assets are available or placeholders are acceptable.

Do not invent an Expo `owner`, EAS `projectId`, app store IDs, or credentials.

Use `examples/app.json` as the standard local-only baseline when creating a new JSON app config. If modifying an existing config, merge the same fields without replacing unrelated settings.

## 4. Configure NativeWind

Read `nativewind.md`, install the selected NativeWind line, and configure:

- `src/global.css` for SDK 55-style projects, or `global.css` for root-layout projects
- `tailwind.config.js`
- `babel.config.js`
- `metro.config.js`
- `nativewind-env.d.ts`
- global CSS import in the app root layout or entry file
- `app.json` or `app.config.*` web bundler settings when required by the selected NativeWind version

Use `examples/babel.config.js`, `examples/metro.config.js`, `examples/tailwind.config.js`, and `examples/tsconfig.json` as canonical starting points for a fresh SDK 55-style starter. Adapt paths and preserve existing settings when merging.

Before calling NativeWind configured or invoking gluestack, run a file-level preflight:

- `global.css` exists at the path used by Metro and contains all three directives: `@tailwind base;`, `@tailwind components;`, and `@tailwind utilities;`.
- `metro.config.js` uses `withNativeWind(config, { input: "./src/global.css" })` for SDK 55 `src` layouts, or the equivalent path for the actual app.
- `tailwind.config.js` has explicit static `darkMode: "class"` when gluestack will use `GluestackUIProvider mode="system"`.
- `darkMode` is not env-driven, including `process.env.DARK_MODE`, and cannot resolve to `"media"` under a different shell environment.
- If the root layout or entry file already exists, it imports the same global CSS file. If provider wiring happens later, verify at final wiring that this import appears before rendering the provider.

Treat a failed preflight as an incomplete scaffold, not as a follow-up note. Repair it before gluestack setup continues.

## 5. Bootstrap gluestack

Use the `expo-gluestack-setup` skill for gluestack-specific installation and verification. Pass a concise orchestration brief:

- App root.
- Package manager.
- Expo SDK and React Native versions.
- NativeWind status and global CSS path.
- Route layout, normally `src/app` for SDK 55.
- Desired UI component path, normally `src/components/ui` for SDK 55 `src` layouts.
- Requested gluestack major, or permission to use the current stable compatible major.
- Whether CLI-managed components were explicitly requested.
- Whether layout wiring or route/screen edits are allowed. Default to no; this scaffold normally owns final route and root-layout edits.

Require this handoff before continuing:

```markdown
## Gluestack Handoff
- Outcome:
- Mode: standalone | orchestrated
- Version:
- Package versions:
- Docs/source ref:
- Package manager:
- App root:
- NativeWind prerequisite:
- NativeWind preflight:
- Global CSS path:
- Route root:
- UI component path:
- Provider file path:
- Provider import:
- Provider mode:
- Components installed/copied:
- Official source paths:
- Component exports:
- CLI component management:
- Theme/token status:
- Layout wiring touched:
- Route/screen files touched:
- Commands run:
- Files changed:
- Verification:
- Follow-up:
```

If the outcome is `manual_installed` or `cli_initialized`, continue with official provider/components and do not run additional gluestack CLI commands unless the handoff says CLI component management is verified.

If orchestrated mode was used and the handoff says layout or route/screen files were touched without explicit permission, inspect those edits before continuing and reconcile them in the main scaffold integration step.

If the outcome is `interactive_cli_required`, pause the default scaffold workflow and ask the user to run the exact command from the handoff. Resume only after the user reports completion, then inspect the generated provider/config files before continuing.

If the outcome is `blocked`, stop the default scaffold workflow and report diagnostics. Do not continue with theme wiring, placeholder screens, or final success language that implies official gluestack support. Continue only if the user explicitly approves a non-official fallback and the handoff outcome becomes `fallback_approved`.

After gluestack setup, check and repair config paths using the handoff as source of truth:

- Metro NativeWind input must point at the real CSS file, such as `./src/global.css` when the app uses `src`.
- The Metro input CSS file must contain the Tailwind base/components/utilities directives.
- Tailwind dark mode must be the static string `"class"` for gluestack provider mode `"system"`; remove env-driven `darkMode` expressions.
- Any configured aliases must resolve source code and assets in the actual runtime, not only in TypeScript.
- Tailwind content globs must include the actual app, src, and component directories.
- Root layout must have one CSS import and one official provider wrapper using the provider import from the handoff.

## 6. Configure Theme And Launch Experience

Read `theme.md` and `launch-experience.md`.

For theme:

- Default the generated gluestack provider usage to `mode="system"` when the selected provider supports it.
- Use gluestack token classes such as `bg-background-0`, `text-typography-900`, and `border-outline-200` in starter screens.
- Keep generated `dark:` classes rare and intentional; do not use them for every normal surface.
- Add a tiny runtime theme helper only when JS-only values are needed, such as status bar style or animated launch overlay colors.

For splash and launch:

- Configure native splash through the `expo-splash-screen` config plugin.
- Call `SplashScreen.preventAutoHideAsync()` in module scope only when the app waits on local readiness work.
- Hide the native splash as soon as the first app frame is ready.
- Add an animated launch overlay only when requested or when the scaffold option includes it.

## 7. Add Placeholder Screen

Create or replace only the starter route/screen that belongs to the scaffold. Prefer `src/app/index.tsx` for SDK 55 Expo Router projects, or `app/index.tsx` when the selected template uses a root-level app directory. Use `examples/placeholder-screen.tsx` as the base and adjust imports to match the component paths confirmed in the gluestack handoff. Do not import components that the handoff did not verify.

## 8. Add Root Layout

For Expo Router, wire `src/app/_layout.tsx` after NativeWind and gluestack are set up. If the template uses root-level routes, wire `app/_layout.tsx` with equivalent imports:

- Import the actual global CSS file exactly once, normally `../global.css` from `src/app/_layout.tsx`.
- Wrap the `Stack` with the official `GluestackUIProvider`, using the provider import from the gluestack handoff.
- Pass `mode="system"` unless the user asked for an explicit or persisted theme setting, or the selected provider version uses a different official API.
- Add `StatusBar` with `style="auto"` or the runtime helper style.
- For a static splash only, adapt `examples/root-layout-static.tsx`.
- If animated launch was selected, adapt `examples/root-layout-with-splash.tsx` and `examples/app-launch-overlay.tsx`.
- If using `@/*` aliases in generated code, verify TypeScript, Babel, and Metro all resolve them. Otherwise prefer relative imports in root layout examples.

## 9. Configure EAS

Read `eas.md`, then run official EAS configuration commands where possible. Add scripts and profiles after the CLI has written baseline config. The development profile should produce an `expo-dev-client` build.

For SDK 55 and later, EAS Update publish scripts must include an explicit `--environment` value that matches the target channel unless current EAS docs say otherwise.

## 9a. Configure Expo API Routes When Requested

If the user explicitly wants Expo API routes, configure them inside the Expo Router app rather than only creating a separate backend package:

- Add route handlers under the app route root, such as `src/app/api/health+api.ts` for SDK 55 `src/app` projects.
- Configure the Expo Router/server output required by the current Expo docs for API routes and web/server deployment.
- Add any required server runtime package, output mode, deployment notes, environment variables, and EAS deployment limitations from the current official docs.
- Keep backend-only code out of the mobile bundle unless the API route runtime requires it.
- In a monorepo, shared handlers may live in `packages/api`, but the Expo API route adapter files still belong under `apps/mobile/src/app/api` or the selected Expo route root.

If the user asks only for future backend support or generic API support, create `packages/api` or a backend app as described in `project-structure.md` and document that Expo API routes are not yet wired.

## 10. Update Docs

If the repository has living docs, update them as an explicit scaffold deliverable:

- `docs/architecture/architecture.md`: app/workspace shape, major apps/packages, boundaries, and generated runtime flow.
- `docs/architecture/tech-stack.md`: Expo SDK, React Native, package manager, NativeWind/gluestack strategy, EAS build/update posture, landing/backend choices.
- Relevant operational docs: install, development build, EAS build/update, environment variables, and credential/account steps.
- `AGENTS.md`: merged Expo-generated context and scaffold-specific commands/rules, when agent files were generated or already present.

If these docs do not exist and the repo has no docs convention, either create lightweight factual seed docs or report that docs were not present and no architecture docs were updated.

## 11. Verify

Run the checks in `verification.md` and report exact commands and results.

## 12. Report Post-Scaffold Operations

End the workflow with a `Post-scaffold operations` section. Use `eas.md` as the source of truth, and include exact commands adapted to the project package manager and app root. At minimum, report whether the user still needs to run:

- `eas login`
- `eas init`
- `eas update:configure`
- the first development build command
- device/simulator installation and `expo start`
- credential, store, secret, backend, or deployment setup that could not be completed locally

If a command was already completed during the scaffold, say so and omit it from the required list. If it was intentionally not run because it needs account credentials or user decisions, list it as required or conditional instead of implying the scaffold is fully account-configured.
