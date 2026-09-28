# Validation status

This collection has package checks and synthetic fixture tests. It does not include
a model-quality benchmark or an evaluation runner.

## Executed checks

On 2026-09-27:

| Check | Result |
| --- | --- |
| Package metadata and local links | Passed for `pr-review` and repository documentation. |
| PR-review fixture tests | All 16 tests passed. |
| Installation using `npx skills@latest` | Passed for Cursor, Claude Code, and Codex in a disposable project. Installed skill files matched the source. |

The installer uses `.agents/skills/pr-review` for Cursor and Codex, and links
`.claude/skills/pr-review` for Claude Code. Global installations are not modified.
GitHub Actions runs the package validator, fixture tests, and installation check.

The fixture tests cover the example code and supplied contexts. They do not prove
that a model will find the defects, follow the instructions, or produce a good
review. The installer check does not launch the clients. No model accuracy or
cross-client review-quality score is claimed.

See [test instructions](../tests/README.md) for commands and fixture details.
