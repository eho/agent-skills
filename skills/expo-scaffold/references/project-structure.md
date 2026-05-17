# Project Structure

Choose the project shape before running scaffold commands. Ask the user when the request does not make this clear:

- Do you want only a mobile app for now?
- Do you want backend/API support separated from the mobile app?
- Do you want a landing website app?
- If yes, is the landing app a simple marketing site or does it need SSR/strong SEO?

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

Use this as the default when the user says they may add backend modules, a separate API service, or a landing site. It keeps mobile concerns isolated while leaving clean places for server and web code. Do not treat a separate `packages/api` package as a complete Expo API-routes setup by itself.

## Backend Guidance

For generic backend support, prefer a separate package such as `packages/api` unless the user explicitly wants a standalone server app. The package can later be wired to:

- A standalone Hono, Elysia, Express, or serverless app.
- Shared request handlers consumed by an Expo route adapter.

Keep backend-only dependencies out of `apps/mobile/package.json` unless they are required at runtime in the mobile bundle.

For actual Expo API routes, create route files under the Expo Router app route root, normally `apps/mobile/src/app/api` or `src/app/api`. Expo API routes are part of the Expo app's server/web output, so they require current Expo Router API-route configuration and deployment notes. In a monorepo, `packages/api` can contain shared handlers, validation, or domain logic, but route adapter files still live under the Expo app.

Ask one clarifying question when the user says "API routes" but does not specify the runtime:

- "Do you mean Expo Router API routes inside the mobile/web app, or a separate backend/API package?"

## Landing Site Guidance

If the user wants a landing site, ask whether they prefer:

- Expo web in `apps/mobile`, for a simple shared app/web surface.
- A separate React/Vite or Next app in `apps/landing`, for marketing pages and SEO.

Default to `apps/landing` for a marketing/landing website. Keep it separate from `apps/mobile` so mobile build dependencies, EAS config, and gluestack NativeWind setup do not constrain the website.

For a small separate landing app with Bun and Vite, use this canonical package shape:

```json
{
  "private": true,
  "scripts": {
    "dev": "vite --host 0.0.0.0",
    "build": "tsc -b && vite build",
    "preview": "vite preview --host 0.0.0.0"
  },
  "dependencies": {
    "react": "<expo-compatible-or-current-stable>",
    "react-dom": "<expo-compatible-or-current-stable>"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "<current-stable>",
    "@types/react": "<current-stable>",
    "@types/react-dom": "<current-stable>",
    "typescript": "<current-stable>",
    "vite": "<current-stable>"
  }
}
```

Keep `react` and `react-dom` in `dependencies`. Keep `vite`, `typescript`, `@vitejs/plugin-react`, and React type packages in `devDependencies` unless a specific deployment target installs production dependencies only before building. If you move build tooling to `dependencies` for that reason, document the deployment constraint in the final report.

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
    "mobile:web": "bun run --cwd apps/mobile web",
    "mobile:build:dev": "bun run --cwd apps/mobile build:dev",
    "mobile:build:preview": "bun run --cwd apps/mobile build:preview",
    "mobile:build:production": "bun run --cwd apps/mobile build:production",
    "mobile:update:preview": "bun run --cwd apps/mobile update:preview",
    "mobile:update:production": "bun run --cwd apps/mobile update:production"
  }
}
```

Use `examples/package-monorepo-bun.json` as the canonical starting point for a fresh Bun monorepo root, then add landing, API, lint, test, and docs scripts only when those packages exist.

Use root-level shared config only when it reduces duplication. Keep mobile-specific Babel, Metro, EAS, and app config inside `apps/mobile`.

Bun may create package-local `node_modules` directories that contain workspace links or executable shims even when the authoritative lockfile is at the repo root. Keep those package-local link folders if local scripts depend on them. Remove copied dependency trees from temporary scaffolds, but let the final `bun install` recreate any workspace-local links it needs.

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
