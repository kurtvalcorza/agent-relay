# Agent Relay

**Agent Relay** is an agent-agnostic coordination skill for handing work between independent AI agents or agent sessions using automatic role routing, durable state, reproducible evidence, structured handoffs, review lenses, bounded decision authority, runtime-adapter contracts, and provenance-aware pass records.

It is designed for workflows where different agents have different strengths or environments—for example, one agent builds, another reviews, another has local GPU/Docker access, and a fourth integrates the result.

> **Core idea:** agents do not need shared memory or a direct communication channel if they can coordinate through durable artifacts and verifiable evidence.

## Why Agent Relay?

Multi-agent workflows often fail for predictable reasons:

- a handoff assumes the next agent remembers prior context;
- a reviewer trusts a builder's summary instead of reproducing the result;
- local-only tests are reported as "probably fine" rather than executed;
- mutation boundaries are lost between sessions;
- execution autonomy silently turns into planning authority;
- agents endlessly reply to one another without converging;
- a green local test is mistaken for release readiness;
- stale branches, mutable tags, or prose summaries become the source of truth;
- review findings are not portable across agents;
- runtime adapters silently ignore safety-bearing fields;
- a model/provider name is mistaken for evidence authority.

Agent Relay provides a lightweight protocol for avoiding those failure modes.

## The five roles

| Role | Responsibility |
| --- | --- |
| **Builder** | Implements a change or produces the primary artifact. |
| **Reviewer** | Adversarially inspects work and reports concrete findings. |
| **Executor** | Runs tasks requiring a specific local environment, tool, credential, hardware, or network. |
| **Verifier** | Reproduces claims and turns assertions into executable or inspectable evidence. |
| **Integrator** | Reconciles findings, ownership layers, branches, evidence, authority, and readiness decisions. |

Roles describe responsibilities, not products or identities. The same agent can hold different roles at different stages.

## Review lenses

Starting with **v0.3.0**, Reviewer work can carry explicit review lenses without expanding the five-role model.

Every Reviewer pass remains adversarial in posture. A lens changes the **target of scrutiny**, not the level of skepticism.

| Lens | Core question |
| --- | --- |
| `standard` | Is the implementation correct? |
| `design` | Is the architecture/approach itself sound? |
| `security` | What trust-boundary, privilege, input, secret, or abuse failures exist? |
| `reliability` | What happens under retry, interruption, concurrency, partial failure, or recovery? |
| `test-gap` | What important behavior is not actually exercised? |
| `spec-conformance` | Does behavior match the authoritative specification/contract? |
| `regression` | What previously valid behavior may have changed? |
| `readiness` | What evidence is still missing before a consequential readiness decision? |

The naming is deliberate: **`design`**, not `adversarial`, is the architecture/approach lens because all Reviewer work is already adversarial.

Lens inference is conservative. `Review the security module` is a standard review of security-related code; `Security review this PR` selects `security`.

A readiness review produces an evidence-gap assessment and normally routes:

```text
Reviewer[readiness] -> Verifier -> Integrator
```

Final readiness remains an Integrator decision.

A completed review belongs in durable state, not only in conversation, so a request to review a named artifact carries authority to record the review on that artifact. See **Review recording authority** in [`SKILL.md`](SKILL.md).

See [`references/review-lenses.md`](references/review-lenses.md).

## v0.4: authority, evidence maturity, and bounded runtime coordination

Agent Relay **v0.4.0** adds semantics around the five existing roles rather than adding more roles.

