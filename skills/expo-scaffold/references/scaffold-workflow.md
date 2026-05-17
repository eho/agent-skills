# Scaffold Workflow

Follow this sequence for a new project. For an existing project, start at step 2 and merge changes instead of replacing files.

## Subagent Use

When subagents are available, use them only where parallelism reduces risk:

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

For a monorepo, create the root workspace first, then scaffold the Expo app into `apps/mobile`. After copying from a temporary scaffold, run the selected package manager install from the final workspace root. With Bun, allow that install to recreate package-local `node_modules` link folders inside apps/packages if local scripts need them.

## 2. Create The Expo App

Use Expo SDK 55 unless the user asks for a different SDK. Verify the current official SDK 55 template syntax first, then create the project with the pinned stable template:

```sh
npx create-expo-app@latest <app-slug> --template default@sdk-55
```

Prefer the default TypeScript + Expo Router template unless the user asks for a different template. Expo SDK 55 defaults to a `src/app` Expo Router layout; keep that structure unless the selected template generates root-level `app/` or the user asks for it. Avoid templates that include `@next`, canary, beta, or preview SDKs.

If the user requests a different stable SDK, use the SDK-pinned stable template syntax when available:

```sh
npx create-expo-app@latest <app-slug> --template default@sdk-<stable>
```

Use that only for stable SDK identifiers from official Expo docs.

After creation:

- Confirm `expo`, `react`, `react-native`, and `expo-router` versions are stable.
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

## 4. Configure NativeWind

Read `nativewind.md`, install the selected NativeWind line, and configure:

- `src/global.css` for SDK 55-style projects, or `global.css` for root-layout projects
- `tailwind.config.js`
- `babel.config.js`
- `metro.config.js`
- `nativewind-env.d.ts`
- global CSS import in the app root layout or entry file

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
- Babel aliases must resolve both source code and assets.
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

## 10. Update Docs

If the repository has living docs, update them as an explicit scaffold deliverable:

- `docs/architecture/architecture.md`: app/workspace shape, major apps/packages, boundaries, and generated runtime flow.
- `docs/architecture/tech-stack.md`: Expo SDK, React Native, package manager, NativeWind/gluestack strategy, EAS build/update posture, landing/backend choices.
- Relevant operational docs: install, development build, EAS build/update, environment variables, and credential/account steps.

If these docs do not exist and the repo has no docs convention, either create lightweight factual seed docs or report that docs were not present and no architecture docs were updated.

## 11. Verify

Run the checks in `verification.md` and report exact commands and results.
