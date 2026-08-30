# Prior art references

Agent Relay adapts protocol semantics from external systems without making those systems dependencies or normative authority.

Prefer immutable source identities when the source substrate provides them. When a public source does not expose an immutable revision, record that limitation explicitly and do not make correctness depend on an unverifiable historical reading.

## Claudex

Repository: `promptadvisers/claudex`

Pinned public repository state consulted for the v0.4 implementation:

```text
1f7161d4e806861f901b4c67ceb3ca02fe27ac1a
```

This pin is a locator for the public repository state, not evidence that every behavior described by Agent Relay was exercised independently. Agent Relay adapts bounded-review, operational-loop, status/cancel, and convergence ideas at the protocol level rather than copying provider-specific hooks or commands.

## OpenAI codex-plugin-cc

Repository: `openai/codex-plugin-cc`

Pinned public repository state consulted/referenced for provider-specific review-backend prior art:

```text
db52e28f4d9ded852ab3942cea316258ae4ef346
```

Agent Relay does not require this plugin and does not treat a provider-specific review action as verification or readiness authority.

## Google Antigravity Teamwork

Public documentation locator:

```text
https://antigravity.google/docs/teamwork/
```

Reviewed on 2026-08-30.

The documentation is a mutable web source and did not provide a substrate-native immutable revision to Agent Relay during the review. This limitation is intentional in the evidence record:

- the source is cited as design input only;
- Agent Relay does not depend on the page for runtime behavior;
- the protocol does not copy Antigravity-specific persona names or integrity modes as normative semantics;
- claims about the source remain qualified as observations of the page accessed on that date;
- if an archived/versioned upstream source becomes available, replace this locator with that immutable reference rather than implying the mutable URL was pinned.

The adapted concepts are requirement-level verification planning, bounded authority versus execution autonomy, fresh-context handoff/cold-start resumability, and safe mutation-surface partitioning. Their normative meaning is defined entirely by the Agent Relay repository.

## Evidence rule

External prior art can justify a design direction but cannot override Agent Relay's own evidence hierarchy, mutation boundaries, decision authority, finding lifecycle, or verification requirements.
