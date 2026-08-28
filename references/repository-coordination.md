# Repository Coordination Adapter

This is an optional substrate adapter for Git/VCS + pull-request workflows. The Agent Relay core remains platform-neutral.

## Repository state

Capture:
- repository identity;
- branch/PR stack;
- base/head commit IDs;
- changed-file scope;
- mergeability/conflict state;
- relevant checks;
- unresolved review findings.

Before acting on a prior handoff, fetch live heads again.

## Repository review

Use the substrate-neutral Reviewer lenses in [`review-lenses.md`](review-lenses.md), then bind them to repository-specific evidence.

For a repository/PR review, record where available:
- repository identity;
- immutable base revision;
- immutable head/reviewed revision;
- changed-file scope;
- relevant PR/branch context;
- relevant checks/tests;
- unresolved prior findings;
- explicit mutation/read-only boundaries.

Prefer commit SHAs in durable findings and pass records. Branch names and mutable tags may locate work, but they are not sufficient identity for consequential evidence.

### Lens application

- `standard`: inspect implementation correctness within the changed scope and relevant surrounding invariants.
- `design`: challenge the architecture/approach and whether the selected ownership layer is correct.
- `security`: inspect trust boundaries and misuse paths; route unavailable scanners/environments to Executor.
- `reliability`: inspect retry, interruption, concurrency, partial-write, recovery, and dependency-failure behavior.
- `test-gap`: inspect whether tests discriminate fixed from broken and whether important paths/platforms are unexercised.
- `spec-conformance`: compare implementation behavior with the identified authoritative requirement/specification.
- `regression`: compare against the appropriate base revision and identify previously valid behavior that changed.
- `readiness`: inventory evidence gaps, then route consequential readiness through Verifier and Integrator.

A subject noun is not a lens signal. `review the security module` remains a standard implementation review unless security-review intent is explicit.

## Stacked changes

For a stack such as:

`PR5 -> PR4 -> PR3 -> PR2 -> PR1 -> main`

apply fixes to the earliest layer that normatively owns the behavior.

Then propagate/restack forward and verify actual ancestry. Do not merely copy equivalent files into higher branches while leaving stale ancestry.

After propagation verify:
- each PR base is the intended lower head;
- mergeability;
- changed-file scope;
- tests at affected heads;
- review comments are still relevant to current code.

## Review findings

Repository findings use the finding record in [`evidence-protocol.md`](evidence-protocol.md) plus the review extensions in [`review-lenses.md`](review-lenses.md).

A good durable review finding contains:
- concrete defect/failure condition;
- severity;
- review lens or lenses;
- affected requirement/invariant;
- exact reviewed revision;
- affected file/location when applicable;
- expected behavior;
- observed behavior;
- reproduction or source evidence;
- suggested owning layer, if known;
- lifecycle state.

After fixing:
1. fetch the current head again;
2. verify the failure condition on the current code;
3. rerun discriminating regression evidence when practical;
4. reply with the fixing revision and evidence when useful;
5. resolve only then.

Do not bulk-resolve old threads because they appear outdated.

## Re-review after repair

A previous review is tied to its reviewed snapshot. After a repair:
- do not silently retarget old findings to the new head;
- preserve the original finding revision;
- record the fixing revision separately;
- re-evaluate affected findings against current code;
- distinguish `FIXED` from merely `STALE` discussion context.

## PR/body documentation

Use PR descriptions for durable current-state architecture and evidence summaries.
Use review threads for localized defects and technical debate.
Use top-level comments for pass summaries/checkpoints.
Use code/tests as the strongest evidence.

For substantive generated review comments, a compact provenance footer may record the generating agent/client, role, lens, and reviewed snapshot. Attribution is provenance, not proof or approval.

## Read-only repositories

Credentials granting write access do not override a user-declared read-only boundary.

If a source repository is read-only:
- inspect at immutable revision;
- record evidence elsewhere;
- do not comment, create issues, or open PRs there;
- implement adapters/audit records in an authorized repository only.
