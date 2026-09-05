# Decision authority and mission anchors

Decision authority records who may decide which aspects of a mission. It is independent of mutation permission.

Mutation boundaries answer:

> What may this actor change?

Decision authority answers:

> What may this actor decide?

A Builder may have repository write permission without authority to redefine an accepted API contract. An Integrator may have architecture/adjudication authority while remaining read-only in the repository.

## Authority classes

Keep the vocabulary intentionally small:

- `mission` — desired outcome / problem definition;
- `scope` — what work is in or out;
- `architecture` — system-level or normative approach and ownership decisions;
- `acceptance` — what counts as done;
- `implementation` — file/code/configuration mechanics inside approved boundaries;
- `execution` — environment-specific command/procedure choices;
- `evidence` — whether relied-upon evidence is sufficient for a claim;
- `readiness` — consequential merge/release/deployment/sign-off recommendation.

These are semantic delegation classes, not an ACL language.

## Default responsibility guidance

Defaults are guidance and never override explicit user/project policy.

- User/request owner: `mission`, `scope`, and explicit acceptance policy unless delegated.
- Builder: `implementation` within the mission anchor and mutation boundary.
- Executor: `execution` choices needed to run the declared procedure in the provided environment.
- Reviewer: no implicit authority to redefine mission/architecture/acceptance merely by finding a defect.
- Verifier: `evidence` judgment for the exact claim/verification contract being checked.
- Integrator: reconciliation/ownership decisions and `readiness`; architecture authority only when explicitly or project-policy delegated.

Role inference MUST NOT widen decision authority.

## Delegation

An actor encountering a required decision outside its delegated authority must route/escalate rather than silently decide.

Delegation must be attributable to an actor or durable policy that currently holds the authority being delegated. Self-delegation is invalid.

Example:

```text
Current architecture authority: user
Requested change: delegate architecture decisions to Integrator
Valid authority source: explicit user statement / durable project policy
```

A vague continuation instruction such as `continue` does not by itself transfer a different authority class.

### Standing authorization for a routine action

A holder of an authority MAY pre-authorize a repeating routine outward action under an explicit condition, so the action does not require a fresh ask each round. Record durably:

- the authorizing actor;
- the exact action authorized;
- the gate condition;
- the bound: expiry, count, or the mission-anchor revision it is bound to;
- that anything outside the envelope still stops for the holder.

Example:

```text
Authorized by: user
Action: push, then post the paced comment batch
Condition: Windows suite green, Linux suite green, CI green
Bound: this anchor revision
Outside the envelope: stops for the user
```

A standing authorization removes a repeated ask for an already-authorized action. It does not change what must be true before the action is taken:

- the gate condition MUST be evidence-backed when the envelope is exercised — a green check is a claim until inspected (see [`evidence-protocol.md`](evidence-protocol.md) § Infrastructure vs code failure);
- the envelope grants no `evidence` and no `readiness` authority;
- it does not survive an anchor revision that changes the meaning of its gate condition.

## Mission anchor

A mission anchor is the immutable identity of the planning state an execution route is acting against.

A mission anchor SHOULD contain or resolve to:

- mission / desired outcome;
- scope and explicit exclusions;
- authoritative specification references with observed revisions;
- invariants / constraints;
- acceptance criteria;
- verification contracts or references to them;
- decision-authority envelope;
- mutation boundaries;
- required assurance profile;
- known environment requirements;
- known failure modes where material.

A mission anchor is not an approval token. It is an identity for the planning state.

## Immutable identity requirement

A mission anchor MUST resolve to an immutable substrate-native revision or carry a content digest that identifies exactly the planning text relied upon.

A mutable issue body, live document, branch name, or editable comment is not sufficient identity by itself.

Where the planning carrier has no immutable revision, materialize or digest the relevant content and record that immutable/digested identity. The mutable location may remain a locator/pointer.

Example:

```text
Mission anchor locator: issue #8
Mission anchor digest: sha256:<digest-of-reviewed-body-and-amendments>
Authoritative spec: spec.md @ <commit-sha>
```

## Anchor revisions

Changes to mission, scope, architecture, acceptance criteria, authority allocation, mutation boundaries, assurance requirements, or verification contracts must produce an explicit new mission-anchor revision when the change is material to downstream work.

A revision records:

- previous anchor identity;
- new anchor identity;
- changed authority-bearing fields;
- authorizing actor/policy;
- durable statement or policy relied upon.

An anchor revision that widens or reassigns an authority class is valid only when authorized by the current holder of that class (or an explicitly superior project authority). A Builder cannot author an anchor revision that grants itself architecture authority merely because it can write the anchor file.

Prior pass records remain bound to the anchor revision they cited; they do not silently inherit later authority changes.

## External specification drift

If the mission anchor references an external specification, requirement set, policy, dataset schema, or other authoritative artifact, the reference must include the revision observed when the anchor was created.

At the start of a substantive resumed/handoff pass:

1. re-resolve live authoritative state;
2. compare relevant referenced revisions with the anchor;
3. if a referenced authority has moved, do not silently continue under the stale anchor;
4. route the divergence to the holder of `mission`, `scope`, `architecture`, or `acceptance` authority as appropriate;
5. create an authorized anchor revision before relying on changed semantics.

This is the mission-anchor form of Agent Relay's existing rule that durable handoffs are claims about prior state, not current truth.

## Anchor completeness

Do not create a second `SUFFICIENT / PARTIAL / INSUFFICIENT` lifecycle over planning context.

Instead, record missing mission-anchor fields explicitly. Broad autonomous execution is justified only to the extent that the required anchor fields, authority envelope, mutation boundaries, assurance profile, and verification contracts are present for the task.

Example:

```text
Mission-anchor gaps:
- acceptance criterion for retry behavior missing
- production environment requirement unknown
```

Missing planning context is evidence of an unresolved planning decision, not evidence about the user's expertise.

## Authority versus permissions

No authority class grants credentials or technical capability. No credential or writable substrate grants an authority class.

A runtime adapter that cannot honor the declared authority envelope must refuse the pass under `runtime-adapters.md`.
