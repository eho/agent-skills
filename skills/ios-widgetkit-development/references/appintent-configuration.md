# AppIntent Configuration Transport

## Trace checkpoints

Do not diagnose configurable widget behavior from the picker alone. Capture the
value at each checkpoint:

1. Generated parameter declaration and options/default metadata.
2. Widget Gallery/Edit Widget picker selection.
3. SpringBoard or AppIntents persistence/finalization logs.
4. `AppIntentTimelineProvider` configuration received by snapshot/timeline.
5. Configuration copied into any framework render environment or props bridge.
6. Visible output from a fresh widget.

Clear or timestamp diagnostic events before changing the selection so old
default renders cannot be mistaken for the new request.

## Interpret failures

| Observation | Likely boundary |
| --- | --- |
| Option missing from picker | Generated schema/metadata or stale descriptor |
| Picker saves but provider receives default or `nil` | AppIntent decoding, type identity, generated bridge, or cached instance |
| Provider receives correct value but render gets default | Provider-to-render bridge |
| Render gets correct value but output is unchanged | Filtering/render logic |
| Fresh instance works but existing one does not | Cached descriptor or saved configuration schema |

Configuration intent `perform()` is not a reliable edit-save hook. A
`WidgetConfigurationIntent` describes configuration; do not assume saving Edit
Widget calls `perform()` or use that assumption to force reloads.

## Handle AppEnum compatibility deliberately

Prefer typed parameters when they decode correctly. If direct native evidence
shows a generated AppEnum is persisted but becomes `nil` or a default at the
provider boundary:

1. Confirm the exact package, Xcode, and OS versions.
2. Inspect generated Swift and AppIntent metadata.
3. Rule out duplicate module identities and stale widget instances.
4. Use a primitive `String` parameter constrained by a
   `DynamicOptionsProvider` as a compatibility fallback when supported.
5. Preserve friendly option titles, a deterministic default result, stable raw
   values, and validation of unknown values.
6. Re-test all checkpoints with a freshly added widget.

Keep version-specific workarounds in a framework-specific reference or patch;
do not make primitive strings a universal rule.

## Cache discipline

- Remove and add a fresh widget after changing parameters, defaults, options,
  AppEnum cases, intent module ownership, or widget kind.
- Verify the unfiltered provider list before treating Widget Gallery search as
  registration evidence.
- Retry an unhealthy gallery only within the project or simulator automation
  budget. Distinguish a globally empty provider service from a product-specific
  missing widget.
- Never report configuration as passed without observing a value-dependent
  render state.
