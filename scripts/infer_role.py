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

_LENS_TOKEN = (
    r"(?:standard|design|architecture|architectural|adversarial|security|"
    r"reliability|test[- ]gaps?|spec(?:ification)?[- ]conformance|regression|readiness)"
)
_LENS_SEPARATOR = r"(?:\s*,\s*(?:and\s+|&\s*)?|\s*(?:and|&)\s*)"
_LENS_LIST = rf"{_LENS_TOKEN}(?:{_LENS_SEPARATOR}{_LENS_TOKEN})*"


# Spans text inside a single clause: stops at clause punctuation and at a
# connective that introduces a separate command, so a later repair clause
# cannot donate its subject to an earlier inspection phrase.
_SAME_CLAUSE = r"(?:(?!\b(?:then|but|however|yet)\b)[^.;,\n])*"


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


def _normalize_lens_sequence(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    ordered = _dedupe(list(items))
    if "standard" in ordered and len(ordered) > 1:
        ordered = tuple(item for item in ordered if item != "standard")
    return ordered


def _lenses_from_fragment(fragment: str) -> list[str]:
    """Map an explicit review-lens phrase fragment to canonical lens names."""

    lenses: list[str] = []
    lowered = fragment.lower()

    if re.search(r"\b(?:design|architecture|architectural|adversarial)\b", lowered):
        lenses.append("design")
    if re.search(r"\bsecurity\b", lowered):
        lenses.append("security")
    if re.search(r"\breliability\b", lowered):
        lenses.append("reliability")
    if re.search(r"\btest[- ]gaps?\b", lowered):
        lenses.append("test-gap")
    if re.search(r"\bspec(?:ification)?[- ]conformance\b", lowered):
        lenses.append("spec-conformance")
    if re.search(r"\bregression\b", lowered):
        lenses.append("regression")
    if re.search(r"\breadiness\b", lowered):
        lenses.append("readiness")
    if re.search(r"\bstandard\b", lowered):
        lenses.append("standard")

    return lenses


def _infer_review_lenses(text: str) -> tuple[str, ...]:
    """Infer lenses only from explicit/unambiguous review intent phrases."""

    lenses: list[str] = []

    # Prefix forms, including compound requests:
    # "security review", "security and reliability review".
    for match in re.finditer(
        rf"\b(?P<lenses>{_LENS_LIST})\s+review\b",
        text,
        flags=re.IGNORECASE,
    ):
        lenses.extend(_lenses_from_fragment(match.group("lenses")))

    # Suffix forms, including compound requests:
    # "review this PR for security and reliability".
    for match in re.finditer(
        rf"\breview\b[^.;\n]{{0,100}}\bfor\s+(?P<lenses>{_LENS_LIST})\b",
        text,
        flags=re.IGNORECASE,
    ):
        lenses.extend(_lenses_from_fragment(match.group("lenses")))

    # Explicit standalone intent forms that need not contain the word "review".
    if _has(
        text,
        r"\badversarial(?:ly)?\s+review\b",
        r"\bchallenge\s+(?:the\s+)?(?:design|architecture|approach|assumptions?)\b",
    ):
        lenses.append("design")

    if _has(
        text,
        rf"\baudit\b{_SAME_CLAUSE}\b(?:security|trust boundar(?:y|ies))\b",
        r"\baudit\s+trust boundar(?:y|ies)\b",
    ):
        lenses.append("security")

    if _has(
        text,
        r"\b(?:assess|audit)\b.*\b(?:retry|retries|interruption|concurrency|partial failure|recovery)\b",
        r"\breview\b.*\bproduction failure modes?\b",
    ):
        lenses.append("reliability")

    if _has(
        text,
        r"\breview\b.*\btest gaps?\b",
        r"\bidentify\s+(?:the\s+)?test gaps?\b",
        r"\bwhat (?:is|isn't|is not) tested\b",
    ):
        lenses.append("test-gap")

    if _has(
        text,
        r"\b(?:review|check)\b.*\bagainst\s+(?:the\s+)?(?:spec|specification|contract|requirements?)\b",
    ):
        lenses.append("spec-conformance")

    if _has(text, r"\breview\b.*\bfor\s+regressions?\b"):
        lenses.append("regression")

    if _has(
        text,
        r"\breadiness\s+review\b",
        r"\b(?:assess|review|audit)\s+(?:merge|release|deployment|production)?\s*readiness\b",
        r"\breview\b.*\bfor\s+(?:merge|release|deployment|production)\s+readiness\b",
    ):
        lenses.append("readiness")

    return _normalize_lens_sequence(lenses)


def _normalize_explicit_lenses(
    values: tuple[str, ...] | list[str] | None,
) -> tuple[str, ...]:
    if not values:
        return ()
    normalized = tuple(dict.fromkeys(value.lower().strip() for value in values))
    unknown = [value for value in normalized if value not in REVIEW_LENSES]
    if unknown:
        raise ValueError(f"unknown review lens: {unknown[0]}")
    return _normalize_lens_sequence(normalized)


def _infer_build_intent(text: str) -> bool:
    """Infer mutation intent from command-like phrasing, not artifact nouns."""

    mutation_verbs = r"(?:implement|fix|repair|build|update|revise|refactor)"
    if _has(
        text,
        rf"^\s*(?:please\s+)?{mutation_verbs}\b",
        rf"[,;:]\s*(?:please\s+)?{mutation_verbs}\b",
        rf"(?:[.!?]|\n)\s*(?:please\s+)?{mutation_verbs}\b",
        rf"\b(?:and|then|please|also|but|however|yet|while)\s+{mutation_verbs}\b",
        rf"\b(?:can|could|would|will)\s+you\s+{mutation_verbs}\b",
        rf"\b(?:want|need)\s+(?:you\s+)?to\s+{mutation_verbs}\b",
        r"\badd (?:a |an |the )?(?:test|tests|feature|file|support)\b",
    ):
        return True

    return False


def _infer_review_operation(text: str) -> bool:
    """Infer an inspection operation from command-like phrasing, not artifact nouns."""

    if _has(
        text,
        r"^\s*(?:please\s+)?(?:review|audit)\b",
        r"\b(?:and|then|please|also)\s+(?:review|audit)\b",
        r"\b(?:can|could|would|will)\s+you\s+(?:review|audit)\b",
        r"\b(?:want|need)\s+(?:you\s+)?to\s+(?:review|audit)\b",
        r"\b(?:do|run|perform|conduct)\s+(?:an?\s+)?(?:[\w-]+\s+(?:and\s+[\w-]+\s+)*)?(?:review|audit)\b",
        rf"^\s*(?:please\s+)?{_LENS_LIST}\s+review\b",
        r"\b(?:review|audit)\s+(?:this|that|it|these|those|the|a|an|my|our)\b",
        r"\bhunt bugs?\b",
        r"\bchallenge\s+(?:the\s+)?(?:design|architecture|approach|assumptions?)\b",
        r"\bidentify\s+(?:the\s+)?test gaps?\b",
        r"\b(?:assess|audit)\b.*\b(?:retry|retries|interruption|concurrency|partial failure|recovery)\b",
        r"\bcheck\b.*\bagainst\s+(?:the\s+)?(?:spec|specification|contract|requirements?)\b",
        r"\b(?:assess|audit)\s+(?:merge|release|deployment|production)?\s*readiness\b",
    ):
        return True

    return False


def _global_mutation_prohibition(text: str) -> bool:
    """Detect whole-task mutation prohibitions without swallowing scoped boundaries."""

    return _has(
        text,
        r"^\s*read[- ]only\b",
        r"\b(?:this|the)\s+(?:task|repo|repository|artifact|work)\s+is\s+read[- ]only\b",
        r"\bread[- ]only\s+(?:mode|request|review)\b",
        r"\bno mutations?\b",
        r"\bdo not (?:edit|modify|change|write|fix|repair)(?:\s+(?:anything|this|it|the (?:repo|repository|codebase)))?\s*(?:[.!?]|$)",
        r"\bwithout (?:editing|modifying|changing|writing)(?:\s+(?:anything|this|it))?\s*(?:[.!?]|$)",
    )


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
        if explicit_lenses and role != "reviewer":
            raise ValueError("review lenses require Reviewer role")
        if role == "reviewer":
            lenses = explicit_lenses or _infer_review_lenses(text) or ("standard",)
            sequence = (
                ("reviewer", "verifier", "integrator")
                if "readiness" in lenses
                else ("reviewer",)
            )
            return Route(role, "high", "Explicit role assignment", sequence, False, lenses)
        return Route(role, "high", "Explicit role assignment", (role,), False)

    inferred_lenses = _infer_review_lenses(text)
    build = _infer_build_intent(text)
    review_operation = _infer_review_operation(text)

    # An explicit lens is itself explicit review intent. Inferred lens phrases count as
    # review intent unless the same phrase is merely the subject of a mutation command
    # ("implement the readiness review lens", "update the review template").
    review = bool(explicit_lenses) or review_operation or (bool(inferred_lenses) and not build)
    review_lenses = (
        explicit_lenses
        if explicit_lenses
        else (inferred_lenses if review and inferred_lenses else (("standard",) if review else ()))
    )
    readiness_review = review and "readiness" in review_lenses

    if _global_mutation_prohibition(text):
        build = False

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
        if readiness_review:
            seq = ("reviewer", "integrator", "builder", "verifier", "integrator")
        else:
            seq = ("reviewer", "integrator", "builder", "verifier")
        return Route(
            "reviewer",
            "high",
            "Task combines review and authorized repair",
            seq,
            False,
            review_lenses,
        )

    if unresolved_finding and build:
        seq = ("integrator", "builder", "verifier")
        return Route("integrator", "high", "Open finding must be adjudicated before repair", seq, False)

    if readiness_review:
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

    try:
        route = infer_role(
            args.task,
            explicit_role=args.explicit_role,
            explicit_review_lenses=args.review_lenses,
            environment_available=not args.environment_unavailable,
            unresolved_finding=args.unresolved_finding,
            implementation_complete=args.implementation_complete,
            verification_missing=args.verification_missing,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(json.dumps(route.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
