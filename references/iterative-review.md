# Bounded iterative review

Iterative review is a composition of ordinary Agent Relay passes over evolving durable state. It is not a sixth role, a second finding lifecycle, or an autonomous swarm primitive.

A runtime may automate the sequence; Agent Relay defines what each durable pass must preserve.

## Cycle metadata

A review cycle MAY add metadata to ordinary Agent Pass Records:

- cycle ID;
- planned lens sequence;
- current pass/round number;
- previous and current immutable snapshot;
- cycle budget;
- per-pass execution status;
- termination reason;
- mutation-surface transition when a pass mutated state.

Prefer extending `assets/AGENT-PASS.md` over inventing a parallel `REVIEW-CYCLE.md` record and lifecycle.

## Planned versus executed passes

The planned sequence and the evidence of what actually executed are different facts.

Example:

```text
Planned lenses: design -> security -> reliability

Pass 1: design      RAN
Pass 2: security    FAILED
Pass 3: reliability SKIPPED
```

A planned pass that failed or was skipped produced no review evidence. Its surface remains unverified.

A cycle MUST NOT convert a non-executed pass into "no findings".

## Per-pass execution status

Use these execution statuses for planned passes:

- `RAN` — the pass actually executed against the recorded snapshot;
- `FAILED` — the pass began but did not produce a valid result;
- `SKIPPED` — the planned pass did not run.

These are pass execution statuses, not finding lifecycle states and not claim
maturity. The axis deliberately uses `RAN` rather than `EXECUTED`: `EXECUTED` is
a claim-maturity state in `evidence-protocol.md`, and a single record carries
both fields. A pass may be `RAN` while every claim it produced is still
`ASSERTED`.

## Finding continuity across snapshots

A finding receives a stable ID when first observed and preserves the immutable snapshot where the failure condition was observed.

Across later passes, a cycle may record observation metadata such as:

- `NEW` — first observed in this cycle;
- `PERSISTS` — re-observed on a later snapshot;
- `NOT_OBSERVED` — not seen by this pass.

These labels are observation metadata only. `NOT_OBSERVED` is not `DISPROVED`, and a Builder saying a finding is fixed is not `FIXED`.

The finding lifecycle is owned by [`evidence-protocol.md`](evidence-protocol.md) and is not restated here.

During an active cycle a finding may remain `OPEN`. Before the cycle is durably terminated, every unresolved finding must receive an explicit terminal disposition or remain attached to a successor active cycle.

A Builder revision may propose a disposition, but closure still requires the existing evidence/Verifier rules.

## Carry-forward rule

Open findings MUST be carried forward across changed snapshots until they are dispositioned. Changing the Reviewer lens does not make earlier findings disappear.

A runtime may insert an Integrator between every review and repair pass, but this is not required when the finding owner/action is already unambiguous. What is required is durable carry-forward of unresolved findings and ownership.

## Plan/design review

Plans, designs, specifications, and ADRs are ordinary durable artifacts and can be reviewed before implementation.

A recommended route is:

```text
Builder produces/revises durable plan
  -> Reviewer[design]
  -> carry findings forward
  -> Builder revises within authority
  -> Reviewer[security]
  -> carry findings forward
  -> Builder revises
  -> Reviewer[reliability]
  -> Integrator reconciles unresolved findings
  -> Verifier checks consequential factual/spec claims where required
```

The plan is never "locked" merely because a review cycle ended. A reviewed immutable snapshot plus explicit open findings and authority state is preferable to an ambiguous approval token.

## Termination reasons

Keep the normative termination vocabulary small:

- `NO_NEW_FINDINGS`;
- `BOUND_EXHAUSTED`;
- `BLOCKED`;
- `CANCELLED`.

Provider/runtime-specific reasons may be recorded as detail under one of these categories.

### `NO_NEW_FINDINGS`

This is a mechanical predicate, not an approval judgment.

It may be used only when:

1. every pass required by the configured termination rule actually executed;
2. no such pass produced a finding not already tracked in the cycle;
3. failed/skipped planned surfaces are not being treated as reviewed;
4. the record identifies whether the predicate was evaluated on the same snapshot or a changed snapshot.

`NO_NEW_FINDINGS` does not mean `VERIFIED`, `READY`, `APPROVED`, or `RELEASED`.

### `BOUND_EXHAUSTED`

The configured round/tool/execution budget ended before a clean review predicate was reached.

Budget exhaustion never lowers the declared assurance profile. Missing required evidence remains explicit. Unresolved findings must be `DEFERRED` with an owner/revisit condition or `BLOCKED` where an external constraint prevents progress, unless a successor active cycle immediately carries them forward.

### `BLOCKED`

A required permission, environment, dependency, evidence source, immutable state, or other external condition prevents the next required pass.

This is a cycle-level state and is distinct from a `BLOCKED` finding: it says the
cycle could not continue, not that any particular defect is unrepairable. See the
vocabulary table in [`evidence-protocol.md`](evidence-protocol.md).

### `CANCELLED`

Automation or the user stopped the cycle. Preserve the last completed snapshot, mutations already performed, evidence, findings, and next recovery action.

## Stagnation and bounds

Runtime/cycle logic detects bounded non-progress. `stagnation-escalation.md` interprets that signal for routing.

Stagnation is a signal, not a lifecycle state and not a termination reason by itself.

```text
repeated non-progress / bound reached
        ↓
cycle records evidence + termination or continuation
        ↓
stagnation signal
        ↓
Integrator / changed Reviewer lens / Executor / replanning
```

This avoids a third lifecycle competing with finding state and cycle termination state.

## Assurance and budget independence

An assurance profile is an evidence requirement, not a budget target.

```text
assurance: consequential
budget: exhausted before required independent verification
```

results in an explicit evidence gap and `BLOCKED`/`DEFERRED` disposition as appropriate. It never silently becomes `standard` or `exploratory` assurance.

## Mutation and attribution

When a review cycle includes repairs, every mutation-producing pass follows `runtime-adapters.md`:

- mutation boundaries survive every transition;
- parallel writers require disjoint surfaces or declared safe multi-writer semantics;
- from/to snapshots remain attributable to the pass/cycle that produced them.

## Readiness

A bounded review cycle can establish review coverage and finding dispositions. Consequential readiness still follows:

```text
Reviewer evidence
  -> Verifier
  -> Integrator
```

unless adequate current verification evidence already exists.

Repeated reviewer agreement or `NO_NEW_FINDINGS` never substitutes for executable/inspectable evidence required by the mission's verification contracts.
