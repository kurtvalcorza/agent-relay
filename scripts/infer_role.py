#!/usr/bin/env python3
"""Reference role router for Agent Relay.

This is intentionally conservative and illustrative. It infers a role sequence from
plain task text plus optional workflow-state flags. It does not grant permissions or
authorize mutations.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict

ROLES = {"builder", "reviewer", "executor", "verifier", "integrator"}


@dataclass(frozen=True)
class Route:
    inferred: str
    confidence: str
    reason: str
    sequence: tuple[str, ...]
    handoff_required: bool


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def infer_role(
    task: str,
    *,
    explicit_role: str | None = None,
    environment_available: bool = True,
    unresolved_finding: bool = False,
    implementation_complete: bool = False,
    verification_missing: bool = False,
) -> Route:
    """Infer a conservative Agent Relay role route.

    The result is workflow guidance only. Callers must enforce their own permission,
    safety, and mutation boundaries independently.
    """

    text = task.strip()

    if explicit_role:
        role = explicit_role.lower().strip()
        if role not in ROLES:
            raise ValueError(f"unknown role: {explicit_role}")
        return Route(role, "high", "Explicit role assignment", (role,), False)

    local_required = _has(
        text,
        r"\bwsl\b",
        r"\blinux\b",
        r"\bcuda\b",
        r"\bgpu\b",
        r"\bdocker\b",
        r"local(?:ly)?",
        r"private (?:file|fixture|network|repo|repository)",
    )
    review = _has(text, r"\breview\b", r"\baudit\b", r"hunt bugs", r"challenge")
    signoff = _has(
        text,
        r"sign[ -]?off",
        r"approve",
        r"ready to merge",
        r"can (?:we|i) merge",
        r"declare .*pass",
        r"release ready",
    )
    verify = _has(text, r"\bverify\b", r"\bconfirm\b", r"\breproduce\b", r"check whether")
    build = _has(
        text,
        r"\bbuild\b",
        r"\bimplement\b",
        r"\bfix\b",
        r"\brepair\b",
        r"\bupdate\b",
        r"\brevise\b",
        r"\brefactor\b",
        r"\badd (?:a |the )?(?:test|tests|feature|file|support)\b",
    )
    integrate = _has(
        text,
        r"\breconcile\b",
        r"\brestack\b",
        r"\badjudicate\b",
        r"which layer",
        r"remaining blocker",
        r"what still blocks",
    )

    if local_required and not environment_available:
        seq = ["executor"]
        if signoff or verify or verification_missing:
            seq.append("verifier")
        if signoff or integrate:
            seq.append("integrator")
        return Route(
            "executor",
            "high",
            "Required execution environment is unavailable to the current agent",
            tuple(dict.fromkeys(seq)),
            True,
        )

    if review and build:
        seq = ("reviewer", "integrator", "builder", "verifier")
        return Route("reviewer", "high", "Task combines review and authorized repair", seq, False)

    if unresolved_finding and build:
        seq = ("integrator", "builder", "verifier")
        return Route("integrator", "high", "Open finding must be adjudicated before repair", seq, False)

    if review and signoff:
        return Route(
            "reviewer",
            "high",
            "Review request includes consequential sign-off",
            ("reviewer", "verifier"),
            False,
        )

    if signoff:
        return Route(
            "verifier",
            "high",
            "Consequential readiness or merge claim requires verification",
            ("verifier", "integrator"),
            False,
        )

    if integrate:
        return Route("integrator", "high", "Task requires reconciliation or ownership decision", ("integrator",), False)

    if verify or (implementation_complete and verification_missing):
        return Route("verifier", "high", "Existing claim or completed implementation requires evidence", ("verifier",), False)

    if review:
        return Route("reviewer", "high", "Task requests adversarial inspection", ("reviewer",), False)

    if local_required:
        return Route("executor", "medium", "Task is primarily environment-specific execution", ("executor",), False)

    if build:
        return Route("builder", "high", "Task requests creation or modification", ("builder",), False)

    if unresolved_finding:
        return Route("integrator", "medium", "Workflow state contains an unresolved finding", ("integrator",), False)

    return Route("reviewer", "low", "Ambiguous inspection-oriented default", ("reviewer",), False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer an Agent Relay role route")
    parser.add_argument("task", help="Task text to route")
    parser.add_argument("--explicit-role", choices=sorted(ROLES))
    parser.add_argument("--environment-unavailable", action="store_true")
    parser.add_argument("--unresolved-finding", action="store_true")
    parser.add_argument("--implementation-complete", action="store_true")
    parser.add_argument("--verification-missing", action="store_true")
    args = parser.parse_args()

    route = infer_role(
        args.task,
        explicit_role=args.explicit_role,
        environment_available=not args.environment_unavailable,
        unresolved_finding=args.unresolved_finding,
        implementation_complete=args.implementation_complete,
        verification_missing=args.verification_missing,
    )
    print(json.dumps(asdict(route), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
