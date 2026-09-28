#!/usr/bin/env python3
"""Build presentation contexts with separate reference expectations."""

import argparse
import json
import tempfile
from copy import deepcopy
from pathlib import Path

from fixture_files import digest, write_json

HERE = Path(__file__).resolve().parent


def generate(destination):
    corpus = json.loads((HERE / "presentation_cases.json").read_text())
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Destination must be empty; existing files are never removed")
    reference = destination / "reference"
    reference.mkdir()
    write_json(reference / "expectations.json", {
        "shared": corpus["presentation_oracle"],
        "cases": {f"case-{index:02d}": {"source_id": case["id"], **case["oracle"]}
                  for index, case in enumerate(corpus["cases"], 1)},
    })
    manifest = {"schema_version": 1, "cases": []}
    for index, case in enumerate(corpus["cases"], 1):
        name = f"case-{index:02d}"
        directory = destination / "cases" / name
        directory.mkdir(parents=True)
        context = {**deepcopy(corpus["common"]), **deepcopy(case["context"])}
        context["source_coverage"] = {
            **corpus["common"]["source_coverage"], **case["context"].get("source_coverage", {})
        }
        context["claims"] = [deepcopy(corpus["finding_catalog"][key]) for key in case["findings"]]
        write_json(directory / "context.json", context)
        manifest["cases"].append({
            "id": name,
            "context": str(directory / "context.json"),
            "context_hash": digest(directory / "context.json"),
        })
    write_json(destination / "manifest.json", manifest)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or Path(tempfile.mkdtemp(prefix="pr-review-presentation-"))
    print(json.dumps(generate(output), indent=2))
