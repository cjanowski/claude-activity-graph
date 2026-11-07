#!/usr/bin/env bash
# Install the activity graph into ~/.claude and scaffold a vault.
#
#   ./install.sh <vault-dir> [--force]
#
# Copies tools, the Stop hook and the `graph` skill into ~/.claude, scaffolds the vault
# from vault-template/ if the folder is empty or missing, and writes the vault pointer.
# It does not edit settings.json or CLAUDE.md; it prints the two snippets to add.
# Existing files are left alone unless --force is given.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
vault="${1:?usage: ./install.sh <vault-dir> [--force]}"
force="${2:-}"
claude="${CLAUDE_HOME:-$HOME/.claude}"

copy() {  # copy <src> <dst>, refusing to overwrite without --force
  if [[ -e "$2" && "$force" != "--force" ]]; then
    echo "  keep   $2 (exists; --force to overwrite)"
  else
    mkdir -p "$(dirname "$2")"; cp "$1" "$2"; echo "  write  $2"
  fi
}

echo "Tools, hook, skill -> $claude"
for f in vaultlib.py vault_lint.py vault_graph.py github_ingest.py graph_template.html; do
  copy "$here/tools/$f" "$claude/tools/$f"
done
copy "$here/claude/hooks/session_note_check.py" "$claude/hooks/session_note_check.py"
copy "$here/claude/skills/graph/SKILL.md" "$claude/skills/graph/SKILL.md"

mkdir -p "$vault"
vault="$(cd "$vault" && pwd)"
if [[ -z "$(ls -A "$vault")" ]]; then
  echo "Scaffold vault -> $vault"
  cp -R "$here/vault-template/." "$vault/"
  find "$vault" -name .gitkeep -delete
else
  echo "Vault $vault is not empty; leaving its contents alone"
fi
if [[ -e "$claude/tools/vault_path" && "$force" != "--force" ]]; then
  echo "  keep   $claude/tools/vault_path -> $(cat "$claude/tools/vault_path")"
else
  printf '%s\n' "$vault" > "$claude/tools/vault_path"; echo "  write  $claude/tools/vault_path"
fi

python3 "$claude/tools/vault_lint.py" --vault "$vault" >/dev/null && echo "Lint OK"

cat <<EOF

Two manual steps:

1. Merge into $claude/settings.json:
$(cat "$here/claude/settings.hooks.json")

2. Append to $claude/CLAUDE.md:
   cat "$here/claude/CLAUDE.md.snippet" >> "$claude/CLAUDE.md"

Then open $vault in Obsidian.
EOF
