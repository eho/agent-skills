# Project Structure

Choose the project shape before running scaffold commands. Ask the user when the request does not make this clear:

- Do you want only a mobile app for now?
- Do you want backend/API support separated from the mobile app?
- Do you want a landing website app?

## Recommended Shapes

### Mobile Only

Use a simple app when the user has no backend or landing-site requirement:

```text
<repo>/
  assets/
  src/
    app/
    components/
    global.css
    lib/
  app.json
  eas.json
  package.json
```

This is the least moving parts and matches the Expo SDK 55 default template shape. If the selected SDK or template still generates a root-level `app/` directory, keep that layout and adjust the example import paths instead of moving files just to match this document.

### Mobile With Backend Or Landing Site

Use a workspace monorepo as soon as the user wants backend support, API-route separation, a landing site, or likely future apps:

```text
<repo>/
  apps/
    mobile/
      assets/
      src/
        app/
        components/
        global.css
        lib/
      app.json
      eas.json
      package.json
    landing/
      src/
      public/
      package.json
  packages/
    api/
      src/
      package.json
    config/
      eslint/
      typescript/
      tailwind/
    shared/
      src/
      package.json
  package.json
  bun.lock
  tsconfig.base.json
```

Use this as the default when the user says they may add Expo API routes, backend modules, or a landing site. It keeps mobile concerns isolated while leaving clean places for server and web code.

## Backend Guidance

For "Expo API routes" or backend support, prefer a separate package such as `packages/api` unless the user explicitly wants API routes colocated under the mobile app. The package can later be wired to:

- Expo Router API routes if they choose Expo web/server output.
- A standalone Hono, Elysia, Express, or serverless app.
- Shared request handlers consumed by an Expo route adapter.

Keep backend-only dependencies out of `apps/mobile/package.json` unless they are required at runtime in the mobile bundle.

## Landing Site Guidance

If the user wants a landing site, ask whether they prefer:

- Expo web in `apps/mobile`, for a simple shared app/web surface.
- A separate React/Vite or Next app in `apps/landing`, for marketing pages and SEO.

Default to `apps/landing` for a marketing/landing website. Keep it separate from `apps/mobile` so mobile build dependencies, EAS config, and gluestack NativeWind setup do not constrain the website.

## Workspace Setup

For Bun workspaces, create root `package.json` like:

```json
{
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "mobile:start": "bun run --cwd apps/mobile start",
    "mobile:ios": "bun run --cwd apps/mobile ios",
    "mobile:android": "bun run --cwd apps/mobile android",
    "mobile:build:preview": "bun run --cwd apps/mobile build:preview",
    "mobile:update:preview": "bun run --cwd apps/mobile update:preview"
  }
}
```

Use root-level shared config only when it reduces duplication. Keep mobile-specific Babel, Metro, EAS, and app config inside `apps/mobile`.

For shared packages that the mobile app imports at runtime:

- Give each package a real workspace package name such as `@repo/shared`.
- Add the shared package to `apps/mobile/package.json` dependencies using the workspace protocol supported by the selected package manager.
- Add package `exports` for source or built entry points, for example `./src/index.ts` in Bun-first internal workspaces.
- Keep backend-only packages out of the mobile app dependency graph.
- Verify Metro can bundle the shared import at runtime; TypeScript path resolution alone is not enough.

## Alias Policy

Use app-local aliases for mobile:

- `@/*` -> `<mobile-root>/src/*` for SDK 55-style projects.
- `@/assets/*` -> `apps/mobile/assets/*` or `./assets/*` from the mobile app root.

If using shared packages, prefer package imports such as `@repo/shared` over aliases that jump across workspace boundaries.
