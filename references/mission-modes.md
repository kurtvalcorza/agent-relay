# Mission modes

Mission mode describes the kind of work a pass is performing. It is orthogonal to role, Reviewer lens, mutation permission, decision authority, and evidence maturity.

When the `Mission mode` field is used, use one primary value from this vocabulary:

- `build`;
- `fix`;
- `test`;
- `orchestrate`;
- `operate`;
- `understand`;
- `plan`;
- `analyze`;
- `communicate`.

The field is optional metadata. It does not create new roles or permissions.

## Modes are not routes

The same mode can involve different roles depending on responsibility.

### `build`
Create the primary artifact or implementation.

Typical role: Builder.

### `fix`
Repair an accepted finding or defect.

Typical route when a finding is already open:

```text
Integrator -> Builder -> Verifier
```

### `test`
Work whose primary subject is test/proof behavior.

Possible responsibilities:

- Reviewer[test-gap] identifies missing/non-discriminating tests;
- Builder authors or repairs test code/fixtures;
- Executor runs tests requiring a specific environment;
- Verifier judges whether the result establishes the relied-upon claim.

The mode does not collapse those responsibilities.

### `orchestrate`
Coordinate multiple passes/runtimes, budgets, checkpoints, or mutation surfaces.

Typical responsibility: Integrator or an external runtime adapter operating under Agent Relay semantics.

A runtime is not promoted to Integrator merely because it schedules work.

### `operate`
Perform environment-specific operational actions against a declared target.

Typical role: Executor.

### `understand`
Inspect, map, explain, or summarize mechanisms without an adversarial defect judgment.

A pure read-only exploration that produces an explanatory/map artifact can use:

```text
Role: Builder
Mission mode: understand
Mutation boundary: source substrate read-only
```

This does not imply source mutation: Builder means responsibility for producing the primary artifact, and role inference never grants write permission.

If the purpose is to challenge correctness, security, reliability, conformance, or another invariant, use Reviewer with the appropriate lens instead. Reviewer passes remain adversarial; `understand` does not weaken that contract.

If the investigation requires a special local environment or execution, route that evidence step to Executor.

### `plan`
Produce or revise a plan/design/decision artifact within the current decision-authority envelope.

Typical responsibility: Builder for the artifact, with Integrator/User authority governing out-of-envelope decisions.

### `analyze`
Analyze data, experiments, logs, requirements, or another substrate.

Role depends on the output: Builder for the primary analysis artifact, Reviewer for adversarial assessment, Verifier for a relied-upon claim, Executor for environment-specific execution.

### `communicate`
Produce a durable communication/documentation artifact.

Typical role: Builder.

## Conservative inference

Mission mode should be inferred only when it materially improves handoff/routing clarity. Do not turn ambiguous prose into a false precision field.

Role is still selected from responsibility and workflow state. Mode never grants:

- mutation permission;
- credentials;
- decision authority;
- review-recording authority;
- verification status;
- readiness/sign-off.

## Runtime-persona mapping

Provider/runtime persona names should decompose into existing Agent Relay responsibilities rather than become protocol roles.

Examples inspired by Google Antigravity Teamwork:

- Explorer-like read-only mapping/explanation -> Builder + `understand` + read-only source boundary;
- Worker -> Builder;
- Critic -> Reviewer;
- Challenger-like adversarial test generation -> Reviewer[test-gap] identifies the gap -> Builder authors tests -> Executor runs where required -> Verifier assesses the evidence;
- Auditor -> Verifier when the activity is independent claim verification;
- Success-auditor/coordinator -> Verifier followed by Integrator readiness decision.

The mapping is about responsibilities, not provider identity.