- **Mission modes** describe the kind of work (`build`, `fix`, `test`, `orchestrate`, `operate`, `understand`, `plan`, `analyze`, `communicate`) without granting permission or authority.
- **Decision authority** separates who may decide mission, scope, architecture, acceptance, implementation, execution, evidence, and readiness from who can technically mutate a substrate.
- **Mission anchors** bind work to an immutable planning revision or content digest so scope/acceptance/authority changes cannot drift silently.
- **Claim maturity** makes `ASSERTED -> INSPECTED -> EXECUTED -> VERIFIED` explicit without replacing the finding lifecycle.
- **Assurance profiles** (`exploratory`, `standard`, `consequential`) determine how demanding a verification contract must be before a claim can become `VERIFIED`.
- **Verification contracts** bind consequential requirements to falsifiable procedures/oracles and evidence.
- **Bounded iterative review** records planned versus executed passes, finding continuity, explicit budgets, and termination without treating `NO_NEW_FINDINGS` as readiness.
- **Runtime adapter contracts** are versioned separately from `agent-relay-v1` and fail closed when an adapter cannot honor safety-bearing fields.
- **Cold-start resumability** makes a substantive handoff reconstructible from durable state without requiring shared conversation history.
- **Parallel mutation safety** requires disjoint mutation surfaces or declared safe multi-writer semantics; otherwise execution serializes or refuses.
- **Stagnation** is a routing signal for changing decision function/lens/environment, not a third lifecycle state.

The design principle is simple:

> **Execution autonomy does not imply planning authority, and runtime completion does not imply verified success.**

See [`references/decision-authority.md`](references/decision-authority.md), [`references/evidence-protocol.md`](references/evidence-protocol.md), [`references/mission-modes.md`](references/mission-modes.md), [`references/iterative-review.md`](references/iterative-review.md), [`references/runtime-adapters.md`](references/runtime-adapters.md), and [`references/stagnation-escalation.md`](references/stagnation-escalation.md).

## Automatic role routing

Starting with **v0.2.0**, Agent Relay can infer the role needed from the task and live workflow state. v0.3.0 adds conservative Reviewer-lens inference.

Examples:

| Situation | Inferred route |
| --- | --- |
| `Implement this change` | `Builder` |
| `Review this PR` | `Reviewer[standard]` |
| `Adversarially review the design` | `Reviewer[design]` |
| `Review this PR for test gaps` | `Reviewer[test-gap]` |
| `Write regression tests for this finding` | `Builder` |
| `Review and sign off if clean` | `Reviewer[standard] -> Verifier` |
| `Review this and fix what you find` | `Reviewer -> Integrator -> Builder -> Verifier` |
| `Assess merge readiness for this PR` | `Reviewer[readiness] -> Verifier -> Integrator` |
| `Is this ready to merge?` | `Verifier -> Integrator` |
| `Fix the reported finding` | `Integrator -> Builder -> Verifier` when an unresolved finding exists |
| `Run this under WSL/CUDA locally` | `Executor` or handoff to an Executor |
| `Confirm that this fix actually works` | `Verifier` |
| `Reconcile these two reviews` | `Integrator` |
| `Continue` | inferred from the current durable state |

Routing precedence is conservative:

1. explicit user role assignment;
2. mutation, safety, decision-authority, and access boundaries;
3. environment feasibility;
4. live workflow state;
5. task intent;
6. conservative default.

Role/lens/mode routing **never grants permissions or decision authority**. Inferring `Builder` does not create write access; inferring `Integrator` does not authorize merge; inferring `Reviewer` does not authorize changing the reviewed artifact; inferring `Executor` does not grant credentials or private-data access; selecting `security` does not grant scanner execution.

The one exception is granted by the request, not the role: asking for a review of a **named** artifact carries authority to record that review on that artifact's own review channel — a PR or issue comment, a review thread, a document comment. It carries nothing else, and an explicit read-only boundary still overrides it.

Before sign-off, approval, declaring a finding fixed, resolving a thread because it is said to be fixed, declaring a gate PASS, recommending merge based on correctness, or declaring release/readiness/stability, Agent Relay automatically requires **Verifier behavior** unless adequate current evidence already exists.

See [`references/role-routing.md`](references/role-routing.md). A small non-normative reference router is available at [`scripts/infer_role.py`](scripts/infer_role.py).

## How it works

A typical relay looks like this:

```text
Mission anchor + authority + verification expectations
  ↓
Builder
  ↓
Durable artifact / repository / document
  ↓
Reviewer + optional lens
  ↓
Structured findings + evidence
  ↓
Executor or Verifier
  ↓
Reproducible results
  ↓
Integrator
  ↓
Fixed / Disproved / Deferred / Blocked + readiness decision
```

