# Validation status

This collection includes executable offline regression tests and synthetic review
fixtures. These are development tools, not a model-quality benchmark.

## Executed checks

On 2026-09-27:

| Check | Result |
| --- | --- |
| Package metadata and local links | Passed for `pr-review` and repository documentation. |
| Skill Creator validation | Passed. |
| Offline regression suite | All 32 tests passed. |
| Local installation using `npx skills@latest` | Passed for Cursor, Claude Code, and Codex in a disposable project. All installed skill files matched the source. |

The installer used `.agents/skills/pr-review` for Cursor and Codex, and linked
`.claude/skills/pr-review` for Claude Code. It did not modify global installations.

## What the checks cover

- Skill discovery metadata, packaged resources, and relative documentation links.
- Installation with the standard skills CLI into temporary project paths for
  Cursor, Claude Code, and Codex. Installed files must match the source package.
- Synthetic fixture behavior, scoped guidance and presentation cases, and the
  evaluation harness's evidence hashes, immutable snapshots, and result accounting.

## What remains unverified

The installer check does not launch the clients or prove that a model will follow
the review instructions. This repository does not publish a production accuracy
score, a comparison between models, or an end-to-end review benchmark across all
three clients. Existing fixture preparation can support those runs; each needs
an authenticated host, an actual review, preserved evidence, and human adjudication.

See [evaluation instructions](../eval/skill_review/README.md) for how to prepare a
review exercise. Developer commands are in [CONTRIBUTING.md](../CONTRIBUTING.md).
