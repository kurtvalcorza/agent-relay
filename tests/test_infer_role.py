import unittest

from scripts.infer_role import infer_role


class RoleRouterTests(unittest.TestCase):
    def test_explicit_role_wins(self):
        route = infer_role("review and fix this", explicit_role="executor")
        self.assertEqual(route.inferred, "executor")
        self.assertEqual(route.sequence, ("executor",))
        self.assertEqual(route.review_lenses, ())

    def test_explicit_non_reviewer_rejects_review_lens(self):
        with self.assertRaises(ValueError):
            infer_role(
                "Implement the feature",
                explicit_role="builder",
                explicit_review_lenses=["security"],
            )

    def test_explicit_reviewer_composes_with_lens(self):
        route = infer_role(
            "Act as Reviewer and do a security review",
            explicit_role="reviewer",
        )
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("security",))

    def test_explicit_review_lens_overrides_inference(self):
        route = infer_role(
            "Review this implementation",
            explicit_role="reviewer",
            explicit_review_lenses=["design"],
        )
        self.assertEqual(route.review_lenses, ("design",))

    def test_explicit_readiness_lens_routes_through_verifier_integrator(self):
        route = infer_role(
            "Review this PR",
            explicit_review_lenses=["readiness"],
        )
        self.assertEqual(route.review_lenses, ("readiness",))
        self.assertEqual(route.sequence, ("reviewer", "verifier", "integrator"))

    def test_explicit_reviewer_readiness_lens_keeps_checkpoint(self):
        route = infer_role(
            "Review this PR",
            explicit_role="reviewer",
            explicit_review_lenses=["readiness"],
        )
        self.assertEqual(route.sequence, ("reviewer", "verifier", "integrator"))

    def test_review_and_fix_is_a_sequence(self):
        route = infer_role("Review this PR and fix what you find")
        self.assertEqual(route.sequence, ("reviewer", "integrator", "builder", "verifier"))
        self.assertEqual(route.review_lenses, ("standard",))

    def test_design_review_fix_and_signoff_is_a_sequence(self):
        route = infer_role("Adversarially review this design, fix blockers, then sign off")
        self.assertEqual(route.sequence, ("reviewer", "integrator", "builder", "verifier"))
        self.assertEqual(route.review_lenses, ("design",))

    def test_readiness_review_fix_returns_to_integrator(self):
        route = infer_role("Assess merge readiness, fix blockers, then verify")
        self.assertEqual(
            route.sequence,
            ("reviewer", "integrator", "builder", "verifier", "integrator"),
        )
        self.assertEqual(route.review_lenses, ("readiness",))

    def test_signoff_requires_verifier(self):
        route = infer_role("Review this PR and sign off if clean")
        self.assertEqual(route.sequence, ("reviewer", "verifier"))
        self.assertEqual(route.review_lenses, ("standard",))

    def test_unavailable_local_environment_triggers_handoff(self):
        route = infer_role(
            "Run the CUDA tests locally and verify the result",
            environment_available=False,
        )
        self.assertEqual(route.inferred, "executor")
        self.assertTrue(route.handoff_required)
        self.assertIn("verifier", route.sequence)

    def test_review_needing_unavailable_environment_preserves_reviewer(self):
        route = infer_role(
            "Security review this and run the scanner locally",
            environment_available=False,
        )
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.sequence[:2], ("reviewer", "executor"))
        self.assertEqual(route.review_lenses, ("security",))
        self.assertTrue(route.handoff_required)

    def test_open_finding_before_fix_routes_through_integrator(self):
        route = infer_role("Fix the reported defect", unresolved_finding=True)
        self.assertEqual(route.sequence, ("integrator", "builder", "verifier"))

    def test_completed_but_unverified_routes_to_verifier(self):
        route = infer_role(
            "continue",
            implementation_complete=True,
            verification_missing=True,
        )
        self.assertEqual(route.sequence, ("verifier",))

    def test_plain_build_request(self):
        route = infer_role("Implement support for a new handoff field")
        self.assertEqual(route.sequence, ("builder",))
        self.assertNotIn("review_lenses", route.to_dict())

    def test_command_style_build_verbs_still_mutate(self):
        for task in (
            "Build the feature",
            "Can you update the spec?",
            "Review this PR and update the docs",
            "Please revise the document",
            "Then refactor the parser",
            "Fix a bug",
            "Fix a typo",
            "Fix CI",
            "fix flaky tests",
            "Fix everything",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertIn("builder", route.sequence)

    def test_scoped_prohibition_does_not_cancel_authorized_mutation(self):
        for task in (
            "Update the documentation, but do not edit source files",
            "Refactor the parser without changing behavior",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.sequence, ("builder",))

    def test_global_prohibition_suppresses_mutation(self):
        route = infer_role("Read-only review: fix the bug")
        self.assertNotIn("builder", route.sequence)

    def test_artifact_nouns_do_not_authorize_mutation(self):
        for task in (
            "Review the build",
            "Review the update",
            "Review the refactor",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.sequence, ("reviewer",))
                self.assertNotIn("builder", route.sequence)

    def test_review_subject_nouns_do_not_activate_reviewer(self):
        for task in (
            "Implement the review lens",
            "Update the review template",
            "Add tests for the review validator",
            "Implement the readiness review lens",
            "Fix the bug in assets/REVIEW.md",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.sequence, ("builder",))
                self.assertEqual(route.review_lenses, ())

    def test_ambiguous_default_is_non_mutating_standard_review(self):
        route = infer_role("continue")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.confidence, "low")
        self.assertEqual(route.review_lenses, ("standard",))

    def test_design_review_is_distinct_from_baseline_adversarial_posture(self):
        route = infer_role("Adversarially review the design and challenge the assumptions")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("design",))

    def test_security_subject_does_not_select_security_lens(self):
        route = infer_role("Review the security module")
        self.assertEqual(route.review_lenses, ("standard",))

    def test_security_fix_noun_does_not_authorize_mutation(self):
        route = infer_role("Review the security fix (read-only, do not edit)")
        self.assertEqual(route.sequence, ("reviewer",))
        self.assertEqual(route.review_lenses, ("standard",))
        self.assertNotIn("builder", route.sequence)

    def test_unambiguous_security_review_selects_security_lens(self):
        route = infer_role("Run a security review of this PR")
        self.assertEqual(route.review_lenses, ("security",))

    def test_reliability_subject_does_not_select_reliability_lens(self):
        route = infer_role("Review the reliability module")
        self.assertEqual(route.review_lenses, ("standard",))

    def test_reliability_intent_without_review_keyword_activates_reviewer(self):
        route = infer_role("Assess retry and recovery behavior")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("reliability",))

    def test_explicit_test_gap_intent_selects_lens(self):
        route = infer_role("Review this PR for test gaps")
        self.assertEqual(route.review_lenses, ("test-gap",))

    def test_test_gap_intent_without_review_keyword_activates_reviewer(self):
        route = infer_role("Identify the test gaps")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("test-gap",))

    def test_spec_conformance_intent_selects_lens(self):
        route = infer_role("Review this implementation against the specification")
        self.assertEqual(route.review_lenses, ("spec-conformance",))

    def test_spec_intent_without_review_keyword_activates_reviewer(self):
        route = infer_role("Check this implementation against the specification")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("spec-conformance",))

    def test_regression_intent_selects_lens(self):
        route = infer_role("Do a regression review of this change")
        self.assertEqual(route.review_lenses, ("regression",))

    def test_readiness_review_preserves_integrator_decision(self):
        route = infer_role("Assess merge readiness for this PR")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("readiness",))
        self.assertEqual(route.sequence, ("reviewer", "verifier", "integrator"))

    def test_direct_ready_to_merge_remains_verifier_integrator(self):
        route = infer_role("Is this ready to merge?")
        self.assertEqual(route.inferred, "verifier")
        self.assertEqual(route.sequence, ("verifier", "integrator"))
        self.assertEqual(route.review_lenses, ())

    def test_named_review_survives_verification_signal(self):
        route = infer_role("Review test gaps and confirm the tests really run")
        self.assertEqual(route.sequence, ("reviewer", "verifier"))
        self.assertEqual(route.review_lenses, ("test-gap",))

    def test_review_lenses_can_compose_when_intent_is_explicit(self):
        route = infer_role("Do a design review and review this for security")
        self.assertEqual(route.review_lenses, ("design", "security"))

    def test_compound_prefix_lenses_are_preserved(self):
        route = infer_role("Do a security and reliability review of this PR")
        self.assertEqual(route.review_lenses, ("security", "reliability"))

    def test_compound_suffix_lenses_are_preserved(self):
        route = infer_role("Review this PR for security and reliability")
        self.assertEqual(route.review_lenses, ("security", "reliability"))

    def test_standard_is_removed_when_composed_with_specific_lens(self):
        route = infer_role(
            "Review this PR",
            explicit_review_lenses=["standard", "security"],
        )
        self.assertEqual(route.review_lenses, ("security",))

    def test_non_reviewer_serialization_preserves_historical_shape(self):
        route = infer_role("Implement this feature")
        self.assertEqual(
            set(route.to_dict()),
            {"inferred", "confidence", "reason", "sequence", "handoff_required"},
        )


