# Wendao Skills

Portable agent skills for thoughtful engineering. Install the workflows you need in
Cursor, Claude Code, Codex, or another client that supports
[Agent Skills](https://agentskills.io/specification).

## Install

Requires Node.js/npm and Git. Installing from a private repository also requires
repository access and Git authentication.

For Cursor, available across your projects:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill pr-review --agent cursor -g
```

For Cursor, Claude Code, and Codex together:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill pr-review \
  --agent cursor claude-code codex -g
```

Omit `-g` to install into the current project. The
[skills CLI](https://github.com/vercel-labs/skills) manages the installation paths
and lets you choose symlinks or copies. This collection uses ordinary skill folders;
no custom installer, service, or npm package is required.

Browse the collection or update an installed skill:

```sh
npx skills@latest add SoulEvill/wendao-skills --list
npx skills@latest update pr-review -g
```

## Skills

| Skill | What it does |
| --- | --- |
| [pr-review](skills/pr-review/SKILL.md) | Reviews PRs across correctness, reliability, security, architecture, scalability, simplicity, reuse, tests, and docs. Offers Standard and Deep review, scoped repository guidance, and a draft before publishing. |

## First review

In Cursor or Claude Code, invoke `/pr-review`. In Codex, invoke `$pr-review`.
If the skill does not appear, start a fresh session or reload the client.

```text
/pr-review Review <PR URL> at Standard level. Prepare a draft here first.
```

For a larger change:

```text
/pr-review Review <PR URL> at Deep level, including broader architecture
and scalability. Prepare the overall comment and inline comments as a draft.
```

The skill uses the active host model and reasoning effort by default. Standard and
Deep control review coverage and investigation; they do not switch models.
Explicit model/effort requests depend on the host's available controls. The agent
needs repository access through its existing tools, authenticated GitHub CLI or
connector, or a local base/head diff. Installation does not grant access or
permission to publish.

See [runtime controls](skills/pr-review/references/runtime-controls.md) for details.
Cursor Cloud Agents and remote workers need their own skill availability; a local
global installation alone does not deploy a skill to those environments.

## Repository preferences

Start with no extra configuration. To add team or personal guidance, supply a
`preferences_root` and an explicitly bound repository key, or selected scoped files.
Keep these sources outside the installed skill so package updates preserve them.

```text
<preferences_root>/
  pr-review/
    preferences.md
    example-api/
      instructions.md
```

Example: `Use pr-review with preferences_root=/my/preferences and
preferences_repo=example-api for this repository.`

The skill only reads applicable guidance. Feedback collection and preference
updates belong to the user or their framework. See the
[guidance contract](skills/pr-review/references/guidance.md).

## Add a skill

Add `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
Keep required resources inside that folder and add one row to the catalog above.
See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and packaging checks.

## Validation

The [test suite](tests/README.md) checks package installation and synthetic review
fixtures. These tests do not call models or measure review quality. The collection
does not include an evaluation runner or benchmark. See
[validation status](docs/validation.md) for what was executed.

## Design and license

The collection follows the self-contained, composable approach used by
[Matt Pocock's skills](https://github.com/mattpocock/skills), with a flat layout
for a small catalog. The portable file format comes from the
[Agent Skills specification](https://agentskills.io/specification).
The review rubric's sources are recorded in
[design references](skills/pr-review/references/research.md).

[MIT](LICENSE).
