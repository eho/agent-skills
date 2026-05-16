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
npx expo install nativewind react-native-reanimated react-native-safe-area-context
npm install --save-dev tailwindcss@^3.4.17 prettier-plugin-tailwindcss@^0.5.11 babel-preset-expo
```

Adjust package manager commands for Bun, npm, pnpm, or Yarn as appropriate.

Create `global.css`:

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

module.exports = withNativeWind(config, { input: "./global.css" });
```

Create `nativewind-env.d.ts`:

```ts
/// <reference types="nativewind/types" />
```

Import `global.css` once at the root, normally in `app/_layout.tsx`:

```ts
import "../global.css";
```

## Existing Project Merge Notes

- Preserve existing Babel plugins and keep `react-native-reanimated/plugin` last.
- Preserve existing Metro resolver customizations before wrapping with `withNativeWind`.
- Add all source roots to Tailwind `content`, including `src`, `features`, or monorepo package paths if present.
