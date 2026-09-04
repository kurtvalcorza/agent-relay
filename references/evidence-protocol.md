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

Agent identity, model identity, provider identity, or a provenance footer does not change this hierarchy. Attribution records who or what produced a claim; it does not make the claim stronger evidence.

## Claim / evidence maturity

Claim maturity describes how strongly one relied-upon claim has been established. It does not replace finding lifecycle.

Use, when useful:

- `ASSERTED` — a human/agent/tool/durable record says the claim is true, but the relevant direct evidence has not yet been inspected;
- `INSPECTED` — the relevant source/artifact has been directly inspected against an immutable or otherwise well-qualified state, but the behavior has not necessarily been exercised;
- `EXECUTED` — the relevant behavior actually ran in a qualified environment and produced observable evidence;
- `VERIFIED` — Verifier behavior established the claim using the declared discriminating verification contract against the relevant immutable state/environment.

`VERIFIED` is deliberately one absolute token, not `VERIFIED@exploratory` versus `VERIFIED@consequential`. Assurance changes the verification contract that must be satisfied **before** the claim can be promoted; it does not change the meaning of the token after promotion.

A maturity statement should remain bound to the claim, verification contract, source snapshot, and environment where environment semantics matter. If a source revision later changes, the historical verification remains true only for the state it names; a new state requires new evidence rather than "downgrading" the old claim.

Only Verifier behavior promotes a consequential claim to `VERIFIED`. An Integrator may reuse adequate current `VERIFIED` evidence without manufacturing another verification pass, but must still make the separate readiness decision.

`VERIFIED` for one claim does not imply that the whole artifact is ready, mergeable, released, deployed, or approved.

## Assurance profiles

Assurance profile describes how demanding a mission's verification contracts must be. It does not grant permissions or authority.

Use a small provider-neutral vocabulary:

### `exploratory`

- rapid iteration;
- focused/local checks may be sufficient;
- independent verification is optional unless the mission says otherwise.

### `standard`

- immutable snapshot required for consequential claims;
- discriminating regression/inspection where applicable;
- relevant surrounding invariants/suite checked;
- environment-qualified execution when semantics depend on environment.

### `consequential`

- independent Verifier preferred or required by project policy;
- negative/discriminating controls where applicable;
- exact environment/artifact identity;
- end-to-end or externally relevant evidence where the gate depends on it;
- unresolved evidence gaps remain explicit;
- final readiness remains Integrator-owned.

The profile is selected from mission risk/impact and explicit user/project policy, never from agent identity or a rating of the user.

Execution/round budget exhaustion MUST NOT lower a declared assurance profile. Missing evidence remains `BLOCKED`, `DEFERRED`, or explicitly unverified according to the owning workflow.

## Verification contracts

A verification contract binds a consequential requirement/acceptance criterion to a declared falsifiable verification method before the result is relied upon.

Keep these layers distinct:

```text
requirement
  -> acceptance criterion
  -> verification procedure/oracle
  -> evidence produced
  -> Verifier judgment
```

A useful verification contract records:

- requirement/claim ID;
- acceptance criterion;
- failure condition the oracle must distinguish;
- exact verification procedure/oracle;
- source snapshot / artifact identity;
- required environment when applicable;
- expected evidence to capture;
- required assurance profile;
- independence requirement when policy calls for one.

For a consequential repaired defect, prefer a negative/discriminating control: demonstrate the old/pre-fix or deliberately mutated failure condition, then demonstrate the corrected behavior. A declaration-only check is insufficient.

If no practicable discriminating verification method exists, do not leave the field silently absent. Record:

```text
verification: none — <reason>
```

and treat the missing oracle as an explicit evidence limitation for readiness decisions.

A Builder or Executor may run the declared method, but a runtime's successful command is at most execution evidence until Verifier behavior establishes the claim.

Failure or inability to execute the verification contract remains visible as negative evidence, `BLOCKED`, or an unverified surface. Non-execution never reads as success.

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

### Review finding extension

When a finding is produced by a Reviewer, the review protocol extends this record rather than replacing it. Add, when applicable:

- review lens or lenses;
- confidence when useful;
- affected location or surface;
- violated requirement/invariant;
- recommended action.

Expected and observed behavior remain normative fields for significant review findings because they make the claimed defect falsifiable. See [`review-lenses.md`](review-lenses.md).

## Fix evidence

A fix is not complete because code changed. Prefer all applicable layers:

- regression/negative control demonstrates the old failure;
- regression passes with the fix;
- relevant broader suite passes;
- static/schema/type/lint checks pass where applicable;
- downstream composition still passes;
- external/local environment evidence is rerun if the fix affects it.

The declared verification contract should reuse these requirements rather than restating a weaker test.

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

Environment qualification must survive handoff/checkpoint rotation; dropping it silently weakens the claim.

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

## Finding lifecycle

This file owns the finding lifecycle. Other references and templates cite it
rather than restating it.

```text
OPEN -> FIXED | DISPROVED | DEFERRED | BLOCKED
```

- `OPEN`: observed and not yet dispositioned;
- `FIXED`: defect corrected and evidence rerun;
- `DISPROVED`: claimed defect not present;
- `DEFERRED`: valid but intentionally postponed; record owner/reason/revisit condition;
- `BLOCKED`: cannot currently establish or repair because of an external constraint.

`FIXED` and `DISPROVED` are resolutions: the finding needs no further tracking.
`DEFERRED` and `BLOCKED` are terminal dispositions that remain **tracked** — they
answer "what happened to this finding", not "may we stop carrying it". A handoff's
open-findings section therefore continues to list `OPEN`, `DEFERRED`, and
`BLOCKED` findings until they are resolved or carried into a successor cycle.

Avoid indefinite conversational debate.

### Distinguishing the four vocabularies

Four axes use overlapping words. A single record can carry all of them at once,
so read each token against its own field:

| Axis | Values | Owner |
|---|---|---|
| Finding lifecycle | `OPEN`, `FIXED`, `DISPROVED`, `DEFERRED`, `BLOCKED` | this file |
| Claim maturity | `ASSERTED`, `INSPECTED`, `EXECUTED`, `VERIFIED` | this file |
| Pass execution status | `RAN`, `FAILED`, `SKIPPED` | `iterative-review.md` |
| Cycle termination reason | `NO_NEW_FINDINGS`, `BOUND_EXHAUSTED`, `BLOCKED`, `CANCELLED` | `iterative-review.md` |

`BLOCKED` appears deliberately in two of them and means different things: a
**finding** is `BLOCKED` when that defect cannot be established or repaired; a
**cycle** terminates `BLOCKED` when the next required pass cannot proceed. A cycle
can terminate `BLOCKED` with no blocked finding, and a finding can be `BLOCKED`
inside a cycle that terminates `NO_NEW_FINDINGS`.

Claim maturity and finding lifecycle are separate axes: a finding may remain `OPEN` while a Builder's repair claim moves from `ASSERTED` to `EXECUTED`, and the finding closes only after the appropriate verification/disposition.

## Provenance is not verification

A durable finding, pass record, handoff, or review may include a footer such as:

```text
Generated by Claude Code
Agent Relay role: Reviewer
Review lenses: design
Source snapshot: <immutable-id>
```

Equivalent attribution may name OpenAI ChatGPT, Codex, Gemini CLI, a local agent, or another generating client/system. Model identity is optional when it cannot be established reliably.

This metadata is **self-reported provenance unless independently authenticated**. It must not be treated as proof that the named agent produced the content, as approval, or as independent verification. Use repository actors, signed commits/tags, immutable revisions, artifact digests, workflow identities, or other inspectable mechanisms when stronger provenance is required.
