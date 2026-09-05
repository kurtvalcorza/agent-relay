# Provenance

This document records the origin and authorship context of Agent Relay at a level appropriate for a public repository.

## Origin

Agent Relay originated from a practical workflow for coordinating independent AI agents that did not share a direct communication channel or common conversational memory.

The recurring pattern was:

1. one agent acted as the primary builder or integrator;
2. another acted as an adversarial reviewer;
3. work requiring a specific local environment, hardware, credential, or tool was handed to an executor;
4. results were returned as reproducible evidence;
5. durable repository state, tests, review threads, and explicit handoffs acted as the shared coordination substrate.

The protocol was generalized from that workflow so it would not depend on a particular model vendor, repository host, programming language, or domain.

## Initial public version

The initial public skill was assembled on 2026-08-25.

Human maintainer:

- Kurt Valcorza

AI-assisted development and review included:

- OpenAI ChatGPT — primary drafting, protocol synthesis, packaging, public-release preparation, and automatic role-routing design;
- Anthropic Claude — independent review and local-execution patterns that materially informed the protocol's evidence and handoff model.

The maintainer selected the project name, directed scope and design decisions, approved the public contents, and chose the MIT License.

## v0.2.0 — automatic role routing

The v0.2.0 revision added automatic role routing so an agent can infer whether the current work calls for Builder, Reviewer, Executor, Verifier, or Integrator behavior from task intent and durable workflow state.

The feature was deliberately constrained by three provenance and governance principles:

1. explicit human role instructions take precedence;
2. role inference never creates permissions or weakens mutation boundaries;
3. consequential readiness, sign-off, and closure claims require Verifier behavior unless adequate current evidence already exists.

A small deterministic reference router and tests were added as examples. The normative behavior remains the written protocol in `SKILL.md` and `references/role-routing.md` rather than any one heuristic implementation.

## Review protocol development

The review-lens protocol was designed through an explicit multi-agent review process.

The initial proposal introduced review profiles for standard implementation review, design/adversarial review, security, reliability, test-gap analysis, specification conformance, regression analysis, and readiness assessment while preserving the existing five-role model.

An independent Claude Code design-review pass identified important corrections before implementation, including:

- preserving adversarial posture as a property of all Reviewer work and naming the architecture/approach lens `design`;
- keeping final readiness decisions with the Integrator;
- distinguishing review intent from subject-matter nouns in router heuristics;
- extending rather than replacing the existing finding schema;
- keeping substrate-neutral review semantics separate from Git/PR mechanics;
- carrying review metadata through handoffs, pass records, and validation.

These findings materially shaped the implemented protocol.

## Review recording authority

Agent Relay v0.3.1 resolved an ambiguity surfaced while reviewing an RFC with the protocol itself: the specification said where review findings belong but never said whether a Reviewer was permitted to put them there, so a review could stall in conversation while rule 1 declared durable state the source of truth.

The maintainer decided that a request to review a named durable artifact carries authority to record that review on that artifact's own review channel. The authority is deliberately narrow — it comes from the request naming the artifact rather than from the inferred role, it covers recording alone, and an explicit read-only boundary still overrides it.

## v0.4.0 — decision, evidence, and runtime semantics

The v0.4.0 revision added semantics around the existing five roles rather than adding roles: decision authority as an axis separate from mutation permission, immutable mission anchors, claim maturity (`ASSERTED`, `INSPECTED`, `EXECUTED`, `VERIFIED`), assurance profiles, falsifiable verification contracts, bounded iterative review, and a separately versioned runtime-adapter contract that fails closed on safety-bearing fields.

Prior art consulted for the runtime and bounded-review semantics is recorded with source pins in `references/prior-art.md`. Where a public source exposes no immutable revision, that limitation is recorded rather than concealed.

Two review passes shaped the released form:

1. an independent review of the executable surface found that the finding-snapshot check was satisfied by the handoff template's own table header, so a table with empty snapshot cells validated clean. The check was replaced with structural table parsing, and the v0.4 vocabularies were extended to handoff sections, which had been unvalidated.

2. a spec-coherence review found that the pass execution status reused `EXECUTED`, already a claim-maturity state, in records that carry both fields. The pass axis was renamed to `RAN | FAILED | SKIPPED`. The same pass consolidated four partial statements of the finding lifecycle into one owned by `references/evidence-protocol.md`, which now also disambiguates `BLOCKED` as both a finding state and a cycle termination reason.

Both passes are recorded on the pull requests that introduced them; neither agent's summary is treated as evidence independent of the diffs and tests it cites.

