# Contributor guidance

This repository contains portable agent skills. Keep runtime instructions under
`skills/` and developer-only checks and fixtures under `tests/`.

- Use `skills/<name>/` or `skills/<group>/<name>/`, with `SKILL.md` and a human-facing
  `README.md` in each skill. Groups have no `SKILL.md`; allow only one group level,
  no nested skills, and unique skill names across the catalog.
- Prefix skill names with `wd-` and match each skill's folder and frontmatter name.
- Keep skill folders self-contained with focused relative references.
- Keep shared instructions independent of one client, model, or PR provider.
- Put host-specific controls in references and verify them against current docs.
- Preserve optional external guidance; do not turn one repository's preference
  into a universal review rule.
- Keep installation standard: use the existing skills CLI.
- Link each skill's README from the root catalog. Add groups only when needed.
- Use `uv` for Python development tools; commit `uv.lock` when dependencies change.
- Run `uv run python scripts/validate_package.py` and
  `uv run python -m unittest discover -s tests/package -v` for package changes.
- Run `uv run python -m unittest discover -s tests/pr_review -v` for review changes.
- Run `bash tests/package.sh` after packaging or discovery changes. It installs
  only into a temporary project and requires network access.
- Do not present fixture checks as model-quality scores. Record unrun host checks.
- Keep generated reviews, transcripts, credentials, and personal preferences out
  of the repository.
- Prefer focused branches and small changes. No em dashes in maintained prose.

## Scripts inside skills

- Prefer an existing published tool when it fits the task, invoked with a pinned
  version such as `uvx package@version` or `npx package@version`.
- Bundle scripts for workflow-specific logic. Python scripts use a PEP 723 header
  declaring their dependencies and run with `uv run`; standard-library-only scripts
  can declare `dependencies = []`.
- Document prerequisites and commands relative to the skill folder. Provide
  `--help`, noninteractive inputs, and useful errors. Test bundled behavior.
- Persistent installs such as `pip install --user`, `uv tool install`, or
  `npm install -g` need a stated reason and user authorization. Existing authorization
  counts; do not ask again for an already authorized install.

See the [Agent Skills scripts guide](https://agentskills.io/skill-creation/using-scripts).
