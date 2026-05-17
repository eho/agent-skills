# gluestack-ui v3 Setup

Use the official gluestack CLI from the project root. Check the current docs before running commands because v3 package names and generated paths may change.

gluestack initialization is a hard gate for the default scaffold. Do not hand-write lookalike components and call the project initialized. A local non-official UI fallback is allowed only if the user explicitly asks to continue without official gluestack initialization.

Track one of these outcomes:

- `initialized`: CLI init succeeded and generated the expected provider/config.
- `manual_init_required`: automated init could not complete because the CLI requires a real interactive terminal; pause and ask the user to run the exact init command manually before continuing.
- `blocked`: init failed after manual interactive execution, failed for a non-interactivity CLI error, or still did not generate the expected provider/config after the user reported manual completion; stop the default workflow and report diagnostics.
- `fallback_approved`: the user explicitly approved a non-official fallback after being told it will not be CLI-generated gluestack.

## Bootstrap

Inspect the current CLI first:

```sh
npx gluestack-ui init --help
```

Run init with a TTY when possible because `gluestack-ui init` can fail in non-interactive shells. Use documented flags to avoid prompts where the current CLI supports them.

For a Bun project using the SDK 55 `src` layout, try the current documented equivalent of:

```sh
bunx gluestack-ui init --use-bun --path src/components/ui --projectType app
```

If the project does not use `src`, use `components/ui` instead of `src/components/ui`. If flags have changed, use the current CLI help and keep the same choices: Expo-compatible initialization, Bun package manager when applicable, and the actual UI component path.

If the first documented init attempt fails because of non-TTY execution, retry once in a TTY if the environment supports it. If the TTY retry also fails, hangs at an interactive package-manager prompt, or shows that the CLI cannot be driven reliably from the agent environment, set the outcome to `manual_init_required` and pause the workflow.

When pausing for manual init, tell the user:

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

Do not continue to theme wiring, placeholder screens, `gluestack-ui add`, or final scaffold verification while the outcome is `manual_init_required`. After the user reports that manual init completed, inspect the generated files. If the provider/config exists, change the outcome to `initialized` and continue. If manual init fails or the expected files are still missing, change the outcome to `blocked`, report diagnostics, and stop unless the user explicitly approves a non-official fallback.

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

Do not proceed to `gluestack-ui add` unless init reached `initialized`.

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

Only run `add` after verifying init produced the expected provider/config files. If `add` says gluestack is not initialized, return to `blocked` status and stop.

If multi-add is not documented or the command fails, add the starter components one at a time with the selected package manager and any documented path/package-manager flags. If a component name has changed, use the current CLI suggestions and keep the intent of the starter set:

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

After successful init, inspect generated files and wire the provider exactly as the CLI expects. Common locations include:

- `components/ui/gluestack-ui-provider`
- `components/ui/gluestack-ui-provider/index.tsx`
- `gluestack-ui.config.json`
- generated CSS/theme files

For Expo Router, the provider normally belongs in `src/app/_layout.tsx` around the root `Stack` for SDK 55-style projects, or `app/_layout.tsx` for templates that still use root-level routes.

Also ensure `global.css` is imported before rendering UI.

For the default scaffold, pass `mode="system"` to the generated `GluestackUIProvider` so the app follows the device light/dark setting. Do not replace the generated provider with a hand-written approximation unless the CLI output is broken and the current official docs support the replacement.

gluestack-ui v3 supports light/dark mode through CSS-variable token maps in the generated provider config. Prefer token classes such as `bg-background-0`, `text-typography-900`, and `border-outline-200` in scaffolded screens. Avoid adding `dark:` variants everywhere; reserve them for intentional exceptions outside the token system.

## Post-Init Config Repair

gluestack may rewrite app config files. Immediately inspect and repair:

- `metro.config.js`: NativeWind input path must match the real CSS file. Use `./src/global.css` for `src` layouts and `./global.css` for root layouts.
- `babel.config.js`: preserve existing plugins and aliases. Do not add aliases that break asset resolution.
- `tailwind.config.js`: content globs must match the real `app`, `src`, `components`, and generated UI paths.
- `src/app/_layout.tsx` or `app/_layout.tsx`: keep exactly one global CSS import and one gluestack provider wrapper. Remove duplicate imports and noisy formatting.
- TypeScript aliases: ensure `@/*` and `@/assets/*` resolve consistently with Metro and Babel.

## Placeholder Screen

Use `examples/placeholder-screen.tsx` as a structure, but adjust import paths to match the generated component files. If the generated API differs, prefer the current generated component API over the example.

## Verification Criteria

Before reporting gluestack success, verify:

- The init outcome is `initialized`.
- The generated provider exists and is imported by the root layout.
- Expected config/theme files exist for the current CLI version, such as `gluestack-ui.config.json` or the generated provider config.
- Starter component files exist at the selected UI path.
- Placeholder screen imports use CLI-generated component paths, not local fallback primitives.
- `gluestack-ui add` did not fail with an uninitialized-project error.

In the final report, include the gluestack outcome label. If the outcome is `manual_init_required` or `blocked`, do not describe the scaffold as complete. If the outcome is `fallback_approved`, describe it as a user-approved non-official fallback rather than official gluestack initialization.
