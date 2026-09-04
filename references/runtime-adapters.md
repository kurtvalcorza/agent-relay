# Runtime adapters

Runtime adapters are optional execution backends for Agent Relay passes. They may invoke a CLI, another agent, CI, a local shell, a GPU host, a document system, or another runtime. Agent Relay defines the durable coordination contract; it does not require or implement any named runtime.

## Protocol versus adapter contract

The Agent Relay protocol identifier and the adapter data contract are versioned separately.

```yaml
protocol: agent-relay-v1
adapter_contract: 1
```

`protocol` identifies the coordination semantics. `adapter_contract` identifies the machine-facing request/return shape understood by a runtime adapter.

An adapter MUST NOT infer that a familiar `protocol` identifier means it understands a newer adapter payload.

## Fail-closed safety-bearing fields

The following request fields are safety-bearing when present:

- `source_snapshot`;
- `mission_anchor`;
- `mutation_boundary`;
- `decision_authority`;
- `assurance_profile`;
- cycle/round/execution budget bounds;
- any field explicitly marked by the request as required for safe execution.

If an adapter does not recognize, cannot parse, or cannot honor a safety-bearing field, it MUST refuse the pass rather than ignore the field and execute a wider task.

Unknown non-safety metadata MAY be preserved or ignored according to the adapter contract version, but the adapter SHOULD report what it did not interpret.

This rule is intentionally stricter than ordinary forward-compatible JSON handling: silently dropping a read-only boundary, authority ceiling, assurance requirement, immutable snapshot, or execution bound changes the task.

## Example request

```yaml
protocol: agent-relay-v1
adapter_contract: 1
cycle_id: plan-review-001
round: 2
role: reviewer
review_lenses:
  - security
mission_mode: plan
mission_anchor: sha256:<digest>
source_snapshot: <immutable-id>
mutation_boundary:
  mode: read-only
decision_authority:
  architecture: integrator
assurance_profile: consequential
cycle_budget:
  max_rounds: 3
mission: Review the current plan for security failures.
required_return:
  - execution_status
  - findings
  - evidence
  - environment
  - mutations_performed
  - unverified_surfaces
  - source_snapshot
  - termination_reason
  - provenance
```

The example is illustrative rather than a universal serialization schema. A document store or experiment system may represent the same semantics differently.

## Required return semantics

A substantive adapter result SHOULD include, when applicable:

- `execution_status`: whether the requested pass actually ran (`RAN`, `FAILED`, or `SKIPPED`);
- the exact `source_snapshot` evaluated or mutated;
- findings and their observation snapshots;
- executable or inspectable evidence;
- environment qualification for execution evidence;
- `mutations_performed`, including `none` for a read-only pass;
- unverified surfaces;
- cycle/round termination reason when a cycle is involved;
- provenance.

A pass that did not execute MUST NOT be represented as a pass that executed and found nothing.

Non-execution never reads as success. This is an evidence rule; iterative-review records encode it mechanically with per-pass execution status.

## Runtime liveness versus evidence safety

A runtime MAY fail open for control flow so a broken hook, plugin, or adapter returns control to the user.

```text
adapter failure -> stop automation -> return control
```

It MUST fail closed for evidence and authority claims.

```text
adapter failure
!= executed review
!= no new findings
!= verified
!= ready
```

## Cold-start resumability

Cold-start resumability is a protocol property of a substantive handoff, not a requirement that a runtime spawn new agents.

A handoff is cold-start resumable when:

1. it structurally validates as an Agent Relay handoff;
2. its current immutable snapshot is re-resolved at resume time and is still relevant;
3. each carried finding preserves the snapshot at which the finding was observed;
4. execution evidence preserves the environment to which it applies;
5. mutation permissions, open findings, ordered next actions, verification checkpoint, and completion criteria are durable;
6. any referenced mission anchor or external specification revision is resolvable;
7. the successor can continue without relying on private/shared conversational memory.

