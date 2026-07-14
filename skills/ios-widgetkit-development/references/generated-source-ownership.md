# Generated Source and Target Ownership

## Build an ownership map

For each native file involved in the widget, record:

| Question | Evidence |
| --- | --- |
| What is the canonical source? | App config, template, package generator, or checked-in Swift path |
| What regenerates it? | Prebuild plugin, package script, Xcode build phase, or manual source control |
| Which module owns the type? | Swift module name from the compiled target |
| Which target compiles the file? | Generated Xcode Sources phase or build log |
| Which bundle embeds the result? | Built `.app`, `.appex`, or framework |

Inspect both generator inputs and generated output. A correct plugin unit test
does not prove that Xcode compiled the resulting file into the correct target.

## Preserve type identity

Swift types with identical source are different when compiled into different
modules. This matters for `AppIntent`, `WidgetConfigurationIntent`, AppEnum, and
AppIntentsPackage discovery.

- Compile a configuration type in the module that owns it.
- Share one compiled module when the host and extension truly require the same
  type identity; do not compile duplicate source into both targets and assume it
  is shared.
- Do not add a generated widget source to the host app merely to expose intent
  metadata unless the framework contract explicitly requires that membership.
- Inspect the built AppIntent metadata and runtime logs after changing module
  ownership.

## Keep patches layered

Use a dependency patch only for dependency-owned files or generator behavior.
Do not use a vendor patch as the source of truth for product-specific Swift.

Preferred order:

1. Fix app-owned canonical source or config-plugin template.
2. Fix the dependency generator if it emits incorrect integration code.
3. Patch dependency runtime code only when its behavior is wrong and no
   supported configuration exists.
4. Regenerate the patch from a pristine dependency copy and check that it
   applies cleanly.

After prebuild, assert that generated product-specific files are absent from
unexpected app or dependency targets.

## Review checklist

- Canonical source is checked in.
- Generated output is not edited as the durable fix.
- Product-specific source is absent from vendor patches.
- Every relevant Swift file has one intended target membership.
- AppIntent and AppEnum types have deliberate module identity.
- The built `.appex` contains the expected metadata and entitlements.
- A clean prebuild reproduces the same graph.
