import unittest

from scripts.infer_role import infer_role


class DeferredRouterGapTests(unittest.TestCase):
    def test_review_command_after_sentence_boundary_is_kept(self):
        route = infer_role("Implement the patch. Review for regressions.")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.sequence, ("reviewer", "integrator", "builder", "verifier"))
        self.assertEqual(route.review_lenses, ("regression",))

    def test_named_lens_prefix_applies_to_audit(self):
        cases = {
            "Run a security audit": ("security",),
            "Conduct a reliability audit": ("reliability",),
            "Do a test-gap audit": ("test-gap",),
        }
        for task, expected in cases.items():
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.inferred, "reviewer")
                self.assertEqual(route.review_lenses, expected)

    def test_boundary_vocabulary_as_feature_object_keeps_build_intent(self):
        for task in (
            "Implement read-only mode",
            "Build a read-only request handler",
            "Implement support for no mutations",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.inferred, "builder")
                self.assertEqual(route.sequence, ("builder",))

    def test_whole_task_prohibition_still_suppresses_builder(self):
        for task in (
            "Read-only mode. Implement the patch.",
            "Implement the patch. No mutations.",
            "Implement the patch, but do not modify anything.",
            "Please work in read-only mode and inspect the parser.",
            "Review the parser in read-only mode and fix what you find",
            "Review the parser, no mutations, then fix it",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertNotEqual(route.inferred, "builder")
                self.assertNotIn("builder", route.sequence)

    def test_test_authoring_is_build_intent(self):
        for task in (
            "Write tests for the parser edge cases",
            "Write an adversarial test suite for the parser",
            "Create a regression test for the retry path",
        ):
            with self.subTest(task=task):
                route = infer_role(task)
                self.assertEqual(route.inferred, "builder")
                self.assertEqual(route.sequence, ("builder",))

    def test_audit_log_subject_is_not_a_lens_prefix(self):
        route = infer_role("Review the audit log")
        self.assertEqual(route.inferred, "reviewer")
        self.assertEqual(route.review_lenses, ("standard",))


if __name__ == "__main__":
    unittest.main()
