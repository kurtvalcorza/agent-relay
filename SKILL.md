---
name: agent-relay
description: Coordinate work across independent AI agents or agent sessions using automatic role routing, durable state, reproducible evidence, structured handoffs, review lenses, bounded authority, runtime-adapter contracts, and provenance-aware pass records. Use when building, reviewing, executing, verifying, integrating, resuming another agent's work, reconciling findings, handing work to an agent with different local tools or environments, or using repositories, issues, PRs, documents, experiments, or other shared artifacts as the coordination substrate.
metadata:
  version: "0.4.0"
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

## Mission, authority, and evidence semantics

Agent Relay v0.4 adds orthogonal semantics around the five roles rather than adding new roles.

- **Mission mode** — what kind of work is occurring: `build`, `fix`, `test`, `orchestrate`, `operate`, `understand`, `plan`, `analyze`, or `communicate`. Mode never grants permission or authority. See [references/mission-modes.md](references/mission-modes.md).
- **Decision authority** — who may decide mission, scope, architecture, acceptance, implementation, execution, evidence, and readiness. Mutation permission and decision authority are separate axes. See [references/decision-authority.md](references/decision-authority.md).
- **Mission anchor** — the immutable revision/digest of the planning state a pass is acting against. Mutable issue/document locations may locate an anchor but cannot identify it without a substrate-native revision or content digest.
- **Claim/evidence maturity** — `ASSERTED`, `INSPECTED`, `EXECUTED`, `VERIFIED`. The state applies to a claim, not to a finding. See [references/evidence-protocol.md](references/evidence-protocol.md).
- **Assurance profile** — `exploratory`, `standard`, or `consequential`; it determines how demanding the verification contract must be before a claim can become `VERIFIED`.
- **Verification contract** — a declared falsifiable procedure/oracle connecting a consequential requirement and acceptance criterion to evidence and Verifier judgment.
- **Stagnation signal** — evidence that the current route is not converging and should be reconsidered. It is not a finding state or cycle termination state. See [references/stagnation-escalation.md](references/stagnation-escalation.md).

Execution autonomy does not imply planning authority. A Builder may autonomously modify many files within a writable surface while remaining prohibited from changing the mission, architecture, acceptance criteria, or verification burden.

## Automatic role routing

Infer the active role, optional Reviewer lens or lenses, and when useful a role sequence from the user's request plus current durable workflow state. The user should normally be able to say "continue" without manually assigning a role.

Apply this precedence:

1. explicit user role assignment;
2. mutation, safety, approval, access, and decision-authority boundaries;
3. environment feasibility;
4. current workflow state;
5. task intent;
6. conservative default.

Typical routes:

- build/fix/update -> `Builder`
- review/audit/hunt bugs -> `Reviewer[standard]`
- adversarial/design/architecture review -> `Reviewer[design]`
- identify missing/non-discriminating tests -> `Reviewer[test-gap]`
- author/create tests -> `Builder`
- unavailable WSL/Linux/GPU/CUDA/Docker/private-local execution -> hand off to `Executor`
- confirm/reproduce/check a claim -> `Verifier`
- reconcile findings/layers/branches/readiness/authority conflicts -> `Integrator`
- review and sign off -> `Reviewer[standard] -> Verifier`
- review and fix -> `Reviewer -> Integrator -> Builder -> Verifier`
- explicit review + verification -> `Reviewer -> Verifier`
- readiness review -> `Reviewer[readiness] -> Verifier -> Integrator`
- direct consequential readiness claim such as "is this ready to merge?" -> `Verifier -> Integrator`
- valid unresolved finding + authorized repair -> `Integrator -> Builder -> Verifier`
- local execution + readiness decision -> `Executor -> Verifier -> Integrator`

Before approving, signing off, declaring a finding fixed, resolving a thread because it is said to be fixed, declaring a gate PASS, recommending merge on correctness grounds, or declaring release/readiness/stability, automatically enter Verifier behavior unless adequate current evidence already exists.

