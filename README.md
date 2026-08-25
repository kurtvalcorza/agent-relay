# Agent Relay

**Agent Relay** is an agent-agnostic coordination skill for handing work between independent AI agents or agent sessions using explicit roles, durable state, reproducible evidence, and structured handoffs.

It is designed for workflows where different agents have different strengths or environments—for example, one agent builds, another reviews, another has local GPU/Docker access, and a fourth integrates the result.

> **Core idea:** agents do not need shared memory or a direct communication channel if they can coordinate through durable artifacts and verifiable evidence.

## Why Agent Relay?

Multi-agent workflows often fail for predictable reasons:

- a handoff assumes the next agent remembers prior context;
- a reviewer trusts a builder's summary instead of reproducing the result;
- local-only tests are reported as "probably fine" rather than executed;
- mutation boundaries are lost between sessions;
- agents endlessly reply to one another without converging;
- a green local test is mistaken for release readiness;
- stale branches, mutable tags, or prose summaries become the source of truth.

Agent Relay provides a lightweight protocol for avoiding those failure modes.

## The five roles

Agent Relay uses five reusable roles. They describe responsibilities, not products or identities.

| Role | Responsibility |
| --- | --- |
| **Builder** | Implements the change or produces the primary artifact. |
| **Reviewer** | Adversarially inspects the work and reports concrete findings. |
| **Executor** | Runs tasks requiring a specific local environment, tool, credential, hardware, or network. |
| **Verifier** | Reproduces claims and converts assertions into executable or inspectable evidence. |
| **Integrator** | Reconciles findings, places fixes in the correct ownership layer, and decides readiness. |

The same agent can hold different roles at different stages. When practical, the builder should not be the sole verifier of its own work.

## How it works

A typical relay looks like this:

```text
Builder
  ↓
Durable artifact / repository / document
  ↓
Reviewer
  ↓
Findings + evidence
  ↓
Executor or Verifier
  ↓
Reproducible results
  ↓
Integrator
  ↓
Fixed / Disproved / Deferred / Blocked
```

The shared substrate can be Git, GitHub, a document store, experiment tracker, dataset, issue system, database, or any other durable state that multiple agents can inspect.

## Core rules

1. **Durable state beats conversational memory.**
2. **Evidence beats assertions.**
3. **Explicit mutation boundaries survive every handoff.**
4. **Prefer immutable references** such as commit SHAs, content digests, exact artifact IDs, or versioned documents.
5. **Do not relay private chain-of-thought.** Relay decisions, evidence, findings, commands, constraints, and unresolved questions.
6. **Do not claim unexecuted verification.** Hand it to an Executor instead.
7. **Every finding must converge** to `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.
8. **Fix the owning layer**, then propagate downstream.
9. **Verify before resolving** a review thread, gate, or blocker.
10. **Implementation completeness and release readiness are separate states.**

## Quick start

### 1. Assign a role

```text
You are the Reviewer for this pass.
Inspect the current repository head, reproduce existing claims where possible,
and report concrete findings with severity and evidence.
```

### 2. Identify the durable substrate

```text
Repository: example/project
PR: #42
Reviewed head: 3f4c1a2...
```

### 3. State mutation boundaries explicitly

```text
Allowed to mutate:
- example/project

Strictly read-only:
- upstream/model-worker
- production/backend
```

Read-only means no commits, comments, issues, PRs, labels, branches, file edits, or other mutations unless the user explicitly revokes that constraint.

### 4. Hand off executable work precisely

Instead of:

```text
Please test this on Linux.
```

send:

```text
Role: Executor
Environment: Ubuntu 24.04 / Python 3.10 / NVIDIA Docker
Source revision: 3f4c1a2...
Mission: execute the full test suite and symlink-containment tests
Acceptance criteria:
- zero unexpected failures
- symlink tests actually execute rather than skip
Evidence to return:
- uname / Python version
- exact commands
- pytest counts
- skipped tests
- relevant logs
Do not mutate the upstream repositories.
```

The included `assets/HANDOFF.md` template formalizes this packet.

## Example: software engineering relay

```text
Agent A — Builder
  Implements the feature and regression tests.

