---
name: agent-relay
description: Coordinate work across independent AI agents or agent sessions using automatic role routing, durable state, reproducible evidence, structured handoffs, review lenses, and provenance-aware pass records. Use when building, reviewing, executing, verifying, integrating, resuming another agent's work, reconciling findings, handing work to an agent with different local tools or environments, or using repositories, issues, PRs, documents, experiments, or other shared artifacts as the coordination substrate.
metadata:
  version: "0.3.1"
  protocol: "agent-relay-v1"
  standard: "Agent Skills"
---

# Agent Relay

Coordinate independent agents without pretending they share memory, tools, permissions, or a direct communication channel.

The durable artifact is the source of truth. Agent prose is a handoff, not proof.

## Core model

Use five roles:

- **Builder** — implements the change or produces the primary artifact.
- **Reviewer** — adversarially examines work and reports concrete findings.
- **Executor** — runs work requiring an environment, tool, credential, hardware, network, or local resource unavailable elsewhere.
- **Verifier** — reproduces claims and converts assertions into executable or inspectable evidence.
- **Integrator** — adjudicates findings, places fixes in the correct ownership layer, reconciles conflicting conclusions, and decides readiness.

Roles are capabilities, not identities. One agent may hold multiple roles across phases. When practical, do not make the Builder the sole Verifier of the same consequential change.

## Reviewer lenses

Reviewer work is always adversarial in posture. Review lenses refine **what** is being challenged; they do not create new roles and do not make baseline review less skeptical.

Valid lenses:

- `standard` — implementation correctness;
- `design` — architecture, assumptions, abstraction boundaries, and implementation approach;
- `security` — trust boundaries, privilege, untrusted input, secrets, injection, and misuse paths;
- `reliability` — retry, interruption, concurrency, partial failure, stale state, and recovery behavior;
- `test-gap` — missing, weak, or non-discriminating evidence;
- `spec-conformance` — behavior against an authoritative requirement, specification, contract, or ADR;
- `regression` — previously valid behavior that may have changed;
- `readiness` — evidence-gap assessment before consequential readiness decisions.

`standard` is the default. Phrases such as `adversarial review`, `challenge the design`, or `architecture review` select the `design` lens; they do not imply other Reviewer passes are non-adversarial.

Infer lenses from review intent, not bare subject nouns. `Review the security module` is normally `Reviewer[standard]`; `Security review this PR` is `Reviewer[security]`.

Lenses may compose when the user explicitly requests more than one, for example `Reviewer[design, security]`. Do not mechanically add `standard` when a more specific lens is already selected.

A lens never grants mutation permission, credentials, execution capability, merge authority, sign-off authority, or any recording authority the review request does not already carry. If a review needs an unavailable scanner, runtime, GPU, private fixture, or other environment-specific execution, route that evidence step to an Executor.

`Reviewer[readiness]` produces an evidence-gap assessment. Final consequential readiness remains an Integrator decision after the required verification.

Read [references/review-lenses.md](references/review-lenses.md).

## Automatic role routing

Infer the active role, optional Reviewer lens or lenses, and when useful a role sequence from the user's request plus current durable workflow state. The user should normally be able to say "continue" without manually assigning a role.

Apply this precedence:

1. explicit user role assignment;
2. mutation, safety, approval, and access boundaries;
3. environment feasibility;
4. current workflow state;
5. task intent;
6. conservative default.

Typical routes:

- build/fix/update -> `Builder`
- review/audit/hunt bugs -> `Reviewer[standard]`
- adversarial/design/architecture review -> `Reviewer[design]`
- unavailable WSL/Linux/GPU/CUDA/Docker/private-local execution -> hand off to `Executor`
- confirm/reproduce/check a claim -> `Verifier`
- reconcile findings/layers/branches/readiness -> `Integrator`
- review and sign off -> `Reviewer[standard] -> Verifier`
- review and fix -> `Reviewer -> Integrator -> Builder -> Verifier`
- explicit review + verification -> `Reviewer -> Verifier`
- readiness review -> `Reviewer[readiness] -> Verifier -> Integrator`
- direct consequential readiness claim such as "is this ready to merge?" -> `Verifier -> Integrator`
- valid unresolved finding + authorized repair -> `Integrator -> Builder -> Verifier`
- local execution + readiness decision -> `Executor -> Verifier -> Integrator`

