#!/usr/bin/env python3
"""Lightweight structural validator for Agent Relay Markdown handoffs.

Uses only the Python standard library. It does not interpret correctness,
permissions, or whether a role route is semantically appropriate; it checks
that a handoff contains the minimum resumability and routing fields.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REQUIRED_HEADINGS = (
    "Mission",
    "Current role",
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
)


def validate(text: str) -> list[str]:
    errors: list[str] = []
    headings = {
        line.lstrip("#").strip()
        for line in text.splitlines()
        if line.startswith("#")
    }
    for heading in REQUIRED_HEADINGS:
        if heading not in headings:
            errors.append(f"missing heading: {heading}")

    lowered = text.lower()
    if "read-only" not in lowered and "forbidden" not in lowered:
        errors.append("mutation boundary is not explicit (no read-only/forbidden statement)")

    placeholders = (
        "<commit",
        "<digest",
        "<what outcome",
        "<builder | reviewer",
        "<explicit user assignment",
        "<e.g. executor",
    )
    if any(token in lowered for token in placeholders):
        errors.append("template placeholders appear to remain unfilled")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("handoff", type=Path)
    args = parser.parse_args()

    try:
        text = args.handoff.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = validate(text)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Agent Relay handoff structure: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
