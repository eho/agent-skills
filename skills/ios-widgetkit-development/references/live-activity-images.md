# Live Activity Image Pipeline

Use this workflow when an image in a Lock Screen Live Activity or Dynamic
Island presentation is missing, blank, monochrome, gray, tinted, blurry, or
incorrectly scaled. Treat the symptom as a resource-pipeline failure until the
exact built artifact proves otherwise.

## Why view-level fixes often fail

SwiftUI frame modifiers change the displayed view size; they do not change the
logical size or scale of the decoded source image. A dynamically decoded
1024-by-1024 PNG with scale 1 is a 1024-point image even if the view later uses
`.frame(width: 30, height: 30)`. That is materially different from a compiled
named image set containing 30-, 60-, and 90-pixel renditions for a 30-point
asset.

Rendering modifiers also act too late to repair missing target membership,
stale generated resource references, an absent compiled rendition, or an image
that exceeds the presentation's resource limits. Do not cycle through
`.renderingMode(.original)`, template modes, accent APIs, or different bundle
lookups without first proving the earlier pipeline stages.

## Trace each boundary

Record one observable probe for every stage:

```text
canonical image
  -> crop, alpha, color space, and scale renditions
  -> named .xcassets image set
  -> podspec/package/plugin resource declaration
  -> generated Xcode resource build phase
  -> compiled Assets.car in the exact host and extension artifacts
  -> bundle-aware SwiftUI lookup
  -> Lock Screen and every Dynamic Island presentation
```

Stop at the first mismatch. A valid source PNG does not prove target membership,
and target membership does not prove the runtime presentation.

## Build a bounded named asset

Prefer a target-owned named asset catalog over loading a large loose PNG into
`UIImage` at runtime:

1. Determine the largest logical point size the product actually displays.
2. Crop the source to the intended content bounds. Preserve transparency when
   the design requires it; do not mistake a transparent canvas for useful
   padding.
3. Generate explicit 1x, 2x, and 3x renditions at the corresponding pixel
   dimensions. For a 30-point square, that means 30, 60, and 90 pixels.
4. Declare those files in one named `.imageset` with a valid `Contents.json`.
5. Keep the source asset and generated renditions under the canonical
   product-owned resource directory rather than patching generated Xcode output.

The 30-point example is illustrative, not a universal Live Activity icon size.
Choose dimensions from the actual layout and current platform constraints.

## Prove resource ownership

- Declare the asset catalog in every target that renders it, especially the Live
  Activity extension; include the host application only when the architecture
  also loads the asset there. In CocoaPods-based Expo modules, inspect the
  podspec resource bundle or resource glob and the generated Pods resource build
  phase.
- After changing a loose PNG to an asset catalog, regenerate the native project
  or refresh CocoaPods as required. A build error that still names the deleted
  PNG usually indicates a stale generated resource graph, not a reason to
  restore the obsolete file.
- Inspect the generated project after prebuild. Configuration-plugin tests or a
  correct podspec alone do not prove that the catalog entered the intended
  target.
- Preserve the repository's source-of-truth direction: edit the podspec,
  package, or generator that owns membership, then regenerate.

## Load the compiled asset directly

Use a bundle-aware named SwiftUI image from the resource bundle that owns the
catalog, for example:

```swift
Image("DinnerActivityIcon", bundle: resourceBundle)
  .resizable()
  .renderingMode(.original)
  .scaledToFit()
  .frame(width: iconSize, height: iconSize)
```

Adapt the bundle helper and image name to the project. Avoid decoding the same
asset with `UIImage(contentsOfFile:)` or `Data` merely to pass it back through
`Image(uiImage:)`; that discards the asset catalog's scale selection and makes
the logical-size contract easier to violate.

Use template or accented rendering only when the product intentionally wants
those semantics and the deployment target supports them. Full-color or original
rendering is not evidence that the resource was compiled, found, or accepted by
the Live Activity presentation.

## Inspect the exact built artifact

After a clean build that includes the resource-membership change:

1. Record the exact `.app` and embedded `.appex` paths.
2. Locate every relevant `Assets.car` in the host, extension, and resource
   bundles.
3. Use `assetutil --info` or the installed Xcode equivalent to confirm the named
   rendition exists with the intended scale and pixel dimensions.
4. Inspect the source renditions for width, height, alpha, and color type with a
   deterministic image tool.
5. If the architecture expects copies in both host and extension bundles,
   compare them; do not assume identical copies are required in every project.
6. Confirm the extension embedded in the exact app is the one that will be
   installed.

Source-level assertions should cover the image-set manifest, resource
declaration, named SwiftUI lookup, expected rendition metadata, and removal of
the obsolete loose-file or UIKit decode path. Artifact inspection remains a
separate gate.

## Require runtime proof

Install the same inspected artifact and start a fresh Live Activity fixture.
Check the image independently on:

- Lock Screen;
- compact leading and compact trailing presentations as applicable;
- minimal Dynamic Island;
- expanded Dynamic Island;
- StandBy or other supported presentation modes.

Capture screenshots or equivalent native evidence. Report source, build, and
artifact checks as passed when they pass, but keep rendering marked **manual
verification required** until the colored and correctly scaled image is
observed on the actual surface. Runtime confirmation can also disprove a
plausible pipeline fix; preserve that evidence and continue from the first
unproven boundary.

## Diagnostic matrix

| Evidence | Most likely next boundary |
| --- | --- |
| Source PNG is wrong | Crop/export pipeline |
| Source PNG is correct, generated project omits catalog | Podspec, package, plugin, or target membership |
| Build references a deleted loose PNG | Stale generated project or Pods graph |
| `Assets.car` lacks the named rendition | Resource compilation or bundle ownership |
| Rendition exists but has oversized scale-1 dimensions | Asset-set scale contract |
| Artifact is correct but lookup fails | Image name or bundle selection |
| Lookup and artifact are correct but surface is monochrome | Intended template/accent semantics or platform presentation behavior |
| Simulator/device shows the correct image | Render gate passed for that exact artifact and surface |
