# Wendao Skills

Portable agent skills for thoughtful engineering. Install the workflows you need in
Cursor, Claude Code, Codex, or another client that supports
[Agent Skills](https://agentskills.io/specification).

## Install

Requires Node.js/npm and Git. Installing from a private repository also requires
repository access and Git authentication.

Browse the collection:

```sh
npx skills@latest add SoulEvill/wendao-skills --list
```

For Cursor, available across your projects:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill wd-pr-review --agent cursor -g
```

For Cursor, Claude Code, and Codex together:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill wd-pr-review \
  --agent cursor claude-code codex -g
```

Omit `-g` to install into the current project. The
[skills CLI](https://github.com/vercel-labs/skills) manages the installation paths
and supports symlinks or copies. Choose the agents you use: `--agent '*'` targets
every supported agent, including ones you do not have installed.

Update an installed skill:

```sh
npx skills@latest update wd-pr-review -g
```

Use `-p` instead of `-g` to update the current project's installation.

Git commits identify catalog versions. To pin or roll back, replace the placeholder
below with a full commit SHA. Updates preserve the selected ref; a full SHA stays
fixed while branches and tags can move.

```sh
npx skills@latest add 'https://github.com/SoulEvill/wendao-skills#<full-commit-sha>' \
  --skill wd-pr-review --agent cursor -g
```

The selected commit must contain that skill name. For GitHub Enterprise or other Git
hosts, prefer a clone URL ending in `.git#<full-commit-sha>`. The CLI also recognizes
bare GitHub Enterprise URLs when their host is configured through `GH_HOST`; an
unrecognized bare HTTPS host may not parse `#ref` as a Git revision. See the
[CLI source parser](https://github.com/vercel-labs/skills/blob/7407f3893ad4dceab546ac002c3ef806e4000c73/src/source-parser.ts).

## Skills

Skill names use `wd-` (Wendao), for example `/wd-pr-review`.

| Skill | What it does |
| --- | --- |
| [wd-pr-review](skills/wd-pr-review/README.md) | Reviews PRs across nine axes with Standard or Deep investigation, scoped repository guidance, and a draft before publishing. |

## Add a skill

Use `skills/<name>/` or one optional group level, `skills/<group>/<name>/`.
Each skill needs `SKILL.md` and a human-facing `README.md`; groups have no `SKILL.md`.
Names must be unique across the catalog because installation is flat by name.
Keep required resources inside the skill folder and add one row to the catalog above.
See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and packaging checks.

## Validation

The [test suite](tests/README.md) checks package installation and synthetic review
fixtures. These tests do not call models or measure review quality. The collection
does not include an evaluation runner or benchmark. See
[validation status](docs/validation.md) for what was executed.

## Design and license

The collection follows the self-contained, composable approach used by
[Matt Pocock's skills](https://github.com/mattpocock/skills). The portable file format
comes from the
[Agent Skills specification](https://agentskills.io/specification).
The review rubric's sources are recorded in
[design references](skills/wd-pr-review/references/research.md).

[MIT](LICENSE).