The shared substrate can be Git, GitHub, a document store, experiment tracker, dataset, issue system, database, or any other durable state that multiple agents can inspect.

## Core rules

1. **Durable state beats conversational memory.**
2. **Evidence beats assertions.**
3. **Explicit mutation boundaries and decision-authority limits survive every role/lens/mode change and handoff.**
4. **Prefer immutable references** such as commit SHAs, content digests, exact artifact IDs, or versioned documents.
5. **Do not relay private chain-of-thought.** Relay decisions, evidence, findings, commands, constraints, and unresolved questions.
6. **Do not claim unexecuted verification.** Route it to an Executor instead.
7. **Every finding must converge** to `FIXED`, `DISPROVED`, `DEFERRED`, or `BLOCKED`.
8. **Fix the owning layer**, then propagate downstream.
9. **Verify before resolving** a review thread, gate, blocker, or consequential readiness claim.
10. **Implementation completeness and release readiness are separate states.**
11. **Attribution is provenance, not authority.** A named model/client does not make a claim stronger evidence.
12. **Execution autonomy is not planning authority.**
13. **Consequential requirements should have falsifiable verification contracts when practicable.**
14. **Runtime adapters fail closed on safety-bearing fields.**
15. **Non-execution never reads as success.**

## Quick start

Install the skill, point the agent at the durable task state, and work normally. Explicit roles/lenses are optional.

```text
Review this PR and fix anything that is genuinely blocking.
```

Agent Relay should infer something like:

```text
Reviewer[standard] -> Integrator -> Builder -> Verifier
```

For a design-focused pass:

```text
Adversarially review the design and challenge its assumptions.
```

Agent Relay should use:

```text
Reviewer[design]
```

If the decisive evidence requires an unavailable environment:

```text
Run the CUDA path locally and tell me whether the release gate can pass.
```

Agent Relay should route the unavailable portion to an Executor with a structured packet containing the immutable source revision, mission anchor where relevant, required environment, mutation boundaries, exact experiment/verification contract, acceptance criteria, and evidence to return.

Use [`assets/HANDOFF.md`](assets/HANDOFF.md) for substantive handoffs and [`assets/REVIEW.md`](assets/REVIEW.md) for substantive review passes.

## Structured review findings

Review findings extend the existing evidence protocol rather than introducing a parallel schema.

A significant review finding should preserve, when applicable:

- ID;
- lens/lenses;
- severity and optional confidence;
- immutable reviewed/observation state;
- affected location/surface;
- concrete failure condition;
- expected behavior;
- observed behavior;
- violated requirement/invariant;
- owning layer;
- evidence;
- recommended action;
- lifecycle state.

Expected versus observed behavior is retained because it makes a finding falsifiable and easier for another agent to verify or disprove.

See [`references/evidence-protocol.md`](references/evidence-protocol.md).

## Finding lifecycle

| State | Meaning |
| --- | --- |
| `FIXED` | Reproduced, corrected, and relevant verification now passes. |
| `DISPROVED` | The suspected defect was tested or inspected and is not present. |
| `DEFERRED` | Valid work intentionally postponed with reason/owner/trigger recorded. |
| `BLOCKED` | Required permission, environment, dependency, evidence, or external state is unavailable. |

Finding lifecycle is separate from claim maturity (`ASSERTED/INSPECTED/EXECUTED/VERIFIED`), pass execution status, and bounded-cycle termination.

## Provenance footer

For substantive durable agent-generated records, Agent Relay recommends compact attribution such as:

```text
Generated by: Claude Code
Agent Relay role: Reviewer
Review lenses: design
Source snapshot: 4271a5a...
```

or:

```text
Generated by: OpenAI ChatGPT
Agent Relay role: Integrator
Source snapshot: <immutable-id>
```

`Model:` may be added when the exact model is reliably known.

This is **provenance, not sign-off**. Attribution does not prove who generated the content, authenticate it, approve it, or independently verify it. Agent Relay deliberately reserves sign-off for consequential workflow decisions that require evidence/verification.

