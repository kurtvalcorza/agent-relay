#!/usr/bin/env python3
"""Reference role router for Agent Relay.

This is intentionally conservative and illustrative. It infers a role sequence and,
for Reviewer routes, optional review lenses from plain task text plus workflow state.
It does not grant permissions or authorize mutations.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass

ROLES = {"builder", "reviewer", "executor", "verifier", "integrator"}
REVIEW_LENSES = {
    "standard",
    "design",
    "security",
    "reliability",
    "test-gap",
    "spec-conformance",
    "regression",
    "readiness",
}


@dataclass(frozen=True)
class Route:
    inferred: str
    confidence: str
    reason: str
    sequence: tuple[str, ...]
    handoff_required: bool
    review_lenses: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Serialize while preserving the historical shape for non-Reviewer routes."""

        result: dict[str, object] = {
            "inferred": self.inferred,
            "confidence": self.confidence,
            "reason": self.reason,
            "sequence": list(self.sequence),
            "handoff_required": self.handoff_required,
        }
        if self.review_lenses:
            result["review_lenses"] = list(self.review_lenses)
        return result


def _has(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def _infer_review_lenses(text: str) -> tuple[str, ...]:
    """Infer lenses only from unambiguous review intent, not bare subject nouns."""

    lenses: list[str] = []

    if _has(
        text,
        r"\badversarial(?:ly)?\s+review\b",
        r"\bdesign\s+review\b",
        r"\barchitecture\s+review\b",
        r"\barchitectural\s+review\b",
        r"\bchallenge\s+(?:the\s+)?(?:design|architecture|approach|assumptions?)\b",
    ):
        lenses.append("design")

    if _has(
        text,
        r"\bsecurity\s+review\b",
        r"\breview\b.*\bfor\s+security\b",
        r"\baudit\b.*\b(?:security|trust boundar(?:y|ies))\b",
        r"\baudit\s+trust boundar(?:y|ies)\b",
    ):
        lenses.append("security")

    if _has(
        text,
        r"\breliability\s+review\b",
        r"\breview\b.*\bfor\s+(?:reliability|production failure modes?)\b",
        r"\b(?:assess|audit)\b.*\b(?:retry|interruption|concurrency|partial failure|recovery)\b",
    ):
        lenses.append("reliability")

    if _has(
        text,
        r"\btest[- ]gap\s+review\b",
        r"\breview\b.*\b(?:test gaps?|what (?:is|isn't|is not) tested)\b",
        r"\bidentify\s+(?:the\s+)?test gaps?\b",
    ):
        lenses.append("test-gap")

    if _has(
        text,
        r"\bspec(?:ification)?[- ]conformance\s+review\b",
        r"\breview\b.*\bagainst\s+(?:the\s+)?(?:spec|specification|contract|requirements?)\b",
        r"\bcheck\b.*\bagainst\s+(?:the\s+)?(?:spec|specification|contract|requirements?)\b",
    ):
        lenses.append("spec-conformance")

    if _has(
        text,
        r"\bregression\s+review\b",
        r"\breview\b.*\bfor\s+regressions?\b",
    ):
        lenses.append("regression")

    if _has(
        text,
        r"\breadiness\s+review\b",
        r"\b(?:assess|review|audit)\s+(?:merge|release|deployment|production)?\s*readiness\b",
        r"\breview\b.*\bfor\s+(?:merge|release|deployment|production)\s+readiness\b",
    ):
        lenses.append("readiness")

    return _dedupe(lenses) if lenses else ("standard",)


def _normalize_explicit_lenses(values: tuple[str, ...] | list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    normalized = tuple(dict.fromkeys(value.lower().strip() for value in values))
    unknown = [value for value in normalized if value not in REVIEW_LENSES]
    if unknown:
        raise ValueError(f"unknown review lens: {unknown[0]}")
    if "standard" in normalized and len(normalized) > 1:
        normalized = tuple(value for value in normalized if value != "standard")
    return normalized


def infer_role(
    task: str,
    *,
    explicit_role: str | None = None,
    explicit_review_lenses: tuple[str, ...] | list[str] | None = None,
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
    explicit_lenses = _normalize_explicit_lenses(explicit_review_lenses)

    if explicit_role:
        role = explicit_role.lower().strip()
        if role not in ROLES:
            raise ValueError(f"unknown role: {explicit_role}")
        if role == "reviewer":
            lenses = explicit_lenses or _infer_review_lenses(text)
            return Route(role, "high", "Explicit role assignment", (role,), False, lenses)
        return Route(role, "high", "Explicit role assignment", (role,), False)

    mutation_forbidden = _has(
        text,
        r"\bread[- ]only\b",
        r"\bdo not (?:edit|modify|change|write|fix|repair)\b",
        r"\bno mutations?\b",
        r"\bwithout (?:editing|modifying|changing|writing)\b",
    )

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

    readiness_review = _has(
        text,
        r"\breadiness\s+review\b",
        r"\b(?:assess|review|audit)\s+(?:merge|release|deployment|production)?\s*readiness\b",
        r"\breview\b.*\bfor\s+(?:merge|release|deployment|production)\s+readiness\b",
    )
    review = readiness_review or _has(
        text,
        r"\breview\b",
        r"\baudit\b",
        r"hunt bugs",
        r"\bchallenge\b",
    )
    signoff = _has(
        text,
        r"sign[ -]?off",
        r"\bapprove\b",
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
        r"\bfix\b(?=\s+(?:this|that|the|it|what|anything|finding|bug|defect|issue|code|implementation|problem|reported))",
        r"\brepair\b(?=\s+(?:this|that|the|it|finding|bug|defect|issue|code|implementation|problem))",
        r"\bupdate\b",
        r"\brevise\b",
        r"\brefactor\b",
        r"\badd (?:a |the )?(?:test|tests|feature|file|support)\b",
    )
    if mutation_forbidden:
        build = False

    integrate = _has(
        text,
        r"\breconcile\b",
        r"\brestack\b",
        r"\badjudicate\b",
        r"which layer",
        r"remaining blocker",
        r"what still blocks",
    )

    review_lenses = explicit_lenses or (_infer_review_lenses(text) if review else ())

    if local_required and not environment_available:
        if review:
            seq = ["reviewer", "executor"]
            if signoff or verify or verification_missing or readiness_review:
                seq.append("verifier")
            if signoff or integrate or readiness_review:
                seq.append("integrator")
            return Route(
                "reviewer",
                "high",
                "Review requires an execution environment unavailable to the current agent",
                _dedupe(seq),
                True,
                review_lenses,
            )

        seq = ["executor"]
        if signoff or verify or verification_missing:
            seq.append("verifier")
        if signoff or integrate:
            seq.append("integrator")
        return Route(
            "executor",
            "high",
            "Required execution environment is unavailable to the current agent",
            _dedupe(seq),
            True,
        )

    if review and build:
        seq = ["reviewer", "integrator", "builder", "verifier"]
        if signoff or readiness_review:
            seq.append("integrator")
        return Route(
            "reviewer",
            "high",
            "Task combines review and authorized repair",
            _dedupe(seq),
            False,
            review_lenses,
        )

    if unresolved_finding and build:
        seq = ("integrator", "builder", "verifier")
        return Route("integrator", "high", "Open finding must be adjudicated before repair", seq, False)

    if review and readiness_review:
        return Route(
            "reviewer",
            "high",
            "Readiness review requires evidence-gap assessment, verification, and Integrator decision",
            ("reviewer", "verifier", "integrator"),
            False,
            review_lenses,
        )

    if review and signoff:
        return Route(
            "reviewer",
            "high",
            "Review request includes consequential sign-off",
            ("reviewer", "verifier"),
            False,
            review_lenses,
        )

    if review and verify:
        return Route(
            "reviewer",
            "high",
            "Task explicitly combines review with verification",
            ("reviewer", "verifier"),
            False,
            review_lenses,
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
        return Route(
            "reviewer",
            "high",
            "Task requests adversarial inspection",
            ("reviewer",),
            False,
            review_lenses,
        )

    if local_required:
        return Route("executor", "medium", "Task is primarily environment-specific execution", ("executor",), False)

    if build:
        return Route("builder", "high", "Task requests creation or modification", ("builder",), False)

    if unresolved_finding:
        return Route("integrator", "medium", "Workflow state contains an unresolved finding", ("integrator",), False)

    return Route(
        "reviewer",
        "low",
        "Ambiguous inspection-oriented default",
        ("reviewer",),
        False,
        ("standard",),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Infer an Agent Relay role route")
    parser.add_argument("task", help="Task text to route")
    parser.add_argument("--explicit-role", choices=sorted(ROLES))
    parser.add_argument(
        "--review-lens",
        action="append",
        choices=sorted(REVIEW_LENSES),
        dest="review_lenses",
        help="Explicit Reviewer lens; repeat to compose lenses",
    )
    parser.add_argument("--environment-unavailable", action="store_true")
    parser.add_argument("--unresolved-finding", action="store_true")
    parser.add_argument("--implementation-complete", action="store_true")
    parser.add_argument("--verification-missing", action="store_true")
    args = parser.parse_args()

    route = infer_role(
        args.task,
        explicit_role=args.explicit_role,
        explicit_review_lenses=args.review_lenses,
        environment_available=not args.environment_unavailable,
        unresolved_finding=args.unresolved_finding,
        implementation_complete=args.implementation_complete,
        verification_missing=args.verification_missing,
    )
    print(json.dumps(route.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
