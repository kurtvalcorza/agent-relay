# Automatic Role Routing

Agent Relay may infer the active role, optional Reviewer lenses, and the next role sequence from the current task and durable workflow state. Role/lens inference reduces manual coordination; it does **not** create permissions, weaken mutation boundaries, or authorize an action the user did not authorize.

## Decision precedence

Apply these inputs in order:

1. **Explicit user role assignment** — if the user says which role to use, use it unless doing so would violate a higher-level safety or permission constraint.
2. **Mutation and safety boundaries** — read-only, forbidden, approval, credential, or environment constraints always survive role changes.
3. **Environment feasibility** — if execution requires unavailable hardware, software, credentials, network, or local state, route that step to an Executor rather than pretending it was run.
4. **Workflow state** — open findings, authored changes, missing evidence, conflicting conclusions, or release gates can determine the correct role even when the user's wording is brief.
5. **Task intent** — infer from what must actually happen, not only from keywords.
6. **Conservative default** — when state is genuinely ambiguous, prefer Reviewer for inspection-only work and Builder for explicitly authorized change work. Ask only when the ambiguity changes permissions, risk, or expected outcome.

Review lens selection is orthogonal to role assignment. An explicit `Reviewer` role may still carry an inferred or explicit lens. An explicit non-Reviewer role does not inherit a review lens merely because the task mentions review subject matter.

## Canonical role signals

### Builder

Use Builder when the next required action is to create, implement, repair, refactor, or update an artifact.

Typical signals:
- implement this;
- fix the finding;
- update the spec;
- revise the document;
- add tests.

Do not infer mutation intent from a noun alone. For example, `review the security fix (read-only)` describes the artifact under review; `fix` there is not authorization to modify it.

### Reviewer

Use Reviewer when the next action is adversarial inspection without immediately assuming a change is needed.

Typical signals:
- review this PR;
- audit this implementation;
- find bugs;
- challenge the design;
- assess merge readiness.

Reviewer may carry one or more lenses defined in [`review-lenses.md`](review-lenses.md). `standard` is the default. `design` is selected by unambiguous intent such as `adversarial review`, `design review`, or `challenge the assumptions`; every Reviewer pass remains adversarial in posture.

Bare subject nouns must not select lenses. `review the security module` is `Reviewer[standard]`; `security review this PR` is `Reviewer[security]`.

### Executor

Use Executor when the decisive step depends on a particular environment, local resource, hardware, credential, private network, device, or runtime unavailable to the current agent.

Typical signals:
- run under WSL/Linux;
- reproduce on CUDA/GPU;
- execute against a local database;
- test with a private fixture;
- inspect a machine-local artifact.

Executor is about **where evidence can be produced**, not who is more trusted. A review lens never changes environment routing: if a `Reviewer[security]` pass requires an unavailable scanner/environment, route the execution step to an Executor.

### Verifier

Use Verifier when a claim already exists and must be reproduced or checked before relying on it.

Typical signals:
- confirm the fix;
- reproduce the reported result;
- check whether the tests really passed;
- validate the artifact digest;
- verify the release gate.

### Integrator

Use Integrator when multiple findings, agents, layers, branches, or evidence sources must be reconciled into one decision or ordered change set.

Typical signals:
- reconcile these reviews;
- decide which layer owns the fix;
- restack or propagate a lower-layer repair;
- adjudicate conflicting results;
- determine what still blocks readiness.

The Integrator owns the final readiness/progress decision. `Reviewer[readiness]` produces an evidence-gap assessment and normally routes to `Verifier -> Integrator`.

## Role sequences

A task may require a sequence rather than a single role. Infer the smallest sequence that preserves independent verification where practical.

Examples:

