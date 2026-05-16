# Scaffold Workflow

Follow this sequence for a new project. For an existing project, start at step 2 and merge changes instead of replacing files.

## 1. Choose And Prepare The Workspace

Read `project-structure.md` first. If the target directory is not empty, do not run `create-expo-app` directly in it. `create-expo-app .` refuses directories containing files such as `.agents`, `AGENTS.md`, `skills-lock.json`, existing lockfiles, or app code.

Recommended flow for non-empty targets:

1. Scaffold into `/private/tmp/<slug>-expo-scaffold`.
2. Complete package installation and CLI initialization there.
3. Copy the generated files into the target location or into `apps/mobile` for a monorepo.
4. Exclude `.git`, temporary build output, generated native folders unless requested, and lockfiles from package managers the project is not using.

For a monorepo, create the root workspace first, then scaffold the Expo app into `apps/mobile`.

## 2. Create The Expo App

Use Expo SDK 55 unless the user asks for a different SDK. Verify the current official SDK 55 template syntax first, then create the project with the pinned stable template:

```sh
npx create-expo-app@latest <app-slug> --template default@sdk-55
```

Prefer the default TypeScript + Expo Router template unless the user asks for a different template. Avoid templates that include `@next`, canary, beta, or preview SDKs.

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

## 3. Add Baseline App Metadata

Update `app.json` or `app.config.*` conservatively:

- `name`: display name from the user.
- `slug`: URL/package-safe slug.
- `scheme`: lower-case slug by default.
- `userInterfaceStyle`: `automatic`.
- `orientation`: `portrait` unless the user requests otherwise.
- `ios.bundleIdentifier` and `android.package`: ask the user or leave placeholders if not provided.
- `plugins`: include `expo-splash-screen` with config-plugin options when splash assets are available or placeholders are acceptable.

Do not invent an Expo `owner`, EAS `projectId`, app store IDs, or credentials.

## 4. Configure NativeWind

Read `nativewind.md`, install the selected NativeWind line, and configure:

- `global.css`
- `tailwind.config.js`
- `babel.config.js`
- `metro.config.js`
- `nativewind-env.d.ts`
- global CSS import in the app root layout or entry file

## 5. Bootstrap gluestack-ui v3

Read `gluestack.md`, then run the gluestack CLI from the project root. Add a starter component set, not the entire library unless the user requests it.

After gluestack commands, check and repair generated config paths:

- Metro NativeWind input must point at the real CSS file, such as `./src/global.css` when the app uses `src`.
- Babel aliases must resolve both source code and assets.
- Tailwind content globs must include the actual app, src, and component directories.
- Root layout must have one CSS import and one provider wrapper.

## 6. Configure Theme And Launch Experience

Read `theme.md` and `launch-experience.md`.

For theme:

- Default the generated gluestack provider usage to `mode="system"`.
- Use gluestack token classes such as `bg-background-0`, `text-typography-900`, and `border-outline-200` in starter screens.
- Keep generated `dark:` classes rare and intentional; do not use them for every normal surface.
- Add a tiny runtime theme helper only when JS-only values are needed, such as status bar style or animated launch overlay colors.

For splash and launch:

- Configure native splash through the `expo-splash-screen` config plugin.
- Call `SplashScreen.preventAutoHideAsync()` in module scope only when the app waits on local readiness work.
- Hide the native splash as soon as the first app frame is ready.
- Add an animated launch overlay only when requested or when the scaffold option includes it.

## 7. Add Placeholder Screen

Create or replace only the starter route/screen that belongs to the scaffold. Prefer `app/index.tsx` when using Expo Router. Use `examples/placeholder-screen.tsx` as the base and adjust imports to match gluestack's generated component paths.

## 8. Add Root Layout

For Expo Router, wire `app/_layout.tsx` after NativeWind and gluestack are initialized:

- Import `global.css` exactly once.
- Wrap the `Stack` with the generated `GluestackUIProvider`.
- Pass `mode="system"` unless the user asked for an explicit or persisted theme setting.
- Add `StatusBar` with `style="auto"` or the runtime helper style.
- If animated launch was selected, adapt `examples/root-layout-with-splash.tsx` and `examples/app-launch-overlay.tsx`.

## 9. Configure EAS

Read `eas.md`, then run official EAS configuration commands where possible. Add scripts and profiles after the CLI has written baseline config. The development profile should produce an `expo-dev-client` build.

## 10. Verify

Run the checks in `verification.md` and report exact commands and results.
