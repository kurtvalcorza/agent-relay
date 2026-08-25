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

## Review comments

A good durable review finding contains:
- concrete defect;
- severity;
- affected requirement/invariant;
- exact reviewed revision;
- reproduction or source evidence;
- suggested owning layer, if known.

After fixing:
1. verify the condition on the current code;
2. reply with the fixing revision and regression evidence when useful;
3. resolve only then.

Do not bulk-resolve old threads because they appear outdated.

## PR/body documentation

Use PR descriptions for durable current-state architecture and evidence summaries.
Use review threads for localized defects and technical debate.
Use top-level comments for pass summaries/checkpoints.
Use code/tests as the strongest evidence.

## Read-only repositories

Credentials granting write access do not override a user-declared read-only boundary.

If a source repository is read-only:
- inspect at immutable revision;
- record evidence elsewhere;
- do not comment, create issues, or open PRs there;
- implement adapters/audit records in an authorized repository only.
