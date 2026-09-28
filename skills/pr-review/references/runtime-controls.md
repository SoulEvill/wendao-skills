# Runtime controls

This skill specifies a review workflow. The host selects the model and reasoning
effort; text such as "act as model X" cannot change the running model.

## Discovery and reuse

Install the complete skill folder through the standard skills CLI:

```sh
npx skills@latest add SoulEvill/wendao-skills --skill pr-review --agent cursor -g
```

Select `claude-code` or `codex` for those clients; the installer accepts multiple
agents. Omit `-g` for project installation. It manages each client's discovery
location. Invoke `/pr-review` in Cursor or Claude Code and `$pr-review` in Codex.
A fresh session may be needed for discovery. Automatic selection remains enabled.

For manual installation, copy the whole folder with its references into a supported
skill directory. For another host, supply its path or load its instructions and
relevant references. See [skills CLI](https://github.com/vercel-labs/skills),
[Cursor skills](https://cursor.com/docs/skills),
[Codex skills](https://learn.chatgpt.com/docs/build-skills), and
[Claude Code skills](https://code.claude.com/docs/en/skills). Local installation does
not deploy a skill to remote workers or cloud sessions.

## Four independent controls

| Control | Resolution |
| --- | --- |
| `model` | `current` inherits the active host selection; otherwise request an exact available identifier. |
| `reasoning_effort` | `current` inherits; otherwise use a native value supported by the chosen model and host. |
| `review_depth` | `standard` or `deep` changes investigation and verification, not the model. |
| `holistic` | `auto` is off for Standard and on for Deep; explicit `on` or `off` overrides it. |

All depths cover all axes. Holistic off still requires the targeted architecture,
caller, and reuse checks in SKILL.md. Do not translate "deep" into a provider effort
value, or assume similarly named effort levels have equivalent cost across providers.

## Resolve before reviewing

1. Inspect the active host's tools, installed CLI help, and model availability.
   Check model/effort compatibility and organization restrictions. Do not maintain
   a fixed model catalog in this skill.
2. For `current`, keep the selection. For explicit values, apply actual host controls
   before the substantive review, using a supported new invocation or delegation
   if necessary. Do not edit global defaults merely to perform one review.
3. If the host cannot apply an explicit selection, report a capability error naming
   the unsupported control and the supported route. Do not silently substitute or
   run the review as though the selection succeeded. Context gathering can continue.
4. If the host exposes only the requested setting, record actual execution as
   `unknown` or `unverified`. If an observed cap, fallback, or substitution conflicts
   with the explicit request, disclose it and obtain a revised selection before
   continuing. Do not claim an exact configuration was verified without evidence.

`current` is scoped to the session receiving the request. Native delegation can
inherit it only when the host guarantees inheritance. A newly launched CLI process
does not automatically inherit a parent app/session's overrides. When relaunching
for that parent, pass its resolved model and effort explicitly if observable. If
they cannot be resolved, keep work in the original session or explain that preserving
its selection requires user input; do not silently use the new process's defaults.
For a request initiated directly in a fresh CLI with no parent selection to preserve,
`current` means that CLI's configured defaults.

## Cursor

Use the active Agent chat's model selection. For an explicit model request, verify
that the requested model is available and selected before reviewing. If the agent
cannot apply that setting itself, ask the user to select it. Apply native effort
controls only when the installed client and model expose them; Standard and Deep
remain review-depth choices. Do not infer effective effort from a model name.

Use native subagent tools for Deep when available. Pass bounded scopes, exact
revisions, the rubric, and applicable preferences to each reviewer. If the host
does not expose delegation, follow the documented sequential fallback and disclose
it. No separate Cursor-specific skill or custom subagent definition is required.
See [Cursor Agent](https://cursor.com/docs/agent/overview) and
[Cursor subagents](https://cursor.com/docs/subagents).

## Codex

In an existing app/CLI session, use the host's model and reasoning controls. A skill
invocation does not itself reset them. For a separate CLI run, first verify
`codex exec --help`, then use these supported controls:

```sh
codex exec --model '<available-model-id>' \
  -c 'model_reasoning_effort="<supported-effort>"' \
  --sandbox read-only - < review-request.txt
```

Replace placeholders with validated selections. The request file must identify the
skill path, PR or base/head, review depth, and holistic choice; ensure the host can
read the skill and references. Omit overrides only when the request intentionally
uses this fresh CLI's defaults, not when preserving another session's `current`.
A read-only run may need a separate permitted scratch workspace for tests; report blocked checks.
The CLI supports `--json` event output, but do not assume every event stream exposes
the resolved model and effort. [Codex configuration](https://developers.openai.com/codex/config-reference/)
documents `model_reasoning_effort`; use installed help for CLI flag compatibility.

For Deep, prefer the native subagent tools exposed in the session. Follow their
actual schema and context-inheritance constraints. If selecting a child model,
resolve its effort too: selecting a model alone can use that model's default effort.
Pass exact revisions, bounded scope, relevant rubric, and output requirements to
each child. Collect and reconcile every result. [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
documents model/effort inheritance and configuration; session capabilities take
precedence over examples for another release.

## Claude Code

Check `claude --help` before launch. Its session flags are independent:

```sh
claude --print --model '<available-model-id>' \
  --effort '<supported-effort>' --permission-mode plan < review-request.txt
```

Use the same request-file contract and process-boundary rules as above. Omit overrides
only when the request intentionally uses this fresh CLI's own defaults.
`--permission-mode plan` supports an inspection-first run; it is not an OS sandbox.
Do not enable fallback models when the user requires an exact model. Local help
and the [CLI reference](https://code.claude.com/docs/en/cli-reference) establish flags,
not account entitlement or the actual effective setting.

Prefer native subagents for Deep. Custom subagent definitions support `model` and
`effort`; effort otherwise inherits from the session. Check the installed version's
precedence rules and environment overrides. Give each child the rubric explicitly
or use supported skill preloading; do not assume parent instructions are inherited.
See [Claude Code subagents](https://code.claude.com/docs/en/sub-agents).

Claude Code can cap effort or substitute restricted models. In some versions,
structured output does not warn about effort caps. Record requested and observed
values separately; neither a successful exit nor a launch flag proves the effective
effort. See [model configuration](https://code.claude.com/docs/en/model-config).

## API and other hosts

The caller must load the skill and relevant references, provide repository context
or inspection tools, and implement any delegation. A single text API call cannot
search the repository by itself or create independent reviewers through prose.

| Host | Model control | Native effort control |
| --- | --- | --- |
| OpenAI Responses | Request `model` | Request `reasoning.effort` |
| Anthropic Messages | Request `model` | Request `output_config.effort` |
| Other host | Its documented model selector | Its documented effort control, if any |

Validate each pair against current provider documentation. Keep workflow controls in
the review instructions. Handle provider rejection as an error, not a fallback.
Retain response model metadata and request IDs when available, without credentials.
See [OpenAI reasoning](https://developers.openai.com/api/docs/guides/reasoning) and
[Anthropic effort](https://platform.claude.com/docs/en/build-with-claude/effort).

## Delegation and execution record

Prefer native delegation over recursively launching CLIs. Use independent contexts
for independent passes; a sequential self-check is useful but is not independent.
When delegation is unavailable, complete Deep's sequential passes and disclose that
limitation. An explicit demand for independent agents requires a capability error.
Respect concurrency and cost limits; never silently change child models to save cost.

Record requested model/effort, observed model/effort or `unknown`, the source of that
observation, host/version, requested/resolved depth and holistic mode, actual review
topology, child settings, reviewed SHAs, completed checks, and truncated/failed work.
Distinguish configured values from runtime metadata. Token counts and the model's
own assertion do not prove which reasoning effort executed.

Verified 2026-09-27 against official references, `codex-cli 0.142.5` help, and
Claude Code `2.1.222` help. No model calls were executed to validate these examples.
