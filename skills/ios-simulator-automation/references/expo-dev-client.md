# Expo Dev Client

Read this reference only when the target is an Expo Go host or Expo development build.

## Start Metro Deliberately

- Use the repository's package-manager and Expo commands.
- Prefer `agent-device metro prepare --kind expo` when preparing Metro for automation.
- Supply the actual project root, port, public or proxy base URL, platform, and the task's session/state context.
- Reuse a healthy Metro process for the same project and revision. Do not start competing bundlers on the same port.

## Open the Correct Host and URL

- For Expo Go, open the known host plus the provided project URL. Do not invent a bundle identifier.
- For a development build, open the installed dev-client app identifier or name, then open a provided dev-client URL when the workflow requires one.
- Do not trust a “Recently opened” entry: it may retain a stale LAN address or project route.
- Do not infer success from a URL-open exit code. Snapshot immediately and verify that the intended app UI—not the runner shell, loading screen, or dev menu—is foregrounded.

If no app identifier or URL can be discovered from the task or normal project metadata, stop and request it instead of guessing.

## Stabilize Before Verification

1. Wait for bundle loading to finish.
2. Snapshot interactive state.
3. Dismiss a visible Expo dev menu or error overlay only when it is not the test target.
4. Assert a stable, app-owned element before beginning the feature flow.

For JavaScript-only changes with Metro attached, use the reload command documented by current `agent-device help workflow`. For native changes, install or launch the newly built artifact; Metro reload cannot validate native code.

## Avoid Unnecessary Native Rebuilds

Build once per native-code revision and retain the exact `.app` identity in the handoff. Reuse that artifact for UI attempts unless native sources, generated native files, entitlements, extensions, or build configuration changed.
