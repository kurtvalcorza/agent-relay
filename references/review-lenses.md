# Review Lenses

Agent Relay treats review lenses as **Reviewer profiles, not roles**. The five core roles remain Builder, Reviewer, Executor, Verifier, and Integrator.

Every Reviewer pass is adversarial in posture: it should try to falsify claims, find concrete failure conditions, and avoid trusting implementation summaries. A lens changes **what the Reviewer concentrates on**, not how skeptical the Reviewer is.

## Baseline and design review

### `standard`

Default implementation review. Ask whether the artifact is correct as implemented.

Typical targets:
- correctness defects;
- incomplete logic;
- semantic mismatches;
- API misuse;
- error-handling gaps;
- regressions introduced by the change;
- contradictions between code, tests, and requirements.

### `design`

Challenge the implementation approach itself rather than only the code as written.

Typical targets:
- hidden assumptions;
- brittle architecture;
- incorrect abstraction boundaries;
- unnecessary coupling;
- unsafe fallback behavior;
- stale identity/state assumptions;
- interruption, retry, race, or rollback failure modes;
- misleading success states;
- operational blind spots;
- cases where a materially different design would reduce risk or complexity.

Phrases such as `adversarial review`, `challenge the design`, `architecture review`, and `challenge the assumptions` may route to the `design` lens. This does **not** imply that `standard` review is non-adversarial.

## Additional lenses

The following lenses are valid Reviewer profiles. The reference router should infer them only from unambiguous review intent, not from bare subject-matter nouns.

### `security`

Inspect trust boundaries and misuse paths, including authentication/authorization, privilege boundaries, untrusted input, injection, secret handling, data exposure, unsafe execution/deserialization, path traversal, SSRF-style access, supply-chain assumptions, sensitive logging, and abuse-resistant defaults.

`review the security module` is a standard review of security-related code. `security review this PR` or `review this for security` selects the security lens.

### `reliability`

Inspect retries, idempotency, interruption/cancellation, partial writes, concurrency, stale state, dependency failure, timeout handling, cleanup, restart/recovery, cross-platform assumptions, and resource exhaustion where relevant.

### `test-gap`

Inspect the evidence surface: important behavior not covered by tests, declaration-only tests, missing negative/boundary cases, mocks that hide integration behavior, unexercised runtime/platform combinations, and tests that cannot discriminate fixed from broken.

### `spec-conformance`

Compare behavior against an identified authoritative specification, contract, ADR, requirement, issue, or other durable artifact. Distinguish implementation defects from ambiguous, contradictory, stale, or intentionally out-of-scope requirements.

### `regression`

Focus on behavior that existed before a change and may have been unintentionally altered. On versioned substrates, compare against the appropriate base state rather than reviewing the new state in isolation.

### `readiness`

Produce an **evidence-gap assessment**, not the final readiness decision. Identify whether current evidence is sufficient for merge, release, deployment, or other consequential readiness claims and enumerate missing gates such as CI, production qualification, hardware-specific tests, governance, security validation, or independent reproduction.

A readiness pass should normally route:

`Reviewer[readiness] -> Verifier -> Integrator`

The Integrator owns the final readiness/progress decision after evidence is established.

## Lens composition

Lenses may compose when the user explicitly asks for multiple review intents, for example:

`Reviewer[design, security]`

Do not add `standard` alongside a more specific lens; `standard` is the default when no specific lens applies.

Automatic composition should remain conservative. Prefer explicit intent over broad keyword matching.

## Intent, not subject matter

Lens inference must distinguish review intent from the topic being reviewed.

Examples:

| Request | Lens |
| --- | --- |
| `Review this PR` | `standard` |
| `Review the security module` | `standard` |
| `Security review this PR` | `security` |
| `Adversarially review the design` | `design` |
| `Review this PR for test gaps` | `test-gap` |
| `Assess merge readiness for this PR` | `readiness` |

Bare nouns such as `security`, `reliability`, `test`, `spec`, or `regression` should not select a lens by themselves.

## Roles, permissions, and execution

A lens never:
- creates mutation permission;
- grants credentials or private-data access;
- authorizes public comments, merges, releases, or approvals;
- changes environment-feasibility routing;
- makes the Reviewer the Executor or Verifier.

If a security, reliability, or test-gap review requires tooling unavailable to the current agent, route the required experiment to an Executor and return evidence to the review workflow.

## Finding contract

Review findings are a **superset of the finding record in `evidence-protocol.md`**, not a parallel schema.

A significant review finding should preserve, when applicable:
- ID or stable short name;
- review lens or lenses;
- severity/impact;
- confidence when useful;
- immutable reviewed state;
- affected location or surface;
- concrete failure condition;
- expected behavior;
- observed behavior;
- violated requirement/invariant;
- owning layer;
- evidence;
- recommended action when useful;
- state: `OPEN`, `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.

Expected versus observed behavior should remain explicit because it makes a finding falsifiable and therefore easier for another agent to verify or disprove.

## Review versus verification

A Reviewer identifies and characterizes findings. A Verifier establishes whether a consequential claim can be relied upon.

A review finding does not become `FIXED` merely because another agent reports a code change. Reproduce or inspect the discriminating evidence first.

## Review provenance

A durable review may record the agent/client that generated it, the model when reliably known, the Agent Relay role, selected lenses, and reviewed snapshot.

Agent attribution is provenance only. It is **not proof, authentication, approval, authorship authority, or verification**, and it must not increase a finding's evidentiary weight merely because of the named model or provider.
