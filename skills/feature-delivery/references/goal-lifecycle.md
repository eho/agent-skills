# Goal Lifecycle

Use goals as durable outer objectives, not as detailed workflow storage.

## Portable behavior

- Inspect goal state when the runtime exposes it.
- Reuse a matching active goal.
- Create a goal only after an explicit user request to do so.
- Keep queue, issue, PR, review, and audit state recoverable from the design document and GitHub.
- Continue a goal across interruptions by rehydrating external state rather than trusting memory.
- Let the runtime own pause, usage-limit, and token-budget states.
- Mark complete only after the feature completion invariant is independently rechecked.
- Mark blocked only when no meaningful work remains, the blocker is concrete, and the runtime's blocked-state policy is satisfied.

Do not hard-code one vendor's slash command or tool name into the workflow. Use the goal capability exposed by the current runtime.

## Recommended objective

```text
Use the feature-delivery workflow to fully deliver <design-doc>. Reconcile every
in-scope story to GitHub, implement and independently review each story, merge it
according to repository policy, remediate final-audit findings, and finish only
when all stories are merged, required verification passes, documentation is
current, and the final audit reports Ready. Issue creation, PR approval, or
creation of follow-up issues does not constitute completion.
```

Adjust the final threshold only when the user explicitly permits `Ready with follow-ups`.

## Goal versus story blockers

A story blocker is local state. Keep the goal active while any of these remain possible:

- independent stories can progress;
- an existing PR can be reviewed or repaired;
- issue or dependency metadata can be reconciled;
- diagnostics can narrow the blocker;
- audit findings can be classified or remediated.

Escalate to a goal blocker only when the remaining work requires an external state change or a product decision that the agent cannot safely infer.