## v0.5.0 — orchestrated delegation

The v0.5.0 revision has a narrower origin than v0.4.0: it comes from operating the protocol as an orchestrator through a multi-round external-review loop on a separate repository, where an agent dispatched subordinate agent passes rather than handing work to a peer. Peer relay was already specified. Dispatch was not, and three defects appeared in practice that the existing rules did not prevent.

First, a scope extension that no owner had granted was relayed to a subordinate pass as an owner clearance. The orchestrator had decided the extension was warranted — that was within its authority — but the subordinate pass received the decision as though it came from the owner, and could not tell the difference from inside its own window. The subordinate pass's own review caught it. Rule 11 already said attribution is provenance rather than authority; the mirror case, that a relayed *statement about* authority is not authority either, was unstated. It is now rule 16, and it is enforced rather than merely asserted: the delegation brief carries an authority provenance source from a closed vocabulary, and `owner-grant` and `delegated-grant` fail validation unless the record names the grantor, quotes the scope verbatim, and cites when it was granted. A grant that cannot be quoted is recorded as `orchestrator-judgment`, which makes an ungranted extension impossible to record silently.

Second, claims computed over the whole substrate went stale at intermediate states. Counts recorded in a readme and a pull-request description were true at the branch tip and false at several commits behind it, because each lane changed part of the whole. Such claims are now declared centrally owned by the single writer, and briefs ask subordinate passes for the inputs instead.

Third, a repair's discriminating control was reported by the same pass that authored the repair, and was initially adopted on that report. A related instance of the same defect class survived a repair round and was found by the next external review round, which is the empirical reason the revision requires the adopting agent to re-derive the control itself rather than accept a report of it, and requires declared deviations to be read before any number from a subordinate pass is reused. Adopting a result makes its claim the adopter's own; that is rule 17.

The executable surface is a fourth validated record kind in `scripts/validate_handoff.py` — the delegation brief — with structural tests in `tests/test_protocol_v05.py`. The same revision adds a version-consistency test, since the skill version is declared in both `SKILL.md` metadata and `README.md` and had no check binding them together.

The limitation is recorded rather than concealed: these three defects were observed on one repository, in one orchestration pattern, with a single orchestrating agent. The requirements they motivated are structural and expected to generalize, but they have not been validated across multiple substrates or runtimes. Review of this revision is recorded on the pull request that introduced it; neither the drafting agent's summary nor a reviewer's is treated as evidence independent of the diffs and tests it cites.

## Agent attribution convention

Agent Relay supports compact provenance footers for substantive durable agent-generated records.

A minimal footer may be:

```text
Generated by Claude Code
```

or:

```text
Generated by OpenAI ChatGPT
```

For consequential Agent Relay passes, richer attribution is preferred when available:

```text
Generated by: <agent/client>
Model: <model if reliably known>
Agent Relay role: <role>
Review lenses: <lens list or N/A>
Source snapshot: <immutable-id>
```

The agent/client identity is normally more stable than model identity, because clients may route dynamically or hide the exact model. Model identification is therefore optional unless it can be established reliably.

### Attribution is not sign-off

Agent attribution is provenance only. It is **not**:

- proof that the named agent actually generated the record;
- cryptographic authentication;
- human authorship authority;
- approval;
- merge or release sign-off;
- independent verification;
- a reason to increase the evidentiary weight of the claim.

A footer such as `Generated by Claude Code` is self-reported metadata unless independently authenticated. Stronger provenance may use repository actors, signed commits/tags, immutable commit IDs, artifact digests, workflow identities, or other independently inspectable mechanisms.

This distinction is intentional because Agent Relay uses **sign-off** as a consequential workflow concept that requires verification. Provenance attribution must not accidentally grant that meaning.

## Source-of-truth principle

This repository is the source of truth for the public Agent Relay specification and templates.

Where historical discussions, agent summaries, generated packages, or other artifacts disagree with the committed repository, committed source at an identified revision should take precedence.

## Provenance expectations for downstream use

Agent Relay encourages downstream users to record, when useful:

- the generating agent/client;
- the model when reliably known;
- the agent or system role;
- selected review lenses when applicable;
- whether the role/lens was explicit or inferred;
- the source revision or artifact identifier;
- the execution environment;
- commands or procedures used;
- resulting evidence;
- unresolved limitations or blockers;
- material AI assistance.

Provenance should capture decisions and evidence, not private chain-of-thought or sensitive information.

## Change history

Git history provides the authoritative change history after public release. Tagged releases may add stronger release-level provenance such as source commit IDs, generated-package digests, validation results, and environment metadata.
