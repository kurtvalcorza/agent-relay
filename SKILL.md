---
name: agent-relay
description: Coordinate work across independent AI agents or agent sessions using explicit roles, durable state, reproducible evidence, and structured handoffs. Use when assigning builder, reviewer, executor, verifier, or integrator roles; handing work to an agent with different local tools or environments; resuming another agent's work; reconciling agent findings; or using repositories, issues, PRs, documents, or other shared artifacts as the coordination substrate.
metadata:
  version: "0.1.0"
  protocol: "agent-relay-v1"
  standard: "Agent Skills"
---

# Agent Relay

Coordinate independent agents without pretending they share memory, tools, or a direct communication channel.

The durable artifact is the source of truth. Agent prose is a handoff, not proof.

## Core model

Use five roles. One agent may hold multiple roles across different phases, but avoid making the builder the sole verifier of the same change when independent verification is practical.

- **Builder** — implements the change or produces the primary artifact.
- **Reviewer** — adversarially examines the builder's work and reports concrete findings.
- **Executor** — runs work requiring an environment, tool, credential, hardware, network, or local resource unavailable to another agent.
- **Verifier** — reproduces claims and converts assertions into executable or inspectable evidence.
- **Integrator** — adjudicates findings, places fixes in the correct ownership layer, reconciles conflicting agent conclusions, and decides readiness.

Roles are capabilities, not identities. Switch roles when useful.

## Non-negotiable rules

