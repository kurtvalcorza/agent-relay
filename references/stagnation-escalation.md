# Stagnation escalation

Stagnation means the current route is no longer producing evidence of progress. It is a routing signal, not a lifecycle state and not proof that the implementation is wrong.

## Candidate signals

Examples include:

- the same discriminating failure survives repeated repair attempts;
- a Builder repeatedly changes code without changing the observed failure;
- Reviewer and Builder conclusions remain contradictory against the same immutable snapshot;
- execution evidence contradicts a claimed `FIXED` state;
- repairs spread into unrelated ownership layers without evidence that the defect belongs there;
- an assumed invariant is repeatedly corrected by the user or authoritative specification;
- competing branches encode incompatible normative semantics;
- retries fail before reaching the behavior they are supposedly testing;
- a bounded cycle exhausts attempts without reducing open findings or producing new evidence.

A runtime may use numeric retry thresholds, but Agent Relay does not prescribe provider-specific counts.

## Signal, not state

Do not add `STAGNATED` to the finding lifecycle or cycle termination vocabulary.

The authoritative finding lifecycle remains:

```text
OPEN -> FIXED | DISPROVED | DEFERRED | BLOCKED
```

The bounded-cycle termination vocabulary remains owned by `iterative-review.md`.

Stagnation is recorded as evidence that the current route should be reconsidered.

## One detector, one interpreter

Runtime/cycle logic detects and bounds non-progress. This reference defines what the resulting signal means for routing.

```text
repeated non-progress / bound exhausted
        ↓
cycle/runtime records evidence
        ↓
stagnation signal
        ↓
Integrator / changed Reviewer lens / Executor / replanning
```

A stagnation signal does not terminate a cycle by itself. The cycle still records its ordinary termination or continuation state.

## Escalation behavior

Prefer a different decision function over another blind retry.

Typical routes:

```text
Builder -> same failure -> Builder -> same failure
                         ↓
                    Integrator
                         ↓
               Reviewer[test-gap]
                         ↓
                    Builder
                         ↓
                    Verifier
```

or:

```text
Builder changes multiple layers without discriminating evidence
        ↓
Integrator decides owning layer
        ↓
Reviewer[design/spec-conformance]
        ↓
Builder
```

or, when the missing discriminator requires unavailable hardware/environment:

```text
stagnation signal
  -> Integrator
  -> Executor
  -> Verifier
```

## What escalation preserves

Escalation MUST preserve:

- the mission anchor and current authority envelope;
- immutable snapshots evaluated so far;
- finding IDs and original observation snapshots;
- failed/discriminating experiments;
- mutation boundaries;
- current assurance profile;
- unverified surfaces.

Escalation cannot lower the evidence burden, erase failed attempts, or silently redefine acceptance criteria.

## Relationship to budgets

A budget is a control-flow limit. An assurance profile is an evidence requirement.

If a budget ends before the required evidence exists, the required assurance remains unchanged. The cycle records `BOUND_EXHAUSTED` and unresolved work is carried as `DEFERRED`, `BLOCKED`, or into an explicit successor cycle according to `iterative-review.md`.

## Manufactured progress

The following do not count as progress by themselves:

- more generated text;
- more files changed;
- another same-shaped retry;
- a new branch name;
- a Builder assertion that the finding is fixed;
- a runtime reaching its final configured round.

Progress requires a changed durable state relevant to the finding, new discriminating evidence, a justified ownership/authority decision, or an explicit terminal disposition.
