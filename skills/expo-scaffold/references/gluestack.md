# gluestack-ui v3 Setup

Use the official gluestack CLI from the project root when it runs reliably. Check the current docs before running commands because v3 package names and generated paths may change. If CLI init requires interaction or fails for agent-environment reasons, use the official manual installation flow instead of blocking the scaffold.

gluestack setup is a hard gate for the default scaffold, but CLI init is not. Do not hand-write lookalike components and call the project initialized. Manual setup is valid only when it follows the official gluestack manual installation path and copies official provider/component source. A local non-official UI fallback is allowed only if the user explicitly asks to continue without official gluestack.

Track one of these outcomes:

- `cli_initialized`: CLI init succeeded and generated the expected provider/config.
- `manual_installed`: CLI init was skipped or failed, and the official manual installation flow completed with official provider/component source copied into the app.
- `interactive_cli_required`: current official docs do not provide enough manual source/config detail to proceed, so a real terminal run of the exact CLI command is required before continuing.
- `blocked`: both CLI and official manual setup are unusable, provider/component source cannot be verified, or generated/copied files still do not build; stop the default workflow and report diagnostics.
- `fallback_approved`: the user explicitly approved a non-official fallback after being told it will not be official gluestack.

## Bootstrap

Inspect the current CLI first:

```sh
npx gluestack-ui init --help
```

Run init with a TTY when possible because `gluestack-ui init` can fail in non-interactive shells. Use documented flags to avoid prompts where the current CLI supports them. As of the v3 CLI docs, `init` documents `--path <path>` and package-manager flags such as `--use-bun`, `--use-npm`, `--use-yarn`, and `--use-pnpm`; do not rely on undocumented flags unless `--help` confirms them in the current version.

For a Bun project using the SDK 55 `src` layout, try the documented command shape:

```sh
bunx gluestack-ui init --use-bun --path src/components/ui
```

If current `--help` documents an additional Expo project-type flag, include it only after confirming the exact flag name:

```sh
bunx gluestack-ui init --use-bun --path src/components/ui <documented-expo-flag>
```

If the project does not use `src`, use `components/ui` instead of `src/components/ui`. If flags have changed, use the current CLI help and keep the same choices: Expo-compatible initialization, Bun package manager when applicable, and the actual UI component path.

If the first documented init attempt fails because of non-TTY execution, retry once in a TTY if the environment supports it. If the TTY retry also fails, hangs at an interactive package-manager prompt, or shows that the CLI cannot be driven reliably from the agent environment, switch to the official manual installation flow below. Do not pause for the user to run interactive init unless manual setup is not possible from current official docs/source.

When pausing with `interactive_cli_required`, tell the user:

- The exact command to run from the project root.
- That they should complete the gluestack prompts using the same choices already selected for the scaffold, such as package manager and component path.
- To reply when the command has finished, including any error output if it fails.

Also include a pause diagnostic summary:

- The exact automated commands attempted.
- Whether each command ran with a TTY.
- Package manager and lockfile state.
- Expo SDK, React Native, Bun/npm versions when available.
- The exact stderr/stdout errors or hang point.
- Any generated files left behind by the failed automated init.

Do not continue to theme wiring, placeholder screens, `gluestack-ui add`, or final scaffold verification while the outcome is `interactive_cli_required`. After the user reports that manual init completed, inspect the generated files. If the provider/config exists, change the outcome to `cli_initialized` and continue. If manual init fails or the expected files are still missing, try the official manual setup if it is viable; otherwise change the outcome to `blocked`, report diagnostics, and stop unless the user explicitly approves a non-official fallback.

If init crashes with a CLI bug such as `Cannot read properties of undefined`, and the same command has already been offered for manual interactive execution or is clearly unrelated to TTY handling, do not keep retrying variants blindly.

Known blocking examples to report exactly if seen:

```sh
TTY initialization failed: uv_tty_init returned EINVAL (invalid argument)
Cannot read properties of undefined (reading 'dependencies')
gluestack is not initialized in the project
```

When init is blocked, stop before wiring the placeholder screen or claiming gluestack support. Report:

