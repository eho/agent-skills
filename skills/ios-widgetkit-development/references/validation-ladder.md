# Widget Validation Ladder

## Evidence categories

Collect each category independently:

| Category | Required evidence |
| --- | --- |
| Deterministic logic | Focused tests for selection, reset, serialization, and malformed inputs |
| Storage | Property-list validation, maximum payload, interrupted write, rollback, and decode |
| Generated integration | Clean prebuild plus target/source/entitlement inspection |
| Build | Exact `.app` and `.appex` paths, source revision, zero relevant errors |
| Registration | Installed extension identity and WidgetKit discovery/launch evidence |
| Configuration | Selected raw value observed in the configured provider |
| Render | Fresh widget displays the expected value-dependent state |
| Interaction | Before/after state, persistence or reset, host app foreground state |
| Performance | Repeated tap-to-feedback and tap-to-content timings on the same artifact |

Do not let a higher-volume lower category replace a missing user-visible one.
One thousand passing tests do not prove a configured widget rendered correctly.

## Fixture selection

Use different fixtures for different questions:

- **Maximum:** storage size, truncation, large typography, and boundary entries.
- **Distinct interaction:** visibly different phrases/states for Next, Reveal,
  toggles, or counters.
- **Timed boundary:** controlled timestamps for passive timeline transitions.
- **Ordinary:** realistic app-published data restored after verification.

Never use visually identical maximum entries to prove an interaction changed.

## Fresh-widget rule

Remove and add a new widget after changing:

- AppIntent parameters, defaults, options, or enum cases;
- configuration intent module identity;
- widget kind or generated descriptor metadata;
- provider type or extension registration.

Record whether the observed widget was fresh or retained. Do not infer fresh
schema behavior from an existing instance.

## Performance measurement

Measure at least these timestamps:

1. Input dispatched.
2. Immediate visual/invalidation feedback visible.
3. New content visible in accessibility/render state.
4. Persistent state committed, when relevant.

Measure multiple runs before and after a change. Separate application work from
WidgetKit-controlled scheduling and archive installation.

## Acceptance gate

- Mark **pass** only when the required native state was observed on the exact
  artifact.
- Mark **manual verification required** when the criterion is unobservable or
  the bounded environment retry is exhausted.
- Mark **blocked** when the product criterion fails or required evidence cannot
  be obtained and deferral is not accepted.
- Keep core unobserved behavior out of an Implemented/shipped state. A manual
  deferral must remain visible in status and release criteria.

## Handoff template

```text
WidgetKit development handoff
- Canonical source changed:
- Generated output inspected:
- Dependency patches:
- Source/target membership:
- Revision and exact app artifact:
- Host app and widget extension IDs:
- Simulator/device and OS:
- Deterministic and storage checks:
- Registration observed:
- Configuration checkpoints observed:
- Fresh widget: yes | no
- Render states observed:
- Interaction states observed:
- Performance measurements:
- States not observed:
- Environment/tool failures:
- Evidence paths:
- Fixtures restored and cleanup completed:
- Decision: pass | manual verification required | blocked
```
