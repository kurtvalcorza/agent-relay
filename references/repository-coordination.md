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

On this substrate, the review channel of a named PR or issue is its review threads and comments. A request to review a named PR, issue, or revision therefore carries authority to record that review there. It does not carry authority to push, merge, approve, request changes as a blocking gate, resolve threads, reopen or close the item, or comment on any other artifact.

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

## External review handoff

A repository workflow may hand a named pull request to an external or hosted code-review agent when independent review is useful and the substrate supports it. This is a downstream Reviewer handoff, not a new Agent Relay role.

Before requesting the external review:
- capture the repository and pull-request identity;
- capture the immutable PR head SHA being handed off;
- preserve mutation and decision-authority boundaries;
- record what the external reviewer is expected to assess when the review scope is narrower than a normal implementation review.

The external reviewer receives review-recording authority only to the extent supported by the named PR's review channel. A review handoff does **not** authorize the external reviewer, the handing-off agent, or a later receiving agent to merge, push fixes, resolve threads, approve on the user's behalf, release, or otherwise broaden mutation/decision authority.

Do not automatically merge after requesting an external review. Review handoff and merge are separate actions; merge requires its own authority and readiness decision.

### GitHub Copilot Code Review

GitHub Copilot Code Review is one supported example of an external Reviewer on the GitHub substrate. Request it through the review mechanism available to the current GitHub environment rather than depending on one hard-coded username, API field, or trigger syntax.

Copilot review status may be exposed differently from an ordinary human/team review request. In particular, a Copilot review can be visibly running in GitHub even when the normal requested-reviewers list is empty. Therefore:
- an empty `requested_reviewers` result is **not** sufficient evidence that the Copilot handoff failed;
- treat a visible/running Copilot review, substrate-native review status, or resulting Copilot review record as stronger evidence that the handoff started;
- if the API and GitHub UI disagree about whether the review is running, preserve the discrepancy rather than inventing a failure or success state;
- do not repeatedly re-request the review merely because the ordinary reviewer list is empty.

When the Copilot review completes:
1. fetch the current PR head and the immutable revision Copilot actually reviewed;
2. ingest Copilot findings as Reviewer findings, preserving their reviewed snapshot and evidence;
3. do not treat the provider identity as evidentiary authority or automatic approval;
4. route valid unresolved findings through `Integrator -> Builder -> Verifier` when repair is authorized;
5. if the external review is clean, use it as review evidence, then route consequential merge/readiness through Verifier and Integrator as usual;
6. if the PR head moved after the reviewed snapshot, do not silently extend that review to the new head—re-review or otherwise verify the changed surface as required by the assurance profile.

A hosted reviewer may also fail, be unavailable, hit usage limits, or return no review record. Record that external-state outcome explicitly; do not convert non-execution into a clean review.

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

A user-declared read-only boundary outranks review recording authority. If a source repository is read-only:
- inspect at immutable revision;
- record evidence elsewhere;
- do not comment, create issues, or open PRs there;
- implement adapters/audit records in an authorized repository only.