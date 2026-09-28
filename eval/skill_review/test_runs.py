"""Deterministic harness checks. These tests do not validate a live model/provider."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from runs import command_for, digest, prepare, record, summarize, write_json

SKILL = Path(__file__).resolve().parents[2] / "skills/pr-review"
HOSTS = {
    "codex": {"available": True, "executable": "codex", "version": "test-double",
              "help": "--model --config --sandbox --json"},
    "claude": {"available": True, "executable": "claude", "version": "test-double",
               "help": "--print --model --effort --permission-mode --output-format --verbose"},
    "manual": {"available": True, "version": "test-double", "help": ""},
}


class PreparedRunTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="review-runs-test-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)

    def prepare(self, cases=("standard",), providers=("manual",), **kwargs):
        self.destination = self.root / "prepared"
        return prepare(self.destination, SKILL, list(providers), case_ids=list(cases),
                       hosts=HOSTS, **kwargs)

    def evidence(self, run, *, status="completed", source="host_observation"):
        data = json.loads((run / "evidence-template.json").read_text())
        data.update(status=status, reason="Bounded test double", grader="unit-test-only")
        reference = [{"artifact": "trace", "start": 1, "end": 1}]
        for assessment in data["assessments"].values():
            assessment.update(verdict="pass", rationale="Synthetic harness assertion only",
                              evidence=reference)
        for key, value in (("model", "test-model"), ("reasoning_effort", "test-effort"),
                           ("topology", "integrated")):
            data["observations"][key] = {"value": value, "source": source, "evidence": reference}
        path = self.root / "evidence.json"
        write_json(path, data)
        report, trace = self.root / "report.txt", self.root / "trace.txt"
        report.write_text("Synthetic report, not a live review.\n")
        trace.write_text("Synthetic host record, not a live provider.\n")
        return path, report, trace

    def test_matrix_prepares_controls_without_leaking_oracles(self):
        manifest = self.prepare(
            ("standard", "deep", "deep-without-holistic", "standard-with-holistic",
             "guidance-bound", "guidance-unbound", "guidance-missing"), ("codex", "claude")
        )
        self.assertEqual(len(manifest["runs"]), 14)
        for entry in manifest["runs"]:
            plan_path = Path(entry["plan"])
            plan = json.loads(plan_path.read_text())
            self.assertEqual(digest(plan_path), entry["plan_hash"])
            self.assertIsNotNone(plan["command"]["argv"])
            self.assertNotIn(plan["oracle"], plan["allowed_inputs"])
            self.assertFalse(any(Path(plan["oracle"]).is_relative_to(Path(p))
                                 for p in plan["allowed_inputs"]))
            request = (plan_path.parent / "request.md").read_text()
            self.assertNotIn("expected_findings", request)
            self.assertNotIn("writer-capacity", request)
            if entry["id"].endswith("-deep"):
                self.assertTrue(plan["resolved_holistic"])
                self.assertIn("deep", plan["criteria"])
                self.assertIn("holistic", plan["criteria"])
            if entry["id"].endswith("deep-without-holistic"):
                self.assertFalse(plan["resolved_holistic"])
                self.assertNotIn("holistic", plan["criteria"])
            if plan["fixture"] == "guidance-unbound":
                self.assertFalse(any(p.endswith("/preferences") for p in plan["allowed_inputs"]))
            if plan["fixture"] == "guidance-missing":
                root = next(p for p in plan["allowed_inputs"] if p.endswith("/preferences"))
                self.assertFalse((Path(root) / "pr-review/unavailable-profile").exists())
        self.assertEqual(summarize(self.destination)["not_run"], 14)

    def test_explicit_flags_are_native_separate_arguments_without_fallback(self):
        controls = {"model": "exact-model", "reasoning_effort": "high"}
        codex = command_for("codex", controls, HOSTS["codex"])["argv"]
        claude = command_for("claude", controls, HOSTS["claude"])["argv"]
        self.assertEqual(codex[codex.index("--model") + 1], "exact-model")
        self.assertEqual(codex[codex.index("-c") + 1], 'model_reasoning_effort="high"')
        self.assertEqual(claude[claude.index("--effort") + 1], "high")
        self.assertNotIn("--fallback-model", claude)
        self.assertEqual(codex[codex.index("--sandbox") + 1], "read-only")
        self.assertEqual(claude[claude.index("--permission-mode") + 1], "plan")
        current = {"model": "current", "reasoning_effort": "current"}
        self.assertNotIn("--model", command_for("codex", current, HOSTS["codex"])["argv"])
        for host in ({"available": False, "reason": "not installed"},
                     {"available": True, "help": "--model"}):
            blocked = command_for("codex", controls, host)
            self.assertEqual(blocked["status"], "blocked")
            self.assertIsNone(blocked["argv"])

    def test_missing_explicit_selection_is_blocked_and_output_is_not_overwritten(self):
        manifest = self.prepare(("explicit-controls",))
        plan = json.loads(Path(manifest["runs"][0]["plan"]).read_text())
        self.assertEqual(plan["command"]["status"], "blocked")
        with self.assertRaises(ValueError):
            self.prepare()
        with self.assertRaises(ValueError):
            prepare(self.root / "other", SKILL, ["manual"], model="test", hosts=HOSTS)

    def test_pass_requires_observed_controls_and_seals_artifacts_once(self):
        manifest = self.prepare()
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        result = record(run, evidence, report=report, trace=trace)
        self.assertEqual(result["result"], "passed")
        self.assertEqual(summarize(self.destination)["passed"], 1)
        with self.assertRaises(FileExistsError):
            record(run, evidence, report=report, trace=trace)
        (run / "sealed/trace.txt").write_text("Changed\n")
        with self.assertRaisesRegex(ValueError, "artifact changed"):
            summarize(self.destination)

    def test_launch_configuration_does_not_prove_effective_settings(self):
        manifest = self.prepare(("explicit-controls",), model="test-model", effort="test-effort")
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run, source="configured")
        result = record(run, evidence, report=report, trace=trace)
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(set(result["effective"].values()), {"unverified"})

    def test_explicit_observed_fallback_fails_even_with_passing_assessments(self):
        manifest = self.prepare(("explicit-controls",), model="required-model", effort="high")
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        self.assertEqual(record(run, evidence, report=report, trace=trace)["result"], "failed")

    def test_selected_settings_apply_equally_to_standard_and_deep(self):
        manifest = self.prepare(("standard", "deep", "unsupported-controls"),
                                model="selected-model", effort="selected-effort")
        for entry in manifest["runs"]:
            plan = json.loads(Path(entry["plan"]).read_text())
            if entry["id"].endswith("unsupported-controls"):
                self.assertEqual(plan["controls"]["model"], "unavailable-review-test-model")
            else:
                self.assertEqual(plan["controls"]["model"], "selected-model")
                self.assertEqual(plan["controls"]["reasoning_effort"], "selected-effort")

    def test_unexecuted_template_cannot_pass(self):
        manifest = self.prepare()
        run = Path(manifest["runs"][0]["plan"]).parent
        result = record(run, run / "evidence-template.json")
        self.assertEqual(result["result"], "unverified")
        self.assertEqual(summarize(self.destination)["passed"], 0)
        data = json.loads((run / "sealed/record.json").read_text())
        data["result"] = "passed"
        write_json(run / "sealed/record.json", data)
        with self.assertRaisesRegex(ValueError, "record changed"):
            summarize(self.destination)

    def test_blocked_capability_case_never_counts_as_provider_pass(self):
        manifest = self.prepare(("unsupported-controls",))
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run, status="blocked", source="unverified")
        result = record(run, evidence, report=report, trace=trace)
        self.assertEqual(result["result"], "blocked")
        self.assertEqual(result["evidence"]["assessments"]["fail_closed"]["verdict"], "pass")
        self.assertEqual(summarize(self.destination)["passed"], 0)

    def test_expected_reviewer_refusal_passes_without_fabricated_requested_controls(self):
        manifest = self.prepare(("unsupported-controls",))
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run, source="unverified")
        result = record(run, evidence, report=report, trace=trace)
        self.assertEqual(result["result"], "passed")
        self.assertEqual(result["evaluation_kind"], "expected_refusal")
        self.assertEqual(set(result["effective"].values()), {"unverified"})

    def test_substantive_fallback_review_fails_negative_control(self):
        manifest = self.prepare(("unsupported-controls",))
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        data = json.loads(evidence.read_text())
        data["assessments"]["fail_closed"].update(
            verdict="fail", rationale="Reviewer continued substantive review after substitution"
        )
        write_json(evidence, data)
        self.assertEqual(record(run, evidence, report=report, trace=trace)["result"], "failed")

    def test_no_pass_without_real_referenced_artifact_lines(self):
        manifest = self.prepare()
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        with self.assertRaisesRegex(ValueError, "report and trace"):
            record(run, evidence, report=report)
        data = json.loads(evidence.read_text())
        for refs in ([], [{"artifact": "trace", "start": 1, "end": 200}]):
            data["assessments"]["quality"]["evidence"] = refs
            write_json(evidence, data)
            with self.assertRaises(ValueError):
                record(run, evidence, report=report, trace=trace)
        data["assessments"]["quality"]["evidence"] = [
            {"artifact": "trace", "start": 1, "end": 1}
        ]
        data["observations"]["model"]["evidence"] = [
            {"artifact": "report", "start": 1, "end": 1}
        ]
        write_json(evidence, data)
        with self.assertRaisesRegex(ValueError, "not report claims"):
            record(run, evidence, report=report, trace=trace)

    def test_changed_frozen_inputs_cannot_be_recorded(self):
        manifest = self.prepare()
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        skill = self.destination / "inputs/skill/SKILL.md"
        skill.write_text(skill.read_text() + "\nChanged instructions\n")
        with self.assertRaisesRegex(ValueError, "reviewer inputs changed"):
            record(run, evidence, report=report, trace=trace)

    def test_modified_plan_is_rejected(self):
        manifest = self.prepare()
        path = Path(manifest["runs"][0]["plan"])
        evidence, report, trace = self.evidence(path.parent)
        data = json.loads(path.read_text())
        data["controls"]["review_depth"] = "deep"
        write_json(path, data)
        with self.assertRaisesRegex(ValueError, "plan changed"):
            record(path.parent, evidence, report=report, trace=trace)

    def test_cli_prepares_and_summarizes_without_model_execution(self):
        script = Path(__file__).with_name("runs.py")
        destination = self.root / "cli"
        output = subprocess.check_output(
            [sys.executable, str(script), "prepare", "--output", str(destination),
             "--skill", str(SKILL), "--provider", "manual", "--case", "standard"], text=True
        )
        self.assertEqual(len(json.loads(output)["runs"]), 1)
        output = subprocess.check_output(
            [sys.executable, str(script), "summarize", str(destination)], text=True
        )
        self.assertEqual(json.loads(output),
                         {"passed": 0, "failed": 0, "blocked": 0, "unverified": 0, "not_run": 1})

    def test_companion_evidence_is_referenced_and_sealed_separately(self):
        manifest = self.prepare()
        run = Path(manifest["runs"][0]["plan"]).parent
        evidence, report, trace = self.evidence(run)
        companion = self.root / "companion.md"
        companion.write_text("Synthetic coverage and provenance record.\n")
        data = json.loads(evidence.read_text())
        data["assessments"]["coverage"]["evidence"] = [
            {"artifact": "companion", "start": 1, "end": 1}
        ]
        write_json(evidence, data)
        result = record(run, evidence, report=report, trace=trace, companion=companion)
        self.assertEqual(result["result"], "passed")
        self.assertEqual((run / "sealed/companion.txt").read_text(), companion.read_text())
        self.assertEqual(result["artifact_hashes"]["companion"],
                         digest(run / "sealed/companion.txt"))


if __name__ == "__main__":
    unittest.main()
