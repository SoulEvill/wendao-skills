# PR Review

Review a PR or base/head diff across correctness, simplicity, reuse, architecture,
security, reliability, performance, tests, and docs. The agent follows
[SKILL.md](SKILL.md); this guide covers using the skill.

## First review

Install for Cursor:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill wd-pr-review --agent cursor -g
```

In Cursor or Claude Code, invoke `/wd-pr-review`. In Codex, invoke `$wd-pr-review`.
If the skill does not appear, start a fresh session or reload the client.

```text
/wd-pr-review Review <PR URL> at Standard level. Prepare a draft here first.
```

For a larger change:

```text
/wd-pr-review Review <PR URL> at Deep level, including broader architecture
and scalability. Prepare the overall comment and inline comments as a draft.
```

The local draft explains the PR's purpose, whether it achieves that purpose, and the
flow through relevant files before showing the proposed comments. Findings link to
their PR diff locations. The evidence summary shows findings or gaps per axis and
explains what the verification checks established.

After reviewing the draft, say `post it` to publish the proposed comments. This
authorizes comments, not an approval or request-changes event. The reviewer refreshes
the PR first and asks again only when material changes require a revised draft.

The skill uses the active host model and reasoning effort by default. Standard and
Deep control review coverage and investigation; they do not switch models.
Explicit model/effort requests depend on the host's available controls. The agent
needs repository access through its existing tools, authenticated GitHub CLI or
connector, or a local base/head diff. Installation does not grant access or
permission to publish.

See [runtime controls](references/runtime-controls.md) for details. Cursor Cloud
Agents and remote workers need their own skill availability; a local global
installation alone does not deploy a skill to those environments.

## Repository preferences

Start with no extra configuration. To add team or personal guidance, supply a
`preferences_root` and an explicitly bound repository key, or selected scoped files.
Keep these sources outside the installed skill so package updates preserve them.

```text
<preferences_root>/
  wd-pr-review/
    preferences.md
    example-api/
      instructions.md
```

Example: `Use wd-pr-review with preferences_root=/my/preferences and
preferences_repo=example-api for this repository.`

The skill only reads applicable guidance. Feedback collection and preference
updates belong to the user or their framework. See the
[guidance contract](references/guidance.md).
