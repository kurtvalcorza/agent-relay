#!/usr/bin/env python3
"""Lightweight structural validator for Agent Relay handoff/review Markdown.

Uses only the Python standard library. It does not interpret correctness,
permissions, or whether a role route is semantically appropriate; it checks
that a durable relay record contains the minimum resumability fields.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

HANDOFF_REQUIRED_HEADINGS = (
    "Mission",
    "Current role",
    "Review lenses",
    "Role source",
    "Recommended role sequence",
    "Authoritative substrate",
    "Current immutable snapshot",
    "Mutation permissions",
    "Completed work",
    "Verified evidence",
    "Open findings",
    "Ordered next actions",
    "Verification checkpoint",
    "Completion criteria",
    "Provenance",
)

REVIEW_REQUIRED_HEADINGS = (
    "Mission",
    "Reviewer profile",
    "Reviewed state",
    "Mutation boundaries",
    "Evidence baseline",
    "Findings summary",
    "Structured findings",
    "Executed or inspectable evidence",
    "Unverified surfaces",
    "Recommended next role/pass",
    "Readiness/sign-off status",
    "Provenance",
)


def _detect_kind(text: str) -> str:
    if "# Agent Relay Review" in text:
        return "review"
    return "handoff"


def validate(text: str, *, kind: str = "auto") -> list[str]:
    errors: list[str] = []
    selected_kind = _detect_kind(text) if kind == "auto" else kind
    if selected_kind not in {"handoff", "review"}:
        raise ValueError(f"unknown record kind: {selected_kind}")

    required_headings = (
        REVIEW_REQUIRED_HEADINGS if selected_kind == "review" else HANDOFF_REQUIRED_HEADINGS
    )
    headings = {
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    }
    for heading in required_headings:
        if heading not in headings:
            errors.append(f"missing heading: {heading}")

    lowered = text.lower()
    if "read-only" not in lowered and "forbidden" not in lowered:
        errors.append("mutation boundary is not explicit (no read-only/forbidden statement)")

    placeholders = (
        "<commit",
        "<digest",
        "<what outcome",
        "<what review outcome",
        "<builder | reviewer",
        "<explicit user assignment",
        "<e.g. executor",
        "<agent/client>",
        "<immutable-id>",
        "<standard | design",
    )
    if any(token in lowered for token in placeholders):
        errors.append("template placeholders appear to remain unfilled")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--kind", choices=("auto", "handoff", "review"), default="auto")
    args = parser.parse_args()

    try:
        text = args.record.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = validate(text, kind=args.kind)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    label = "review" if (args.kind == "review" or (args.kind == "auto" and _detect_kind(text) == "review")) else "handoff"
    print(f"Agent Relay {label} structure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