| Situation | Recommended route |
| --- | --- |
| `Review this PR` | `Reviewer[standard]` |
| `Adversarially review the design` | `Reviewer[design]` |
| `Review and sign off if clean` | `Reviewer[standard] -> Verifier` |
| `Review this PR and fix what you find` | `Reviewer[standard] -> Integrator -> Builder -> Verifier` |
| `Review test gaps and confirm the tests really run` | `Reviewer[test-gap] -> Verifier` |
| `Assess merge readiness for this PR` | `Reviewer[readiness] -> Verifier -> Integrator` |
| `Is this ready to merge?` | `Verifier -> Integrator` |
| `Fix Claude's latest finding` | `Integrator -> Builder -> Verifier` |
| `Run this locally and tell me whether it is ready` | `Executor -> Verifier -> Integrator` |
| `Continue` with an unresolved valid finding and authorized write access | `Integrator -> Builder -> Verifier` |
| implementation complete but required runtime evidence is missing | `Verifier`, or `Executor -> Verifier` if the environment is unavailable |

When the user explicitly names a review intent and also asks for verification, preserve the Reviewer at the head of the route instead of allowing verification keywords to consume the review request.

Do not add roles mechanically. For a trivial authorized edit, `Builder` alone may be enough. For consequential readiness claims, include independent verification when practical.

## Review lens inference

The valid lenses are:

- `standard`
- `design`
- `security`
- `reliability`
- `test-gap`
- `spec-conformance`
- `regression`
- `readiness`

The reference router automatically supports `standard` and `design` as the primary v1 inference surface and recognizes the other lenses only from explicit/unambiguous intent phrases. It should remain conservative rather than classify by broad topic nouns.

Lenses may compose when multiple review intents are explicit. Use an ordered list representation such as:

```json
"review_lenses": ["design", "security"]
```

Omit lens metadata for non-Reviewer routes so existing consumers of the reference router's non-review JSON shape remain compatible.

## Workflow-state inference

When the coordination substrate exposes state, use it.

Examples:

- **Open unresolved review finding + no fix yet**: `Integrator` to adjudicate, then `Builder` if valid.
- **Current agent authored the change + user asks whether it is correct**: prefer `Verifier`; independent verification is better when available.
- **Implementation is complete + tests were reported by another agent**: `Verifier` before relying on the report.
- **Required test cannot run in the current environment**: `Executor` handoff.
- **Multiple branches/layers must receive one lower-layer fix**: `Integrator -> Builder -> Verifier`.
- **All code findings closed but release gates remain**: `Integrator` to separate implementation completeness from evidence/readiness blockers.

## Verification checkpoint for consequential actions

Before any of the following claims or actions, automatically enter Verifier behavior unless adequate current evidence already exists:

- approve or sign off;
- declare a finding fixed;
- resolve a review thread because the defect is said to be fixed;
- declare a gate PASS;
- declare release/readiness/stability;
- recommend merge based on correctness evidence.

This checkpoint does not mean every action requires rerunning the entire test suite. Verification should be proportional and discriminating: inspect the exact fix, run the regression that distinguishes fixed from broken, and confirm relevant surrounding invariants.

## Permissions are not roles or lenses

Role/lens routing never grants capabilities.

`Builder` does not imply write permission. `Integrator` does not imply permission to merge. `Reviewer` does not imply permission to comment publicly. `Executor` does not imply permission to access credentials or private data. A `security`, `design`, or other lens adds no authority.

Before mutating durable state, independently confirm that the requested mutation is authorized.

## Handoff trigger

Set `handoff_required: true` when the selected next role depends on a capability or environment unavailable to the current agent.

The current agent should then:

1. define the exact experiment or task;
2. pin the immutable input state;
3. preserve mutation boundaries;
4. state acceptance criteria;
5. specify evidence to return;
6. hand the packet to an appropriate Executor or other agent.

Use [`../assets/HANDOFF.md`](../assets/HANDOFF.md).

## Suggested internal state

Agents may maintain a compact role-routing state internally or in durable coordination metadata:

```yaml
role:
  inferred: reviewer
  review_lenses:
    - design
  confidence: high
  reason: "Current task asks for design-focused adversarial review"
  sequence:
    - reviewer
    - verifier
  handoff_required: false
```

This block is optional. Do not emit it mechanically in normal conversation; expose it when it helps coordination, debugging, or handoff clarity.

## Fail-closed ambiguity

When role/lens ambiguity affects permissions, destructive actions, release claims, or access to sensitive resources, do not guess. Preserve the safest existing boundary and obtain clarification or additional evidence.
