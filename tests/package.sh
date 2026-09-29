#!/usr/bin/env bash
# Install through the real CLI without changing the user's global skill folders.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# An optional remote source must match this checkout's expected skill contents.
source_repo="${1:-$repo_root}"
if [ -d "$source_repo" ]; then
  source_repo="$(cd "$source_repo" && pwd)"
fi
scratch="$(mktemp -d "${TMPDIR:-/tmp}/wendao-package.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT
export DISABLE_TELEMETRY=1
export npm_config_cache="$scratch/npm-cache"

check_install() (
  install_source="$1"
  expected_root="$2"
  project="$3"
  mkdir "$project"
  git init -q "$project"
  uv run --locked --project "$repo_root" python "$repo_root/scripts/validate_package.py" \
    --root "$expected_root" --list > "$project/skills.tsv"
  cd "$project"

  count=0
  while IFS=$'\t' read -r name source_directory; do
    npx --yes skills@latest add "$install_source" --skill "$name" \
      --agent cursor claude-code codex --yes < /dev/null
    # Cursor and Codex share .agents; Claude Code has a separate discovery path.
    for destination in ".agents/skills/$name" ".claude/skills/$name"; do
      test -f "$destination/SKILL.md"
      diff -r "$source_directory" "$destination"
    done
    count=$((count + 1))
  done < "$project/skills.tsv"

  test "$count" -gt 0
  echo "Installed and compared $count skill package(s) for Cursor, Claude Code, and Codex."
)

check_install "$source_repo" "$repo_root" "$scratch/project"

# Exercise multiple skills and grouped discovery even while the catalog is small.
for relative in wd-package-flat engineering/wd-package-grouped; do
  directory="$scratch/catalog/skills/$relative"
  mkdir -p "$directory/assets"
  cat > "$directory/SKILL.md" <<EOF
---
name: ${relative##*/}
description: Temporary installation test fixture.
---
Read [the sample](assets/sample.txt).
EOF
  printf '# Usage\n\nSee [the sample](assets/sample.txt).\n' > "$directory/README.md"
  printf '%s\n' "$relative" > "$directory/assets/sample.txt"
done
check_install "$scratch/catalog" "$scratch/catalog" "$scratch/fixtures-project"
