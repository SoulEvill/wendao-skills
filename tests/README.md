# Development tests

Run from the repository root:

```sh
uv sync --locked
uv run python scripts/validate_package.py
uv run python -m unittest discover -s tests/package -v
uv run python -m unittest discover -s tests/pr_review -v
bash tests/package.sh
```

The 16 tests under `package/` cover flat and grouped discovery, unique `wd-` names,
required skill READMEs, and Markdown links. Code examples are ignored; real broken
links and links escaping a skill still fail.

The installation check discovers every catalog skill and compares its installed
files with the source for Cursor, Claude Code, and Codex. A temporary two-skill
catalog also exercises flat and grouped installation. It needs network access
and leaves global skill installations untouched.

## PR-review fixtures

The 16 tests under `pr_review/` verify synthetic review inputs:

- Behavioral examples contain the intended defects or preserve the intended behavior.
- Guidance examples keep the code change fixed while varying repository preferences.
- Presentation examples preserve reviewer decisions, duplicate findings, uncertainty,
  and publication permissions.
- Generated fixtures are reproducible and preserve existing output directories.

Generators and reference expectations are kept beside their tests. Guidance and
presentation expectations stay separate from generated reviewer inputs. The tests
check fixture behavior and consistency; they do not execute the skill through a
model, grade generated reviews, or produce quality scores.

There is no evaluation execution or result-recording framework in this repository.
Future evaluation can consume these fixtures through a separate framework.

Tests create temporary files and Git repositories with fixture identities. They
do not publish reviews. None of these development files are installed with a skill.
