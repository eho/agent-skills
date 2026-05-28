---
name: expo-ios-agent-device
description: Drive the Kotoba Expo iOS simulator effectively with agent-device. Use when verifying iOS UI behavior, testing Expo dev-client flows, seeding
simulator app state, diagnosing accessibility selectors, or automating simulator QA for this repo.
---

# Expo iOS Agent Device

Use this skill when automating Kotoba on the iOS simulator with `agent-device`.

## Preflight

Run these before planning commands:

```sh
agent-device --version
agent-device help workflow
agent-device devices --platform ios
agent-device apps --platform ios

For debugging, logs, traces, or runtime failures, also read:

agent-device help debugging

Use one stable session id for mutating commands.

## Preferred Launch Flow

Prefer agent-device metro prepare for Expo simulator automation instead of relying on the Expo dev-client launcher or recently opened URLs.

agent-device metro prepare \
  --public-base-url http://127.0.0.1:8081 \
  --project-root /Users/eho/dev/komorebi \
  --port 8081 \
  --kind expo \
  --platform ios \
  --session <session>

Launch the dev client with the bundle URL returned by Metro prepare, typically:

agent-device open com.edwinho.kotoba \
  'http://127.0.0.1:8081/index.bundle?platform=ios&dev=true&minify=false' \
  --session <session> \
  --platform ios \
  --device "iPhone 17 Pro" \
  --relaunch

Do not rely on “Recently opened” dev-client URLs. They may point at stale LAN IPs such as 192.168.x.x:8081.

Do not use raw http://127.0.0.1:8081 or exp://127.0.0.1:8081 as the primary launch target unless you have verified it opens the app bundle. In this repo, those c
an land in the runner shell instead of Kotoba.

## After Launch

Expect the Expo dev menu after bundle load. Dismiss it before verifying app behavior.

agent-device snapshot -i --session <session> --platform ios
agent-device press 'label="Close"' --session <session> --platform ios
agent-device wait text "YOUR PHRASES" 5000 --session <session> --platform ios

If the app is still on Loading from Metro..., Downloading 100%..., or the dev menu, fix launch state before testing the feature.

## Interaction Pattern

Use this loop:

open -> snapshot -i -> act -> re-snapshot -> verify -> close

Selector priority:

1. Durable selectors, especially test IDs:

    agent-device press 'id="library-card-update-button"' --session <session> --platform ios

2. Current snapshot refs:

    agent-device snapshot -i --session <session> --platform ios
    agent-device press @e46 --session <session> --platform ios

3. Coordinates only after inspecting layout:

    agent-device snapshot -i -c --json --session <session> --platform ios

Use snapshot -i -c --json when accessibility grouping hides an actionable child, a ref is not hittable, or aggregate text suggests a control exists but the
simulator cannot press it.

## Nested Pressables

For controls inside expandable cards, verify both action and parent behavior.

agent-device snapshot -i --session <session> --platform ios
agent-device press @e46 --session <session> --platform ios
agent-device snapshot -i --session <session> --platform ios

Confirm the child action fired and the parent row did not collapse unless collapse is expected.

## Text Entry

Prefer fill with a small delay, then wait for UI changes.

agent-device fill @e11 "Hello" --delay-ms 80 --session <session> --platform ios
agent-device wait text "In Library" 3000 --session <session> --platform ios

On iOS, do not assume keyboard dismiss works. Prefer visible app controls such as Dismiss keyboard, Clear input, or tapping a non-input control.

## Seeding Simulator State

When deterministic UI state is required, seed local SQLite deliberately and narrowly.

First locate the app container:

xcrun simctl get_app_container booted com.edwinho.kotoba data

Inspect schema before writing SQL. Current phrase columns are camelCase, for example:

inputText
inputMode
libraryScope
translationSchemaVersion
enrichmentPromptVersion

Example stale-row setup:

sqlite3 '<container>/Documents/SQLite/kotoba.db' \
  'update phrases set enrichmentPromptVersion=1 where id=58;'

Restore seeded rows afterward to avoid contaminating later manual testing.

When using simctl or reading app containers, expect sandbox escalation. Keep commands narrow: get container path, inspect schema, update one row, restore one row.

AsyncStorage settings may be inspected at:

Library/Application Support/com.edwinho.kotoba/RCTAsyncLocalStorage_V1/manifest.json

Use this to confirm language or runtime settings before attributing behavior to UI bugs.

## Translation Runtime Checks

If a translation action fails, snapshot immediately and record the visible error.

agent-device snapshot -i --session <session> --platform ios

Separate runtime/setup limitations from feature UI failures. Do not keep repeating taps against a bad runtime state.

## Cleanup

Always close the session.

agent-device close --session <session> --platform ios