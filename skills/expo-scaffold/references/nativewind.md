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
npx expo install nativewind@^4.1.23 react-native-reanimated react-native-safe-area-context
npm install --save-dev tailwindcss@^3.4.17 prettier-plugin-tailwindcss@^0.5.11 babel-preset-expo
```

Adjust package manager commands for Bun, npm, pnpm, or Yarn as appropriate. Re-check the latest stable v4 patch before using `^4.1.23`; the important constraint is that this v4-style config must install a v4 `nativewind` major, not whatever the unpinned latest tag resolves to.

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
    presets: [["babel-preset-expo", { jsxImportSource: "nativewind" }]],
    plugins: ["react-native-reanimated/plugin"],
  };
};
```

Create or update `metro.config.js`:

```js
const { getDefaultConfig } = require("expo/metro-config");
const { withNativeWind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativeWind(config, { input: "./src/global.css" });
```

Create `nativewind-env.d.ts`:

```ts
/// <reference types="nativewind/types" />
```

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
