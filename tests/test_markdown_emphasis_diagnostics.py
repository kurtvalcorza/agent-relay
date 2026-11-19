"""R-12 (#18): inline Markdown emphasis in record fields fails closed with a named cause.

Fields are parsed as plain text. A key or value wrapped in emphasis
(`**Source:**`, `Source: **owner-grant**`, `_x_`, `__x__`) is still refused;
the refusal now names the emphasis instead of reporting a bare invalid or
missing field. None of these forms is accepted.
"""

import unittest

from scripts.validate_handoff import validate
from tests.test_protocol_v05 import BASE_PASS_V05, VALID_BRIEF

_PLAIN_SOURCE = "- Source: owner-grant"
_PLAIN_GRANTOR = "- Grantor: mission owner"
_HINT = "inline Markdown emphasis"


def _emphasis_errors(errors: list[str]) -> list[str]:
    return [error for error in errors if _HINT in error]


class BriefSourceEmphasisTests(unittest.TestCase):
    def assert_refused_for_emphasis(self, replacement: str) -> None:
        errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE, replacement))
        self.assertTrue(errors, f"{replacement!r} must not validate")
        self.assertTrue(_emphasis_errors(errors), errors)

    def test_control_plain_source_validates_clean(self):
        self.assertEqual(validate(VALID_BRIEF), [])

    def test_bold_key_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- **Source:** owner-grant")

    def test_bold_value_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- Source: **owner-grant**")

    def test_underscore_italic_key_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- _Source:_ owner-grant")

    def test_underscore_italic_value_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- Source: _owner-grant_")

    def test_double_underscore_key_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- __Source:__ owner-grant")

    def test_double_underscore_value_is_refused_naming_emphasis(self):
        self.assert_refused_for_emphasis("- Source: __owner-grant__")

    def test_emphasized_key_still_reports_missing_source(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE, "- __Source:__ owner-grant"))
        self.assertTrue(
            any("must declare an authority provenance source" in e for e in errors), errors
        )

    def test_plain_invalid_source_carries_no_emphasis_hint(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE, "- Source: implied"))
        self.assertIn("invalid authority provenance source: implied", errors)
        self.assertEqual(_emphasis_errors(errors), [])

    def test_plain_missing_source_carries_no_emphasis_hint(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE + "\n", ""))
        self.assertTrue(errors)
        self.assertEqual(_emphasis_errors(errors), [])


class BriefGrantFieldEmphasisTests(unittest.TestCase):
    def test_emphasized_grantor_key_is_refused_naming_emphasis(self):
        for replacement in ("- __Grantor:__ mission owner", "- _Grantor:_ mission owner"):
            with self.subTest(replacement=replacement):
                errors = validate(VALID_BRIEF.replace(_PLAIN_GRANTOR, replacement))
                self.assertTrue(any("Grantor" in e and _HINT in e for e in errors), errors)

    def test_missing_grantor_carries_no_emphasis_hint(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_GRANTOR + "\n", ""))
        self.assertTrue(any("Grantor" in e for e in errors), errors)
        self.assertEqual(_emphasis_errors(errors), [])


class PassSourceEmphasisTests(unittest.TestCase):
    def test_control_plain_pass_source_validates_clean(self):
        self.assertEqual(validate(BASE_PASS_V05 + "Authority provenance: none\n"), [])

    def test_emphasized_pass_source_is_refused_naming_emphasis(self):
        for line in (
            "**Authority provenance:** none",
            "Authority provenance: **none**",
            "Authority provenance: _none_",
            "Authority provenance: __none__",
        ):
            with self.subTest(line=line):
                errors = validate(BASE_PASS_V05 + line + "\n")
                self.assertTrue(_emphasis_errors(errors), errors)

    def test_emphasized_pass_grantor_key_is_refused_naming_emphasis(self):
        text = BASE_PASS_V05 + "\n".join([
            "Authority provenance: owner-grant",
            "__Grantor:__ mission owner",
            'Granted scope (verbatim): "fix the bug"',
            "Granted at: 2026-09-09",
        ])
        errors = validate(text)
        self.assertTrue(any("Grantor" in e and _HINT in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
