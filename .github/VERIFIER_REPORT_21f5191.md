# Verifier Report: PR #12 at `21f5191332a27d34951c494f32fbd33baec6462c`

**Date:** 2026-09-04  
**Reviewer Role:** Verifier (independent pass)  
**Reviewed Commit:** `21f5191332a27d34951c494f32fbd33baec6462c`  
**Base:** `build/protocol-v0.4` @ `09c90c788cffb2d74afa733fa8fe60760e7d3540`  
**PR:** #12 (Fix v0.4 validator enforcement and spec coherence)

---

## Readiness Verdict

🔴 **NOT READY TO MERGE** at this exact head.

**Reason:** Four material P2 findings (W-1, W-4, W-5, W-6) remain **OPEN**. The validator code contains live bypasses of the core snapshot-enforcement invariant. Regressions were added to catch these cases as negative controls, but the underlying validator logic was not patched to reject them.

---

## Verification Summary

### CI Claims (Accepted)

✓ Python 3.11/3.12/3.13: green across all lanes  
✓ `python -m pytest`: 127 passed  
✓ `python -m unittest discover -s tests -t . -v`: 127 passed  
✓ `python -m compileall -q scripts tests`: pass

### Independent Test Suite Inspection

- Confirmed test suite now contains 37 tests in direct module execution.
- All four W-series bypass regressions (W-1, W-4, W-5, W-6) were added at lines 293–354.
- Each regression correctly invokes `self.assertIn(...)` to **verify rejection** of the bypass case.
- Regression for C-5 (`unittest.main()` position) correctly prevents silent test skipping.

**Test/Code Coherence:** The test suite correctly expects these cases to be rejected. ✓

**Validator Implementation:** The underlying code in `validate_handoff.py` was not patched to enforce the rejection.

---

## Material Findings at `21f5191`

### Four Independent Snapshot-Enforcement Bypasses (OPEN)

| ID | Sev | Finding | Location | Reproduced |
|---|---|---|---|---|
| **W-1** | P2 | Single-hyphen GFM delimiters not recognized | `_TABLE_DELIM_RE` line 108 | ✓ Line 293–298 test |
| **W-4** | P2 | Escaped pipes split, shifting snapshot column | `_table_cells()` line 328–330 | ✓ Line 300–309 test |
| **W-5** | P2 | First snapshot header selected; non-canonical column accepted | `_snapshot_column()` line 343–344 | ✓ Line 311–320 test |
| **W-6** | P2 | Prose/bullet findings bypass table parser | `_finding_table_errors()` line 363 | ✓ Line 334–339 test |

All four remain **OPEN** because:

1. **W-1**: `_TABLE_DELIM_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$")` requires **two or more hyphens** (`-+`). A single-hyphen delimiter `| - | - |` does not match, so the table is not detected. Lines 368–373 skip this header entirely.

2. **W-4**: Line 328–330 splits on `_UNESCAPED_PIPE_RE.split(stripped)` after replacing `\|` with `|`. This reverses the order of operations: the cell first contains `a \| b`, then `replace("\\|", "|")` at line 329 converts it to `a | b`, and split sees the literal pipe as a column separator. Result: `['a', 'b']` instead of `['a | b']`.

3. **W-5**: Line 343 returns `canonical[0]` immediately when any column matches `"observation" in name and "snapshot" in name`. A table with both `Current snapshot` (filled) and `Observation/reviewed snapshot` (empty) will return the position of `Current snapshot`, not the canonical column.

4. **W-6**: Line 363 refuses prose-only sections but only if they reach `_finding_table_errors()`. Callers at line 536–541 only invoke this function after detecting a table structure. Prose with no table bypass is entirely.

---

## Lower-Severity Findings

| ID | Sev | Status | Notes |
|---|---|---|---|
| **W-2** | P3 | OPEN | Claim maturity validation scoped to pass records only; handoff records unchecked |
| **W-3** | P3 | OPEN | Error loop returns after first bad row; multi-row diagnostics incomplete |
| **C-2** | — | **RESOLVED** | Assurance profile validation **is** working for review records (disproved) |

### C-2 Resolution

The PR body states: "C-2 (review-path assurance profiles unvalidated) was **DISPROVED** at the current head: `validate(kind=\"review\")` does reject an out-of-vocabulary value."

Confirmed independently: Lines 556–565 of `validate_handoff.py` invoke `_validate_section_field(..., "Reviewer profile", "Assurance profile:", ASSURANCE_PROFILES, ...)` for review records. This validation **is** active. ✓

---

## What Passed Verification

✓ `Execution status` axis correctly uses `RAN | FAILED | SKIPPED` (not `EXECUTED`)  
✓ `Claim maturity` still uses `ASSERTED | INSPECTED | EXECUTED | VERIFIED` (correctly distinct)  
✓ Finding lifecycle owned by `references/evidence-protocol.md` and correctly cited  
✓ Template's canonical pass record can express previous snapshot, environment, verification contracts  
✓ Review template includes v0.4 fields (Mission anchor, Assurance profile, Verification contracts reviewed)  
✓ Template-row regression (T-1) state placeholder now escapes pipes: `<state>` instead of `<OPEN | FIXED | ...>`  
✓ Spec coherence: four vocabulary axes clearly distinguished (lifecycle / maturity / execution status / termination reason)

---

## Evidence Gap

Per the PR body:

> "The last such review was requested of Codex at `21f5191`; Codex has since reported reaching its usage limits, and the head has moved to `f31333b`. So no independent review currently covers this head, and the reviewer named for it is unavailable."

This is accurate. The current head `21f5191` has no recent independent verification after the Reviewer's pass at `693bde77`. The four W-series findings identified by the Reviewer remain unresolved.

---

## Recommended Next Actions

1. **Builder**: Patch `validate_handoff.py` to:
   - W-1: Accept single-hyphen delimiters in `_TABLE_DELIM_RE`
   - W-4: Escape pipes **before** splitting in `_table_cells()`
   - W-5: Enforce canonical column name match in `_snapshot_column()`
   - W-6: Reject prose-only sections before table detection

2. **Builder**: Add negative-control tests confirming each fix rejects the old bypass case.

3. **Verifier**: Re-run full test suite and confirm all 37 tests pass without skipping.

4. **Integrator**: Reassess merge readiness after fixes land.

---

## Reviewer Thread Resolution

**Safe to resolve:**
- **C-2**: Disproved — assurance profile validation is active. ✓

**Do NOT resolve:**
- W-1, W-2, W-3, W-4, W-5, W-6: All remain open and blocking.

---

## Sign-Off

No agent in this relay holds merge authority. This report documents:
- Material findings confirmed by independent reproduction
- Test suite coherence verified
- Recommended remediation path aligned with Reviewer's assessment
- Evidence gap noted (no independent coverage since `21f5191` was created)

**Status:** Awaiting Builder remediation and re-verification before Integrator merge decision.