Role/lens/mode inference never grants permissions or decision authority. `Builder` does not imply write access. `Integrator` does not imply merge authority. `Reviewer` does not imply permission to modify the reviewed artifact. `Executor` does not imply access to credentials or private data. The one narrow authority a review request does carry is defined in **Review recording authority** below; it comes from the request naming an artifact, not from the inferred role.

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
10. **Separate implementation completeness from release readiness.** Green local work does not automatically satisfy external, production, CI, governance, hardware, assurance, or independent-evidence gates.
11. **Attribution is provenance, not authority.** A footer naming Claude Code, ChatGPT, Codex, Gemini, a local model, or another agent does not increase evidentiary weight or constitute sign-off.
12. **Autonomy is not authority.** Mutation capability or broad execution discretion never permits an agent to redefine a decision outside its authority envelope.
13. **Consequential requirements need falsifiable evidence when practicable.** Bind them to a verification contract; if no practicable oracle exists, record `verification: none — <reason>` rather than silently omitting evidence expectations.
14. **Fail closed on safety-bearing adapter fields.** A runtime that cannot honor source identity, mission anchor, mutation boundary, decision authority, assurance profile, or configured bounds refuses the pass rather than dropping the field.
15. **Non-execution is never success.** A failed/skipped pass cannot be represented as a clean review or verification result.

## Start of every relay task

Before changing anything:

1. Identify the mission and requested end state.
2. Read the live authoritative substrate instead of trusting stale handoff identifiers.
3. Resolve the current mission anchor or create/reference an immutable/digested planning state when the mission is consequential or long-running.
4. Extract explicit mutation permissions/prohibitions and decision-authority boundaries.
5. Record the current immutable snapshot or best available equivalent.
6. Infer the current role, mission mode, any Reviewer lenses, and any necessary role sequence.
7. Select/confirm the assurance profile and verification contracts for consequential relied-upon requirements where applicable.
8. Separate:
   - completed and verified work;
   - completed but unverified work and its claim maturity;
   - open findings;
   - externally blocked work;
   - environment-specific work requiring another Executor.
9. If the selected next role requires an unavailable capability or an out-of-authority decision, produce a structured handoff/escalation instead of improvising a result.

For software or repository work, also read [references/repository-coordination.md](references/repository-coordination.md).

## Builder workflow

1. Confirm authoritative state, mission anchor, authority envelope, and ownership layer.
2. Convert requirements into observable acceptance criteria and, for consequential requirements when practicable, a discriminating verification contract.
3. Implement the smallest correct change in the correct layer and inside mutation/authority boundaries.
4. Add or update regression/negative-control evidence for repaired defects when practical.
5. Execute tests available in the current environment.
6. Record claims no stronger than the evidence (`ASSERTED`, `INSPECTED`, or `EXECUTED` until Verifier behavior establishes `VERIFIED`).
7. Record what remains unexecuted or outside the current assurance burden.
8. Update the durable coordination substrate when authorized.
9. Route consequential changes to independent Review or Verification when practical.

A Builder must not describe unexecuted tests as passing or self-promote a consequential claim to `VERIFIED`.

## Reviewer workflow

1. Fetch or read the current immutable state and mission anchor when applicable.
2. Resolve the actual review target and relevant reference/base state.
3. Select the review lens or lenses from explicit intent and workflow state; use `standard` when no specific lens applies.
4. Reproduce existing claims where practical before searching for new defects.
5. Review adversarially for the selected target, including silent fallback, semantic mutation, declaration-only success, stale identity, incomplete error handling, concurrency/interruption behavior, cross-platform assumptions, caller-supplied evidence, provenance gaps, partial readiness evidence, contradictory requirements/tests, and design-level assumptions when `design` is selected.
6. Challenge the verification contract itself when a claimed oracle would not distinguish the relevant failure condition.
7. Report significant findings using the finding record in [references/evidence-protocol.md](references/evidence-protocol.md) plus the review extensions in [references/review-lenses.md](references/review-lenses.md).
8. Preserve expected versus observed behavior and the original observation snapshot so findings remain falsifiable across later repairs.
9. Distinguish code/artifact defects from infrastructure/environment failures.
10. Do not approve solely because the implementation is extensive, tests were reported by the Builder, or the finding was produced by a named model/provider.
11. Route unavailable environment-specific experiments to Executor rather than pretending the Reviewer ran them.

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

