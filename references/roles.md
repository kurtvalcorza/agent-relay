# Role Playbook

Agent Relay separates implementation authority from evidence authority so independent agents can contribute without assuming shared memory or identical capabilities.

## Builder

Use when the agent is responsible for producing or modifying the primary artifact.

Responsibilities:
- identify the owning layer;
- implement the minimum correct change;
- add regression evidence;
- execute available verification;
- disclose unexecuted surfaces;
- preserve compatibility and stated mutation boundaries;
- prepare work for independent review.

Builder anti-patterns:
- self-approving consequential work;
- calling tests green when they were not run;
- fixing a symptom in a downstream layer when the defect is owned upstream;
- treating reviewer disagreement as an obstacle instead of evidence to adjudicate.

## Reviewer

Use for adversarial inspection of an existing artifact.

Responsibilities:
- read the exact reviewed revision;
- reproduce failures where practical;
- identify concrete failure cases;
- distinguish correctness defects from quality/style preferences;
- bind findings to requirements or acceptance criteria;
- keep unresolved uncertainty visible.

High-value reviewer prompts:
- What can silently succeed without proving the claim?
- What mutable state is being mistaken for identity?
- What happens during interruption, retry, or concurrent execution?
- Can malformed but schema-valid input crash the system?
- Can partial evidence satisfy a readiness state?
- Does an external dependency change the semantics without changing identity?
- Is one environment accidentally defining the contract?

## Executor

Use when work depends on an environment unavailable to the coordinating agent.

Examples:
- WSL/Linux filesystem semantics;
- GPU/CUDA/NVIDIA Container Toolkit;
- private locally cloned repositories;
- enterprise credentials;
- physical devices;
- browser/session state;
- language/runtime versions unavailable elsewhere.

Responsibilities:
- execute the specified experiment on the specified state;
- avoid expanding scope without recording it;
- capture commands, versions, logs, test counts, skipped tests, and artifacts needed for reproduction;
- never convert an environment-specific result into a universal claim without justification;
- obey read-only boundaries even if local credentials permit writes.

## Verifier

Use to independently establish whether a reported claim is true.

Responsibilities:
- start from the reported immutable state;
- reproduce the evidence using an independent path where practical;
- check the acceptance criterion, not just whether a command exits zero;
- distinguish "not reproduced" from "disproved";
- identify environmental differences.

A Verifier may be the same agent as a previous Reviewer but should not rely on its earlier conclusion.

## Integrator

Use when multiple layers, agents, or conflicting findings need reconciliation.

Responsibilities:
- determine normative ownership;
- decide where fixes belong;
- preserve stack/dependency order;
- reconcile conflicting agent results using evidence;
- update readiness/progress state;
- keep external blockers separate from repo-side defects;
- ensure durable documentation reflects the actual current state.

## Role switching

Roles can switch between passes:

- Agent A builds; Agent B reviews.
- Agent B runs local GPU evidence as Executor.
- Agent A integrates the findings.
- Agent B re-verifies the integrated state.

This is preferred to assigning permanent status to specific agent products.