1. **Durable state beats conversational memory.** Re-read the current repository, document, issue, PR, dataset, or other authoritative artifact before acting on a handoff.
2. **Evidence beats assertions.** Prefer tests, logs, immutable revisions, diffs, checksums, source citations, or reproducible commands over an agent's summary.
3. **Preserve mutation boundaries.** Treat explicit read-only or forbidden resources as immutable until the user explicitly revokes the restriction. A handoff never weakens an existing boundary.
4. **Prefer immutable references.** Use commit SHAs, content digests, versioned artifact IDs, exact file paths plus revision, or equivalent immutable identifiers whenever available.
5. **Do not relay hidden reasoning.** Handoffs contain decisions, evidence, findings, commands, and unresolved questions—not private chain-of-thought.
6. **Do not manufacture verification.** If the needed environment is unavailable, hand the experiment to an Executor instead of claiming it passed.
7. **Do not create agent ping-pong.** Every finding should converge to one of: `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.
8. **Verify before resolving.** Never close a review thread, issue, gate, or blocker merely because a later agent says it is fixed.
9. **Put fixes in the owning layer.** In a stacked or layered system, repair the earliest normative/architectural owner, then propagate forward.
10. **Separate implementation completeness from release readiness.** Green local work does not automatically satisfy external, production, CI, governance, or independent-evidence gates.

## Start of every relay task

Before changing anything:

1. Identify the **mission** and requested end state.
2. Identify the current **role** you are being asked to play.
3. Identify the **coordination substrate**: repository, PR stack, issue tracker, shared folder, document set, database, experiment store, or other durable state.
4. Read the live state rather than trusting stale handoff identifiers.
5. Extract all explicit **mutation permissions and prohibitions**.
6. Record the current immutable snapshot or best available equivalent.
7. Separate:
   - completed and verified work;
   - completed but unverified work;
   - open findings;
   - externally blocked work;
   - local-execution work that requires another environment.

If the task is software/repository work, read [references/repository-coordination.md](references/repository-coordination.md).

## Choose the next role

Use this decision order:

- If the user asks you to **build or fix**, act as Builder unless the work requires an unavailable environment.
- If the user asks you to **review, audit, hunt bugs, challenge, or sign off**, act as Reviewer.
- If the work requires **local execution, GPU/CUDA, Docker, WSL/Linux, private local files, credentials, devices, or inaccessible repos**, define the experiment and hand it to an Executor with that environment.
- If a previous agent reports successful work but the user wants confidence, act as Verifier first.
- If multiple agents have produced conflicting findings or a stacked/layered system must be reconciled, act as Integrator.

Read [references/roles.md](references/roles.md) for the full role playbook.

## Builder workflow

1. Confirm the authoritative state and ownership layer.
2. Convert requirements into observable acceptance criteria.
3. Implement the smallest correct change in the correct layer.
4. Add or update regression evidence for every repaired defect when practical.
5. Execute all tests available in the current environment.
6. Record what remains unexecuted.
7. Update the durable coordination substrate with the change and evidence.
8. Request independent review or verification for consequential changes.

A Builder must not describe unexecuted tests as passing.

## Reviewer workflow

1. Fetch or read the current immutable state.
2. Reproduce existing claims where possible before searching for new defects.
3. Review adversarially for:
   - silent fallback or semantic mutation;
   - declaration-only success;
   - stale or mutable identity;
   - incomplete error handling;
   - concurrency and interruption behavior;
   - cross-platform assumptions;
   - trust in caller-supplied evidence;
   - missing provenance or dependency closure;
   - partial evidence satisfying readiness;
   - contradictory tests or requirements.
4. Report findings with severity, concrete failure mode, owning layer, and evidence.
5. Distinguish code defects from infrastructure or environment failures.
6. Do not approve solely because the implementation is extensive or the diff looks reasonable.

Use the finding states in [references/evidence-protocol.md](references/evidence-protocol.md).

## Local-execution relay

When another agent has the necessary environment, do not send a vague request such as "please test this." Produce an execution packet containing:

- exact mission;
- exact immutable source revision(s);
- allowed and forbidden mutations;
- environment required;
- commands or experiment procedure;
- expected observables;
- acceptance criteria;
- evidence to capture;
- what not to infer from the result;
- where to record findings.

The Executor should return evidence, not just a conclusion.

Use [assets/HANDOFF.md](assets/HANDOFF.md) as the default packet and [references/local-execution.md](references/local-execution.md) for environment-specific guidance.

## Receiving a handoff

Treat a handoff as a claim about prior state, not as current truth.

1. Re-resolve current state.
2. Check whether referenced revisions are still live/relevant.
3. Confirm mutation boundaries.
4. Verify the highest-risk completed claims first.
5. Reproduce reported failures before changing code when practical.
6. Reject contradictions explicitly instead of silently choosing one agent's account.
7. Continue from the durable state, not from the prose narrative.

If a handoff reports test counts, preserve the environment context: OS, architecture, interpreter/runtime version, container/image, relevant hardware, and skipped tests.

## Integrating multiple agent results

When two agents disagree:

1. Identify whether they evaluated the same immutable state.
2. Identify environment differences.
3. Identify whether they are using the same requirement/acceptance criteria.
4. Prefer direct executable or source evidence.
5. Run a discriminating experiment if the disagreement remains.
6. Record the decision and evidence in the durable substrate.

Never resolve disagreement by agent reputation alone.

## Completion semantics

A finding closes only as one of:

- **FIXED** — the defect was reproduced, corrected, and the relevant evidence now passes.
- **DISPROVED** — the suspected defect was tested or inspected and the claimed failure condition is not present.
- **DEFERRED** — valid work intentionally postponed; record owner/reason/condition for revisit.
- **BLOCKED** — cannot proceed because required evidence, permission, environment, dependency, or external state is unavailable.

A task may be implementation-complete while release-readiness remains BLOCKED.

## Required handoff content

For substantive work, a handoff should contain at least:

- Mission
- Current role and recommended next role
- Authoritative substrate
- Current immutable snapshot
- Allowed mutations
- Forbidden/read-only resources
- Completed work
- Executable/inspectable evidence
- Open findings with states
- Environment-specific gaps
- Ordered next actions
- Completion criteria
- Documentation/update obligations

Use [assets/HANDOFF.md](assets/HANDOFF.md).

## Agent pass record

After a significant pass, leave a compact durable record whenever the substrate supports it:

```text
Agent pass: <short-name>
Role: <builder|reviewer|executor|verifier|integrator>
Reviewed/modified snapshot: <immutable-id>
Findings: <count>
Fixed: <count>
Disproved: <count>
Deferred: <count>
Blocked: <count>
Executable evidence: <environment + result>
Unverified: <remaining surfaces>
Next recommended role/pass: <role + task>
```

Do not treat the record itself as proof; link or identify the underlying evidence.

## Progress estimates

When asked for percentage progress, report at least two dimensions when relevant:

- **implementation/repo-side progress** — work that can be completed inside the shared artifact;
- **release/evidence progress** — includes external execution, CI, production, independent verification, governance, hardware, or other gates.

Base percentages on remaining task/evidence surface, not lines of code or number of commits. Call out uncertainty.

## Tool and platform neutrality

The core protocol must not depend on GitHub, Claude, ChatGPT, Codex, or any named agent product.

A repository/PR workflow is only one substrate adapter. The same protocol applies to:

- documents and editorial review;
- research and literature verification;
- data analysis and experiment replication;
- infrastructure operations;
- model evaluation;
- incident response;
- policy/compliance review.

If using GitHub or another VCS/issue tracker, apply [references/repository-coordination.md](references/repository-coordination.md).

## Final quality check

Before ending a relay pass, verify:

- Did I read the current authoritative state?
- Did I preserve every explicit mutation prohibition?
- Did I distinguish assertions from executed/inspectable evidence?
- Did I state the environment for execution claims?
- Did every new finding get a concrete state?
- Did fixes land in the correct ownership layer?
- Did I avoid claiming readiness from partial evidence?
- Is the next agent able to resume without reconstructing hidden context?
- Did I update the durable coordination substrate when authorized?

If any answer is no, the relay is incomplete.
