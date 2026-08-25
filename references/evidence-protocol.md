# Evidence Protocol

## Evidence hierarchy

Prefer evidence in roughly this order when applicable:

1. Reproducible executable result on an immutable state.
2. Direct source inspection tied to an immutable revision.
3. Content digest or signed/versioned artifact identity.
4. Structured logs or machine-readable reports.
5. Durable human review tied to exact source locations.
6. Agent prose summary.

Lower-ranked evidence may still be sufficient when higher-ranked evidence is impossible, but state the limitation.

## Finding record

Each significant finding should carry:

- ID or stable short name;
- severity/impact;
- immutable reviewed state;
- concrete failure condition;
- expected behavior;
- observed behavior;
- owning layer;
- evidence;
- state: `OPEN`, `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.

## Fix evidence

A fix is not complete because code changed. Prefer all applicable layers:

- regression test demonstrates the old failure;
- regression passes with the fix;
- relevant broader suite passes;
- static/schema/type/lint checks pass where applicable;
- downstream composition still passes;
- external/local environment evidence is rerun if the fix affects it.

## Environment-qualified claims

Always qualify execution evidence with the environment when semantics may differ:

- OS/distribution and version;
- kernel when filesystem/container behavior matters;
- architecture;
- language/runtime version;
- dependency lock/resolution state;
- container/image identity;
- GPU/device/driver/CUDA state when relevant;
- skipped tests.

Example:

`Linux / Ubuntu 24.04 / x86_64 / CPython 3.12.5: 154 passed, 0 skipped`

is stronger than:

`tests pass`.

## Infrastructure vs code failure

A red status is not necessarily a failed implementation.

Before attributing failure to code, check whether:
- a runner actually started;
- checkout occurred;
- dependencies installed;
- test steps executed;
- credentials/billing/quota/network prevented startup;
- the result belongs to the current head.

Record infrastructure failure as `BLOCKED` unless it proves a product requirement failure.

## Disproving findings

Use `DISPROVED` only when the alleged failure condition was meaningfully tested or inspected.

Do not use `DISPROVED` for:
- "I couldn't reproduce it" under a materially different environment;
- stale code without checking the reported revision;
- a test that does not exercise the claimed path.

## Evidence closure

Every open finding should eventually converge to:

- `FIXED`: defect corrected and evidence rerun;
- `DISPROVED`: claimed defect not present;
- `DEFERRED`: valid but intentionally postponed;
- `BLOCKED`: cannot currently establish or repair because of an external constraint.

Avoid indefinite conversational debate.
