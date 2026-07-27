---
name: ios-simulator-automation
description: Coordinate reliable iOS Simulator verification across project-native commands, simctl, agent-device, and serve-sim. Use for repeated or cross-agent flows, Expo development clients, authentication, system surfaces, accessibility matrices, recovery, or formal evidence handoff.
metadata:
  author: eho
  version: '2.1.1'
---

# iOS Simulator Automation

Reuse compatible infrastructure, but bind observations to the runtime that produced them.

## Choose the workflow

For a healthy one-agent check with no shared evidence or configuration matrix, use:

`preflight -> open -> snapshot -> act -> re-snapshot -> assert -> cleanup`

Use the runtime ledger for feature delivery, cross-agent or reusable evidence, multi-criterion matrices, or a shared retry budget. Authentication alone does not require the ledger.

## Route and load

- Read the current `agent-device` skill for app-owned UI, assertions, app diagnostics, and React Native inspection.
- Read the current `serve-sim` skill for SpringBoard, system UI, hardware input, or system gestures.
- Read only the applicable recipe: [Expo](references/expo-dev-client.md), [authentication/backend](references/authenticated-flows.md), or [system/accessibility](references/system-surfaces.md).

Upstream skills and CLI help own command syntax. Stay with the tool that owns the current surface.

## Verify

1. Select an exact UDID. Run `scripts/check-simulator-environment.sh` when the current device/runtime has not already been verified.
2. For formal work, use `scripts/runtime_manifest.py` and its subcommand `--help`; create or validate the ledger, declare every criterion in its scope with a feature-unique ID such as `STORY:AC`, and bind the current runtime identity.
3. Reuse a build, Metro process, backend, or authenticated fixture only while its binding remains compatible. Rebuild or restart only for an invalidating change.
4. Observe behavior semantically after each interaction. A command exit or screenshot alone is not behavioral evidence; never guess coordinates without current accessibility geometry.
5. Record each failed or inconclusive complete strategy—not individual UI actions—as an attempt. Record successful independent checks as `observed` evidence, not attempts; retry budgets survive agents and resumed turns.
6. Rebind changed runtime identity; the ledger invalidates prior observations. Reviewers may reuse infrastructure, but must perform and record fresh behavioral observations.
7. Restore changed settings, stop task-owned helpers, move the ledger to `CLEANED`, then emit the final handoff. Evidence completeness is not product approval.

When a strategy fails, classify the symptom before trying one materially different fallback or environment repair. If that also fails or the state is unobservable, stop and record `not_observed`; do not create a fresh budget through another agent or device.

Assertion references must identify durable, non-secret artifacts containing the semantic result and binding. Do not destructively reset shared simulator state or broaden network exposure unless authorized. Never convert pending or unobserved evidence into a pass.
