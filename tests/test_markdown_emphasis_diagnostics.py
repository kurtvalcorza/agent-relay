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


class EmphasisOnlyValueTests(unittest.TestCase):
    """Owner ruling on #18: a value of only emphasis markers counts as empty.

    Deliberately breaking: `- **Grantor:**` and similar validated clean before
    because list-marker stripping left `**` as the value, which was not an
    absent token. They now fail closed.
    """

    _EMPTY_FORMS = ("**", "__", "*", "_", "** **", "****")
    _GRANT_LINES = (
        "- Grantor: mission owner",
        '- Granted scope (verbatim): "fix the state-write symlink window"',
        "- Granted at: 2026-09-05, against snapshot e6c6874",
    )

    def test_bold_grantor_key_with_no_value_is_refused(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_GRANTOR, "- **Grantor:**"))
        self.assertTrue(any("requires a named grantor" in e and _HINT in e for e in errors), errors)

    def test_emphasis_only_brief_grant_values_are_refused_as_empty(self):
        for line in self._GRANT_LINES:
            key = line.split(":", 1)[0] + ":"
            field = key[2:].rstrip(":").split(" (")[0]
            for form in self._EMPTY_FORMS:
                with self.subTest(line=line, form=form):
                    errors = validate(VALID_BRIEF.replace(line, f"{key} {form}"))
                    self.assertTrue(
                        any("requires" in e and f"({field}" in e and _HINT in e for e in errors),
                        errors,
                    )

    def test_emphasis_only_brief_source_is_refused_as_missing(self):
        for form in self._EMPTY_FORMS:
            with self.subTest(form=form):
                errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE, f"- Source: {form}"))
                self.assertTrue(
                    any("must declare an authority provenance source" in e and _HINT in e
                        for e in errors),
                    errors,
                )

    def test_emphasis_only_pass_values_are_refused(self):
        grant = [
            "Authority provenance: owner-grant",
            "Grantor: mission owner",
            'Granted scope (verbatim): "fix the bug"',
            "Granted at: 2026-09-09",
        ]
        for index, line in enumerate(grant):
            key = line.split(":", 1)[0] + ":"
            for form in self._EMPTY_FORMS:
                with self.subTest(line=line, form=form):
                    lines = list(grant)
                    lines[index] = f"{key} {form}"
                    errors = validate(BASE_PASS_V05 + "\n".join(lines))
                    self.assertTrue(errors, "emphasis-only value must not validate")
                    self.assertTrue(_emphasis_errors(errors), errors)

    def test_bold_pass_grantor_key_with_no_value_is_refused(self):
        text = BASE_PASS_V05 + "\n".join([
            "Authority provenance: owner-grant",
            "- **Grantor:**",
            'Granted scope (verbatim): "fix the bug"',
            "Granted at: 2026-09-09",
        ])
        errors = validate(text)
        self.assertTrue(any("requires a named grantor" in e and _HINT in e for e in errors), errors)

    def test_emphasized_pass_authority_key_is_refused_not_ignored(self):
        for line in (
            "__Authority provenance:__ owner-grant",
            "_Authority provenance:_ none",
            "- __Authority provenance:__ none",
        ):
            with self.subTest(line=line):
                errors = validate(BASE_PASS_V05 + line + "\n")
                self.assertTrue(
                    any("pass must declare an authority provenance source" in e and _HINT in e
                        for e in errors),
                    errors,
                )

    def test_pass_without_authority_provenance_still_validates(self):
        self.assertEqual(validate(BASE_PASS_V05), [])

    def test_real_grant_values_keep_current_behaviour(self):
        # Plain real values validate; emphasized real grant text is still read
        # as text (unchanged), while emphasized sources stay refused with the hint.
        self.assertEqual(validate(VALID_BRIEF), [])
        self.assertEqual(
            validate(VALID_BRIEF.replace(_PLAIN_GRANTOR, "- Grantor: **mission owner**")), []
        )
        self.assertEqual(
            validate(VALID_BRIEF.replace(_PLAIN_GRANTOR, "- **Grantor:** mission owner")), []
        )
        errors = validate(VALID_BRIEF.replace(_PLAIN_SOURCE, "- Source: **owner-grant**"))
        self.assertTrue(
            any("invalid authority provenance source" in e and _HINT in e for e in errors), errors
        )

    def test_plain_absent_grant_value_carries_no_emphasis_hint(self):
        errors = validate(VALID_BRIEF.replace(_PLAIN_GRANTOR, "- Grantor: none"))
        self.assertTrue(any("requires a named grantor" in e for e in errors), errors)
        self.assertEqual(_emphasis_errors(errors), [])


if __name__ == "__main__":
    unittest.main()
