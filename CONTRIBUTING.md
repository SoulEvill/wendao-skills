# Contributing

Each installable skill lives at `skills/<name>/` or `skills/<group>/<name>/`.
Include `SKILL.md` with `name` and `description` frontmatter and a `README.md` for
people. Names start with `wd-`, match their folders, and are unique across the catalog.
A group has no `SKILL.md`; deeper nesting and skills containing other skills are not supported.
Use `references/`, `scripts/`, or `assets/` only when the workflow needs them.
Every runtime local reference must resolve inside that skill folder.

Add a one-line entry linking the skill's README from the root catalog. Keep
instructions specific to the workflow and portable across clients. Host model
selection, effort settings, delegation, authentication, and publishing permission
are separate capabilities.
Follow the [script conventions](AGENTS.md#scripts-inside-skills) for bundled scripts
and published tools.

## Checks

```sh
uv sync --locked
uv run python scripts/validate_package.py
uv run python -m unittest discover -s tests/package -v
uv run python -m unittest discover -s tests/pr_review -v
bash tests/package.sh
```

The package check discovers every skill and uses the real skills CLI to install and
compare it with its source in a temporary project for Cursor, Claude Code, and Codex.
It does not install into your global skill folders, run a model, or publish a review.

For changes to review decisions, use a relevant fixture or a bounded manual review
exercise. Fixture tests verify the example inputs, not the model's review quality.
Keep expected answers out of reviewer input and record what was actually checked.
See [test instructions](tests/README.md).

## Publishing

Users install from this repository's default branch. Review changes, run checks,
then merge. Commits identify versions: install with `#<full-commit-sha>` to pin or
roll back; updates preserve that ref. Add a Git tag when a named reference is useful.
There is no separate npm publishing step. Native plugin marketplaces are an optional
future distribution channel; installation uses the standard skills CLI.
