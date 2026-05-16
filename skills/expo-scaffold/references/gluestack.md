# gluestack-ui v3 Setup

Use the official gluestack CLI from the project root. Check the current docs before running commands because v3 package names and generated paths may change.

## Bootstrap

Initialize gluestack-ui:

```sh
npx gluestack-ui init
```

Run the CLI with a TTY because `gluestack-ui init` may fail or hang in non-interactive shells. Before adding flags, check the installed CLI help and current docs:

```sh
npx gluestack-ui init --help
```

If using a `src` layout with Bun, prefer explicit documented flags when supported:

```sh
bunx gluestack-ui init --use-bun --path src/components/ui
```

If the project does not use `src`, use `components/ui` instead of `src/components/ui`. If flags have changed, use the current CLI help and keep the same choices: Expo-compatible initialization, Bun package manager when applicable, and the actual UI component path.

If the current CLI still requires interactive choices after documented flags are supplied, do not let the agent sit in a hung command. Stop, report the exact command, and ask the user to run it in an interactive terminal or provide the missing choices.

## Starter Components

Install a practical starter set:

```sh
npx gluestack-ui add box vstack hstack text heading button card input badge divider icon toast alert
```

With Bun:

```sh
bunx gluestack-ui add box vstack hstack text heading button card input badge divider icon toast alert
```

If a component name has changed, use the current CLI suggestions and keep the intent of the starter set:

- Layout: Box, VStack, HStack
- Typography: Text, Heading
- Action: Button
- Form: Input
- Display: Card, Badge, Divider
- Feedback: Toast or Alert
- Media/icon: Icon

Do not install every component unless the user asks for a kitchen-sink starter.

## Lockfile Hygiene

After each gluestack command, inspect the app directory for unexpected lockfiles. The CLI may call npm internally and create `package-lock.json`. If the project uses Bun, remove `package-lock.json`, `yarn.lock`, and `pnpm-lock.yaml` unless the user explicitly wants them, then run the chosen package manager install again.

## Provider Wiring

After init, inspect generated files and wire the provider exactly as the CLI expects. Common locations include:

- `components/ui/gluestack-ui-provider`
- `components/ui/gluestack-ui-provider/index.tsx`
- generated CSS/theme files

For Expo Router, the provider normally belongs in `app/_layout.tsx` around the root `Stack`.

Also ensure `global.css` is imported before rendering UI.

For the default scaffold, pass `mode="system"` to the generated `GluestackUIProvider` so the app follows the device light/dark setting. Do not replace the generated provider with a hand-written approximation unless the CLI output is broken and the current official docs support the replacement.

gluestack-ui v3 supports light/dark mode through CSS-variable token maps in the generated provider config. Prefer token classes such as `bg-background-0`, `text-typography-900`, and `border-outline-200` in scaffolded screens. Avoid adding `dark:` variants everywhere; reserve them for intentional exceptions outside the token system.

## Post-Init Config Repair

gluestack may rewrite app config files. Immediately inspect and repair:

- `metro.config.js`: NativeWind input path must match the real CSS file. Use `./src/global.css` for `src` layouts and `./global.css` for root layouts.
- `babel.config.js`: preserve existing plugins and aliases. Do not add aliases that break asset resolution.
- `tailwind.config.js`: content globs must match the real `app`, `src`, `components`, and generated UI paths.
- `app/_layout.tsx`: keep exactly one global CSS import and one gluestack provider wrapper. Remove duplicate imports and noisy formatting.
- TypeScript aliases: ensure `@/*` and `@/assets/*` resolve consistently with Metro and Babel.

## Placeholder Screen

Use `examples/placeholder-screen.tsx` as a structure, but adjust import paths to match the generated component files. If the generated API differs, prefer the current generated component API over the example.