See [`PROVENANCE.md`](PROVENANCE.md).

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
│   Public origin, agent-attribution convention, and provenance record.
├── LICENSE
│   MIT License.
├── references/
│   ├── roles.md
│   ├── role-routing.md
│   ├── review-lenses.md
│   ├── decision-authority.md
│   ├── evidence-protocol.md
│   ├── mission-modes.md
│   ├── iterative-review.md
│   ├── runtime-adapters.md
│   ├── stagnation-escalation.md
│   ├── local-execution.md
│   └── repository-coordination.md
├── assets/
│   ├── HANDOFF.md
│   ├── REVIEW.md
│   └── AGENT-PASS.md
├── scripts/
│   ├── infer_role.py
│   └── validate_handoff.py
└── tests/
    ├── __init__.py
    ├── test_infer_role.py
    ├── test_validate_handoff.py
    └── test_protocol_v04.py
```

## Reference role router

The router is intentionally small and conservative. It demonstrates the protocol; it is not the normative definition of role/lens routing.

```bash
python scripts/infer_role.py "Adversarially review the design and sign off if clean"
```

Example output:

```json
{
  "inferred": "reviewer",
  "confidence": "high",
  "reason": "Review request includes consequential sign-off",
  "sequence": ["reviewer", "verifier"],
  "handoff_required": false,
  "review_lenses": ["design"]
}
```

Non-Reviewer routes preserve the historical JSON shape by omitting `review_lenses`.

An explicit lens can be supplied to the reference router:

```bash
python scripts/infer_role.py "Review this PR" --review-lens security
```

Run all tests with:

```bash
python -m unittest discover -s tests -t . -v
```

CI also runs `python -m pytest` on Python 3.11, 3.12, and 3.13.

## Agent pass records

For consequential work, Agent Relay recommends leaving a compact durable record. The v0.3 minimum remains valid; v0.4 permits additional mission/authority/cycle metadata:

```text
Agent pass: runtime-design-review
Role: reviewer
Review lenses: design
Role source: inferred
Role sequence: reviewer -> integrator -> builder
Reviewed/modified snapshot: 3f4c1a2
Findings: 4
Fixed: 0
Disproved: 1
Deferred: 0
Blocked: 0
Executable/inspectable evidence: Ubuntu 24.04 / Python 3.12 / 154 passed
Verification checkpoint: reproduce F-002 on Python 3.10
Unverified: Python 3.10, CUDA path
Next recommended role/pass: Builder — repair findings F-002..F-004
Provenance:
- Generated by: Claude Code
- Source snapshot: 3f4c1a2
```

The record is an index to evidence, not proof itself. See [`assets/AGENT-PASS.md`](assets/AGENT-PASS.md) for the v0.4 fields.

## Progress reporting

Agent Relay distinguishes at least two dimensions:

- **implementation progress** — work that can be completed inside the shared artifact or repository;
- **release/evidence progress** — external execution, CI, production qualification, governance, hardware, independent verification, or other gates.

This avoids calling something "100% complete" when implementation is finished but required evidence is still missing.

## AI use and provenance

Agent Relay was developed with substantial AI assistance under human direction and review. Development and review involved AI assistants from multiple providers, including OpenAI ChatGPT and Anthropic Claude, while the maintainer retained responsibility for scope, design decisions, public contents, and release decisions.

The review protocol and v0.4 coordination semantics were refined through independent adversarial review before implementation.

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
- a permission- or authority-escalation mechanism;
- a provider-specific review/runtime framework;
- a reason to trust one model's conclusions over another's evidence.

It is a **coordination protocol for independent agents operating over shared durable state**.

## Design goals

Agent Relay aims to remain **agent-agnostic, tool-agnostic, role-based, evidence-first, portable, fail-closed, provenance-aware, and human-governed**.

## Version

Current skill version: **0.4.0**  
Protocol identifier: **`agent-relay-v1`**

## License

Agent Relay is licensed under the [MIT License](LICENSE).