Snapshot currency is a resume-time check, not something a static Markdown validator can prove.

A runtime MAY deliberately rotate to a fresh context between milestones. Before rotation it SHOULD persist a validated handoff/checkpoint; the successor MUST re-resolve live authoritative state and MUST NOT treat predecessor prose as current truth.

### Checkpoint preservation

Rotation or checkpointing MUST preserve, where applicable:

- predecessor pass identity and provenance;
- mission-anchor identity;
- current snapshot;
- every finding's original observation snapshot and lifecycle state;
- executed evidence and its environment;
- mutation boundaries and decision-authority envelope;
- unverified surfaces;
- next role/pass and verification checkpoint.

A carried finding is never silently retargeted to a new head. The fixing/reviewed revision is recorded separately from the revision where the finding was first observed.

## Parallel mutation surfaces

Parallel mutation is a runtime concern with protocol-level safety requirements.

Within one coordination scope, mutation surfaces MUST be declared in one namespace with a stated comparison rule. Agent Relay does not standardize a global substrate syntax.

Examples of substrate-specific surfaces might be:

```text
repo:src/parser/**
document:section-4
database:schema.foo
dataset:partition-A
deployment:staging
```

These examples are not interoperable merely because they are strings. A runtime must know the namespace and comparison rule for the coordination scope in which it is deciding overlap.

If two declared surfaces cannot be shown disjoint under that comparison rule, they are treated as overlapping.

Parallel mutation of a shared surface MUST NOT proceed unless either:

1. the surfaces are established disjoint; or
2. the substrate provides an explicit safe multi-writer mechanism, and its conflict/commit semantics are declared in the durable record.

Otherwise the runtime MUST serialize or refuse the mutations.

CRDTs, serializable transactions, conditional writes, and similar mechanisms can satisfy the second case when their semantics are explicit. "The runtime usually handles conflicts" is not sufficient.

## Transition attribution

Every mutation-producing pass or cycle MUST make its attributable state transition inspectable where the substrate supports immutable state:

```text
mutation surface: <surface>
from snapshot: <immutable-id>
to snapshot: <immutable-id>
produced by pass/cycle: <id>
```

Exclusive mutation ownership and transition attribution are separate properties; both may be required.

Scratch directories, worktrees, temporary branches, and staging areas are implementation details until their state is explicitly promoted to the durable authoritative substrate.

## Status, diagnostics, cancel, and rollback

A runtime executing a bounded cycle SHOULD expose, where practical:

- cycle/pass identity;
- current role and Reviewer lenses;
- current immutable snapshot;
- execution status;
- findings by lifecycle state;
- unverified/blocked surfaces;
- next transition;
- remaining budget.

Before autonomous execution, a runtime SHOULD check only the capabilities required for the declared route: source access, requested mutation authority, environment/tool availability, storage, authentication, and resolvability of safety-bearing references.

Cancellation preserves completed evidence, open findings, last completed snapshot, mutations already performed, and the next recovery action.

Rollback is adapter-specific. A runtime that offers rollback must state exactly what it can revert; orchestration-state cleanup, Git history changes, database rollback, and production rollback are not equivalent operations.

## Interaction with decision/evidence semantics

Runtime adapters consume, but do not define, the semantics in:

- `decision-authority.md`;
- `mission-modes.md`;
- `evidence-protocol.md`;
- `stagnation-escalation.md`.

An adapter cannot grant decision authority, lower an assurance profile, promote a claim to `VERIFIED`, or declare readiness merely because it can execute the pass.

## Prior art

Bounded loop/status/cancel/concurrency ideas were informed by provider-specific runtimes such as Claudex and Google Antigravity Teamwork. Their pinned source identities and the limits of those pins are recorded in [`prior-art.md`](prior-art.md). Those systems are mutable prior art, not Agent Relay dependencies or protocol authority. Provider-specific agent names, hooks, commands, and orchestration behavior remain non-normative.
