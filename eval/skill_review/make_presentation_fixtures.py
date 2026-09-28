#!/usr/bin/env python3
"""Prepare isolated post-review presentation requests, without executing a reviewer."""

import argparse
import json
import shutil
import tempfile
from copy import deepcopy
from pathlib import Path

from runs import digest, write_json

HERE = Path(__file__).resolve().parent


def generate(destination, skill):
    corpus = json.loads((HERE / "presentation_cases.json").read_text())
    destination, skill = Path(destination).resolve(), Path(skill).resolve()
    if not (skill / "SKILL.md").is_file():
        raise ValueError("Skill must contain SKILL.md")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Destination must be empty; existing files are never removed")
    frozen = destination / "skill"
    shutil.copytree(skill, frozen)
    evaluator = destination / "evaluator-only"
    evaluator.mkdir()
    write_json(evaluator / "oracles.json", {
        "shared": corpus["presentation_oracle"],
        "cases": {f"case-{index:02d}": {"source_id": case["id"], **case["oracle"]}
                  for index, case in enumerate(corpus["cases"], 1)},
    })
    manifest = {"schema_version": 1, "skill_hash": digest(frozen), "cases": []}
    for index, case in enumerate(corpus["cases"], 1):
        name = f"case-{index:02d}"
        directory = destination / "reviewer" / name
        directory.mkdir(parents=True)
        context = {**deepcopy(corpus["common"]), **deepcopy(case["context"])}
        context["source_coverage"] = {
            **corpus["common"]["source_coverage"], **case["context"].get("source_coverage", {})
        }
        context["claims"] = [deepcopy(corpus["finding_catalog"][key]) for key in case["findings"]]
        write_json(directory / "context.json", context)
        request = (
            f"Use the PR review skill at {frozen / 'SKILL.md'}.\n"
            "This is a bounded presentation-stage regression using synthetic, sealed review "
            "evidence. Produce the review from context.json in this directory. Treat its source "
            "facts and provider effective-review snapshot as given; preserve unknowns. This does "
            "not ask you to discover new defects or infer missing provider evidence.\n"
            "Follow the skill's current public format and recommendation rules. Prepare the "
            "compact overall review and any inline comments, with a separate companion record "
            "for source coverage and provenance. Do not claim to have run the supplied checks.\n"
            "Write public-review.md and companion-record.md in this directory, or return those "
            "two separately labeled artifacts if file writing is unavailable. Do not edit "
            "context.json or the skill. Do not browse, call models, delegate, inspect sibling "
            "cases/oracles, or post any review. A recommendation is not publishing permission.\n"
            f"Allowed inputs: {directory / 'context.json'} and {frozen}.\n"
        )
        (directory / "request.md").write_text(request)
        manifest["cases"].append({
            "id": name, "request": str(directory / "request.md"),
            "context": str(directory / "context.json"),
            "allowed_inputs": [str(directory / "request.md"), str(directory / "context.json"),
                               str(frozen)],
            "context_hash": digest(directory / "context.json"),
            "request_hash": digest(directory / "request.md"),
        })
    write_json(evaluator / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--skill", type=Path, default=HERE.parents[1] / "skills/pr-review")
    args = parser.parse_args()
    output = args.output or Path(tempfile.mkdtemp(prefix="pr-review-presentation-"))
    print(json.dumps(generate(output, args.skill), indent=2))
