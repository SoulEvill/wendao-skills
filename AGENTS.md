# Contributor guidance

This repository contains portable agent skills. Keep runtime instructions under
`skills/<name>/` and developer-only checks and fixtures under `tests/`.

- Prefer one self-contained skill folder and focused relative references.
- Keep shared instructions independent of one client, model, or PR provider.
- Put host-specific controls in references and verify them against current docs.
- Preserve optional external guidance; do not turn one repository's preference
  into a universal review rule.
- Keep installation standard: use the existing skills CLI.
- Add new skills to the README catalog. Add categories only when the catalog needs them.
- Use `uv` for Python development tools; commit `uv.lock` when dependencies change.
- Run `uv run python scripts/validate_package.py` and
  `uv run python -m unittest discover -s tests/pr_review -v` for relevant changes.
- Run `bash tests/package.sh` after packaging or discovery changes. It installs
  only into a temporary project and requires network access.
- Do not present fixture checks as model-quality scores. Record unrun host checks.
- Keep generated reviews, transcripts, credentials, and personal preferences out
  of the repository.
- Prefer focused branches and small changes. No em dashes in maintained prose.
