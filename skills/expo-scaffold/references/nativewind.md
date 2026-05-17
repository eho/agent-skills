# NativeWind Setup

NativeWind compatibility changes frequently. Always verify the currently stable NativeWind line against the selected Expo SDK and React Native version before installing.

## Version Selection

Use this decision rule:

1. Prefer latest stable NativeWind compatible with the selected stable Expo SDK.
2. If the latest docs point to a preview/pre-release line, do not silently use it for a production-oriented scaffold.
3. If stable compatibility is unclear, ask the user whether to use the conservative stable line or the preview line.

As of May 2026, NativeWind v5 documentation describes v5 as pre-release, while the stable Expo setup still commonly uses NativeWind v4 with Tailwind CSS 3.4.x. Treat this as time-sensitive and re-check.

## Stable v4-Style Expo Configuration

Install compatible packages with Expo where possible:

```sh
npx expo install nativewind@^4.2 react-native-reanimated react-native-safe-area-context
npm install --save-dev tailwindcss@^3.4.17 prettier-plugin-tailwindcss@^0.5.11 babel-preset-expo
```

For Bun, prefer:

```sh
bunx expo install nativewind@^4.2 react-native-reanimated react-native-safe-area-context
bun add -d tailwindcss@^3.4.17 prettier-plugin-tailwindcss@^0.5.11 babel-preset-expo
```

Adjust package manager commands for Bun, npm, pnpm, or Yarn as appropriate. Re-check the latest stable v4 patch before using the example version; the important constraint is that this v4-style config must install a v4 `nativewind` major, not whatever the unpinned latest tag resolves to. For SDK 55 with React Native 0.83, prefer the latest stable `nativewind@^4.2.x` if it is available and compatible.

If Bun or the installer resolves Tailwind CSS 4 while using NativeWind v4, force Tailwind CSS back to the 3.4 line and reinstall:

```sh
bun add -d tailwindcss@^3.4.17
```

For SDK 55-style projects, create `src/global.css`. For older/root-layout projects, create `global.css` at the app root:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Create or update `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./app/**/*.{js,jsx,ts,tsx}",
    "./components/**/*.{js,jsx,ts,tsx}",
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {},
  },
  plugins: [],
};
```

Create or update `babel.config.js`:

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    plugins: ["react-native-reanimated/plugin"],
  };
};
```

When merging into an existing Babel config, preserve existing presets/plugins and keep `react-native-reanimated/plugin` last. The v4-style NativeWind setup needs both the `jsxImportSource: "nativewind"` Expo preset option and the `nativewind/babel` preset unless current NativeWind docs say otherwise.

Create or update `metro.config.js`:

```js
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: "./src/global.css" });
```

Create or update `app.json` or `app.config.*` so Expo web uses Metro when the selected NativeWind version requires it:

```json
{
  "expo": {
    "web": {
      "bundler": "metro"
    }
  }
}
```

Preserve existing `web.output`, `favicon`, and other web settings when adding `web.bundler`.

Create `nativewind-env.d.ts`:

```ts
/// <reference types="nativewind/types" />
```

Verify `nativewind-env.d.ts` is included by `tsconfig.json`. If the project uses a restrictive `include` list, add the declaration file or a broad source glob that includes it.

Import `global.css` once at the root, normally in `src/app/_layout.tsx` for SDK 55:

```ts
import "../global.css";
```

If the project uses a root-level `app/` directory, use `./global.css` in Metro and keep the same `../global.css` import from `app/_layout.tsx`.

## Preview v5 Branch

If the user explicitly chooses NativeWind v5 while it is still preview/pre-release, do not reuse the v4 snippet above. Follow the current v5 docs for `nativewind@preview`, `react-native-css`, Tailwind CSS v4, and the matching Metro/CSS setup, then report that the scaffold is using a preview styling stack.

## Existing Project Merge Notes

- Preserve existing Babel plugins and keep `react-native-reanimated/plugin` last.
- Preserve existing Metro resolver customizations before wrapping with `withNativeWind`.
- Add all source roots to Tailwind `content`, including `src`, `features`, or monorepo package paths if present.
- Preserve existing app config web settings while adding `web.bundler: "metro"` when required by NativeWind v4.

## Bun Failure Handling

If Bun install commands fail with sandbox, temp directory, or network errors, retry the exact same command with the environment's approved escalation flow instead of changing package versions or package managers first. After any Expo lint command auto-installs `eslint` or `eslint-config-expo`, run the selected package manager install again and rerun lint in a fresh process.