Agent B — Reviewer
  Tries to break the implementation and leaves source-linked findings.

Agent C — Executor
  Runs WSL, Docker, GPU, or private-local tests unavailable to A/B.

Agent A — Integrator
  Reproduces the findings, fixes the earliest owning layer, and restacks.

Agent B — Verifier
  Re-runs the discriminating tests and closes only verified findings.
```

GitHub can act as the shared coordination substrate, but GitHub is not required by the protocol.

## Example: research relay

Agent Relay is not limited to coding.

```text
Builder     → drafts the literature synthesis
Reviewer    → challenges unsupported claims
Executor    → queries a database or local corpus unavailable to the others
Verifier    → checks citations and reproduces calculations
Integrator  → reconciles conflicts and publishes the final synthesis
```

The same evidence and handoff rules apply.

## Finding lifecycle

| State | Meaning |
| --- | --- |
| `FIXED` | Reproduced, corrected, and relevant verification now passes. |
| `DISPROVED` | The suspected defect was tested or inspected and is not present. |
| `DEFERRED` | Valid work intentionally postponed with reason/owner/trigger recorded. |
| `BLOCKED` | Required permission, environment, dependency, evidence, or external state is unavailable. |

This prevents endless agent-to-agent review loops.

## Installation

Agent Relay follows the Agent Skills directory pattern:

```text
agent-relay/
├── SKILL.md
├── README.md
├── assets/
├── references/
└── scripts/
```

Install or load the **entire `agent-relay/` directory** in any environment that supports Agent Skills-style skill bundles.

If a client does not provide a dedicated skill installer, `SKILL.md` can still be loaded as the governing instruction file and its referenced resources made available alongside it.

Two packaged forms may be produced from this source tree:

- `agent-relay.zip` — standard portable archive of the skill directory;
- `agent-relay.skill` — the same ZIP-compatible bundle using a convenient skill extension for clients that accept it.

Exact installation paths and UI vary by agent/client.

## What's included

```text
agent-relay/
├── SKILL.md
│   Core activation metadata and protocol.
│
├── README.md
│   Human-facing overview and quick start.
│
├── references/
│   ├── roles.md
│   ├── evidence-protocol.md
│   ├── local-execution.md
│   └── repository-coordination.md
│
├── assets/
│   ├── HANDOFF.md
│   └── AGENT-PASS.md
│
└── scripts/
    └── validate_handoff.py
```

## Agent pass records

For consequential work, Agent Relay recommends leaving a compact durable record:

```text
Agent pass: runtime-adversarial-review
Role: reviewer
Reviewed snapshot: 3f4c1a2...
Findings: 4
Fixed: 0
Disproved: 1
Deferred: 0
Blocked: 0
Executable evidence: Ubuntu 24.04 / Python 3.12 / 154 passed
Unverified: Python 3.10, CUDA path
Next recommended role/pass: Builder — repair findings F-002..F-004
```

The record is an index to the evidence—not the evidence itself.

## Progress reporting

Agent Relay distinguishes at least two progress dimensions:

- **implementation progress** — work that can be completed inside the shared artifact or repository;
- **release/evidence progress** — external execution, CI, production qualification, governance, hardware, independent verification, or other gates.

This avoids statements such as "100% complete" when implementation is finished but required evidence is still missing.

## What Agent Relay is not

Agent Relay is not:

- an autonomous swarm framework;
- a multi-agent runtime;
- a hidden agent-to-agent messaging channel;
- a replacement for tests or source control;
- a way to transfer private chain-of-thought;
- a GitHub-specific workflow;
- a reason to trust one model's conclusions over another's evidence.

It is a **coordination protocol for independent agents operating over shared durable state**.

## Design goals

Agent Relay aims to remain:

- **agent-agnostic**
- **tool-agnostic**
- **role-based**
- **evidence-first**
- **portable**
- **fail-closed**
- **human-governed**

## Version

Current skill version: **0.1.0**  
Protocol identifier: **`agent-relay-v1`**

## License

No license is bundled yet. Add one before distributing Agent Relay as an open-source package.
