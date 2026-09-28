"""Verify supplied presentation scenarios and isolation, not model-rendered wording."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from make_presentation_fixtures import generate
from fixture_files import digest


class PresentationFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="presentation-fixture-tests-")
        cls.root = Path(cls.workspace.name)
        with patch("subprocess.check_output", side_effect=AssertionError("No host execution")):
            cls.manifest = generate(cls.root / "cases")
        cls.oracles = json.loads((cls.root / "cases/reference/expectations.json").read_text())
        cls.cases = {
            cls.oracles["cases"][case["id"]]["source_id"]: json.loads(
                Path(case["context"]).read_text()
            ) for case in cls.manifest["cases"]
        }

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def test_contexts_keep_reference_answers_separate(self):
        self.assertEqual(len(self.manifest["cases"]), 11)
        oracle = self.root / "cases/reference/expectations.json"
        for case in self.manifest["cases"]:
            self.assertFalse(oracle.is_relative_to(Path(case["context"]).parent))
            context = json.loads(Path(case["context"]).read_text())
            self.assertNotIn("oracle", context)
            self.assertNotIn("recommendation", context)
            self.assertNotIn("confirmed_root_causes", context)
            self.assertEqual(len(context["source_coverage"]), 9)
            self.assertEqual(digest(case["context"]), case["context_hash"])

    def test_peer_snapshots_preserve_effective_state_instead_of_latest_comment(self):
        active = self.cases["active-peer-request"]["peer_state"]
        self.assertEqual(active["effective_reviews"][0]["state"], "REQUEST_CHANGES")
        self.assertEqual([review["state"] for review in active["history"]],
                         ["REQUEST_CHANGES", "COMMENT", "PENDING"])
        self.assertTrue(active["effective_reviews"][0]["outdated_anchors"])
        superseded = self.cases["superseded-peer-request"]["peer_state"]
        self.assertEqual(superseded["effective_reviews"][0]["state"], "APPROVED")
        self.assertEqual(superseded["history"][0]["reviewer"],
                         superseded["effective_reviews"][0]["reviewer"])
        dismissed = self.cases["dismissed-peer-request"]["peer_state"]
        self.assertEqual(dismissed["effective_reviews"], [])
        self.assertTrue(dismissed["history"][0]["dismissal_recorded"])
        unknown = self.cases["unknown-peer-state"]["peer_state"]
        self.assertEqual(unknown["retrieval"], "unavailable")
        self.assertIsNone(unknown["effective_reviews"])

    def test_duplicate_claim_and_independent_defects_have_discriminating_evidence(self):
        independent = self.cases["independent-material-p2"]["claims"]
        duplicate = self.cases["duplicate-p2-claims"]["claims"]
        self.assertEqual(len(independent), len(duplicate))
        self.assertEqual({claim["severity"] for claim in independent + duplicate}, {"P2"})
        self.assertNotEqual(independent[0]["anchor"], independent[1]["anchor"])
        self.assertEqual(duplicate[0]["anchor"], duplicate[1]["anchor"])
        self.assertEqual(duplicate[0]["remedy"], duplicate[1]["remedy"])
        self.assertNotEqual(duplicate[0]["axis"], duplicate[1]["axis"])
        oracles = {item["source_id"]: item for item in self.oracles["cases"].values()}
        self.assertEqual(oracles["independent-material-p2"]["confirmed_root_causes"], 2)
        self.assertEqual(oracles["duplicate-p2-claims"]["confirmed_root_causes"], 1)
        self.assertEqual(set(oracles["duplicate-p2-claims"]["recommendation"]),
                         {"approve", "request_changes"})

    def test_uncertainty_and_publication_authority_are_not_erased(self):
        medium = self.cases["medium-confidence-assumption"]
        self.assertEqual(medium["claims"][0]["confidence"], "medium")
        self.assertTrue(medium["claims"][0]["missing_evidence"])
        self.assertEqual(medium["source_coverage"]["reliability_and_operations"], "partial")
        low = self.cases["low-confidence-question-only"]["claims"][0]
        self.assertEqual((low["severity"], low["confidence"]), ("P1", "low"))
        merged = self.cases["merged-comment-preview"]
        self.assertEqual(merged["pr_state"], "merged")
        self.assertEqual(merged["authorization"]["permitted_preview_event"], "COMMENT")
        self.assertFalse(merged["authorization"]["post_review"])
        self.assertTrue(all(not case["authorization"]["post_review"]
                            for case in self.cases.values()))

    def test_contexts_are_reproducible_and_existing_outputs_are_preserved(self):
        repeated = generate(self.root / "repeated")
        self.assertEqual([case["context_hash"] for case in repeated["cases"]],
                         [case["context_hash"] for case in self.manifest["cases"]])
        with self.assertRaises(ValueError):
            generate(self.root / "cases")


if __name__ == "__main__":
    unittest.main()
