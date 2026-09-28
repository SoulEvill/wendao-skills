#!/usr/bin/env bash
# Install through the real CLI without changing the user's global skill folders.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_repo="${1:-$repo_root}"
scratch="$(mktemp -d "${TMPDIR:-/tmp}/wendao-package.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT

mkdir "$scratch/project"
git init -q "$scratch/project"
cd "$scratch/project"
export DISABLE_TELEMETRY=1
export npm_config_cache="$scratch/npm-cache"

npx --yes skills@latest add "$source_repo" --skill pr-review \
  --agent cursor claude-code codex --yes

# The installer shares .agents between Cursor and Codex in project scope.
# Claude Code has a separate discovery path, usually linked to that same content.
for destination in .agents/skills/pr-review .claude/skills/pr-review; do
  test -f "$destination/SKILL.md"
  diff -r "$repo_root/skills/pr-review" "$destination"
done

echo "Installed the complete PR-review package for Cursor, Claude Code, and Codex."