- The exact commands attempted.
- Whether each command ran with a TTY.
- Package manager and lockfile state.
- Expo SDK, React Native, Bun/npm versions when available.
- The exact stderr/stdout errors.
- Any generated files left behind by the failed init.
- The manual command attempted or, if no manual attempt happened, the exact command the user can still try in an interactive terminal.

Do not proceed to `gluestack-ui add` unless init reached `cli_initialized`.

## Official Manual Installation

Use this path when CLI init is unavailable or too interactive, or when the user explicitly asks for manual installation. The manual path is still official gluestack setup when it uses current gluestack docs/source instead of local approximations.

1. Confirm NativeWind is already installed and configured through `nativewind.md`. The gluestack manual docs start from an existing NativeWind setup.
2. Install the documented gluestack dependencies with the selected package manager. For Expo apps, use Expo-safe commands as the primary path so generated Expo/RN versions stay SDK-compatible:

```sh
npm i @gluestack-ui/core @gluestack-ui/utils @gluestack/ui-next-adapter
npx expo install react-native-svg react-native-web
```

For Bun, use:

```sh
bun add @gluestack-ui/core @gluestack-ui/utils @gluestack/ui-next-adapter
bunx expo install react-native-svg react-native-web
```

The upstream manual docs may list the broader package set `@gluestack-ui/core @gluestack-ui/utils react-native-svg @gluestack/ui-next-adapter react-native-web react-native`. Adapt that list for Expo by preserving already installed `react-native`, `react`, and Expo package versions.

3. Copy the official provider and required init components into the app's selected UI directory. Use this source-discovery order:

- Prefer the current installation page's Manual tab and GitHub source link.
- Then check the official provider source path referenced by the docs: `https://github.com/gluestack/gluestack-ui/tree/main/src/components/ui/gluestack-ui-provider`.
- For components, use each current component page's Manual tab or the matching official source path under `https://github.com/gluestack/gluestack-ui/tree/main/src/components/ui/<component-name>`.
- If `main` is no longer the docs branch, use the branch linked by the docs page's "Edit this page on GitHub" or source link.

Copy all contents of `gluestack-ui-provider` into `src/components/ui/gluestack-ui-provider` for SDK 55 `src` layouts or `components/ui/gluestack-ui-provider` for root layouts. Also copy official `icon`, `overlay`, and `toast` components when the provider, starter components, or current init docs reference them. Preserve the official local file structure and record the exact source URL/path used in the final report. If the source cannot be found or verified, use `interactive_cli_required` or `blocked`; do not invent provider code.

4. Update `tailwind.config.js` using the current manual docs as the source of truth, while preserving the app's actual content globs and NativeWind preset. Include `src`, `app`, `components`, and the selected UI path. Include gluestack token color mappings and safelist/patterns from the docs when present.
5. Keep `global.css` in the path used by the project, normally `src/global.css` for SDK 55 `src` layouts. If the manual docs assume root `global.css`, adapt Metro and root-layout imports instead of moving files blindly.
6. Wire the copied `GluestackUIProvider` into the Expo Router root layout and pass `mode="system"` by default.
7. Set outcome to `manual_installed` only after the provider imports cleanly, token classes are available in Tailwind config/CSS, and at least the components used by the placeholder screen exist in the selected UI path.

Manual setup does not require `gluestack-ui.config.json`; the CLI docs describe that file as needed for CLI component management, while copy-paste/manual components can work without it. If you create a config file manually to help future CLI `add` calls, verify its paths match the real `tailwind.config.js`, CSS file, app entry, and component directory.

## Starter Components

Install a practical starter set:

```sh
npx gluestack-ui add --help
```

Use the help output to confirm whether the current CLI supports adding multiple components in one command. If multi-add is documented, add this starter set together:

```sh
npx gluestack-ui add box vstack hstack text heading button card input badge divider icon toast alert
```

With Bun, use `bunx gluestack-ui add ...`.

Only run `add` after verifying CLI init produced the expected provider/config files. If `add` says gluestack is not initialized, switch to official manual component copying when possible; otherwise return to `blocked` status and stop.

If multi-add is not documented or the command fails, add the starter components one at a time with the selected package manager and any documented path/package-manager flags. If a component name has changed, use the current CLI suggestions and keep the intent of the starter set:

