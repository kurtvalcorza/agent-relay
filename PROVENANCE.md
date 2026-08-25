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

- OpenAI ChatGPT — primary drafting, protocol synthesis, packaging, and public-release preparation;
- Anthropic Claude — independent review and local-execution patterns that materially informed the protocol's evidence and handoff model.

The maintainer selected the project name, directed scope and design decisions, approved the public contents, and chose the MIT License.

## Source-of-truth principle

This repository is the source of truth for the public Agent Relay specification and templates.

Where historical discussions, agent summaries, or generated artifacts disagree with the committed repository, the committed source at an identified revision should take precedence.

## Provenance expectations for downstream use

Agent Relay encourages downstream users to record, when useful:

- the agent or system role;
- the source revision or artifact identifier;
- the execution environment;
- commands or procedures used;
- resulting evidence;
- unresolved limitations or blockers;
- material AI assistance.

Provenance should capture decisions and evidence, not private chain-of-thought or sensitive information.

## Change history

Git history provides the authoritative change history after public release. Tagged releases may add stronger release-level provenance such as source commit IDs, generated-package digests, validation results, and environment metadata.