- immutable source revision and mission anchor when relevant;
- environment and relevant hardware;
- exact commands/procedure;
- exit status and test/result counts;
- skipped or unexercised surfaces;
- logs or generated evidence needed to reproduce the conclusion;
- any environment-specific limitation;
- mutations actually performed.

Return evidence, not just a conclusion. Successful execution advances an appropriate claim to `EXECUTED`; it does not independently establish `VERIFIED` or readiness.

## Verifier workflow

Verification is proportional, discriminating, and bound to the claim.

1. Identify the exact claim being relied upon and its required assurance profile.
2. Resolve the immutable source state, mission anchor, and environment to which the claim applies.
3. Inspect the declared verification contract and confirm that it can distinguish the relevant failure condition; for consequential repairs, prefer the required negative/regression control.
4. Execute/inspect the smallest experiment that distinguishes fixed from broken, or independently inspect adequate current execution evidence.
5. Check relevant surrounding invariants required by the assurance profile.
6. Record the environment, result, contract, and immutable state.
7. Only then promote the claim to `VERIFIED` and support closure/PASS/merge-readiness/release inputs.

If independent execution is practical, prefer it for consequential changes. `VERIFIED` is a claim status, not whole-artifact readiness.

## Integrator workflow

When findings, layers, branches, authorities, or agents disagree:

1. Confirm they evaluated the same immutable state and mission-anchor revision.
2. Identify environment, review-lens, authority, assurance, or requirement differences.
3. Prefer executable/source evidence over agent reputation.
4. Reproduce a discriminating case if disagreement remains.
5. Decide the earliest correct ownership layer for a fix.
6. Adjudicate out-of-authority decisions rather than letting the executing actor self-delegate; mission-anchor revisions that reassign authority require authorization from the current authority holder.
7. Treat repeated non-progress as a stagnation signal and route to a changed Reviewer lens, Executor, replanning, or another justified decision function rather than blind retry.
8. Propagate/restack downstream state when required.
9. Separate implementation completion from external evidence/readiness blockers and from bounded-cycle termination.
10. Make consequential readiness/progress decisions only after the necessary verification contracts/assurance evidence are established.
11. Record the decision, authority source, evidence, and any mission-anchor revision in durable state.

## Bounded iterative review and runtime adapters

Iterative review is a composition of ordinary passes, not a new role or finding lifecycle. See [references/iterative-review.md](references/iterative-review.md).

A bounded cycle records planned versus executed passes, per-pass execution status, finding continuity across snapshots, explicit bounds, and a small termination vocabulary (`NO_NEW_FINDINGS`, `BOUND_EXHAUSTED`, `BLOCKED`, `CANCELLED`). `NO_NEW_FINDINGS` never means verified or ready.

Runtime adapters are optional execution backends. The Agent Relay protocol identifier and adapter data contract are versioned separately; adapters fail closed on safety-bearing fields. See [references/runtime-adapters.md](references/runtime-adapters.md).

Parallel mutation MUST NOT proceed unless declared surfaces are demonstrably disjoint under the coordination scope's comparison rule or the substrate has an explicit safe multi-writer mechanism with recorded conflict semantics. Otherwise serialize or refuse.

Every mutation-producing pass/cycle keeps from/to snapshot transitions attributable to the pass/cycle that caused them.

## Local-execution relay

When another agent has the necessary environment, do not send a vague request such as "please test this." Produce an execution packet containing:

