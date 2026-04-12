#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  xb — CLI wrapper pour xais-brain
#  Usage : xb <commande> [args...]
# ─────────────────────────────────────────────────────────────────────────────
set -e

VERSION="1.0.0"

# === Couleurs ================================================================
GREEN='\033[0;32m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
WHITE='\033[1;37m'
DIM='\033[2m'
RESET='\033[0m'

# === Résolution du vault =====================================================
resolve_vault() {
  # 1. Variable d'env explicite
  if [ -n "${XAIS_BRAIN_VAULT:-}" ]; then
    echo "$XAIS_BRAIN_VAULT"
    return 0
  fi
  # 2. vault-config.json dans le cwd
  if [ -f "vault-config.json" ]; then
    echo "$(pwd)"
    return 0
  fi
  # 3. Défaut
  if [ -f "$HOME/xais-brain-vault/vault-config.json" ]; then
    echo "$HOME/xais-brain-vault"
    return 0
  fi
  echo "Erreur : vault introuvable." >&2
  echo "Définis XAIS_BRAIN_VAULT ou cd dans ton vault." >&2
  return 1
}

# === Vérification Claude Code ================================================
require_claude() {
  if ! command -v claude &>/dev/null; then
    echo -e "${RED}Erreur${RESET} : Claude Code n'est pas installé." >&2
    echo "  Installe-le : curl -fsSL https://claude.ai/install.sh | sh" >&2
    return 1
  fi
}

# === Commandes ===============================================================

cmd_daily() {
  require_claude
  local vault
  vault="$(resolve_vault)"
  claude -p "/daily" --cwd "$vault"
}

cmd_inbox() {
  require_claude
  local vault
  vault="$(resolve_vault)"
  claude -p "/inbox-zero" --cwd "$vault"
}

cmd_intel() {
  local vault
  vault="$(resolve_vault)"
  local source_dir="$1"
  if [ -z "$source_dir" ]; then
    echo "Usage : xb intel <dossier_source>" >&2
    return 1
  fi
  source_dir="${source_dir/#\~/$HOME}"

  if [ ! -d "$source_dir" ]; then
    echo -e "${RED}Erreur${RESET} : dossier introuvable : $source_dir" >&2
    return 1
  fi

  local cfg="$vault/vault-config.json"
  local inbox_dir
  inbox_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")

  local python_bin="$HOME/.xais-brain-venv/bin/python3"
  if [ ! -x "$python_bin" ]; then
    echo -e "${RED}Erreur${RESET} : venv Python introuvable ($python_bin)." >&2
    echo "  Relance setup.sh pour installer les dépendances." >&2
    return 1
  fi

  "$python_bin" "$vault/scripts/file_intel.py" "$source_dir" "$vault/$inbox_dir"
}

cmd_status() {
  local vault
  vault="$(resolve_vault)"
  local cfg="$vault/vault-config.json"
  local today
  today=$(date +%Y-%m-%d)

  # Lire les noms de dossiers depuis vault-config.json
  local inbox_dir daily_dir provider
  inbox_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")
  daily_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('daily','daily'))" 2>/dev/null || echo "daily")
  provider=$(python3 -c "import json; print(json.load(open('$cfg')).get('llm',{}).get('provider','non configuré'))" 2>/dev/null || echo "?")

  local inbox_count
  inbox_count=$(find "$vault/$inbox_dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')

  local has_daily="non"
  [ -f "$vault/$daily_dir/$today.md" ] && has_daily="oui"

  echo ""
  echo -e "  ${WHITE}xais-brain — status${RESET}"
  echo ""
  echo -e "  Vault    : ${CYAN}$(basename "$vault")${RESET} ${DIM}($vault)${RESET}"
  echo -e "  Inbox    : ${GREEN}$inbox_count${RESET} fichier(s)"
  echo -e "  Daily    : $has_daily ($today)"
  echo -e "  Provider : $provider"
  echo ""
}

cmd_open() {
  local vault
  vault="$(resolve_vault)"

  case "$OSTYPE" in
    darwin*)
      open -a Obsidian "$vault" 2>/dev/null || open "$vault"
      ;;
    linux*)
      if command -v obsidian &>/dev/null; then
        obsidian "$vault" &
      elif command -v flatpak &>/dev/null && flatpak list 2>/dev/null | grep -q md.obsidian.Obsidian; then
        flatpak run md.obsidian.Obsidian "$vault" &
      elif command -v xdg-open &>/dev/null; then
        xdg-open "$vault" &
      else
        echo "Ouvre Obsidian manuellement sur : $vault" >&2
      fi
      ;;
    *)
      echo "OS non supporté. Ouvre Obsidian manuellement sur : $vault" >&2
      ;;
  esac
}

