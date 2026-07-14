# Recovery and Stop Conditions

Read this reference before switching tools, resetting automation state, or trying another Simulator.

## Diagnose Before Retrying

Capture the smallest useful state:

- current device and foreground app
- one fresh accessibility snapshot
- short, marked logs for a runtime failure
- current Metro/serve-sim listener ownership
- exact app artifact or source revision

Do not paste full stale logs into context. Do not repeat taps while the same overlay, wrong host, or unavailable service remains.

## Recovery Ladder

Use the first applicable step, then re-check the precondition:

1. Re-snapshot and use a durable selector or current ref.
2. If iOS accessibility grouping hides a child, derive app coordinates from `agent-device snapshot -i -c --json` and diff afterward.
3. If the surface is system-owned or an `agent-device` gesture fails once, switch only that segment to `serve-sim`.
4. Resolve the target from `serve-sim` accessibility data. For a long press or drag, keep `begin -> move/end` on one WebSocket.
5. If the automation daemon is stale, close the task session and restart with a new task-local state directory.
6. If the Simulator runtime itself is unhealthy, try one alternate installed Simulator/runtime.

Stop after the relevant fallback fails. More devices, rebuilds, and repeated gestures rarely add evidence.

## Stop Immediately When

- the target is absent from accessibility data and no product-supported navigation can expose it
- the app or system reports a reproducible product error
- the exact required state is not observable with available tools
- the same environment symptom survives one clean retry and one alternate Simulator/runtime
- continuing requires destructive reset, unrelated process termination, credentials, or a materially different build

Record the unverified acceptance criteria as a manual checklist. State the attempted devices, artifacts, observed intermediate state, and why automation stopped.

## Evidence Standard

Use semantic assertions for behavior and screenshots only for visual proof. For cross-surface flows, preserve an observation at each boundary:

1. app state before leaving the app
2. system state after the system interaction
3. app state after returning, when applicable

Separate “tool command completed” from “expected UI was observed.” Only the latter supports a pass.