Before approving, signing off, declaring a finding fixed, resolving a thread because it is said to be fixed, declaring a gate PASS, recommending merge on correctness grounds, or declaring release/readiness/stability, automatically enter Verifier behavior unless adequate current evidence already exists.

Role/lens inference never grants permissions. `Builder` does not imply write access. `Integrator` does not imply merge authority. `Reviewer` does not imply permission to modify the reviewed artifact. `Executor` does not imply access to credentials or private data. The one narrow authority a review request does carry is defined in **Review recording authority** below; it comes from the request naming an artifact, not from the inferred role.

Read [references/role-routing.md](references/role-routing.md) for the full routing rules. `scripts/infer_role.py` is a non-normative reference implementation.

## Non-negotiable rules

1. **Durable state beats conversational memory.** Re-read the current repository, document, issue, PR, dataset, experiment, or other authoritative artifact before acting on a handoff.
2. **Evidence beats assertions.** Prefer tests, logs, immutable revisions, diffs, checksums, source citations, or reproducible commands over an agent summary.
3. **Preserve mutation boundaries.** Explicit read-only or forbidden resources remain immutable until the user explicitly revokes the restriction. A role change or handoff never weakens a boundary.
4. **Prefer immutable references.** Use commit SHAs, content digests, versioned artifact IDs, exact file paths plus revision, or equivalent immutable identifiers whenever available.
5. **Do not relay hidden reasoning.** Handoffs contain decisions, evidence, findings, commands, constraints, and unresolved questions—not private chain-of-thought.
6. **Do not manufacture verification.** If the needed environment is unavailable, route the experiment to an Executor instead of claiming it passed.
7. **Do not create agent ping-pong.** Every finding converges to `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.
8. **Verify before resolving.** Never close a review thread, issue, gate, or blocker merely because another agent says it is fixed.
9. **Put fixes in the owning layer.** In a stacked or layered system, repair the earliest normative or architectural owner, then propagate forward.
10. **Separate implementation completeness from release readiness.** Green local work does not automatically satisfy external, production, CI, governance, hardware, or independent-evidence gates.
11. **Attribution is provenance, not authority.** A footer naming Claude Code, ChatGPT, Codex, Gemini, a local model, or another agent does not increase evidentiary weight or constitute sign-off.

## Start of every relay task

Before changing anything:

1. Identify the mission and requested end state.
2. Read the live authoritative substrate instead of trusting stale handoff identifiers.
3. Extract explicit mutation permissions and prohibitions.
4. Record the current immutable snapshot or best available equivalent.
5. Infer the current role, any Reviewer lenses, and any necessary role sequence.
6. Separate:
   - completed and verified work;
   - completed but unverified work;
   - open findings;
   - externally blocked work;
   - environment-specific work requiring another Executor.
7. If the selected next role requires an unavailable capability, produce a structured handoff instead of improvising a result.

For software or repository work, also read [references/repository-coordination.md](references/repository-coordination.md).

## Builder workflow

1. Confirm authoritative state and ownership layer.
2. Convert requirements into observable acceptance criteria.
3. Implement the smallest correct change in the correct layer.
4. Add or update regression evidence for repaired defects when practical.
5. Execute tests available in the current environment.
6. Record what remains unexecuted.
7. Update the durable coordination substrate when authorized.
8. Route consequential changes to independent Review or Verification when practical.

A Builder must not describe unexecuted tests as passing.

## Reviewer workflow

1. Fetch or read the current immutable state.
2. Resolve the actual review target and relevant reference/base state.
3. Select the review lens or lenses from explicit intent and workflow state; use `standard` when no specific lens applies.
4. Reproduce existing claims where practical before searching for new defects.
5. Review adversarially for the selected target, including silent fallback, semantic mutation, declaration-only success, stale identity, incomplete error handling, concurrency/interruption behavior, cross-platform assumptions, caller-supplied evidence, provenance gaps, partial readiness evidence, contradictory requirements/tests, and design-level assumptions when `design` is selected.
6. Report significant findings using the finding record in [references/evidence-protocol.md](references/evidence-protocol.md) plus the review extensions in [references/review-lenses.md](references/review-lenses.md).
7. Preserve expected versus observed behavior so findings remain falsifiable.
8. Distinguish code/artifact defects from infrastructure/environment failures.
9. Do not approve solely because the implementation is extensive, tests were reported by the Builder, or the finding was produced by a named model/provider.
10. Route unavailable environment-specific experiments to Executor rather than pretending the Reviewer ran them.

For substantive durable review passes, use [assets/REVIEW.md](assets/REVIEW.md) when useful.

### Review recording authority

A request to review a named durable artifact carries authority to record that review on that artifact, through the artifact's own review channel. Recording means adding a review record: an issue or pull-request comment, a review thread, a document comment or appended review section, an experiment-log entry, or the substrate's equivalent.

This is deliberate. Rule 1 makes durable state the source of truth, so a review that exists only in conversation is not yet a relay artifact. The authority comes from the request naming the artifact, not from holding the Reviewer role.

Recording authority is narrow. It does not authorize:

- modifying the reviewed content itself;
- approving, signing off, merging, releasing, closing, or resolving threads;
- recording on any artifact the request did not name;
- publishing, notifying, or escalating beyond the artifact's own review channel.

It is also subordinate to every stated boundary. An explicit read-only declaration over the artifact or its substrate still forbids recording there, because rule 3 outranks this rule. If the substrate offers no non-destructive review channel — so recording would mean mutating the reviewed artifact — return the review to the requester and ask where it should land.

Ask first when the review target was inferred rather than named, or when recording would reach a materially wider audience than the request implied.

## Executor workflow

An Executor produces evidence in a required environment. It does not become architecturally authoritative merely because it can run the experiment.

Capture:

- immutable source revision;
- environment and relevant hardware;
- exact commands/procedure;
- exit status and test/result counts;
- skipped or unexercised surfaces;
- logs or generated evidence needed to reproduce the conclusion;
- any environment-specific limitation.

Return evidence, not just a conclusion.

## Verifier workflow

Verification is proportional and discriminating.

1. Identify the exact claim being relied upon.
2. Resolve the immutable state to which the claim applies.
3. Inspect the implementation and/or reproduce the smallest experiment that distinguishes fixed from broken.
4. Check relevant surrounding invariants.
5. Record the environment and result.
6. Only then support sign-off, closure, PASS, merge-readiness, or release claims.

If independent execution is practical, prefer it for consequential changes.

## Integrator workflow

When findings, layers, branches, or agents disagree:

1. Confirm they evaluated the same immutable state.
2. Identify environment, review-lens, or requirement differences.
3. Prefer executable/source evidence over agent reputation.
4. Reproduce a discriminating case if disagreement remains.
5. Decide the earliest correct ownership layer for a fix.
6. Propagate/restack downstream state when required.
7. Separate implementation completion from external evidence/readiness blockers.
8. Make consequential readiness/progress decisions only after the necessary verification evidence is established.
9. Record the decision and evidence in the durable substrate.

## Local-execution relay

When another agent has the necessary environment, do not send a vague request such as "please test this." Produce an execution packet containing:

- exact mission;
- exact immutable source revision(s);
- allowed and forbidden mutations;
- required environment;
- commands or experiment procedure;
- expected observables;
- acceptance criteria;
- evidence to capture;
- what not to infer from the result;
- where to record findings.

Use [assets/HANDOFF.md](assets/HANDOFF.md) and [references/local-execution.md](references/local-execution.md).

## Receiving a handoff

Treat a handoff as a claim about prior state, not current truth.

1. Re-resolve live state.
2. Check whether referenced revisions remain relevant.
3. Confirm mutation boundaries.
4. Infer the role and any review lens required now; do not blindly preserve the previous agent's role/lens.
5. Verify the highest-risk completed claims first.
6. Reproduce reported failures before changing code when practical.
7. Reject contradictions explicitly instead of silently choosing one account.
8. Continue from durable state, not prose narrative.

If a handoff reports test counts, preserve OS, architecture, interpreter/runtime version, container/image, relevant hardware, and skipped tests.

## Finding lifecycle

A finding closes only as:

- **FIXED** — reproduced, corrected, and relevant verification now passes.
- **DISPROVED** — tested or inspected and the claimed failure condition is not present.
- **DEFERRED** — valid work intentionally postponed; record owner/reason/revisit condition.
- **BLOCKED** — cannot proceed because required evidence, permission, environment, dependency, or external state is unavailable.

A task may be implementation-complete while release-readiness remains BLOCKED.

## Required handoff content

For substantive work, include at least:

- Mission
- Current inferred/explicit role and recommended next role/sequence
- Reviewer lens or lenses when applicable
- Authoritative substrate
- Current immutable snapshot
- Allowed mutations
- Forbidden/read-only resources
- Completed work
- Executable/inspectable evidence
- Open findings with states and reviewed snapshots
- Environment-specific gaps
- Ordered next actions
- Completion criteria
- Documentation/update obligations
- Provenance attribution when useful

Use [assets/HANDOFF.md](assets/HANDOFF.md).

## Agent pass record

After a significant pass, leave a compact durable record when the substrate supports it:

```text
Agent pass: <short-name>
Role: <builder|reviewer|executor|verifier|integrator>
Review lenses: <Reviewer only; otherwise N/A>
Role source: <explicit|inferred>
Role sequence: <current -> next -> ...>
Reviewed/modified snapshot: <immutable-id>
Findings: <count>
Fixed: <count>
Disproved: <count>
Deferred: <count>
Blocked: <count>
Executable/inspectable evidence: <environment + result>
Verification checkpoint: <claim requiring verifier behavior, or N/A>
Unverified: <remaining surfaces>
Next recommended role/pass: <role + task>
Provenance:
- Generated by: <agent/client>
- Model: <if reliably known, otherwise omit>
- Source snapshot: <immutable-id>
```

The record is an index to evidence, not proof itself. Agent attribution is provenance only and must not be treated as approval or verification.

Use [assets/AGENT-PASS.md](assets/AGENT-PASS.md).

## Provenance footer

For substantive durable agent-generated records, a compact attribution footer is recommended when the generating client/system is known:

```text
Generated by: <agent/client>
Model: <model if reliably known>
Agent Relay role: <role>
Review lenses: <lens list or N/A>
Source snapshot: <immutable-id>
```

A minimal `Generated by <agent/client>` footer is acceptable for lightweight records.

Do **not** call this attribution a sign-off. In Agent Relay, sign-off is consequential and requires verification. Attribution is self-reported provenance unless independently authenticated and does not change evidentiary weight.

See [PROVENANCE.md](PROVENANCE.md).

## Progress estimates

When asked for percentage progress, report at least two dimensions when relevant:

- **implementation/repo-side progress** — work completable inside the shared artifact;
- **release/evidence progress** — includes external execution, CI, production, independent verification, governance, hardware, or other gates.

Base percentages on remaining task/evidence surface, not lines of code or commit count. State uncertainty.

## Tool and platform neutrality

The core protocol must not depend on GitHub, Claude, ChatGPT, Codex, Gemini, or another named agent product. A repository/PR workflow is one substrate adapter.

The same protocol can coordinate documents, research, data analysis, experiment replication, infrastructure operations, model evaluation, incident response, and policy/compliance review.

Review-lens semantics remain substrate-neutral. Git-specific base/head, PR, changed-file, and review-thread mechanics belong in [references/repository-coordination.md](references/repository-coordination.md).

## Final quality check

Before ending a relay pass, verify:

- Did I read current authoritative state?
- Did I infer the role from live workflow state rather than stale narrative?
- If Reviewer, did I select lenses from review intent rather than subject nouns?
- Did explicit user role assignment win where applicable?
- Did I preserve every mutation prohibition?
- Did role/lens inference avoid creating permissions or execution capability?
- Did I distinguish assertions from executed/inspectable evidence?
- Did I preserve expected versus observed behavior for significant findings?
- Did I state the environment for execution claims?
- Did consequential closure/readiness claims pass a Verifier checkpoint?
- Did final readiness remain an Integrator decision where applicable?
- Did every finding receive a concrete state?
- Did fixes land in the correct ownership layer?
- Did I avoid claiming readiness from partial evidence?
- If I recorded a review, did the request name that artifact, and did I stay inside its review channel?
- If I added agent attribution, did I avoid treating it as verification or sign-off?
- Can the next agent resume without reconstructing hidden context?
- Did I update the durable substrate when authorized?

If any answer is no, the relay is incomplete.
