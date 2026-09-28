"""Verify external-guidance fixture behavior without judging model review quality."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from make_fixtures import git
from make_guidance_fixtures import generate


class GuidanceFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="pr-review-guidance-tests-")
        cls.destination = Path(cls.workspace.name) / "cases"
        cls.manifest = generate(cls.destination)
        cls.cases = {case["id"]: case for case in cls.manifest["cases"]}

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def behavior(self, case, revision):
        archive = subprocess.check_output(
            ["git", "archive", "--format=zip", case[revision]], cwd=case["repo"]
        )
        with tempfile.TemporaryDirectory(prefix="pr-review-guidance-snapshot-") as directory:
            # Only generated, known-safe fixture paths occur in this archive.
            zipfile.ZipFile(io.BytesIO(archive)).extractall(directory)
            environment = {**os.environ, "PYTHONPATH": "", "PYTHONNOUSERSITE": "1"}
            program = """
import json
from app import demo
from client.requests import build_request
from experimental.delays import estimate_delay
result = {"demo": demo()}
for name, function, args in (
    ("client_old_keyword", build_request, ("/orders",)),
    ("experimental_old_keyword", estimate_delay, ()),
):
    try:
        result[name] = function(*args, timeout=5)
    except TypeError as error:
        result[name] = {"error": type(error).__name__, "message": str(error)}
print(json.dumps(result))
"""
            return json.loads(
                subprocess.check_output(
                    [sys.executable, "-B", "-c", program],
                    cwd=directory,
                    env=environment,
                    text=True,
                )
            )

    def test_old_keywords_break_but_maintained_behavior_does_not_change(self):
        for case in self.cases.values():
            with self.subTest(case=case["id"]):
                base, head = (self.behavior(case, revision) for revision in ("base", "head"))
                self.assertEqual(base["demo"], head["demo"])
                self.assertEqual(base["client_old_keyword"], {"url": "/orders", "timeout": 5})
                self.assertEqual(base["experimental_old_keyword"], 10)
                for name in ("client_old_keyword", "experimental_old_keyword"):
                    self.assertEqual(head[name]["error"], "TypeError")
                    self.assertIn("timeout", head[name]["message"])

    def test_same_diff_with_unchanged_guidance_bindings(self):
        diffs = []
        for case in self.cases.values():
            repo = Path(case["repo"])
            diffs.append(git(repo, "diff", case["base"], case["head"]))
            self.assertEqual(
                git(repo, "show", f"{case['base']}:AGENTS.md"),
                git(repo, "show", f"{case['head']}:AGENTS.md"),
            )
            self.assertEqual(git(repo, "status", "--porcelain"), "")
            self.assertEqual(
                set(git(repo, "diff", "--name-only", case["base"], case["head"]).splitlines()),
                {"app.py", "client/requests.py", "experimental/delays.py"},
            )
        self.assertEqual(len(set(diffs)), 1)

    def test_context_is_external_and_oracle_is_not_a_reviewer_input(self):
        oracle = self.destination / "evaluator-only/oracles.json"
        self.assertTrue(oracle.is_file())
        for case in self.cases.values():
            repo = Path(case["repo"])
            self.assertNotIn("oracles", git(repo, "ls-files"))
            self.assertNotIn("preferences/", git(repo, "ls-files"))
            for allowed in case["reviewer_allowed_inputs"]:
                self.assertFalse(oracle.is_relative_to(Path(allowed)))
            if case["preferences_root"]:
                self.assertEqual(
                    (repo / "../../preferences").resolve(), Path(case["preferences_root"])
                )
        unbound = self.cases["guidance-unbound"]
        self.assertIsNone(unbound["preferences_repo"])
        self.assertEqual(unbound["reviewer_allowed_inputs"], [unbound["repo"]])
        self.assertNotIn("preferences_", (Path(unbound["repo"]) / "AGENTS.md").read_text())
        missing = self.cases["guidance-missing"]
        self.assertFalse(
            (Path(missing["preferences_root"]) / "pr-review/unavailable-profile").exists()
        )

    def test_fixtures_are_reproducible_and_non_destructive(self):
        repeated = generate(Path(self.workspace.name) / "repeated")
        for original, duplicate in zip(self.manifest["cases"], repeated["cases"], strict=True):
            self.assertEqual(original["base"], duplicate["base"])
            self.assertEqual(original["head"], duplicate["head"])
        with self.assertRaises(ValueError):
            generate(self.destination)


if __name__ == "__main__":
    unittest.main()
