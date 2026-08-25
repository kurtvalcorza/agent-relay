# Local Execution Relay

Use this reference when one agent cannot execute the required experiment but another agent/session can.

## Define the experiment before handoff

Specify:

1. **Question** — the exact uncertainty being resolved.
2. **Source state** — immutable revision/artifact identity.
3. **Environment** — required OS, runtime, hardware, container, credentials, network, or filesystem capability.
4. **Mutation scope** — what may be changed and what is strictly read-only.
5. **Procedure** — commands or ordered actions.
6. **Observables** — outputs/logs/artifacts that matter.
7. **Acceptance criteria** — what constitutes PASS, FAIL, BLOCKED, or inconclusive.
8. **Evidence capture** — versions, logs, checksums, screenshots, reports, benchmark data, etc.
9. **Recording location** — where results should be written if mutation is authorized.

## Good local-execution request

> On commit `abc123`, run the full suite under CPython 3.10 and 3.12 inside Ubuntu 24.04. Exercise the symlink tests without skip. Record kernel, Python version, dependency install method, pass/fail/skip counts, and failure logs. Do not modify the seven audited source repositories. If a test fails, reproduce it once before changing code and identify the earliest owning PR.

## Bad local-execution request

> Test everything locally and fix it.

The bad request leaves state, permissions, evidence, ownership, and completion undefined.

## GPU/container execution

When GPU is involved, capture where relevant:

- GPU model;
- driver version;
- CUDA/runtime version;
- container image digest/tag;
- NVIDIA Container Toolkit/runtime state;
- visible devices;
- framework-reported accelerator state;
- requested vs observed precision/device;
- peak memory if capacity is part of the claim.

A GPU being visible does not prove a GPU-specific Contract behavior passed.

## Read-only execution sources

Read-only means no mutation through any surface, including:

- commits;
- branches;
- PRs/issues/comments;
- tags/releases;
- file edits;
- generated files inside the source working tree when avoidable;
- remote API writes.

Run experiments in disposable copies, temporary worktrees, containers, or external output directories when needed.
