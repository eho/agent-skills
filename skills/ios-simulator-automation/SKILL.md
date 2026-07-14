---
name: ios-simulator-automation
description: Coordinate reliable iOS Simulator automation across agent-device and serve-sim. Use for app-plus-system flows, Expo dev-client testing, SpringBoard or system-surface interaction, accessibility-derived fallback gestures, simulator-state recovery, bounded retries, cleanup, and evidence handoff when either upstream tool alone is insufficient.
---

# iOS Simulator Automation

Compose `agent-device` and `serve-sim`; do not replace or restate their versioned guidance.

## Load the Upstream Guidance

Before planning or running automation:

1. Read the installed `agent-device` and `serve-sim` skills completely.
2. Run `agent-device --version`, require the minimum version stated by its skill, and read `agent-device help workflow`.
3. Read `agent-device help debugging` only for logs, traces, hangs, alerts, or runtime failures.
4. Follow `serve-sim` prerequisites and read only its references needed for the selected system interaction.

Treat the installed skills and CLI help as the source of truth for command syntax. This skill owns routing, lifecycle, fallback, and evidence.

## Choose the Narrowest Tool

| Need | Primary tool |
| --- | --- |
| App navigation, selectors, text entry, assertions, app logs, network, React Native inspection | `agent-device` |
| SpringBoard, Widget Gallery, Control Center, hardware buttons, simulator stream, accessibility tree outside the app | `serve-sim` |
| Build, install, signing, native compilation | Project-native Expo, Xcode, or `simctl` workflow |

Stay with one tool while it can observe and control the current surface. Switch at an explicit app/system boundary or after one diagnosed tool limitation. Do not alternate tools speculatively.

## Establish a Clean Automation Context

1. Select one Simulator by UDID or exact name. Do not let two booted devices make routing implicit.
2. Choose one task-specific `agent-device` session and state directory. Pass the same `--session`, `--state-dir`, platform, and device to its commands.
3. Run `scripts/check-simulator-environment.sh` from this skill. Use `--device` when multiple Simulators are booted and raise `--min-free-gib` for native builds when the project requires it.
4. Inspect existing Metro and `serve-sim` listeners before starting new ones. Reuse a healthy project-owned Metro process; remove only stale task-owned helpers.
5. Record the app identifier, artifact or source revision, Simulator/runtime, session, and expected observable result.

Never erase a Simulator, reset app data, kill unrelated processes, or replace an installed build without authorization.

## Run the Primary Loop

Use `agent-device` for app-owned UI:

`open -> snapshot -i -> act -> re-snapshot -> assert -> close`

- Prefer durable selectors, then current snapshot refs.
- Re-snapshot after navigation or dynamic UI changes.
- Use coordinates only after `snapshot -i -c --json` exposes the target rectangle and refs/selectors cannot act.
- Keep mutating commands against one session serial.
- Verify named expectations with `wait`, `is`, `get`, or `find`; a screenshot alone is not an assertion.

For an Expo dev client, read [references/expo-dev-client.md](references/expo-dev-client.md).

## Cross Into a System Surface

Use `serve-sim` only for the system-owned portion:

1. Confirm the intended Simulator and discover the live stream URL/port from quiet JSON output.
2. Fetch the current accessibility tree and locate the target by label, identifier, or other stable property.
3. Derive the target center from its frame and normalize it against the current display configuration.
4. Fail if the target is absent. Never guess a coordinate after an accessibility lookup misses.
5. Use `tap` for taps. Use one persistent WebSocket for a reliable long press, drag, or multi-step gesture.
6. Re-read accessibility state or return to `agent-device` and assert the resulting app state.

Read the upstream `serve-sim` gesture, endpoint, and workflow references before bypassing its CLI.

## Bound Recovery

Classify a failure before retrying:

- **Product failure:** the expected observable result is wrong. Preserve evidence and stop retrying the same action.
- **Tool limitation:** the element is visible but the current tool cannot act. Try the documented fallback once.
- **Environment failure:** stale daemon, wrong device, bad Metro route, missing provider registration, or unhealthy runtime. Repair once, then try at most one alternate Simulator/runtime.
- **Unobservable criterion:** no supported tool exposes the required state. Defer it to manual verification explicitly.

Read [references/recovery-and-stop-conditions.md](references/recovery-and-stop-conditions.md) before a fallback or second attempt.

## Clean Up and Hand Off

Close the `agent-device` session and stop task-owned `serve-sim`, Metro, recordings, traces, and debug overlays. Restore permissions, seeded data, and settings changed for the task.

Report:

```text
iOS Simulator automation handoff
- App/artifact and revision:
- Simulator/runtime:
- Primary tool and fallback used:
- Observed:
- Not observed:
- Environment/tool failures:
- Evidence paths:
- Cleanup completed:
- Decision: pass | manual verification required | blocked
```

Never convert an unobserved criterion into a pass.
