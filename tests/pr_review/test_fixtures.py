"""Behavior checks for fixture seeds, kept outside the reviewer's repositories."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from make_fixtures import generate


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workspace = tempfile.TemporaryDirectory(prefix="wd-pr-review-fixture-tests-")
        cls.manifest = generate(Path(cls.workspace.name) / "cases")
        cls.cases = {case["id"]: case for case in cls.manifest["cases"]}

    @classmethod
    def tearDownClass(cls):
        cls.workspace.cleanup()

    def run_at(self, case_id, revision, program, replacements=None):
        case = self.cases[case_id]
        archive = subprocess.check_output(
            ["git", "archive", "--format=zip", case[revision]], cwd=case["repo"]
        )
        with tempfile.TemporaryDirectory(prefix="wd-pr-review-snapshot-") as directory:
            # Archives contain only files created by the fixture generator.
            zipfile.ZipFile(io.BytesIO(archive)).extractall(directory)
            for relative, content in (replacements or {}).items():
                (Path(directory) / relative).write_text(content)
            environment = {**os.environ, "PYTHONPATH": "", "PYTHONNOUSERSITE": "1"}
            output = subprocess.check_output(
                [sys.executable, "-c", program], cwd=directory, env=environment, text=True
            )
            return json.loads(output)

    def export(self, revision, rows, enforce_limit=False):
        return self.run_at(
            "batch-export",
            revision,
            f"""
import json
from jobs.order_export import export_customer
rows = {rows!r}
class Client:
    def __init__(self):
        self.calls = []
    def list_orders(self, customer_id, cursor=None):
        self.calls.append(cursor)
        start = cursor or 0
        end = start + 100
        return {{"items": rows[start:end], "next_cursor": end if end < len(rows) else None}}
class Writer:
    def __init__(self):
        self.batches = []
    def write_batch(self, batch):
        if {enforce_limit!r} and len(batch) > 50:
            raise ValueError("writer batch exceeds 50 rows")
        self.batches.append(batch)
client, writer = Client(), Writer()
try:
    export_customer(client, "customer-1", writer)
    error = None
except ValueError as exc:
    error = str(exc)
print(json.dumps({{"ids": [r["id"] for batch in writer.batches for r in batch],
                  "sizes": [len(batch) for batch in writer.batches],
                  "calls": client.calls, "error": error}}))
""",
        )

    def test_batch_export_excludes_restricted_and_pending_orders_only_in_base(self):
        rows = [
            {"id": "restricted", "status": "ready", "restricted": True},
            {"id": "pending", "status": "pending", "restricted": False},
            {"id": "allowed", "status": "ready", "restricted": False},
        ]
        self.assertEqual(self.export("base", rows)["ids"], ["allowed"])
        self.assertEqual(self.export("head", rows)["ids"], ["restricted", "pending", "allowed"])

    def test_batch_export_loses_pages_only_in_head(self):
        rows = [{"id": i, "status": "ready", "restricted": False} for i in range(125)]
        self.assertEqual(self.export("base", rows)["ids"], list(range(125)))
        self.assertEqual(self.export("head", rows)["ids"], list(range(100)))

    def test_batch_export_respects_writer_capacity_only_in_base(self):
        rows = [{"id": i, "status": "ready", "restricted": False} for i in range(75)]
        base = self.export("base", rows, enforce_limit=True)
        self.assertIsNone(base["error"])
        self.assertEqual(base["sizes"], [50, 25])
        self.assertEqual(
            self.export("head", rows, enforce_limit=True)["error"], "writer batch exceeds 50 rows"
        )

    def test_migration_preserves_outputs_and_is_independent_of_runtime(self):
        program = """
import json, runpy
module = runpy.run_path("migrations/20240915_customer_keys.py")
rows = [{"id": i, "name": name} for i, name in enumerate(
    ["  Acme East  ", "Straße", "CAFÉ", "İSTANBUL", "  "])]
print(json.dumps(module["migrate"](rows)))
"""
        base = self.run_at("migration-snapshot", "base", program)
        head = self.run_at("migration-snapshot", "head", program)
        self.assertEqual(base, head)
        self.assertEqual(
            [row["key"] for row in head], ["acme_east", "strasse", "café", "i̇stanbul", ""]
        )
        self.assertEqual(
            head,
            self.run_at(
                "migration-snapshot",
                "head",
                program,
                {
                    "shared/customer_keys.py": "raise RuntimeError('Current runtime is unavailable')\n"
                },
            ),
        )

    def test_runbook_enables_anonymous_requests_on_public_unauthenticated_edge(self):
        program = """
import json, shlex
from pathlib import Path
from service.security import response_status
environment = {}
for line in Path("docs/production-runbook.md").read_text().splitlines():
    tokens = shlex.split(line)
    if tokens and tokens[0] == "export":
        key, value = tokens[1].split("=", 1)
        environment[key] = value
print(json.dumps({"edge": json.loads(Path("deploy/edge.json").read_text()),
    "anonymous": response_status(environment, has_valid_token=False),
    "authenticated": response_status(environment, has_valid_token=True)}))
"""
        base = self.run_at("runbook-auth", "base", program)
        head = self.run_at("runbook-auth", "head", program)
        self.assertEqual(base["anonymous"], 401)
        self.assertEqual(head["anonymous"], 204)
        self.assertEqual(base["authenticated"], head["authenticated"])
        self.assertTrue(head["edge"]["public"])
        self.assertEqual(head["edge"]["authentication"], "none")

    def test_missing_contract_leaves_both_schema_hypotheses_possible(self):
        program = """
import json
from integration.orders import extract_orders
rows = [{"id": "order-1"}]
results = []
for payload in ({"items": rows}, {"data": {"items": rows}}):
    try:
        results.append(extract_orders(payload))
    except KeyError:
        results.append("KeyError")
print(json.dumps(results))
"""
        self.assertEqual(
            self.run_at("provider-envelope", "base", program), [[{"id": "order-1"}], "KeyError"]
        )
        self.assertEqual(
            self.run_at("provider-envelope", "head", program), ["KeyError", [{"id": "order-1"}]]
        )

    def test_commits_are_reproducible_and_review_inputs_are_clean(self):
        duplicate = generate(Path(self.workspace.name) / "duplicate")
        for original, repeated in zip(self.manifest["cases"], duplicate["cases"], strict=True):
            self.assertEqual(
                (original["base"], original["head"]), (repeated["base"], repeated["head"])
            )
            self.assertEqual(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=original["repo"], text=True
                ),
                "",
            )
            files = subprocess.check_output(
                ["git", "ls-files"], cwd=original["repo"], text=True
            ).splitlines()
            self.assertIn("request.md", files)
            self.assertNotIn("oracles.json", files)
            self.assertNotIn("test_fixtures.py", files)


if __name__ == "__main__":
    unittest.main()