- exact mission and mission-anchor identity when applicable;
- exact immutable source revision(s);
- allowed and forbidden mutations;
- decision-authority limits relevant to execution;
- required environment;
- commands or experiment procedure;
- verification contract / expected observables;
- assurance profile where relevant;
- acceptance criteria;
- evidence to capture;
- what not to infer from the result;
- where to record findings.

Use [assets/HANDOFF.md](assets/HANDOFF.md) and [references/local-execution.md](references/local-execution.md).

## Receiving a handoff

Treat a handoff as a claim about prior state, not current truth.

1. Re-resolve live authoritative state.
2. Check whether referenced source, mission-anchor, and external-specification revisions remain relevant.
3. Confirm mutation boundaries and decision authority.
4. Infer the role, mission mode, and any review lens required now; do not blindly preserve the previous agent's role/lens.
5. Preserve each finding's original observation/reviewed snapshot rather than silently retargeting it to the new head.
6. Preserve environment qualification on carried execution evidence.
7. Verify the highest-risk completed claims first.
8. Reproduce reported failures before changing code when practical.
9. Reject contradictions explicitly instead of silently choosing one account.
10. Continue from durable state, not prose narrative.

If a referenced authoritative specification moved, route the divergence to the appropriate mission/scope/architecture/acceptance authority holder and establish an authorized mission-anchor revision before relying on changed semantics.

If a handoff reports test counts, preserve OS, architecture, interpreter/runtime version, container/image, relevant hardware, and skipped tests.

A substantive handoff should be cold-start resumable: a fresh session with no conversational history can reconstruct the mission, current immutable state, boundaries, findings with observation snapshots, evidence/environment, next action, and verification checkpoint from durable artifacts alone. See [references/runtime-adapters.md](references/runtime-adapters.md).

## Finding lifecycle

The lifecycle is `OPEN -> FIXED | DISPROVED | DEFERRED | BLOCKED`. A finding closes only as:

- **FIXED** — reproduced, corrected, and relevant verification now passes.
- **DISPROVED** — tested or inspected and the claimed failure condition is not present.
- **DEFERRED** — valid work intentionally postponed; record owner/reason/revisit condition.
- **BLOCKED** — cannot proceed because required evidence, permission, environment, dependency, or external state is unavailable.

`DEFERRED` and `BLOCKED` are terminal dispositions that remain tracked, not permission to stop carrying the finding. [references/evidence-protocol.md](references/evidence-protocol.md) owns this vocabulary and disambiguates it from claim maturity, pass execution status, and cycle termination.

A task may be implementation-complete while release-readiness remains BLOCKED.

Finding lifecycle is independent of claim maturity, pass execution status, and bounded-cycle termination. Do not invent a third lifecycle for stagnation.

## Required handoff content

For substantive work, include at least:

- Mission
- Mission anchor / immutable planning reference when material
- Current inferred/explicit role and recommended next role/sequence
- Mission mode when useful
- Reviewer lens or lenses when applicable
- Decision-authority envelope when material
- Assurance profile and verification contracts for consequential claims when applicable
- Authoritative substrate
- Current immutable snapshot
- Allowed mutations
- Forbidden/read-only resources
- Completed work
- Executable/inspectable evidence with environment
- Completed but unverified claims with maturity
- Open findings with states and original observation/reviewed snapshots, or explicit `None.`
- Environment-specific gaps
- Ordered next actions
- Verification checkpoint
- Completion criteria
- Documentation/update obligations
- Provenance attribution when useful

Use [assets/HANDOFF.md](assets/HANDOFF.md).

## Agent pass record

After a significant pass, leave a compact durable record when the substrate supports it. v0.4 permits optional mission/cycle/authority metadata while preserving the v0.3 minimum.

