---
name: expo-gluestack-setup
description: Add, configure, repair, or verify gluestack-ui for an existing Expo or React Native project, especially Expo apps using NativeWind. Use this skill whenever the user asks to install gluestack, configure gluestack-ui v3 or another supported gluestack major, add official gluestack provider/components, recover from gluestack CLI failures, verify an existing gluestack setup, or when another Expo scaffold workflow needs a gluestack setup handoff.
---

# Expo gluestack Setup

Use this skill to configure official gluestack-ui in an Expo or React Native project. It can run directly for an existing app, or as a specialist step inside a larger scaffold workflow such as `expo-scaffold`.

The volatile parts are gluestack package names, CLI behavior, official manual setup source paths, provider APIs, NativeWind compatibility, and generated component structure. Verify current official docs and tool output before locking versions or paths.

## Modes

### Standalone Mode

Use standalone mode when the user asks to add, repair, upgrade, or verify gluestack in an existing project.

Before editing, inspect and resolve:

- Project root and app root.
- Package manager and lockfile policy.
- Expo SDK, React Native, NativeWind, Tailwind CSS, and gluestack versions already present.
- Route/layout shape, especially `src/app`, root `app`, or a non-router entry file.
- Existing UI component path, provider path, `tailwind.config.*`, `metro.config.*`, `babel.config.*`, global CSS path, and TypeScript aliases.
- Whether NativeWind is already configured. If it is missing, either configure it only when the user asked for full gluestack setup, or stop with a clear prerequisite if the task is gluestack-only.
- Whether the NativeWind CSS path used by Metro contains `@tailwind base;`, `@tailwind components;`, and `@tailwind utilities;`, and whether Tailwind uses static `darkMode: "class"` when provider mode is `"system"`.

### Orchestrated Mode

Use orchestrated mode when another skill has already created or inspected the app and passes setup decisions. Respect the caller's choices unless they conflict with official gluestack requirements.

Expected inputs from the orchestrator:

- App root.
- Package manager.
- Expo SDK and React Native versions.
- NativeWind status and global CSS path.
- NativeWind preflight result: Tailwind directives present, Metro input path matches the real CSS file, static `darkMode: "class"` when provider mode is `"system"`, and root layout import status if the caller owns layout wiring.
- Route layout: `src/app`, root `app`, or other.
- Desired UI component path, normally `src/components/ui` for SDK 55 `src` layouts or `components/ui` for root layouts.
- Desired gluestack major, or permission to use the current stable compatible major.
- Whether CLI-managed components are explicitly requested.
- Whether layout wiring or route/screen edits are allowed. Default to no in orchestrated mode.

Return the handoff in the required format below. The orchestrator should use that handoff instead of re-deriving provider paths or setup state.

## Version Policy

Default to the current stable gluestack major compatible with the selected Expo SDK and NativeWind setup. If the user requests a specific major, use that major only when official docs and package metadata support it for the project.

If the requested or current gluestack major has no matching complete version reference in this skill, do not silently follow stale v3 steps. Check current official docs and then either:

- Ask before using the newly researched path when compatibility, source provenance, provider API, CLI/manual setup, or verification criteria are not fully established in this skill.
- Fall back to a documented older stable major only when the user approves or the request explicitly targets that major.
- Return `interactive_cli_required` or `blocked` when the official path cannot be verified without user action.

For gluestack-ui v3, read `references/v3.md` before installing packages, copying provider/components, running CLI commands, or verifying setup.
For other gluestack majors, read the matching version reference if present. If none exists, proceed only after establishing the package set, provider API, source ref, CLI/manual support, NativeWind compatibility, and verification criteria from official docs.

## Workflow

1. Inspect the project and determine standalone or orchestrated mode.
2. Confirm NativeWind is installed and configured before starting official gluestack setup. If NativeWind must be added and no orchestrator already owns that work, follow current NativeWind docs or stop with a precise prerequisite. For `GluestackUIProvider mode="system"`, treat NativeWind as configured only when the CSS file used by Metro contains all Tailwind directives and Tailwind uses static `darkMode: "class"`.
3. Select the gluestack major and setup path:
   - Prefer official manual installation for v3.
   - Use CLI-managed setup only when the user explicitly asks, or when current official docs make CLI the only reliable official path.
4. Follow the relevant version reference. For v3, use `references/v3.md`.
5. Repair gluestack integration points after setup: Tailwind content/theme, Metro NativeWind input path, Babel aliases/plugins required by copied official source, TypeScript aliases, and lockfiles.
6. In orchestrated mode, do not edit root layout or route/screen files unless the caller explicitly allowed layout wiring or route edits. Return exact provider and component import details for the orchestrator instead.
7. Verify that the official provider and each starter component import resolve from official gluestack source or verified CLI output.
8. Return the required handoff. If setup is blocked or interactive CLI is required, stop before claiming completion.

## Outcomes

Track exactly one outcome:

- `cli_initialized`: CLI init succeeded and generated the expected provider/config.
- `manual_installed`: official manual installation completed with official provider/component source copied into the app.
- `interactive_cli_required`: current official docs do not provide enough manual source/config detail, so a real terminal CLI run is required.
- `blocked`: official setup is unusable or cannot be verified.
- `fallback_approved`: the user explicitly approved a non-official fallback after being told it is not official gluestack setup.

Do not hand-write lookalike primitives and report them as gluestack. A fallback is allowed only after explicit user approval and must be labeled `fallback_approved`.

## Handoff

Always end with this handoff when used by another skill, and use the same shape for standalone final reports when practical:

```markdown
## Gluestack Handoff
- Outcome:
- Mode: standalone | orchestrated
- Version:
- Package versions:
- Docs/source ref:
- Package manager:
- App root:
- NativeWind prerequisite:
- NativeWind preflight:
- Global CSS path:
- Route root:
- UI component path:
- Provider file path:
- Provider import:
- Provider mode:
- Components installed/copied:
- Component exports:
- Official source paths:
- CLI component management:
- Theme/token status:
- Layout wiring touched:
- Route/screen files touched:
- Commands run:
- Files changed:
- Verification:
- Follow-up:
```

For `manual_installed`, include the official source URLs or repository paths used for the provider and copied components. For `cli_initialized`, state whether `gluestack-ui add` was verified. For `interactive_cli_required` or `blocked`, include exact attempted commands, TTY status when relevant, package/lockfile state, visible errors or hang points, and any partial files left behind.

## Boundaries

- This skill owns gluestack packages, provider/components, gluestack theme tokens, and gluestack-specific integration repair.
- This skill may touch NativeWind, Tailwind, Metro, Babel, TypeScript aliases, and lockfiles only as needed to make gluestack work.
- In standalone mode, this skill may wire the root layout or a minimal route/screen when that is necessary to verify the requested gluestack setup. In orchestrated mode, it must not edit layout or route/screen files unless the caller explicitly allows those edits.
- This skill does not choose the broader project shape, create a new Expo app, configure EAS, or own full scaffold verification unless the user asks for those tasks directly.
- When called by `expo-scaffold`, keep final integration decisions with the orchestrator and report enough detail through the handoff for it to wire screens and final verification.

## Useful Official Docs

- gluestack-ui install: `https://gluestack.io/ui/docs/home/getting-started/installation`
- gluestack-ui dark mode: `https://gluestack.io/ui/docs/home/theme-configuration/dark-mode`
- gluestack-ui theme customization: `https://gluestack.io/ui/docs/home/theme-configuration/customizing-theme`
- gluestack-ui source: `https://github.com/gluestack/gluestack-ui`
