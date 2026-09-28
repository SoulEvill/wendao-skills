# PR review regression tooling

This is working developer tooling, not an empty placeholder. It contains offline
regression tests, synthetic Git repositories, and preparation/recording tools for
separately executed review exercises. It is not installed with the skill.

The deterministic tests verify seeded before/after behavior, negative controls,
guidance fixture construction, presentation inputs, frozen-input integrity, evidence
records, and result accounting. They do not call models or measure review accuracy.
No production-quality or cross-provider benchmark results are claimed.

## Run offline checks

From the repository root, with Python 3.11+, Git, and uv:

```sh
uv run python -m unittest discover -s eval/skill_review -v
```

The tests create disposable repositories and use explicit fixture Git identities.
They do not read model credentials or publish comments.

## Prepare a review exercise

```sh
uv run python eval/skill_review/runs.py prepare \
  --output /tmp/wendao-review-run --provider manual --case standard
```

Use a new empty output directory for each run. The manual provider supports an
interactive host such as Cursor. `--provider codex` and `--provider claude` prepare
CLI recipes after inspecting local help; preparation still does not run a model.

Preparation freezes the skill and inputs and writes a request, plan, and evidence
template. Give a fresh reviewer only the request and its allowed input paths.
Keep generators, test files, oracles, prior outputs, and grading instructions out
of reviewer context. A folder layout is not access isolation; enforce that boundary
through the host when claiming a blind evaluation.

Run the review separately with the chosen model, native effort, and tools.
Such runs may cost money and need authentication. Preserve its report, trace, and
companion evidence. An evaluator then fills the evidence template with semantic
judgments and evidence references; the harness does not determine whether those
judgments are true.

```sh
uv run python eval/skill_review/runs.py record \
  --run /tmp/wendao-review-run/runs/manual-standard \
  --evidence /tmp/evidence.json --report /tmp/report.txt --trace /tmp/trace.txt
uv run python eval/skill_review/runs.py summarize /tmp/wendao-review-run
```

Keep execution status separate from grading results. Blocked or unverified model
runs are not passes. Do not report prompt-tuning cases as held-out evaluation.
Record the skill revision, model and native effort where observable, exact source
revisions, topology, elapsed time, and relevant limits for meaningful comparisons.

## Fixtures

- `make_fixtures.py` / `oracles.json`: behavioral defects and negative controls.
- `make_guidance_fixtures.py`: repository-specific preferences and missing bindings.
- `make_presentation_fixtures.py` / `presentation_cases.json`: report and approval states.
- `runs.py` / `matrix.json`: preparation, evidence sealing, and execution accounting.

Historical reviews, local transcripts, and prior run artifacts are deliberately not
shipped. Read the current [validation status](../../docs/validation.md) for executed
package checks.
