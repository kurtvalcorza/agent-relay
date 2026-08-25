# Agent Relay

**Agent Relay** is an agent-agnostic coordination skill for handing work between independent AI agents or agent sessions using automatic role routing, durable state, reproducible evidence, and structured handoffs.

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

| Role | Responsibility |
| --- | --- |
| **Builder** | Implements a change or produces the primary artifact. |
| **Reviewer** | Adversarially inspects work and reports concrete findings. |
| **Executor** | Runs tasks requiring a specific local environment, tool, credential, hardware, or network. |
| **Verifier** | Reproduces claims and turns assertions into executable or inspectable evidence. |
| **Integrator** | Reconciles findings, ownership layers, branches, evidence, and readiness decisions. |

Roles describe responsibilities, not products or identities. The same agent can hold different roles at different stages.

## Automatic role routing

Starting with **v0.2.0**, Agent Relay can infer the role needed from the task and live workflow state. You should not have to assign a role manually for every turn.

Examples:

| Situation | Inferred route |
| --- | --- |
| `Implement this change` | `Builder` |
| `Review this PR` | `Reviewer` |
| `Review and sign off if clean` | `Reviewer -> Verifier` |
| `Review this and fix what you find` | `Reviewer -> Integrator -> Builder -> Verifier` |
| `Fix the reported finding` | `Integrator -> Builder -> Verifier` when an unresolved finding exists |
| `Run this under WSL/CUDA locally` | `Executor` or handoff to an Executor |
| `Confirm that this fix actually works` | `Verifier` |
| `Reconcile these two reviews` | `Integrator` |
| `Continue` | inferred from the current durable state |

Routing precedence is conservative:

1. explicit user role assignment;
2. mutation and safety boundaries;
3. environment feasibility;
4. live workflow state;
5. task intent;
6. conservative default.

Role routing **never grants permissions**. Inferring `Builder` does not create write access; inferring `Integrator` does not authorize merge; inferring `Reviewer` does not authorize public comments; inferring `Executor` does not grant credentials or private-data access.

Before sign-off, approval, declaring a finding fixed, resolving a thread because it is said to be fixed, declaring a gate PASS, recommending merge based on correctness, or declaring release/readiness/stability, Agent Relay automatically requires **Verifier behavior** unless adequate current evidence already exists.

See [`references/role-routing.md`](references/role-routing.md). A small non-normative reference router is available at [`scripts/infer_role.py`](scripts/infer_role.py).

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
3. **Explicit mutation boundaries survive every role change and handoff.**
4. **Prefer immutable references** such as commit SHAs, content digests, exact artifact IDs, or versioned documents.
5. **Do not relay private chain-of-thought.** Relay decisions, evidence, findings, commands, constraints, and unresolved questions.
6. **Do not claim unexecuted verification.** Route it to an Executor instead.
7. **Every finding must converge** to `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.
8. **Fix the owning layer**, then propagate downstream.
9. **Verify before resolving** a review thread, gate, blocker, or consequential readiness claim.
10. **Implementation completeness and release readiness are separate states.**

## Quick start

Install the skill, point the agent at the durable task state, and work normally. Explicit roles are optional.

```text
Review this PR and fix anything that is genuinely blocking.
```

Agent Relay should infer something like:

```text
Reviewer -> Integrator -> Builder -> Verifier
```

If the decisive evidence requires an unavailable environment:

```text
Run the CUDA path locally and tell me whether the release gate can pass.
```

Agent Relay should route the unavailable portion to an Executor with a structured packet containing the immutable source revision, required environment, mutation boundaries, exact experiment, acceptance criteria, and evidence to return.

Use [`assets/HANDOFF.md`](assets/HANDOFF.md) for substantive handoffs.

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
├── AI_USE.md
├── PROVENANCE.md
├── LICENSE
├── assets/
├── references/
├── scripts/
└── tests/
```

Install or load the **entire `agent-relay/` directory** in an environment that supports Agent Skills-style bundles.

Two packaged forms may be built from the source tree:

- `agent-relay.zip` — portable archive;
- `agent-relay.skill` — the same ZIP-compatible bundle with a convenient skill extension for clients that accept it.

Exact installation paths and UI vary by agent/client.

## What's included

```text
agent-relay/
├── SKILL.md
│   Core activation metadata and protocol.
├── README.md
│   Human-facing overview and quick start.
├── AI_USE.md
│   AI-assisted development disclosure.
├── PROVENANCE.md
│   Public origin and provenance record.
├── LICENSE
│   MIT License.
├── references/
│   ├── roles.md
│   ├── role-routing.md
│   ├── evidence-protocol.md
│   ├── local-execution.md
│   └── repository-coordination.md
├── assets/
│   ├── HANDOFF.md
│   └── AGENT-PASS.md
├── scripts/
│   ├── infer_role.py
│   └── validate_handoff.py
└── tests/
    └── test_infer_role.py
```

## Reference role router

The router is intentionally small and conservative. It demonstrates the protocol; it is not the normative definition of role routing.

```bash
python scripts/infer_role.py "Review this PR and sign off if clean"
```

Example output:

```json
{
  "inferred": "reviewer",
  "confidence": "high",
  "reason": "Review request includes consequential sign-off",
  "sequence": ["reviewer", "verifier"],
  "handoff_required": false
}
```

Run the router tests with:

```bash
python -m unittest discover -s tests -v
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

The record is an index to evidence, not proof itself.

## Progress reporting

Agent Relay distinguishes at least two dimensions:

- **implementation progress** — work that can be completed inside the shared artifact or repository;
- **release/evidence progress** — external execution, CI, production qualification, governance, hardware, independent verification, or other gates.

This avoids calling something "100% complete" when implementation is finished but required evidence is still missing.

## AI use and provenance

Agent Relay was developed with substantial AI assistance under human direction and review. Development and review involved AI assistants from multiple providers, including OpenAI ChatGPT and Anthropic Claude, while the maintainer retained responsibility for scope, design decisions, public contents, and release decisions.

See [`AI_USE.md`](AI_USE.md) and [`PROVENANCE.md`](PROVENANCE.md).

The project treats material AI assistance as provenance while avoiding disclosure of private chain-of-thought, credentials, sensitive data, or confidential project context.

## What Agent Relay is not

Agent Relay is not:

- an autonomous swarm framework;
- a multi-agent runtime;
- a hidden agent-to-agent messaging channel;
- a replacement for tests or source control;
- a way to transfer private chain-of-thought;
- a GitHub-specific workflow;
- a permission-escalation mechanism;
- a reason to trust one model's conclusions over another's evidence.

It is a **coordination protocol for independent agents operating over shared durable state**.

## Design goals

Agent Relay aims to remain **agent-agnostic, tool-agnostic, role-based, evidence-first, portable, fail-closed, and human-governed**.

## Version

Current skill version: **0.2.0**  
Protocol identifier: **`agent-relay-v1`**

## License

Agent Relay is licensed under the [MIT License](LICENSE).
