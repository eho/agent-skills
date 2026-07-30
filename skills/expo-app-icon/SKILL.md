---
name: expo-app-icon
description: Design and package launcher icons for Expo apps. Use when creating or refining an app-icon concept, deriving iOS and Android adaptive or themed assets from artwork, or updating and validating Expo icon configuration. Do not use for in-app iconography, notification icons, or non-Expo projects.
compatibility: Optional asset scripts require Python 3 and Pillow.
---

# Expo App Icon

Help with only the stages the user needs:

- **Explore** — develop icon concepts or visual variants.
- **Package** — turn selected artwork into platform assets.
- **Configure** — update and validate an Expo project.

Inspect the product context, existing assets, and app config before editing. Preserve unrelated configuration and artwork. Never delete candidates or overwrite existing assets without explicit approval.

## Explore

Base concepts on the product promise, audience, brand language, and misleading associations to avoid. Inspect recurring shapes, spacing, materials, and motifs in the existing product so the launcher feels related without copying the UI.

Favor one memorable metaphor, a strong silhouette, few major shapes, and clear contrast at 48–64 px. Compare directions on audience fit, instant readability, distinctiveness, and unintended associations or value judgments.

Offer a small set of genuinely different directions when the user wants ideas. Generate variants only when requested or useful for choosing a direction. Avoid text, baked rounded-square masks, borders, global shadows, and details that disappear at launcher size.

Use any suitable image, vector, or design tool. The output quality matters more than the tool.

When using an image model, read [references/image-generation-prompts.md](references/image-generation-prompts.md). Read [references/platform-guidance.md](references/platform-guidance.md) when assessing platform constraints.

## Package

Once the user approves a direction, freeze its composition and preserve the selected source unmodified. Derive platform assets from that geometry rather than independently regenerating approximations. If a monochrome, splash, or favicon version intentionally simplifies the mark, document the difference.

For conventional PNG assets, prepare:

- A square, opaque full-color master for iOS and legacy launchers.
- A transparent foreground mark for Android adaptive icons.
- An optional single-color monochrome mark for Android themed icons. If absent, it may be derived from the foreground.

Splash artwork and favicons are adjacent assets, not automatic launcher-icon outputs. Create them only when requested or already in project scope. Accept a separate splash mark when its composition differs from the launcher foreground.

For a full conventional-PNG replacement of both iOS and Android launchers, the bundled script generates the core assets and can merge their paths into `app.json`:

```bash
python3 <skill-dir>/scripts/prepare_expo_icon_assets.py \
  --icon-master /absolute/path/master.png \
  --mark /absolute/path/transparent-mark.png \
  --output-dir /absolute/path/app/assets/images \
  --background-color '#1E2630' \
  --app-json /absolute/path/app/app.json
```

Useful options:

- `--monochrome-mark PATH`
- `--include-splash` and optional `--splash-mark PATH`
- `--include-web`
- `--dry-run`
- `--force` only when the user approved replacing existing generated assets

Without `--app-json`, the script prints a config fragment for manual use. Merge `app.config.js` or `app.config.ts` manually so functions, comments, and environment logic remain intact.

For Android-only, iOS-only, or Apple Icon Composer migrations, generate or edit only the required assets and merge config manually; the bundled generator intentionally targets a complete conventional PNG replacement.

The default Android critical-content bound is `66 / 108` of the layer, matching Android’s documented safe zone. Change it only for a deliberate design reason and preview multiple masks.

Read [references/platform-guidance.md](references/platform-guidance.md) before packaging or editing config because Expo and platform contracts can change.

## Configure

Keep platform roles distinct:

- iOS icon: square and opaque; the OS applies its mask.
- Android foreground: transparent mark.
- Android background: a color or a deliberate background image.
- Android monochrome: single-color themed layer; it may be simplified independently.
- Splash: transparent PNG with its own background configuration.

Do not silently replace an existing adaptive background image or discard existing splash plugin settings. Resolve such choices from the design and the user’s request.

## Verify

Run the bundled validator on an asset set emitted by the generator:

```bash
python3 <skill-dir>/scripts/validate_expo_icon_assets.py \
  --assets-dir /absolute/path/app/assets/images \
  --app-json /absolute/path/app/app.json
```

Also inspect the resolved Expo config when available:

```bash
npx expo config --type public
```

Check dimensions, opacity/transparency, adaptive safe bounds, monochrome simplicity, and config paths. Preview the icon at small sizes and under common Android masks. A simulated themed color is only a preview; Android supplies the real color.

Launcher icons require a native build to verify. Expo Go does not show the shipped icon. Test final splash behavior in a preview or production/release build; Expo Go and development builds do not fully reproduce it.

## Report

Summarize the chosen direction, changed files, config fields, validation results, and remaining build/device checks. Mention replacements or deletions explicitly.
