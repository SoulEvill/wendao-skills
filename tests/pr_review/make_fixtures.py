#!/usr/bin/env python3
"""Build small, independent repositories for blind PR review exercises."""

import argparse
import json
import os
import subprocess
import tempfile
import textwrap
from pathlib import Path


def clean(value):
    return textwrap.dedent(value).lstrip()


CASES = {
    "batch-export": {
        "request": """
            Review the pull request from HEAD^ to HEAD. Inspect relevant repository context.

            PR: Reduce batch export overhead
            The synchronous batch worker now obtains its rows directly from the order
            client. The API already scopes results to the customer, so this preserves
            customer isolation and export completeness. One write reduces overhead for
            our small accounts. The web export route is unchanged.
        """,
        "base": {
            "README.md": "Order exports include every ready, nonrestricted order. Writers accept at most 50 rows per call. API pages contain at most 100 rows.\n",
            "shared/__init__.py": "",
            "jobs/__init__.py": "",
            "web/__init__.py": "",
            "shared/customer_policy.py": """
                def exportable(row):
                    return row["status"] == "ready" and not row["restricted"]
            """,
            "shared/exporting.py": """
                from shared.customer_policy import exportable


                def customer_batches(client, customer_id):
                    cursor, batch = None, []
                    while True:
                        page = client.list_orders(customer_id, cursor=cursor)
                        for row in page["items"]:
                            if exportable(row):
                                batch.append(row)
                                if len(batch) == 50:
                                    yield batch
                                    batch = []
                        cursor = page["next_cursor"]
                        if cursor is None:
                            break
                    if batch:
                        yield batch
            """,
            "web/export.py": """
                from shared.exporting import customer_batches


                def stream_export(client, customer_id, writer):
                    for batch in customer_batches(client, customer_id):
                        writer.write_batch(batch)
            """,
            "jobs/order_export.py": """
                from shared.exporting import customer_batches


                def export_customer(client, customer_id, writer):
                    for batch in customer_batches(client, customer_id):
                        writer.write_batch(batch)
            """,
        },
        "head": {
            "jobs/order_export.py": """
                def export_customer(client, customer_id, writer):
                    page = client.list_orders(customer_id)
                    writer.write_batch(list(page["items"]))
            """,
        },
    },
    "migration-snapshot": {
        "request": """
            Review the pull request from HEAD^ to HEAD. Inspect relevant repository context.

            PR: Freeze the historical customer key transform
            Migration 20240915 is replayed years later, independently of the application.
            Inline its tiny normalization function so changing the shared runtime helper
            cannot alter historical output. This duplication is intentional. The snapshot
            must retain the exact current transform, including Unicode case folding.
        """,
        "base": {
            "README.md": "Runtime code lives in shared/. Historical migration transforms must remain reproducible when runtime helpers evolve.\n",
            "shared/__init__.py": "",
            "shared/customer_keys.py": """
                def normalize(value):
                    return value.strip().casefold().replace(" ", "_")
            """,
            "migrations/README.md": "Migration files are immutable transformation snapshots and must run without importing the current application. Small local copies are permitted for this purpose.\n",
            "migrations/20240915_customer_keys.py": """
                from shared.customer_keys import normalize


                def migrate(rows):
                    return [{**row, "key": normalize(row["name"])} for row in rows]
            """,
        },
        "head": {
            "migrations/20240915_customer_keys.py": """
                # Frozen snapshot: runtime normalization may change after this migration.
                def normalize(value):
                    return value.strip().casefold().replace(" ", "_")


                def migrate(rows):
                    return [{**row, "key": normalize(row["name"])} for row in rows]
            """,
        },
    },
    "runbook-auth": {
        "request": """
            Review the pull request from HEAD^ to HEAD. Inspect relevant repository context.

            PR: Correct production maintenance startup instructions
            This documentation-only change eliminates the authorization errors operators
            see when bringing up the maintenance endpoint behind our public edge proxy.
            No service code changes are needed because the edge handles access.
        """,
        "base": {
            "README.md": "The maintenance API handles destructive account operations. The deployment edge forwards public internet traffic directly to this service.\n",
            "deploy/edge.json": '{"public": true, "authentication": "none", "upstream": "maintenance:8080"}\n',
            "service/__init__.py": "",
            "service/security.py": """
                def response_status(environment, has_valid_token):
                    required = environment.get("AUTH_REQUIRED", "true") == "true"
                    return 401 if required and not has_valid_token else 204
            """,
            "docs/production-runbook.md": """
                # Maintenance service startup

                Run behind the edge configured in deploy/edge.json:

                ```sh
                export BIND_HOST=0.0.0.0
                export AUTH_REQUIRED=true
                maintenance-api --port 8080
                ```

                Supply an operator token when calling maintenance endpoints.
            """,
        },
        "head": {
            "docs/production-runbook.md": """
                # Maintenance service startup

                Run behind the edge configured in deploy/edge.json:

                ```sh
                export BIND_HOST=0.0.0.0
                export AUTH_REQUIRED=false
                maintenance-api --port 8080
                ```

                The edge handles access, so operator tokens are optional here.
            """,
        },
    },
    "provider-envelope": {
        "request": """
            Review the pull request from HEAD^ to HEAD using the available checkout.

            PR: Consume the provider's v3 order envelope
            The provider told us by email that the order list moved into a data envelope.
            Update the response extractor accordingly. Their contract and integration
            environment require partner credentials unavailable in this review sandbox.
            The email and real provider responses are not included in this repository.
        """,
        "base": {
            "README.md": "Provider response schema is defined externally at https://partner.example/contracts/orders-v3.json. No contract snapshot, credentials, or recorded provider responses are available in this checkout. Downstream consumers require a list of order objects.\n",
            "integration/__init__.py": "",
            "integration/orders.py": """
                def extract_orders(response):
                    return response["items"]
            """,
        },
        "head": {
            "integration/orders.py": """
                def extract_orders(response):
                    return response["data"]["items"]
            """,
        },
    },
}


