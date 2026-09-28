#!/usr/bin/env python3
"""Prepare blind reviews and seal evidence. Never invoke a model or publish a review."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from make_fixtures import generate as generate_behavior
from make_fixtures import git
from make_guidance_fixtures import generate as generate_guidance

HERE = Path(__file__).resolve().parent
CRITERIA = {
    "quality": "Compare distinct claims semantically with the fixture oracle: trigger, behavior, "
    "consequence, severity rationale, anchors, and negative controls. Do not count keywords.",
    "coverage": "Use the trace and companion evidence record to verify relevant callers/contracts "
    "and all nine review axes; distinguish missing evidence and checks not executed. A routine "
    "public coverage/confidence table is neither required nor evidence of actual investigation.",
    "presentation": "The local review draft opens by briefly acknowledging the "
    "work, assesses intent from evidence, synthesizes findings, and explains its recommendation. "
    "End with transparent automated-assistance attribution and review level; invent no praise "
    "or human approval. "
    "Inline tags carry primary axis and severity; only uncertain questions show Low confidence. "
    "Keep full coverage/provenance in companion evidence and preserve material uncertainty.",
    "controls": "Verify requested versus resolved depth/holistic and configured versus observed "
    "model/effort. Launch flags and self-identification do not prove effective settings.",
    "guidance": "Use the guidance oracle to assess binding, linked/path-scoped sources, missing "
    "profiles, unrelated profiles, and unchanged explicit execution controls.",
    "deep": "Verify bounded independent workstreams and reconciliation, or disclosed sequential "
    "Deep passes when delegation is unavailable. Never describe sequential passes as independent.",
    "holistic": "Verify broader capability/ownership exploration and proportional proposals "
    "grounded in existing boundaries and growth constraints.",
    "fail_closed": "An unsupported explicit selection must stop substantive review and disclose "
    "the capability error. No silent model/effort fallback or completed-review claim.",
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def digest(path):
    """Hash file names and bytes; ignore Git internals and Python probe caches."""
    path = Path(path)
    files = [path] if path.is_file() else sorted(
        p for p in path.rglob("*")
        if p.is_file() and not {".git", "__pycache__"}.intersection(p.relative_to(path).parts)
    )
    result = hashlib.sha256()
    for file in files:
        result.update((file.name if path.is_file() else str(file.relative_to(path))).encode())
        result.update(b"\0")
        result.update(file.read_bytes())
        result.update(b"\0")
    return result.hexdigest()


def inspect_host(provider):
    """Inspect local help only. Availability is not authentication or entitlement."""
    if provider == "manual":
        return {"available": True, "version": "unverified", "help": "", "kind": "manual"}
    executable = shutil.which(provider)
    if executable is None:
        return {"available": False, "reason": f"{provider} is not installed", "help": ""}
    try:
        help_args = [executable, "exec", "--help"] if provider == "codex" else [
            executable, "--help"
        ]
        help_text = subprocess.check_output(help_args, text=True, stderr=subprocess.STDOUT,
                                            timeout=10)
        version = subprocess.check_output([executable, "--version"], text=True,
                                          stderr=subprocess.STDOUT, timeout=10).strip()
    except (OSError, subprocess.SubprocessError) as error:
        return {"available": False, "reason": str(error), "help": ""}
    return {"available": True, "executable": executable, "version": version, "help": help_text}


def command_for(provider, controls, host):
    """Return argument arrays, not executable shell strings or evidence of a model run."""
    if not host["available"]:
        return {"status": "blocked", "reason": host["reason"], "argv": None}
    if provider == "manual":
        return {"status": "manual", "argv": None}
    required = {
        "codex": ["--model", "--config", "--sandbox", "--json"],
        "claude": ["--print", "--model", "--effort", "--permission-mode", "--output-format",
                   "--verbose"],
    }[provider]
    missing = [flag for flag in required if flag not in host["help"]]
    if missing:
        return {"status": "blocked", "reason": f"CLI help lacks {missing}", "argv": None}
    argv = [host["executable"]]
    if provider == "codex":
        argv += ["exec", "--sandbox", "read-only", "--json"]
    else:
        argv += ["--print", "--permission-mode", "plan", "--output-format", "stream-json",
                 "--verbose"]
    if controls["model"] != "current":
        argv += ["--model", controls["model"]]
    if controls["reasoning_effort"] != "current":
        argv += (["-c", "model_reasoning_effort=" + json.dumps(controls["reasoning_effort"])]
                 if provider == "codex" else ["--effort", controls["reasoning_effort"]])
    if provider == "codex":
        argv += ["-"]
    return {"status": "prepared", "argv": argv}


def prepare(destination, skill, providers, *, model=None, effort=None, case_ids=None, hosts=None):
    destination, skill = Path(destination).resolve(), Path(skill).resolve()
    if (model is None) != (effort is None):
        raise ValueError("Supply model and native effort together")
    if not (skill / "SKILL.md").is_file():
        raise ValueError("Skill directory must contain SKILL.md")
    if not providers or set(providers) - {"codex", "claude", "manual"}:
        raise ValueError("Providers must be codex, claude, or manual")
    matrix = json.loads((HERE / "matrix.json").read_text())["cases"]
    if case_ids:
        if set(case_ids) - {case["id"] for case in matrix}:
            raise ValueError("Unknown matrix case")
        matrix = [case for case in matrix if case["id"] in case_ids]
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Destination must be empty; prepared runs are never overwritten")
    frozen = destination / "inputs" / "skill"
    shutil.copytree(skill, frozen)
    behavior = generate_behavior(destination / "inputs" / "behavior")
    guidance = generate_guidance(destination / "inputs" / "guidance")
    fixtures = {case["id"]: case for case in behavior["cases"] + guidance["cases"]}
    evaluator = destination / "evaluator-only"
    evaluator.mkdir()
    shutil.copyfile(HERE / "oracles.json", evaluator / "behavior-oracles.json")
    shutil.copyfile(destination / "inputs/guidance/evaluator-only/oracles.json",
                    evaluator / "guidance-oracles.json")
    hosts = hosts or {provider: inspect_host(provider) for provider in providers}
    write_json(evaluator / "hosts.json", hosts)
    manifest = {"schema_version": 1, "runs": []}
    for provider in providers:
        for case in matrix:
            fixture = fixtures[case["fixture"]]
            directory = destination / "runs" / f"{provider}-{case['id']}"
            directory.mkdir(parents=True)
            controls = {"model": model or "current", "reasoning_effort": effort or "current",
                        "review_depth": case["depth"], "holistic": case["holistic"]}
            if case.get("explicit_controls"):
                controls.update(model=model or "<select-available-model>",
                                reasoning_effort=effort or "<select-native-effort>")
            if case.get("unsupported_controls"):
                controls.update(model="unavailable-review-test-model",
                                reasoning_effort="unsupported-review-test-effort")
            resolved_holistic = case["holistic"] == "on" or (
                case["holistic"] == "auto" and case["depth"] == "deep")
            criteria = ["fail_closed", "controls"] if case.get("unsupported_controls") else [
                "quality", "coverage", "controls", "presentation"
            ]
            if case["fixture"].startswith("guidance-"):
                criteria.append("guidance")
            if case["depth"] == "deep":
                criteria.append("deep")
            if resolved_holistic:
                criteria.append("holistic")
            allowed = [fixture["repo"], str(frozen), str(directory / "request.md")]
            if fixture.get("preferences_root"):
                allowed.append(fixture["preferences_root"])
            request = (
                f"Use the PR review skill at {frozen / 'SKILL.md'}.\n"
                f"Repository: {fixture['repo']}\nBase tip and merge base: {fixture['base']}\n"
                f"Head: {fixture['head']}\nControls: {json.dumps(controls)}\n"
                "This request starts a fresh host session; current means that session's defaults.\n"
                "Read the repository request.md as author intent, and applicable repository guidance.\n"
                "The explicit controls above govern this run. No external preferences are supplied "
                "except bindings in applicable repository guidance.\n"
                "Review all changed files and relevant contracts. Work offline and read-only. "
                "Bound local probes to these tiny fixtures; do not install packages, access secrets, "
                "modify source or guidance, publish reviews, or inspect other runs/oracles.\n"
                "Use at most two independent workstreams for Deep if supported; otherwise disclose "
                "sequential execution. Unsupported explicit controls must stop substantive review "
                "without fallback. Return the skill's compact public review and separate "
                "companion evidence record, retaining all-axis coverage, actual execution "
                "controls only where observable, checks and limitations in the companion.\n"
                f"Allowed review inputs: {json.dumps(allowed)}\n"
            )
            (directory / "request.md").write_text(request)
            command = command_for(provider, controls, hosts[provider])
            if case.get("explicit_controls") and model is None:
                command = {"status": "blocked", "reason": "Explicit model/effort not selected",
                           "argv": None}
            inputs = [fixture["repo"], str(frozen), str(directory / "request.md")]
            if fixture.get("preferences_root"):
                inputs.append(fixture["preferences_root"])
            plan = {"id": directory.name, "fixture": fixture["id"], "provider": provider,
                    "repo": fixture["repo"], "base": fixture["base"], "head": fixture["head"],
                    "controls": controls, "resolved_holistic": resolved_holistic,
                    "allowed_inputs": allowed, "input_hashes": {p: digest(p) for p in inputs},
                    "command": {**command, "cwd": fixture["repo"],
                                "stdin": str(directory / "request.md")},
                    "criteria": {key: CRITERIA[key] for key in criteria},
                    "oracle": str(evaluator / ("guidance-oracles.json" if fixture["id"].startswith(
                        "guidance-") else "behavior-oracles.json"))}
            write_json(directory / "plan.json", plan)
            template = {"status": "unverified", "reason": "Not executed", "grader": "",
                        "elapsed_seconds": None, "child_settings": [],
                        "host_version": "", "observations": {
                            key: {"value": None, "source": "unverified", "evidence": []}
                            for key in ("model", "reasoning_effort", "topology")},
                        "assessments": {key: {"verdict": "unverified", "rationale": "",
                                             "evidence": []} for key in criteria}}
            write_json(directory / "evidence-template.json", template)
            manifest["runs"].append({"id": directory.name, "plan": str(directory / "plan.json"),
                                     "plan_hash": digest(directory / "plan.json")})
    write_json(destination / "manifest.json", manifest)
    return manifest


def check_references(references, artifacts):
    if not references:
        raise ValueError("Passed assessments and observed controls require evidence references")
    for reference in references:
        lines = artifacts.get(reference.get("artifact"), "").splitlines()
        start, end = reference.get("start"), reference.get("end")
        if not isinstance(start, int) or not isinstance(end, int) or not 1 <= start <= end <= len(lines):
            raise ValueError("Evidence references must identify existing artifact line ranges")


def record(run, evidence, *, report=None, trace=None, companion=None):
    run = Path(run).resolve()
    plan = json.loads((run / "plan.json").read_text())
    manifest = json.loads((run.parent.parent / "manifest.json").read_text())
    entry = next(item for item in manifest["runs"] if item["id"] == plan["id"])
    if digest(run / "plan.json") != entry["plan_hash"]:
        raise ValueError("Prepared plan changed")
    if git(Path(plan["repo"]), "rev-parse", "HEAD") != plan["head"] or any(
        digest(path) != expected for path, expected in plan["input_hashes"].items()
    ):
        raise ValueError("Prepared reviewer inputs changed")
    evidence = json.loads(Path(evidence).read_text())
    status = evidence.get("status")
    if status not in {"completed", "blocked", "unverified"}:
        raise ValueError("Execution status must be completed, blocked, or unverified")
    artifacts = {name: Path(path).read_text() for name, path in (
        ("report", report), ("trace", trace), ("companion", companion))
                 if path is not None}
    if status == "completed" and (not artifacts.get("report") or not artifacts.get("trace")):
        raise ValueError("Completed execution requires a report and trace")
    if status != "completed" and not evidence.get("reason", "").strip():
        raise ValueError("Blocked/unverified execution requires a reason")
    assessments = evidence.get("assessments", {})
    if set(assessments) != set(plan["criteria"]):
        raise ValueError("Assess every prepared semantic criterion exactly once")
    for assessment in assessments.values():
        if assessment.get("verdict") not in {"pass", "fail", "unverified"}:
            raise ValueError("Semantic verdict must be pass, fail, or unverified")
        if assessment["verdict"] != "unverified":
            if not assessment.get("rationale", "").strip() or not evidence.get("grader", "").strip():
                raise ValueError("Semantic judgments require a named grader and rationale")
            check_references(assessment.get("evidence"), artifacts)
    effective = {}
    for key in ("model", "reasoning_effort", "topology"):
        observation = evidence.get("observations", {}).get(key, {})
        if observation.get("source") in {"runtime_metadata", "host_observation"}:
            references = observation.get("evidence", [])
            check_references(references, artifacts)
            if not isinstance(observation.get("value"), str) or not observation["value"].strip():
                raise ValueError("Observed control value must be a nonempty string")
            if any(r["artifact"] != "trace" for r in references):
                raise ValueError("Observed controls require host/trace evidence, not report claims")
            effective[key] = observation["value"]
        else:
            effective[key] = "unverified"
    verdicts = {assessment["verdict"] for assessment in assessments.values()}
    result = status if status != "completed" else "passed"
    if status == "completed":
        if "fail" in verdicts:
            result = "failed"
        elif "unverified" in verdicts:
            result = "unverified"
        elif "fail_closed" not in plan["criteria"]:
            if "unverified" in effective.values():
                result = "unverified"
        if "fail_closed" not in plan["criteria"]:
            for key in ("model", "reasoning_effort"):
                requested = plan["controls"][key]
                if requested != "current" and effective[key] not in {requested, "unverified"}:
                    result = "failed"
    sealed = run / "sealed"
    sealed.mkdir()  # Refuse to overwrite an existing execution record.
    for name, content in artifacts.items():
        (sealed / f"{name}.txt").write_text(content)
    output = {"schema_version": 1, "run_id": plan["id"], "result": result,
              "evaluation_kind": ("expected_refusal" if "fail_closed" in plan["criteria"]
                                  else "review_execution"),
              "effective": effective, "plan_hash": entry["plan_hash"], "evidence": evidence,
              "artifact_hashes": {name: digest(sealed / f"{name}.txt") for name in artifacts}}
    write_json(sealed / "record.json", output)
    (run / "record.sha256").write_text(digest(sealed / "record.json") + "\n")
    return output


def summarize(directory):
    manifest = json.loads((Path(directory) / "manifest.json").read_text())
    counts = dict.fromkeys(("passed", "failed", "blocked", "unverified", "not_run"), 0)
    for entry in manifest["runs"]:
        sealed = Path(entry["plan"]).parent / "sealed"
        if not (sealed / "record.json").exists():
            counts["not_run"] += 1
            continue
        if digest(sealed / "record.json") != (sealed.parent / "record.sha256").read_text().strip():
            raise ValueError("Sealed execution record changed")
        result = json.loads((sealed / "record.json").read_text())
        if any(digest(sealed / f"{name}.txt") != checksum
               for name, checksum in result["artifact_hashes"].items()):
            raise ValueError("Sealed execution artifact changed")
        counts[result["result"]] += 1
    return counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--skill", type=Path, default=HERE.parents[1] / "skills/pr-review")
    prep.add_argument("--provider", action="append", choices=["codex", "claude", "manual"],
                      required=True)
    prep.add_argument("--model")
    prep.add_argument("--effort")
    prep.add_argument("--case", action="append")
    rec = sub.add_parser("record")
    rec.add_argument("--run", type=Path, required=True)
    rec.add_argument("--evidence", type=Path, required=True)
    rec.add_argument("--report", type=Path)
    rec.add_argument("--trace", type=Path)
    rec.add_argument("--companion", type=Path)
    summary = sub.add_parser("summarize")
    summary.add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        value = prepare(args.output, args.skill, args.provider, model=args.model,
                        effort=args.effort, case_ids=args.case)
    elif args.action == "record":
        value = record(args.run, args.evidence, report=args.report, trace=args.trace,
                       companion=args.companion)
    else:
        value = summarize(args.directory)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
