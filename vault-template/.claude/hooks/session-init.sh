#!/bin/bash
# Hook SessionStart — charge le contexte vault au démarrage de Claude Code
# Non-bloquant : exit 0 en cas d'erreur

export VAULT_PATH="${VAULT_PATH:-$(pwd)}"
export TODAY=$(date +%Y-%m-%d)
export YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null || echo "")

# Lecture de vault-config.json si présent
CFG="$VAULT_PATH/vault-config.json"
if [ -f "$CFG" ] && command -v python3 &>/dev/null; then
    # Parse minimal via python stdlib (pas de dep jq)
    eval "$(python3 -c "
import json, sys
try:
    with open('$CFG') as f:
        cfg = json.load(f)
    folders = cfg.get('folders', {})
    for key, value in folders.items():
        print(f'export VAULT_{key.upper()}_DIR=\"{value}\"')
except Exception:
    pass
" 2>/dev/null)"
fi

# Défauts si vault-config absent ou corrompu
: "${VAULT_INBOX_DIR:=inbox}"
: "${VAULT_DAILY_DIR:=daily}"
: "${VAULT_PROJECTS_DIR:=projects}"
: "${VAULT_RESEARCH_DIR:=research}"
: "${VAULT_ARCHIVE_DIR:=archive}"
: "${VAULT_MEMORY_DIR:=memory}"

# Pas de CLAUDE.md → vault non configuré
if [ ! -f "$VAULT_PATH/CLAUDE.md" ]; then
    echo ""
    echo "Ce dossier ne ressemble pas à un vault xais-brain."
    echo "  → Lance : curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash"
    exit 0
fi

# Surface minimal — 3 lignes max
INBOX_COUNT=$(find "$VAULT_PATH/$VAULT_INBOX_DIR" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
echo ""
echo "Vault  : $(basename "$VAULT_PATH")  |  Aujourd'hui : $TODAY"
if [ "${INBOX_COUNT:-0}" -gt 0 ] 2>/dev/null; then
    echo "Inbox  : $INBOX_COUNT fichiers en attente  → /inbox-zero"
fi
DAILY_TODAY="$VAULT_PATH/$VAULT_DAILY_DIR/$TODAY.md"
if [ ! -f "$DAILY_TODAY" ]; then
    echo "Note du jour absente  → /daily"
fi
exit 0
