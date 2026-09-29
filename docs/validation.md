# Validation status

This collection has package checks and synthetic fixture tests. It does not include
a model-quality benchmark or an evaluation runner.

## Executed checks

On 2026-09-28:

| Check | Result |
| --- | --- |
| Package metadata and local links | Passed for `wd-pr-review` and repository documentation. |
| Package validator regression tests | All 16 tests passed, covering discovery, naming, READMEs, code examples, and real links. |
| PR-review fixture tests | All 16 tests passed. |
| Installation using `npx skills@latest` | Passed for every catalog skill and a temporary catalog with flat and grouped skills. Cursor, Claude Code, and Codex installations matched source files. |

The installer uses `.agents/skills/wd-pr-review` for Cursor and Codex, and links
`.claude/skills/wd-pr-review` for Claude Code. Global installations are not modified.
GitHub Actions runs the package validator, fixture tests, and installation check.

The fixture tests cover the example code and supplied contexts. They do not prove
that a model will find the defects, follow the instructions, or produce a good
review. The installer check does not launch the clients. No model accuracy or
cross-client review-quality score is claimed.

See [test instructions](../tests/README.md) for commands and fixture details.
