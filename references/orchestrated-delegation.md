# Orchestrated delegation

Peer relay assumes agents hand work sideways: the sender releases the work, and the
receiver becomes the acting agent. Orchestrated delegation is the other shape. One agent
holds mission and integration authority, opens subordinate passes it controls, and remains
the acting agent for the shared substrate throughout.

The protocol's roles, finding lifecycle, evidence maturities, and bounds are unchanged
here. What changes is that authority now travels through an intermediary, and that several
passes can be in flight against one substrate at once. Both create failure modes that peer
handoff does not have.

## Orchestrator

An Orchestrator is an Integrator-authority agent that also plans and dispatches subordinate
passes. It is not a new role in the routing table: infer `Integrator` with mission mode
`orchestrate`.

The Orchestrator holds recording authority for the shared substrate. Subordinate passes
propose; the Orchestrator commits. It also holds the audit obligation in
[Return contract](#return-contract), and it does not inherit sign-off authority it did not
already have — orchestrating a repair does not make its own repair independently verified.

## Delegation brief

A subordinate pass is opened with a delegation brief ([../assets/DELEGATION-BRIEF.md](../assets/DELEGATION-BRIEF.md)),
not a handoff. The two differ in ways that matter mechanically:

- a handoff transfers the acting position; a brief opens a bounded pass under retained authority;
- a handoff's recipient can read the substrate and the prior durable record; a brief's
  recipient starts from a fresh window and sees only what the brief carries;
- a handoff names the next role; a brief names a lane, its deliverable, and the channels the
  subordinate pass must not touch.

A brief MUST carry its authority provenance, its mutation boundary, the deliverable artifact
expected back, and the forbidden recording channels. A brief that conveys only a task
description is underspecified: the subordinate pass has no way to tell retained authority
from granted authority, and no way to tell a proposal from a commit.

## Authority provenance

Rule 11 says attribution is provenance, not authority. Delegation adds the mirror case: a
statement *about* authority, relayed by an agent, is not authority either.

A subordinate pass cannot inspect the conversation its brief was written in. When a brief
asserts that a grant exists, that assertion is unverifiable from inside the pass, and a
subordinate agent that acts on it has no way to record that it did so on trust. The brief
therefore declares where the authority came from, in a closed vocabulary:

| Source | Meaning |
|---|---|
| `owner-grant` | The mission owner granted this scope directly. |
| `delegated-grant` | A grant received from a higher pass, being passed down unchanged. |
| `orchestrator-judgment` | No grant names this scope; the dispatching agent is authorizing it under its own authority. |
| `none` | No authority is conveyed; the pass is read-only or advisory. |

Normative requirements:

1. `owner-grant` and `delegated-grant` MUST name the grantor, quote the granted scope
   verbatim, and cite when or against what state it was granted. A grant that cannot be
   quoted is recorded as `orchestrator-judgment` instead.
2. A dispatching agent MUST NOT paraphrase, widen, or summarize a grant into a scope the
   grantor did not name. Widening is a new authorization, and its source is
   `orchestrator-judgment`.
3. A subordinate pass MUST carry the declared source into its own durable record unchanged,
   and MUST NOT treat `orchestrator-judgment` as owner authorization.
4. `orchestrator-judgment` scope extensions MUST be disclosed in the pass or cycle record
   that reaches the owner, named as extensions no reviewer or owner requested.
5. A subordinate pass that doubts its brief's authority declaration records the doubt as a
   finding and proceeds only within the boundary it can evidence.

This is a fail-closed field in the sense of rule 14: a runtime that cannot carry the
authority source refuses the brief rather than dropping it.

## Mutation surface

Rule on parallel mutation ([runtime-adapters.md](runtime-adapters.md)) requires demonstrably
disjoint surfaces or declared safe multi-writer semantics. Orchestrated delegation satisfies
it most cheaply by giving subordinate passes no mutation surface on the shared substrate at all:

- the subordinate pass works in its own environment and returns a proposal artifact — a
  patch, a diff, a draft record, a result set;
- the Orchestrator applies proposals in a chosen order and is the only writer;
- recording channels — durable records, review threads, issue and PR state, published
  artifacts, tags, releases — stay forbidden to subordinate passes and are listed as such in
  the brief.

Reading the substrate remains allowed unless separately restricted. Where subordinate passes
must write directly, the brief declares the disjoint surfaces per lane and the substrate's
conflict semantics; overlapping lanes serialize.

Assign distinct file or artifact names per lane even under the proposal model, so that two
proposals cannot collide when applied.

## Derived claims

A claim computed over the whole substrate — counts, totals, coverage figures, inventories,
"all N cases pass" — is not a lane's property. Lanes that each change part of the whole will
each leave such a claim stale, and a claim that is true only at the branch tip is false at
every intermediate state.

Derived claims belong to the single writer. The brief states which claims are centrally
owned and asks the subordinate pass to report the inputs instead. The Orchestrator updates
each derived claim so it is true at the state where it appears, not merely at the end.

## Lane sizing

A separate lane is justified by a different *kind* of work that is also heavy on its own. It
is not justified by volume of one kind: repeated application of one method across many inputs
batches inside a single pass, and splitting it multiplies brief authoring, context
reconstruction, and audit without reducing the work.

Each lane costs a brief, an independent context, a returned artifact, and an audit. Lanes
whose audit costs more than the work they perform are consolidated. Prefer steering an open
subordinate pass over opening another one for related work: a new pass discards the context
the first one built.

## Return contract

A subordinate pass returns:

- its result and the deliverable artifact the brief named;
- its declared deviations — every place it processed less than, or other than, what the brief
  named, or `none`;
- findings it opened outside its lane, reported and left unfixed;
- residual risk and environment-specific gaps.

Deviations are not a courtesy. A count, absence, or coverage claim obtained from partial or
capped input is reported as not assessed at that depth, never as an absence finding, and it
carries that qualification into every summary that reuses it.

Normative requirements:

1. An unaudited subordinate result is not evidence. Until the Orchestrator audits it, its
   maturity is `ASSERTED` regardless of what the subordinate pass ran.
2. The Orchestrator MUST read the declared deviations before adopting any number, claim, or
   artifact from the pass, and MUST propagate them into what it reports upward.
3. A subordinate pass that reports a finding outside its lane MUST NOT fix it. The
   Orchestrator decides whether to extend scope, and records the extension under
   `orchestrator-judgment`.
4. A subordinate pass blocked on an approval or an unavailable environment surfaces the
   block. Neither it nor the Orchestrator substitutes synthesized results for the blocked
   input.

## Verifier minimum for adopted repairs

Adopting a subordinate pass's repair means asserting its claim as the Orchestrator's own. For
a consequential repair, the adopting agent MUST re-derive the discriminating control itself
rather than accept the subordinate pass's report of it: restore the pre-fix state of the
changed surface with the new control in place, observe the expected failure, restore the fix,
and observe the expected pass.

Re-running the subordinate pass's own script is not re-derivation if the script is what is
being audited. Where re-derivation is impracticable, the claim stays at `EXECUTED` with the
reason recorded, and the repair is not presented as independently verified.

An Orchestrator that authored or adopted a change is not an independent reviewer of it.
Consequential adopted changes route to a reviewer outside the delegation tree.

## Cycle bookkeeping

Delegated passes are ordinary passes for accounting purposes. A delegation-heavy repair loop
across several review rounds is a bounded cycle and keeps the cycle identity, planned versus
executed passes, per-pass execution status, finding continuity across snapshots, and a
termination reason from the standard vocabulary. See [iterative-review.md](iterative-review.md).

Absence of a cycle record is a common failure in long orchestrated loops: each round looks
self-contained, so the round count, the carried findings, and the bound go unrecorded.

## Related references

- [roles.md](roles.md) — role definitions and routing
- [decision-authority.md](decision-authority.md) — authority envelopes
- [evidence-protocol.md](evidence-protocol.md) — claim maturities and discriminating controls
- [iterative-review.md](iterative-review.md) — bounded review cycles
- [runtime-adapters.md](runtime-adapters.md) — parallel mutation surfaces and fail-closed fields
- [repository-coordination.md](repository-coordination.md) — recording channels on repository substrates
