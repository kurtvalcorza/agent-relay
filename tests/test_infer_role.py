import unittest

from scripts.infer_role import infer_role


class RoleRouterTests(unittest.TestCase):
    def test_explicit_role_wins(self):
        route = infer_role("review and fix this", explicit_role="executor")
        self.assertEqual(route.inferred, "executor")
        self.assertEqual(route.sequence, ("executor",))

    def test_review_and_fix_is_a_sequence(self):
        route = infer_role("Review this PR and fix what you find")
        self.assertEqual(route.sequence, ("reviewer", "integrator", "builder", "verifier"))

    def test_signoff_requires_verifier(self):
        route = infer_role("Review this PR and sign off if clean")
        self.assertEqual(route.sequence, ("reviewer", "verifier"))

    def test_unavailable_local_environment_triggers_handoff(self):
        route = infer_role(
            "Run the CUDA tests locally and verify the result",
            environment_available=False,
        )
        self.assertEqual(route.inferred, "executor")
        self.assertTrue(route.handoff_required)
        self.assertIn("verifier", route.sequence)

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

    def test_ambiguous_default_is_non_mutating_review(self):
        route = infer_role("continue")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.confidence, "low")


if __name__ == "__main__":
    unittest.main()