- Layout: Box, VStack, HStack
- Typography: Text, Heading
- Action: Button
- Form: Input
- Display: Card, Badge, Divider
- Feedback: Toast or Alert
- Media/icon: Icon

Do not install every component unless the user asks for a kitchen-sink starter.

For `manual_installed`, copy only the starter components needed by the placeholder screen from official gluestack source/docs or from each component page's Manual tab when available. Preserve their exported API and dependency files. If a component has complex dependencies that are hard to verify manually, choose a smaller starter screen that uses only copied components with verified imports rather than inventing substitute primitives. Do not claim that CLI component management is available unless `gluestack-ui.config.json` and `gluestack-ui add` were verified.

## Lockfile Hygiene

After each gluestack command, inspect the app directory for unexpected lockfiles. The CLI may call npm internally and create `package-lock.json`. If the project uses Bun, remove `package-lock.json`, `yarn.lock`, and `pnpm-lock.yaml` unless the user explicitly wants them, then run the chosen package manager install again.

## Provider Wiring

After successful CLI init, inspect generated files and wire the provider exactly as the CLI expects. After manual install, wire the copied provider exactly as the official source expects. Common locations include:

- `components/ui/gluestack-ui-provider`
- `components/ui/gluestack-ui-provider/index.tsx`
- `gluestack-ui.config.json` for CLI-managed projects
- generated CSS/theme files

For Expo Router, the provider normally belongs in `src/app/_layout.tsx` around the root `Stack` for SDK 55-style projects, or `app/_layout.tsx` for templates that still use root-level routes.

Also ensure `global.css` is imported before rendering UI.

For the default scaffold, pass `mode="system"` to the official `GluestackUIProvider` so the app follows the device light/dark setting. Do not replace the official provider with a hand-written approximation unless the user explicitly approves a non-official fallback.

gluestack-ui v3 supports light/dark mode through CSS-variable token maps in the official provider config. Prefer token classes such as `bg-background-0`, `text-typography-900`, and `border-outline-200` in scaffolded screens. Avoid adding `dark:` variants everywhere; reserve them for intentional exceptions outside the token system.

## Post-Init Config Repair

gluestack CLI may rewrite app config files. Manual setup may require the same edits without the rewrite step. Immediately inspect and repair:

- `metro.config.js`: NativeWind input path must match the real CSS file. Use `./src/global.css` for `src` layouts and `./global.css` for root layouts.
- `babel.config.js`: preserve existing plugins and aliases. Do not add aliases that break asset resolution.
- `tailwind.config.js`: content globs must match the real `app`, `src`, `components`, and UI paths.
- `src/app/_layout.tsx` or `app/_layout.tsx`: keep exactly one global CSS import and one gluestack provider wrapper. Remove duplicate imports and noisy formatting.
- TypeScript aliases: ensure `@/*` and `@/assets/*` resolve consistently with Metro and Babel.

## Placeholder Screen

Use `examples/placeholder-screen.tsx` as a structure, but adjust import paths to match the official component files. If the component API differs, prefer the current official component API over the example.

## Verification Criteria

Before reporting gluestack success, verify:

- The setup outcome is `cli_initialized` or `manual_installed`.
- The official provider exists and is imported by the root layout.
- Expected config/theme files exist for the selected path, such as `gluestack-ui.config.json` for CLI setup or copied provider config/theme files for manual setup.
- Starter component files exist at the selected UI path.
- Placeholder screen imports use official gluestack component paths, not local fallback primitives.
- For CLI setup, `gluestack-ui add` did not fail with an uninitialized-project error.
- For manual setup, every placeholder import resolves to copied official source and the final report states that future components should be copied manually or CLI init should be run later to enable CLI-managed adds.

In the final report, include the gluestack outcome label. If the outcome is `interactive_cli_required` or `blocked`, do not describe the scaffold as complete. If the outcome is `manual_installed`, describe it as official manual gluestack setup and clarify that CLI component management was not verified unless it was. If the outcome is `fallback_approved`, describe it as a user-approved non-official fallback rather than official gluestack setup.