class ReviewRoundTwoRegressionTests(unittest.TestCase):
    """Regressions for findings raised against head 139b58a."""

    def test_oxford_comma_prefix_lens_list_preserves_every_lens(self):
        route = infer_role("Do a design, security, and reliability review")
        self.assertEqual(
            route.review_lenses, ("design", "security", "reliability")
        )

    def test_oxford_comma_suffix_lens_list_preserves_every_lens(self):
        route = infer_role(
            "Review this PR for design, security, and reliability"
        )
        self.assertEqual(
            route.review_lenses, ("design", "security", "reliability")
        )

    def test_security_lens_does_not_leak_from_a_later_repair_clause(self):
        route = infer_role("Audit the implementation, then fix the security bug")
        self.assertNotIn("security", route.review_lenses)
        self.assertEqual(
            route.sequence,
            ("reviewer", "integrator", "builder", "verifier"),
        )

    def test_audit_clause_still_selects_its_own_security_lens(self):
        self.assertEqual(
            infer_role("Audit the trust boundary").review_lenses, ("security",)
        )

    def test_mutation_command_after_a_period_is_authorized_repair(self):
        route = infer_role("Review this PR. Fix what you find.")
        self.assertEqual(
            route.sequence,
            ("reviewer", "integrator", "builder", "verifier"),
        )

    def test_mutation_command_after_a_newline_is_authorized_repair(self):
        route = infer_role("Review this PR\nFix what you find")
        self.assertEqual(
            route.sequence,
            ("reviewer", "integrator", "builder", "verifier"),
        )

    def test_scoped_prohibition_routing_is_clause_order_independent(self):
        for task in (
            "Update the docs, but do not edit source files",
            "Do not edit source files, but update the docs",
            "Refactor the parser, but do not modify the tests",
            "Do not modify the tests, but refactor the parser",
        ):
            with self.subTest(task=task):
                self.assertEqual(infer_role(task).inferred, "builder")

    def test_whole_task_prohibition_still_suppresses_builder(self):
        for task in (
            "Do not edit anything. Review this PR.",
            "This task is read-only. Fix nothing.",
            "Review this PR. No mutations.",
            "Do not change anything\nReview the parser",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.inferred, "reviewer")
                self.assertNotIn("builder", route.sequence)


if __name__ == "__main__":
    unittest.main()