cmd_clip() {
  local vault
  vault="$(resolve_vault)"
  local url="$1"
  if [ -z "$url" ]; then
    echo "Usage : xb clip <url>" >&2
    return 1
  fi

  local python_bin="$HOME/.xais-brain-venv/bin/python3"
  if [ ! -x "$python_bin" ]; then
    echo -e "${RED}Erreur${RESET} : venv Python introuvable ($python_bin)." >&2
    echo "  Relance setup.sh pour installer les dépendances." >&2
    return 1
  fi

  local cfg="$vault/vault-config.json"
  local inbox_dir
  inbox_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")

  "$python_bin" "$vault/scripts/web_clip.py" "$url" "$vault/$inbox_dir"
}

cmd_shell() {
  require_claude
  local vault
  vault="$(resolve_vault)"
  echo -e "${DIM}Ouverture de Claude Code dans $vault...${RESET}"
  cd "$vault" && exec claude
}

cmd_help() {
  echo ""
  echo -e "  ${WHITE}xb${RESET} — CLI wrapper pour xais-brain (v$VERSION)"
  echo ""
  echo -e "  ${WHITE}Usage :${RESET} xb <commande> [args...]"
  echo ""
  echo -e "  ${WHITE}Commandes :${RESET}"
  echo ""
  echo -e "  ${CYAN}daily${RESET}            Lance /daily en one-shot (note du jour + contexte)"
  echo -e "  ${CYAN}inbox${RESET}            Lance /inbox-zero en one-shot (tri automatique)"
  echo -e "  ${CYAN}intel${RESET} <dossier>   Traite un dossier de fichiers via LLM (pas besoin de Claude)"
  echo -e "  ${CYAN}clip${RESET} <url>       Clippe une page web en note Markdown dans inbox/"
  echo -e "  ${CYAN}status${RESET}           Affiche l'état du vault (inbox, daily, provider)"
  echo -e "  ${CYAN}open${RESET}             Ouvre Obsidian sur le vault"
  echo -e "  ${CYAN}shell${RESET}            Ouvre une session Claude Code interactive dans le vault"
  echo -e "  ${CYAN}help${RESET}             Affiche cette aide"
  echo -e "  ${CYAN}version${RESET}          Affiche la version"
  echo ""
  echo -e "  ${WHITE}Résolution du vault :${RESET}"
  echo ""
  echo -e "  1. ${DIM}\$XAIS_BRAIN_VAULT${RESET} (variable d'env)"
  echo -e "  2. ${DIM}vault-config.json${RESET} dans le répertoire courant"
  echo -e "  3. ${DIM}~/xais-brain-vault/${RESET} (défaut)"
  echo ""
  echo -e "  ${WHITE}Exemples :${RESET}"
  echo ""
  echo -e "  ${DIM}xb status${RESET}                     # état du vault"
  echo -e "  ${DIM}xb daily${RESET}                      # note du jour"
  echo -e "  ${DIM}xb intel ~/Documents/PDFs${RESET}     # traiter des fichiers"
  echo -e "  ${DIM}xb clip https://example.com/article${RESET}  # clipper une page web"
  echo -e "  ${DIM}XAIS_BRAIN_VAULT=~/autre-vault xb status${RESET}  # vault alternatif"
  echo ""
}

cmd_version() {
  echo "xb v$VERSION"
}

# === Dispatch ================================================================
case "${1:-}" in
  daily)    cmd_daily ;;
  inbox)    cmd_inbox ;;
  intel)    shift; cmd_intel "$@" ;;
  clip)     shift; cmd_clip "$@" ;;
  status)   cmd_status ;;
  open)     cmd_open ;;
  shell)    cmd_shell ;;
  version)  cmd_version ;;
  help|--help|-h)  cmd_help ;;
  "")
    cmd_help
    ;;
  *)
    echo -e "${RED}Commande inconnue${RESET} : $1" >&2
    echo "  Tape 'xb help' pour la liste des commandes." >&2
    exit 1
    ;;
esac
