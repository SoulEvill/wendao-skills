#!/usr/bin/env python3
"""Build independent PR fixtures with scoped external guidance."""

import argparse
import json
import tempfile
from pathlib import Path

from make_fixtures import clean, git, write_files

BASE = {
    "README.md": """
        # Request metadata helpers

        The client package is shipped to downstream consumers. app.py is the maintained
        example. experimental/ contains disposable prototypes, not shipped client APIs.
    """,
    "client/__init__.py": "",
    "client/requests.py": """
        def build_request(url, *, timeout=10):
            return {"url": url, "timeout": timeout}
    """,
    "experimental/__init__.py": "",
    "experimental/delays.py": """
        def estimate_delay(*, timeout=10):
            return timeout * 2
    """,
    "app.py": """
        from client.requests import build_request
        from experimental.delays import estimate_delay


        def demo():
            return build_request("/orders", timeout=5), estimate_delay(timeout=5)
    """,
}

HEAD = {
    "client/requests.py": """
        def build_request(url, *, timeout_seconds=10):
            return {"url": url, "timeout": timeout_seconds}
    """,
    "experimental/delays.py": """
        def estimate_delay(*, timeout_seconds=10):
            return timeout_seconds * 2
    """,
    "app.py": """
        from client.requests import build_request
        from experimental.delays import estimate_delay


        def demo():
            return (
                build_request("/orders", timeout_seconds=5),
                estimate_delay(timeout_seconds=5),
            )
    """,
}

GUIDANCE = {
    "pr-review/preferences.md": """
        # Review preferences

        When recommending a correction, prefer a small local change that preserves the
        intended improvement. Explain a larger framework only when a local correction
        cannot satisfy the contract. I usually prefer Deep reviews for API changes.
    """,
    "pr-review/repo-a/instructions.md": """
        # Repo A review guidance

        For client/**, preserve existing public keyword arguments within the current
        release line. Follow the existing consumer contract in
        [client compatibility](client-compatibility.md).

        This requirement applies only to client/**. experimental/** APIs can change
        freely when maintained callers are updated.
    """,
    "pr-review/repo-a/client-compatibility.md": """
        # Client compatibility contract

        Client releases are deployed independently of downstream consumers. Existing
        deployments invoke build_request("/orders", timeout=5); consumers cannot all be
        upgraded when this package changes. Public keyword compatibility is required
        within this release line. A rename may introduce a new spelling only while
        retaining the old spelling. There is no coordinated breaking release in scope.
    """,
    "pr-review/repo-b/instructions.md": """
        # Repo B review guidance

        Breaking API changes are permitted for this repository, including public
        keyword argument renames in client/**. No backward compatibility layer is
        required when maintained callers are updated. experimental/** APIs may also
        change freely. Judge the new behavior and maintained callers on their merits.
    """,
    "pr-review/neighbor/instructions.md": """
        # Neighbor repository review guidance

        All public functions in this repository must accept a keyword named
        audit_context, because the neighbor runtime passes it on every invocation.
        This requirement applies only to the neighbor repository.
    """,
}

REQUEST = """
    Use the PR review skill to review the pull request from HEAD^ to HEAD in this
    repository. Use Standard depth, holistic off, and the current model and effort.
    Return the review locally. Read-only Python probes are permitted; do not modify
    reviewed files or publish a review.

    PR: Make timeout units explicit
    Rename the timeout keyword to timeout_seconds and update the maintained caller.
    The numerical timeout values and returned metadata are unchanged.
"""

CASES = (
    ("guidance-a", "repo-a"),
    ("guidance-b", "repo-b"),
    ("guidance-unbound", None),
    ("guidance-missing", "unavailable-profile"),
)

ORACLES = {
    "guidance-a": {
        "required": [
            "Load general preferences and the repo-a profile selected by unchanged AGENTS.md.",
            "Resolve client-compatibility.md relative to the repo-a instruction document.",
            "Report the client keyword rename as a supported compatibility defect: existing "
            "build_request('/orders', timeout=5) callers raise TypeError at head only.",
            "Prefer a small local correction to preserve the required existing keyword contract.",
        ],
        "forbidden": [
            "Apply client compatibility requirements to experimental/delays.py.",
            "Load repo-b or neighbor guidance, or require audit_context.",
            "Change the user's Standard depth to Deep based on the general preference.",
        ],
    },
    "guidance-b": {
        "required": [
            "Load general preferences and repo-b guidance only.",
            "Recognize that maintained callers work and intentional breaking APIs are permitted.",
        ],
        "forbidden": [
            "Report the timeout keyword rename as a backward compatibility defect.",
            "Load repo-a supplemental guidance or neighbor guidance.",
            "Change the user's Standard depth to Deep.",
        ],
    },
    "guidance-unbound": {
        "required": [
            "Use normal repository evidence without selecting external profiles.",
            "Keep any unverified external compatibility concern separate from confirmed defects.",
        ],
        "forbidden": [
            "Guess or load sibling preference roots or a profile based on repository name.",
            "Claim the repo-a compatibility contract applies.",
        ],
    },
    "guidance-missing": {
        "required": [
            "Load general preferences, disclose the unavailable configured repo profile, "
            "and continue the review where possible.",
            "Preserve Standard depth despite the general preference for Deep.",
        ],
        "forbidden": [
            "Substitute repo-a, repo-b, or neighbor for the unavailable profile.",
            "Claim repo-specific guidance was successfully loaded.",
        ],
    },
}


def generate(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Destination must be empty; existing files are never removed")
    preferences = destination / "preferences"
    write_files(preferences, GUIDANCE)
    metadata = {"schema_version": 1, "cases": []}
    for name, key in CASES:
        repo = destination / "repositories" / name
        repo.mkdir(parents=True)
        instructions = clean("""
            # Repository instructions

            Review the exact proposed revisions and inspect maintained callers. Read-only
            Python probes are permitted. Do not modify reviewed files or publish reviews.
        """)
        if key is not None:
            instructions += (
                "\nFor the PR review skill, use these repository guidance bindings:\n"
                "- preferences_root: ../../preferences\n"
                f"- preferences_repo: {key}\n"
            )
        git(repo, "init", "--initial-branch=main")
        write_files(repo, {**BASE, "AGENTS.md": instructions, "request.md": REQUEST})
        git(repo, "add", ".")
        git(repo, "commit", "-m", "Baseline")
        base = git(repo, "rev-parse", "HEAD")
        git(repo, "switch", "-c", "change")
        write_files(repo, HEAD)
        git(repo, "add", ".")
        git(repo, "commit", "-m", "Make timeout units explicit")
        inputs = [str(repo)]
        if key is not None:
            inputs.extend(
                [
                    str(preferences / "pr-review/preferences.md"),
                    str(preferences / "pr-review" / key / "instructions.md"),
                ]
            )
            if key == "repo-a":
                inputs.append(str(preferences / "pr-review/repo-a/client-compatibility.md"))
        metadata["cases"].append(
            {
                "id": name,
                "repo": str(repo),
                "base": base,
                "head": git(repo, "rev-parse", "HEAD"),
                "request": str(repo / "request.md"),
                "preferences_root": str(preferences) if key is not None else None,
                "preferences_repo": key,
                "reviewer_allowed_inputs": inputs,
            }
        )
    (destination / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    oracle = destination / "reference" / "expectations.json"
    oracle.parent.mkdir()
    oracle.write_text(json.dumps(ORACLES, indent=2) + "\n")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="An empty output directory")
    arguments = parser.parse_args()
    output = arguments.output or Path(tempfile.mkdtemp(prefix="pr-review-guidance-"))
    print(json.dumps(generate(output), indent=2))
