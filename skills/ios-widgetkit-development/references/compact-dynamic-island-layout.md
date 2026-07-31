# Compact Dynamic Island Layout

Use this workflow when a compact Dynamic Island capsule appears excessively
wide, contains a large blank center span, loses its trailing timer, or gives
inconsistent results after rebuilds.

## Classify the presentation first

Do not rely only on the user's family name. A screenshot with content on the
left and right of the sensor is the compact presentation:

- `compactLeading` and `compactTrailing` render simultaneously around the
  sensor;
- `minimal` is the single small presentation iOS uses when it gives the
  activity minimal space, such as when multiple activities compete;
- `expanded` uses its expanded regions after interaction.

If the screenshot shows a leading icon and trailing countdown, changing the
`minimal` closure cannot fix it. Map the visible elements back to their actual
Dynamic Island closures before editing.

## Separate system geometry from app layout

WidgetKit places `compactLeading` and `compactTrailing` on opposite sides of the
camera and TrueDepth obstruction. The app can control each region's content,
its proposed size, and supported content margins. It cannot set the overall
compact capsule width or collapse the system-owned center obstruction.

Do not attribute all black space to the camera, though. A child that accepts a
large width proposal can inflate one or both compact regions around that fixed
center span.

Model the capsule as:

```text
outer margin
  + compact-leading allocation
  + system camera/TrueDepth obstruction
  + compact-trailing allocation
  + outer margin
```

Measure or log each term when possible. A visual gap alone cannot identify which
term is excessive.

Use edge-specific margins when only the outer silhouette needs breathing room.
For example, a leading margin on `compactLeading` and a trailing margin on
`compactTrailing` protect the outer edges without also adding inner margins
beside the sensor. A generic horizontal margin on both regions can add avoidable
width while appearing to be a harmless padding adjustment.

## Treat live timer text as a special layout participant

Self-updating SwiftUI timer text does not always behave like a static label.
`Text(date, style: .timer)`, `Text(timerInterval:)`, or a timer inside a
`TimelineView` can request space based on future or fallback content rather than
only the currently visible glyphs.

Trailing alignment changes where glyphs sit inside the proposed width; it does
not necessarily reduce the width requested from WidgetKit. Likewise, removing
an app `Spacer` or changing only `contentMargins` cannot correct a child that is
requesting the maximum compact-region allocation.

## Do not assume `fixedSize` is safe

`fixedSize` is appropriate for some ordinary compact content, but do not apply
it reflexively to a self-updating timer or its outer timeline container. On
some runtime and timer combinations it can suppress the timer entirely. iOS may
then fall back to maximum compact-region allocations, producing both symptoms
at once:

- the countdown disappears; and
- the capsule remains or becomes unusually wide.

Applying `fixedSize` directly to the timer instead of the outer container is not
proof of safety. Validate both visibility and geometry on a positively fresh
Live Activity before keeping either form.

## Prove every variant uses a fresh activity

A rebuilt application or extension does not guarantee that the visible Live
Activity was recreated from that build. Retained activities, stale state, and
development-client lifecycle behavior can make a failed or static probe appear
to validate a source change.

Before comparing variants:

1. Bind the test to an exact `.app` and embedded `.appex`.
2. Confirm the intended probe or source revision compiled into that extension.
3. End the prior test activity and verify that it actually ended.
4. Create a new, identifiable activity after installing the candidate.
5. Wait for the transient launch presentation to settle into steady compact
   presentation before measuring.

Do not treat a launcher action as successful merely because it returned without
error. If it reports that zero activities ended, or ActivityKit enumeration is
unreliable in the current development lifecycle, the next screenshot is not a
clean comparison.

For destructive reset methods such as uninstall/reinstall, use a disposable
simulator or isolated clone when preserving the user's installed app and data
matters. Apply the same reset protocol before every candidate so freshness
cannot favor one variant.

## Run discriminating probes

Change one variable at a time:

1. Capture a fresh steady-state baseline at native framebuffer resolution.
2. Record device, OS, display scale, artifact, activity identity, visible timer
   value, and capsule bounds.
3. Replace only the compact timer with a same-looking static label in a
   disposable build. If the capsule contracts, the timer path is inflating a
   content region; if it does not, investigate other region content, margins,
   or system geometry.
4. Restore the live timer and test one sizing strategy at a time.
5. Reject any candidate where the live timer disappears, clips supported
   values, stops updating, or causes maximum-region fallback.

System logs can provide useful corroboration when they expose the obstruction
width and compact-region allocations. Screenshot measurement remains necessary
to bind those allocations to the actual visible result. Convert pixels to
points using the captured framebuffer scale rather than estimating from a
resized screenshot.

Treat another application's source as a candidate pattern, not validation. An
unconstrained timer in a working project does not prove that the same timer,
content, OS, and activity state produced a narrower capsule. Compare built
artifacts and fresh runtime measurements before copying its modifiers.

## Bound only the content that over-requests width

When a live timer is proven to inflate `compactTrailing`, prefer a compact-only
explicit width on the timer content rather than intrinsic-sizing the whole
timeline or changing unrelated presentations:

```swift
Text(deadline, style: .timer)
  .monospacedDigit()
  .lineLimit(1)
  .minimumScaleFactor(0.8)
  .frame(width: compactTimerWidth, alignment: .trailing)
```

Derive `compactTimerWidth` from the supported countdown formats, font, locales,
Dynamic Type behavior, and target OS versions. A width that worked for one
product, such as 48 points for a short minute-and-second countdown, is evidence
for that product—not a universal constant.

Keep the bound surface-specific. Lock Screen and expanded presentations often
need different widths, while compact-leading icons or minimal presentations may
still use intrinsic sizing safely.

## Verify the supported boundary

For the final candidate, require:

- a fresh Live Activity created after installing the exact candidate artifact;
- a visible, updating timer across representative short and long values;
- measured capsule contraction relative to the controlled baseline;
- preserved compact outer margins and leading content;
- no regression to minimal, expanded, Lock Screen, or accessibility behavior;
- focused source tests that prevent reintroducing the failed sizing modifier;
- an arm64 build and inspection of the embedded extension.

Report the remaining center span as expected system-owned geometry only after
the app-controlled region widths have been measured or bounded. State clearly
that WidgetKit provides region content and margin controls, not a direct
overall compact-capsule width control.

## Diagnostic matrix

| Evidence | Interpretation and next step |
| --- | --- |
| Static label and live timer have the same wide capsule | Investigate other region content, margins, transient state, or system geometry |
| Static label contracts the capsule | Live timer or timeline layout is inflating a compact region |
| `fixedSize` hides the timer and regions reach maximum width | Remove it; test a bounded compact-only timer width |
| Candidate appears narrow but no old activity was positively ended | Treat as stale evidence and repeat with a fresh activity |
| Explicit width keeps the timer live and contracts the capsule | Validate formats, locales, OS versions, and other presentations |
| Only the center obstruction remains | App-controllable width is addressed; document the system-owned remainder |
