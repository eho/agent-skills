# Scaffold Workflow

Follow this sequence for a new project. For an existing project, start at step 2 and merge changes instead of replacing files.

## 1. Create The Expo App

Use the latest stable Expo template at execution time:

```sh
npx create-expo-app@latest <app-slug>
```

Prefer the default TypeScript + Expo Router template unless the user asks for a different template. Avoid templates that include `@next`, canary, beta, or preview SDKs.

After creation:

- Confirm `expo`, `react`, `react-native`, and `expo-router` versions are stable.
- Run the package manager install if the CLI did not do so.
- If the package manager should be Bun, normalize scripts to work with `bun run` but keep commands portable inside scripts.

## 2. Add Baseline App Metadata

Update `app.json` or `app.config.*` conservatively:

- `name`: display name from the user.
- `slug`: URL/package-safe slug.
- `scheme`: lower-case slug by default.
- `userInterfaceStyle`: `automatic`.
- `orientation`: `portrait` unless the user requests otherwise.
- `ios.bundleIdentifier` and `android.package`: ask the user or leave placeholders if not provided.

Do not invent an Expo `owner`, EAS `projectId`, app store IDs, or credentials.

## 3. Configure NativeWind

Read `nativewind.md`, install the selected NativeWind line, and configure:

- `global.css`
- `tailwind.config.js`
- `babel.config.js`
- `metro.config.js`
- `nativewind-env.d.ts`
- global CSS import in the app root layout or entry file

## 4. Bootstrap gluestack-ui v3

Read `gluestack.md`, then run the gluestack CLI from the project root. Add a starter component set, not the entire library unless the user requests it.

## 5. Add Placeholder Screen

Create or replace only the starter route/screen that belongs to the scaffold. Prefer `app/index.tsx` when using Expo Router. Use `examples/placeholder-screen.tsx` as the base and adjust imports to match gluestack's generated component paths.

## 6. Configure EAS

Read `eas.md`, then run official EAS configuration commands where possible. Add scripts and profiles after the CLI has written baseline config.

## 7. Verify

Run the checks in `verification.md` and report exact commands and results.