[assets/AGENT-PASS.md](assets/AGENT-PASS.md) is the canonical record; the block below is the common subset and omits the cycle-detail fields (`Cycle pass`, `Planned lens sequence`, `Cycle budget`, `Predecessor pass/checkpoint`, `Stagnation signal`). Three fields here are conditionally required rather than optional: a mutation-producing pass MUST record `Mutation surface/transition` (see **Bounded iterative review and runtime adapters**), executable work MUST record `Environment`, and a consequential requirement MUST record a `Verification contracts` entry or an explicit `verification: none — reason` (rule 13).

```text
Agent pass: <short-name>
Role: <builder|reviewer|executor|verifier|integrator>
Review lenses: <Reviewer only; otherwise N/A>
Mission mode: <mode or N/A>
Role source: <explicit|inferred>
Role sequence: <current -> next -> ...>
Mission anchor: <immutable revision/digest or N/A>
Decision authority: <summary/reference>
Assurance profile: <exploratory|standard|consequential|N/A>
Mutation boundary: <allowed + read-only/forbidden summary>
Previous snapshot: <immutable-id or N/A>
Reviewed/modified snapshot: <immutable-id>
Mutation surface/transition: <surface + from/to snapshots + pass/cycle attribution, or N/A>
Environment: <if executable work occurred, otherwise N/A>
Execution status: <RAN|FAILED|SKIPPED|N/A>
Cycle ID: <id or N/A>
Termination reason: <NO_NEW_FINDINGS|BOUND_EXHAUSTED|BLOCKED|CANCELLED|N/A>
Claims / evidence maturity: <claim + state + snapshot/environment>
Verification contracts: <claim/requirement -> falsifiable procedure/oracle, or `verification: none — reason`>
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

The core protocol must not depend on GitHub, Claude, ChatGPT, Codex, Gemini, Antigravity, or another named agent product. A repository/PR workflow is one substrate adapter. External systems whose ideas Agent Relay adapts are recorded, with their source pins, in [references/prior-art.md](references/prior-art.md); they are prior art, not dependencies or normative authority.

The same protocol can coordinate documents, research, data analysis, experiment replication, infrastructure operations, model evaluation, incident response, and policy/compliance review.

Review-lens semantics remain substrate-neutral. Git-specific base/head, PR, changed-file, and review-thread mechanics belong in [references/repository-coordination.md](references/repository-coordination.md). Runtime-specific loop/concurrency mechanics belong in [references/runtime-adapters.md](references/runtime-adapters.md) and [references/iterative-review.md](references/iterative-review.md).

## Final quality check

Before ending a relay pass, verify:

- Did I read current authoritative state?
- Did I resolve the current mission anchor/specification revision when material?
- Did I infer the role/mode from live workflow state rather than stale narrative?
- If Reviewer, did I select lenses from review intent rather than subject nouns and remain adversarial?
- Did explicit user role assignment win where applicable?
- Did I preserve every mutation prohibition and decision-authority limit?
- Did role/lens/mode inference avoid creating permissions or authority?
- Did consequential requirements have a falsifiable verification contract when practicable, or an explicit reason none exists?
- Did I distinguish `ASSERTED`, `INSPECTED`, `EXECUTED`, and `VERIFIED` claims?
- Did I preserve expected versus observed behavior and original snapshots for significant findings?
- Did I state the environment for execution claims?
- Did consequential closure/readiness claims pass the required assurance/Verifier checkpoint?
- Did final readiness remain an Integrator decision where applicable?
- Did every finding receive a concrete state or remain explicitly carried in an active successor cycle?
- Did fixes land in the correct ownership layer?
- Did I avoid claiming readiness from partial evidence or clean cycle termination?
- If parallel mutation occurred, were surfaces disjoint or safe multi-writer semantics explicitly declared and transitions attributable?
- If I recorded a review, did the request name that artifact, and did I stay inside its review channel?
- If I added agent attribution, did I avoid treating it as verification or sign-off?
- Can a fresh agent/session resume from durable state without reconstructing hidden conversational context?
- Did I update the durable substrate when authorized?

If any answer is no, the relay is incomplete.