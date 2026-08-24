#!/usr/bin/env bash
# Copia le skill di questo plugin nella cartella che Google Antigravity IDE
# legge per le Agent Skills, così restano disponibili anche fuori da Claude
# Code (Antigravity non usa il formato "plugin" di Claude Code: legge
# direttamente le cartelle skill in formato SKILL.md).
#
# Uso:
#   ./install-antigravity.sh            # installa a livello di workspace (.agent/skills)
#   ./install-antigravity.sh --global   # installa a livello globale (~/.gemini/antigravity/skills)

set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS=(homepage-brief-builder homepage-elementor-redesign website-qa-review)

if [[ "${1:-}" == "--global" ]]; then
  DEST="$HOME/.gemini/antigravity/skills"
else
  DEST=".agent/skills"
fi

mkdir -p "$DEST"

for skill in "${SKILLS[@]}"; do
  target="$DEST/$skill"
  rm -rf "$target"
  cp -R "$PLUGIN_ROOT/skills/$skill" "$target"
  echo "Installata: $target"
done

echo ""
echo "Fatto. Antigravity (>= 1.14.2) scopre le skill in $DEST automaticamente via semantic triggering."
echo "Nota: gli hook, i comandi slash e il subagent di questo plugin sono concetti specifici di Claude Code"
echo "e non vengono letti da Antigravity — solo le skill (SKILL.md + references/ + scripts/) sono portabili."
