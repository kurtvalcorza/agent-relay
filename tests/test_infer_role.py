import unittest

from scripts.infer_role import infer_role


class RoleRouterTests(unittest.TestCase):
    def test_explicit_role_wins(self):
        route = infer_role("review and fix this", explicit_role="executor")
        self.assertEqual(route.inferred, "executor")
        self.assertEqual(route.sequence, ("executor",))
        self.assertEqual(route.review_lenses, ())

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

    def test_explicit_test_gap_intent_selects_lens(self):
        route = infer_role("Review this PR for test gaps")
        self.assertEqual(route.review_lenses, ("test-gap",))

    def test_spec_conformance_intent_selects_lens(self):
        route = infer_role("Review this implementation against the specification")
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

    def test_non_reviewer_serialization_preserves_historical_shape(self):
        route = infer_role("Implement this feature")
        self.assertEqual(
            set(route.to_dict()),
            {"inferred", "confidence", "reason", "sequence", "handoff_required"},
        )


if __name__ == "__main__":
    unittest.main()
