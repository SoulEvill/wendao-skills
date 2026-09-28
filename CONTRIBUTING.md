# Contributing

Each installable skill lives at `skills/<name>/SKILL.md` with required `name`
and `description` frontmatter. The name matches its folder. Use `references/`,
`scripts/`, or `assets/` only when the workflow needs them. Every runtime local
reference must resolve inside that skill folder.

Add a one-line entry to the README catalog. Keep instructions specific to the
workflow and portable across clients. Host model selection, effort settings,
delegation, authentication, and publishing permission are separate capabilities.

## Checks

```sh
uv sync --locked
uv run python scripts/validate_package.py
uv run python -m unittest discover -s tests/pr_review -v
bash tests/package.sh
```

The package check uses the real skills CLI to install into a temporary project for
Cursor, Claude Code, and Codex. It does not install into your global skill folders,
run a model, or publish a review.

For changes to review decisions, use a relevant fixture or a bounded manual review
exercise. Fixture tests verify the example inputs, not the model's review quality.
Keep expected answers out of reviewer input and record what was actually checked.
See [test instructions](tests/README.md).

## Publishing

Users install from this repository's default branch. Review changes, run checks,
then merge. Add a Git tag when a stable reference is useful. There is no separate
npm publishing step. Native plugin marketplaces are an optional future distribution
channel; the current installation contract is the standard skills CLI.
