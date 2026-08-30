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
- authorizes merges, releases, or approvals;
- widens where a review may be recorded beyond what the review request already authorizes;
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

## Worked end-to-end finding lifecycle

This example shows how a finding moves through the relay instead of ending as an unverified review comment.

### 1. Reviewer opens the finding

At immutable snapshot `a1b2c3d`, `Reviewer[standard]` identifies `F-007`:

```text
F-007 · high · standard
Reviewed snapshot: a1b2c3d
Failure condition: retrying the operation after a partial write creates a duplicate record.
Expected behavior: retry is idempotent and preserves one logical record.
Observed behavior: the second attempt inserts a second record.
Evidence: regression reproduction on a1b2c3d; 2 records observed after one retry.
Owning layer: persistence adapter
State: OPEN
```

The Reviewer has identified and reproduced the failure, but does not self-authorize a fix or declare readiness.

### 2. Integrator adjudicates ownership

The Integrator confirms that the persistence adapter, not the caller, owns idempotency. The finding remains `OPEN`, and the next route is:

```text
Integrator -> Builder -> Verifier
```

The Integrator records the owning layer and preserves the original reviewed snapshot `a1b2c3d` as the failure baseline.

### 3. Builder repairs the owning layer

The Builder changes the persistence adapter and adds a regression test. The repaired state is a new immutable snapshot, `d4e5f6a`.

The Builder may report:

```text
Changed snapshot: d4e5f6a
Regression added: retry_after_partial_write_is_idempotent
Builder evidence: targeted test passes locally
Finding state: OPEN pending independent verification
```

The finding is **not yet `FIXED`** merely because code changed or the Builder's local test passed.

### 4. Verifier reproduces the discriminating evidence

The Verifier starts from `d4e5f6a`, reruns the regression, and checks the surrounding invariant:

```text
Linux / x86_64 / CPython 3.12
retry_after_partial_write_is_idempotent: PASS
broader persistence suite: 42 passed, 0 skipped
observed records after retry: 1
```

The evidence now distinguishes the repaired state from the original failure at `a1b2c3d`.

### 5. Finding closes as `FIXED`

Only after verification does the durable finding become:

```text
F-007
Failure snapshot: a1b2c3d
Verified fixed snapshot: d4e5f6a
State: FIXED
Verification: Linux / x86_64 / CPython 3.12 — targeted regression PASS; persistence suite 42 passed, 0 skipped
```

If the regression had failed, the finding would remain `OPEN` or become `BLOCKED`; if the alleged failure could not exist under the stated condition, it could become `DISPROVED`. This lifecycle is why Agent Relay treats review findings as durable evidence-bearing state rather than disposable prose.

## Review provenance

A durable review may record the agent/client that generated it, the model when reliably known, the Agent Relay role, selected lenses, and reviewed snapshot.

Agent attribution is provenance only. It is **not proof, authentication, approval, authorship authority, or verification**, and it must not increase a finding's evidentiary weight merely because of the named model or provider.
