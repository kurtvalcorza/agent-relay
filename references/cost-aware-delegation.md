# Cost-aware delegation

Agent Relay routes work to another participant when the current agent cannot produce the required evidence itself. See [`role-routing.md`](role-routing.md) § Handoff trigger and § Executor: routing is about where evidence can be produced, not who is more trusted.

Participants in one relay may also differ in cost per unit of work. This reference defines when that difference MAY influence routing, what shapes of work are safe to delegate to a lower-cost participant, what the delegated pass returns, and when it returns control.

It adds no role, no lens, no permission, and no authority class. A lower-cost participant is an ordinary Builder or Executor.

## Cost is a subordinate routing input

Cost and throughput MAY be routing inputs. They rank below every existing factor in the `SKILL.md` precedence list — explicit user assignment, mutation/safety/approval/access and decision-authority boundaries, and environment feasibility.

An economic input MUST NOT:

- move a decision outside the delegating participant's authority envelope;
- widen the delegate's decision authority or mutation boundary;
- lower a declared assurance profile or weaken a verification contract;
- substitute for a capability-based handoff that the environment actually requires.

Cost orders otherwise-equivalent routes. It never selects a route that a boundary, an authority envelope, or environment feasibility had already excluded.

Normative text here refers to a **lower-cost participant** and a **delegating participant**. Provider, vendor, model, and tier names are implementation detail and do not belong in a durable Agent Relay record except as provenance.

## Delegate by task shape

### Delegable shape

Work that is long-running, parallelizable across independent units, and judgment-light:

- per-item reproduction or repair batches over an already-dispositioned finding set;
- environment-specific runs whose procedure is already fixed;
- corpus, log, or artifact scans against a declared predicate;
- per-layer implementation of an already-decided plan.

The common property is that the delegating participant can check the result mechanically without re-deriving the judgment that produced it.

### Non-delegable shape

Work whose output is a judgment the delegating participant would have to re-derive in order to trust:

- finding dispositions;
- owning-layer placement in a stacked or layered system;
- merge-conflict resolution;
- any change to schema or specification semantics.

Each of these already has an authority home — [`decision-authority.md`](decision-authority.md) § Default responsibility guidance withholds `architecture` and `acceptance` from the executing actor, and `SKILL.md` rule 9 places owning-layer decisions with the Integrator. This section states the routing consequence, not a new rule: do not route them to a delegate merely because the delegate is cheaper.

### Delegation floor

A delegated pass carries fixed overhead: authoring a complete execution packet, and verifying the returned artifact. That overhead is independent of task size.

Do not delegate a task the delegating participant could complete in less effort than its packet and verification require. Below that floor, delegation increases total cost while adding a handoff boundary that can lose state.

Agent Relay does not prescribe a numeric threshold; provider-specific counts are runtime detail.

## Artifact-first returns

A delegated pass SHOULD return a machine-checkable artifact rather than prose: counts, exit codes, immutable revisions, digests, and log paths, in a schema the execution packet declared in advance.

The reason is verification cost. Checking prose against logs is a re-reading; checking a declared artifact against the same logs is a comparison. Where the assurance profile is `consequential`, the machine-checkable return is required rather than preferred.

This does not change the evidence hierarchy in [`evidence-protocol.md`](evidence-protocol.md), and a returned artifact is still at most `EXECUTED` claim maturity. An accurate return is not verification; the delegating participant still compares the artifact with the evidence it references.

The execution packet in [`local-execution.md`](local-execution.md) SHOULD therefore declare the return schema alongside the evidence to capture.

## Layered work is serialized

In a stacked or layered system, layers are **not** disjoint mutation surfaces even when their changed-file sets are disjoint, because merge-forward makes each lower layer's change part of every upper layer's surface.

This is the existing rule in [`runtime-adapters.md`](runtime-adapters.md) § Parallel mutation surfaces applied to a case where "disjoint" is easy to conclude and wrong. Under that rule such surfaces MUST be treated as overlapping, so parallel builders across layers serialize or refuse.

The resulting pattern:

```text
layer 1 (lowest) -> build -> merge forward
layer 2          -> build -> merge forward
layer 3          -> build -> merge forward
```

- one delegate per layer, bottom-up, one layer at a time;
- each in an isolated working copy;
- an explicit merge-forward step between layers.

Shared substrates add their own contention — working-copy checkout locks and substrate rate limits — which is a further reason to serialize, not the reason. Repository-specific stack mechanics remain in [`repository-coordination.md`](repository-coordination.md) § Stacked changes.

## Return-to-delegator conditions

A stagnation signal fires on repeated non-progress; see [`stagnation-escalation.md`](stagnation-escalation.md). The conditions below are a different category: they fire on **first occurrence**, and their effect is that the delegate returns control rather than continuing.

A lower-cost participant SHOULD return to the delegating participant, rather than self-repair, on:

- a test regression appearing after its own change;
- a conflict in a file shared across layers;
- a mismatch between its own report and its logs;
- an environment kill or interruption.

A required decision outside the delegate's authority — including any semantic change to a schema or specification — is already an escalation under [`decision-authority.md`](decision-authority.md) § Delegation and is not restated as a new condition here.

Returning control preserves everything escalation preserves under `stagnation-escalation.md` § What escalation preserves. It does not lower the evidence burden and does not close any finding.

## Durable records survive interruption

A long delegated pass SHOULD write its durable record incrementally rather than only at completion, so that an environment kill costs the last increment rather than the whole pass.

An interrupted pass with no durable record produced no evidence at all. Record it as `BLOCKED` under [`evidence-protocol.md`](evidence-protocol.md) § Infrastructure vs code failure; `SKILL.md` rule 15 already forbids representing it as a clean result.

## What cost-aware delegation is not

- not a model-selection mechanism: the protocol constrains what may be delegated and what must come back, not to whom;
- not a runtime: it schedules nothing;
- not a new role, lens, permission, or authority class;
- not a reduction in evidence burden: a delegated result satisfies exactly the verification contract a direct result would have to satisfy.