def git(repo, *args):
    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": "2024-09-16T12:00:00Z",
        "GIT_COMMITTER_DATE": "2024-09-16T12:00:00Z",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    return subprocess.check_output(
        [
            "git",
            "-c",
            "user.name=Fixture Builder",
            "-c",
            "user.email=fixtures@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            *args,
        ],
        cwd=repo,
        env=env,
        text=True,
        stderr=subprocess.PIPE,
    ).strip()


def write_files(repo, files):
    for relative, content in files.items():
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(clean(content), encoding="utf-8")


def generate(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Destination must be empty; existing files are never removed")
    metadata = {"schema_version": 1, "cases": []}
    for name, case in CASES.items():
        repo = destination / name
        repo.mkdir()
        git(repo, "init", "--initial-branch=main")
        write_files(
            repo,
            {
                **case["base"],
                "request.md": case["request"],
                "AGENTS.md": "Review the PR using repository evidence. Follow relevant callers and shared helpers outside the diff. Do not modify files.\n",
            },
        )
        git(repo, "add", ".")
        git(repo, "commit", "-m", "Baseline")
        base = git(repo, "rev-parse", "HEAD")
        git(repo, "switch", "-c", "change")
        write_files(repo, case["head"])
        git(repo, "add", ".")
        git(repo, "commit", "-m", "Proposed change")
        metadata["cases"].append(
            {
                "id": name,
                "repo": str(repo),
                "base": base,
                "head": git(repo, "rev-parse", "HEAD"),
                "request": str(repo / "request.md"),
            }
        )
    (destination / "manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    return metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="An empty directory; defaults to a fresh temporary directory"
    )
    arguments = parser.parse_args()
    output = arguments.output or Path(tempfile.mkdtemp(prefix="pr-review-fixtures-"))
    print(json.dumps(generate(output), indent=2))
