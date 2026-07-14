# Expo and expo-widgets Integration

Inspect the installed `expo-widgets` package and generated iOS project before
applying this reference. APIs and generator output may change between versions.

## Separate the three source layers

1. **Product source:** widget configuration, TypeScript render code, config
   plugin inputs, and product-specific native templates.
2. **Generated output:** prebuilt Xcode project and widget Swift files. Use this
   to inspect results, not as the durable edit location.
3. **Dependency source:** Expo generator/runtime code. Patch only dependency
   behavior and regenerate the package patch from a pristine copy.

Do not place a product-specific generated Swift file into a dependency patch.
Do not compile the generated widget source into the host app unless the current
Expo contract explicitly requires it.

## Test the serialized runtime

Expo widget layout functions may be serialized and evaluated inside a small
JavaScriptCore context in the widget extension.

For a blank or red surface, check this order and stop at the first failure:

1. The expected layout registration key exists.
2. Timeline props were written and can be read back from shared storage.
3. The exact stored function evaluates with the exact stored props.
4. The resulting node tree decodes through the installed native bridge.
5. The decoded modifiers produce a finite SwiftUI layout.

Do not fix helper scope, payload nullability, and layout modifiers in one pass;
each belongs to a different boundary and needs its own predicted evidence.

- Keep the registered function self-contained.
- Avoid references to module-scoped helpers unless the generated serialized
  function includes them.
- Inspect the stored function string for transformed helper references.
- Evaluate the stored layout through the same runtime entry point when a red
  error surface lacks readable details.
- Reject non-finite layout values such as `Infinity` even if app-side rendering
  accepts them.
- Test the serialized representation as a regression artifact.

## Keep props property-list safe

`expo-widgets` may persist timeline props through shared `UserDefaults`. JSON
values such as `null` can bridge to `NSNull`, which is not property-list safe.

- Omit optional values or map them to an explicit supported representation.
- Validate nested arrays and dictionaries, not only top-level fields.
- Bound total payload size and test maximum real data.
- Keep product JSON snapshots separate when their schema legitimately includes
  nullable values.

Use `../scripts/validate-widget-payload.py` on representative timeline props.

## Treat prebuild as compilation input

- Place config plugins in an order that matches Expo mod execution, not a
  guessed top-to-bottom sequence.
- Run a clean prebuild when generator inputs change.
- Inspect the generated Xcode Sources phases, entitlements, extension plist,
  and AppIntent declarations.
- Build and verify the exact regenerated artifact.
- Add a static verifier for project-critical patch markers and forbidden target
  membership when the dependency patch is long-lived.

## Configuration compatibility

When generated AppEnum parameters appear in the picker but arrive at the
provider as `nil`, follow the AppIntent trace before changing architecture. If
the failure is reproducible after module and cache checks, a generator-level
fallback to primitive strings plus `DynamicOptionsProvider` can preserve picker
labels while avoiding the failing enum decode path.

Keep that workaround version-scoped and require native evidence. Remove it when
the installed Expo version demonstrably transports the typed values correctly.

## Interactions

Inspect the dependency AppIntent implementation before adding reload calls.
WidgetKit can reload a timeline after an interactive intent returns; an
additional explicit `reloadTimelines` may duplicate work. Measure the current
path and use supported invalidatable content for immediate feedback while the
new archive is installed.
