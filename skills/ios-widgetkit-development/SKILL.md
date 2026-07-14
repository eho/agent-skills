---
name: ios-widgetkit-development
description: Implement, debug, review, and verify iOS WidgetKit extensions and AppIntent-configurable widgets, including Expo or expo-widgets generated targets. Use for new widget features, blank or red widgets, stale or ignored Edit Widget configuration, timeline and shared-storage failures, interactive Button/AppIntent behavior, generated Swift ownership, target membership, rebuild and fresh-widget decisions, performance diagnosis, or native acceptance evidence.
---

# iOS WidgetKit Development

Treat a widget as a cross-process native system, not as an app view. Prove each
boundary independently and require direct native evidence for user-visible
behavior.

## Load the Relevant Context

1. Read the repository instructions and current widget architecture.
2. Inspect the installed package source and generated native output for the
   exact dependency version. Do not rely on remembered Expo or WidgetKit
   behavior.
3. Read [references/generated-source-ownership.md](references/generated-source-ownership.md)
   before changing generated Swift, config plugins, Xcode target membership, or
   a dependency patch.
4. Read [references/appintent-configuration.md](references/appintent-configuration.md)
   for configurable widgets, AppEnums, DynamicOptionsProvider, or configuration
   values that appear stale or ignored.
5. Read [references/expo-widgets.md](references/expo-widgets.md) when the project
   uses Expo, `expo-widgets`, serialized JavaScript layouts, or prebuild.
6. Read [references/validation-ladder.md](references/validation-ladder.md) before
   native verification, interaction measurement, or declaring the work done.
7. Invoke `ios-simulator-automation` for app-to-SpringBoard or Widget Gallery
   automation. Keep this skill focused on WidgetKit architecture and evidence.

## Map the Runtime Pipeline

Write down the actual pipeline before editing:

```text
canonical config/source
  -> generator or config plugin
  -> generated Swift and Xcode target membership
  -> built host app and .appex
  -> AppIntent metadata and WidgetKit descriptor
  -> configured timeline provider
  -> timeline/shared storage
  -> render bridge
  -> SwiftUI widget
  -> SpringBoard interaction and reload
```

For each stage, record its owner, module/target, input, output, and one observable
probe. If the suspected failure boundary is unknown, add probes before fixes.

## Classify the Change

| Change | Minimum rebuild action |
| --- | --- |
| App-side data or serialized layout only | Run the new bundle and republish; rebuild only if the installed runtime cannot load it |
| Generated Swift, config plugin, entitlements, extension plist, target membership, or dependency native source | Prebuild if applicable, rebuild, and reinstall the exact `.app` |
| AppIntent parameter/schema or widget kind | Rebuild/reinstall, then remove and add a fresh widget |
| Documentation or tests only | Reuse the last artifact unless source inputs changed |

Do not use repeated rebuilds as a substitute for identifying the failing layer.

## Implement or Diagnose

### 1. Establish source and target ownership

- Identify the canonical source of every generated file.
- Treat generated native output as disposable evidence, not the editing source.
- Keep app-specific source out of vendor patches.
- Patch dependency source or its generator only for dependency-owned behavior.
- Verify each AppIntent/configuration type is compiled in the intended module
  and each generated source is present in exactly the intended target.
- Inspect the generated project after prebuild; plugin tests alone do not prove
  target membership.

### 2. Validate transport and storage contracts

- Keep widget payloads bounded and property-list safe.
- Reject `null`, `NaN`, `Infinity`, non-string dictionary keys, and unsupported
  bridged objects before publishing to shared defaults.
- Run `scripts/validate-widget-payload.py` against representative and maximum
  payloads when JSON props cross into `UserDefaults` or App Group storage.
- Exercise empty, maximum, interrupted-write, previous-version, and rollback
  states when storage is custom or patched.
- Separate maximum-size fixtures from distinct-text interaction fixtures.

### 3. Trace configuration end to end

For every configurable parameter, distinguish these checkpoints:

1. The picker exposes the intended options and default.
2. SpringBoard persists the selected value.
3. The timeline provider receives and decodes the selected value.
4. The render bridge receives the same value.
5. A fresh widget renders visibly different output.

Do not substitute metadata, registration, shared data, or unit tests for a later
checkpoint. Instrument the first mismatching boundary and make the smallest fix
that changes its evidence.

### 4. Keep render code extension-safe

- For a blank or red widget, inspect boundaries in runtime order: layout
  registration, timeline write/readback, serialized evaluation, native node
  decoding, then SwiftUI layout. Stop at the first failing boundary; do not rank
  a later-layer clue above an unverified earlier layer.
- Assume the widget runs in a separate process with a constrained lifecycle.
- Keep serialized render functions self-contained when a framework evaluates
  their source in another JavaScript context.
- Avoid module closures, unsupported globals, non-finite layout values, and
  modifiers the installed native decoder cannot consume.
- Test the serialized form, not only direct function invocation.
- Provide a valid placeholder/snapshot/empty state independently of app launch.

### 5. Implement interactions according to WidgetKit semantics

- Verify whether returning from the AppIntent already reloads the timeline
  before calling `WidgetCenter.reloadTimelines` explicitly.
- Avoid duplicate reload requests and large unchanged storage rewrites.
- Use invalidatable content or an equivalent supported feedback mechanism while
  asynchronous replacement completes.
- Measure tap-to-feedback and tap-to-new-content separately.
- Treat system scheduling latency as distinct from application persistence cost.

### 6. Build and inspect the exact artifact

- Build once per native-source revision and record the exact `.app` path.
- Run `scripts/inspect-widget-artifact.py --app <path>` to inventory the host,
  embedded extensions, entitlements, extension points, and AppIntent metadata.
- Confirm host and extension App Groups, extension embedding, widget kind, and
  generated metadata from the built artifact rather than source files alone.
- Install and verify that same artifact. Do not silently switch artifacts during
  acceptance testing.

### 7. Verify the native behavior

- Start from a fresh widget after configuration schema changes.
- Use a fixture whose expected change is visually and semantically distinct.
- Observe the complete configured state and every interaction/reset state.
- Capture accessibility or state evidence in addition to screenshots.
- Preserve logs from the provider/render boundary when configuration is the
  suspected failure.
- Follow the bounded recovery and cleanup rules from
  `ios-simulator-automation`.

## Apply Evidence Gates

Classify evidence explicitly:

- **Build:** the intended source compiled into the intended artifact.
- **Registration:** WidgetKit discovered and launched the extension.
- **Configuration:** the provider received the selected value.
- **Render:** the fresh widget displayed the expected state.
- **Interaction:** the control changed state and persisted/reset as specified.
- **Performance:** measured latency changed on the exact tested artifact.

Passing one category never implies another. Keep a core behavior unverified if
its native state was not observed, even when tests, metadata, and builds pass.
Manual deferral changes the delivery decision, not the acceptance truth; do not
label or archive the core behavior as implemented solely because verification
was deferred.

## Keep the Diagnosis Narrow

- State each hypothesis with the evidence it predicts.
- Add one probe or make one minimal change at a time.
- Revert disproven diagnostic work before trying another layer.
- Stop broad architectural changes when a lower-level trace can discriminate
  the hypotheses.
- Preserve project-owned uncommitted changes and generated-state evidence.

## Handoff

Use the evidence contract in
[references/validation-ladder.md](references/validation-ladder.md). Report the
canonical source changed, generated outputs inspected, exact artifact, fresh
widget status, observed and unobserved checkpoints, measured performance, and
cleanup. Never report “probably passed.”
