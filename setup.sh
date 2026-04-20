#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  xais-brain — Installateur Obsidian + Claude Code
#  https://github.com/XAISOLUCES/xais-brain
# ─────────────────────────────────────────────────────────────────────────────
set -e

# === Constantes ==============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "$PWD")"
VENV_DIR="$HOME/.xais-brain-venv"
REPO_URL="https://github.com/XAISOLUCES/xais-brain.git"
DEFAULT_VAULT="$HOME/xais-brain-vault"
NUM_STEPS=10

# === Mode CI / non-interactif ================================================
# Si XAIS_BRAIN_CI=true (ou CI=true), tous les read -rp sont bypassés avec des
# valeurs par défaut ou des variables d'env dédiées.
IS_CI="${XAIS_BRAIN_CI:-${CI:-false}}"

# === Couleurs ================================================================
PURPLE='\033[0;35m'
ORANGE='\033[0;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
RED='\033[0;31m'
WHITE='\033[1;37m'
DIM='\033[2m'
RESET='\033[0m'

# === Helpers d'affichage =====================================================
step() { echo ""; echo -e "${WHITE}Étape $1/$NUM_STEPS — $2${RESET}"; }
ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
warn() { echo -e "  ${ORANGE}⚠${RESET}  $1"; }
err()  { echo -e "  ${RED}✗${RESET} $1" >&2; }
info() { echo -e "  ${DIM}$1${RESET}"; }

safe_cp() {
  if [ -f "$1" ]; then
    cp "$1" "$2"
  else
    warn "Fichier source manquant : $1"
    return 0
  fi
}

# === Bootstrap (auto-clone si lancé via curl|bash) ===========================
bootstrap_if_needed() {
  if [ -f "$SCRIPT_DIR/vault-template/CLAUDE.md" ]; then
    return 0
  fi
  echo "Téléchargement du repo xais-brain..."
  local boot
  boot="$(mktemp -d)"
  if ! git clone --depth=1 "$REPO_URL" "$boot" &>/dev/null; then
    echo "Erreur : impossible de cloner le repo. Vérifie ta connexion." >&2
    echo "Alternative : télécharge le ZIP depuis $REPO_URL" >&2
    rm -rf "$boot"
    exit 1
  fi
  # En curl|bash, stdin est le pipe de curl (fermé après le download).
  # On redirige stdin vers le TTY pour que les `read` interactifs marchent.
  if [ ! -t 0 ] && [ -e /dev/tty ]; then
    XAIS_BRAIN_BOOTSTRAP_DIR="$boot" exec bash "$boot/setup.sh" < /dev/tty
  else
    XAIS_BRAIN_BOOTSTRAP_DIR="$boot" exec bash "$boot/setup.sh"
  fi
}

cleanup_bootstrap() {
  if [ -n "${XAIS_BRAIN_BOOTSTRAP_DIR:-}" ] && [ -d "$XAIS_BRAIN_BOOTSTRAP_DIR" ]; then
    rm -rf "$XAIS_BRAIN_BOOTSTRAP_DIR"
  fi
}

# === Bannière ================================================================
show_banner() {
  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip bannière"
    return 0
  fi
  clear
  echo ""
  echo -e "${PURPLE}"
  cat << 'BANNER'
  ██╗  ██╗ █████╗ ██╗███████╗     ██████╗ ██████╗  █████╗ ██╗███╗   ██╗
  ╚██╗██╔╝██╔══██╗██║██╔════╝     ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║
   ╚███╔╝ ███████║██║███████╗     ██████╔╝██████╔╝███████║██║██╔██╗ ██║
   ██╔██╗ ██╔══██║██║╚════██║     ██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║
  ██╔╝ ██╗██║  ██║██║███████║     ██████╔╝██║  ██║██║  ██║██║██║ ╚████║
  ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
BANNER
  echo -e "${RESET}"
  echo -e "${DIM}  Obsidian + Claude Code · Ton second cerveau IA${RESET}"
  echo ""
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo -e "  ${WHITE}Ce script installe :${RESET}"
  echo ""
  echo -e "  ${PURPLE}Obsidian${RESET}        App de notes free, fichiers Markdown locaux"
  echo -e "  ${PURPLE}Claude Code${RESET}     IA Anthropic en CLI, lit et écrit dans ton vault"
  echo -e "  ${PURPLE}Python deps${RESET}     Libs pour traiter PDFs et docs via LLM"
  echo -e "  ${PURPLE}11 skills${RESET}       Slash commands FR pour gérer ton vault"
  echo -e "  ${PURPLE}Hooks FR${RESET}        SessionStart + skill-discovery en français"
  echo -e "  ${PURPLE}Skills Kepano${RESET}   CLI Obsidian officiel (optionnel)"
  echo ""
  echo -e "  ${DIM}Rien n'est uploadé. Ton vault reste sur ta machine.${RESET}"
  echo ""
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# === Détection OS ============================================================
detect_os() {
  case "$OSTYPE" in
    darwin*)  OS="macos" ;;
    linux*)   OS="linux" ;;
    *)
      err "OS non supporté : $OSTYPE"
      info "xais-brain supporte macOS et Linux."
      exit 1
      ;;
  esac
  export OS
}

# === Étape 1 : Gestionnaire de paquets =======================================
step1_package_manager() {
  step 1 "Vérification du gestionnaire de paquets"

  case "$OS" in
    macos)
      if [ "$IS_CI" = "true" ]; then
        if ! command -v brew &>/dev/null; then
          info "CI mode — skip installation Homebrew"
          return 0
        fi
      fi
      if ! command -v brew &>/dev/null; then
        echo "  Installation de Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ok "Homebrew installé"
      else
        ok "Homebrew déjà installé"
      fi
      ;;
    linux)
      # Détecter le package manager natif
      if command -v apt-get &>/dev/null; then
        PKG_MGR="apt"
        ok "apt détecté (Debian/Ubuntu)"
      elif command -v dnf &>/dev/null; then
        PKG_MGR="dnf"
        ok "dnf détecté (Fedora/RHEL)"
      elif command -v pacman &>/dev/null; then
        PKG_MGR="pacman"
        ok "pacman détecté (Arch)"
      else
        PKG_MGR=""
        warn "Gestionnaire de paquets non détecté"
        info "Installe les dépendances manuellement (voir README)"
      fi
      export PKG_MGR
      ;;
  esac
}

# === Étape 2 : Obsidian (avec fix --adopt) ===================================
step2_obsidian() {
  step 2 "Installation d'Obsidian"

  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip installation Obsidian"
    return 0
  fi

  case "$OS" in
    macos)
      if brew list --cask obsidian &>/dev/null 2>&1; then
        ok "Obsidian déjà installé via Homebrew"
        return 0
      fi

      # FIX bug --adopt : si Obsidian est déjà dans /Applications/ (install manuelle),
      # on ne touche à rien. brew install --cask --adopt peut casser sur les vieilles
      # versions qui n'ont pas le binaire obsidian-cli attendu par le cask.
      if [ -d /Applications/Obsidian.app ]; then
        ok "Obsidian déjà installé manuellement (/Applications/Obsidian.app)"
        info "Pour passer en gestion brew plus tard : désinstalle puis brew install --cask obsidian"
        return 0
      fi

      echo "  Installation d'Obsidian..."
      if brew install --cask obsidian; then
        ok "Obsidian installé"
      else
        warn "Échec installation Obsidian — on continue le setup"
        info "Alternative : télécharge depuis https://obsidian.md, puis relance ce script"
      fi
      ;;

    linux)
      if command -v obsidian &>/dev/null || [ -f /usr/bin/obsidian ]; then
        ok "Obsidian déjà installé"
        return 0
      fi

      # Flatpak est le moyen le plus universel sur Linux
      if command -v flatpak &>/dev/null; then
        if flatpak list 2>/dev/null | grep -q md.obsidian.Obsidian; then
          ok "Obsidian déjà installé (Flatpak)"
          return 0
        fi
        echo "  Installation d'Obsidian via Flatpak..."
        if flatpak install -y flathub md.obsidian.Obsidian; then
          ok "Obsidian installé (Flatpak)"
        else
          warn "Échec Flatpak — télécharge manuellement depuis obsidian.md"
        fi
      elif [ "${PKG_MGR:-}" = "pacman" ]; then
        warn "Obsidian disponible via AUR : yay -S obsidian"
        info "Installe-le manuellement puis relance ce script"
      else
        warn "Obsidian non installé — télécharge l'AppImage depuis obsidian.md"
        info "https://obsidian.md/download"
      fi
      ;;
  esac
}

# === Étape 3 : Claude Code CLI ===============================================
step3_claude_code() {
  step 3 "Installation de Claude Code CLI"

  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip installation Claude Code"
    return 0
  fi

  if command -v claude &>/dev/null; then
    ok "Claude Code déjà installé"
    return 0
  fi

  echo "  Installation de Claude Code..."
  if curl -fsSL https://claude.ai/install.sh | sh; then
    ok "Claude Code installé"
    info "Si 'claude' n'est pas trouvé après ce script, redémarre ton terminal"
  else
    warn "Échec installation Claude Code"
    info "Voir https://docs.claude.com/en/docs/claude-code/setup"
  fi
}

# === Étape 4 : Python deps ===================================================
# Trouve le meilleur Python ≥ 3.10 (3.9 est EOL depuis oct 2025 et les libs
# récentes — google-genai, anthropic — balancent des deprecation warnings).
find_python() {
  local v
  for v in 3.13 3.12 3.11 3.10; do
    if command -v "python$v" &>/dev/null; then
      echo "python$v"
      return 0
    fi
  done
  if command -v python3 &>/dev/null; then
    echo python3
    return 0
  fi
  return 1
}

step4_python_deps() {
  step 4 "Installation des dépendances Python"

  PIP_OK=false
  local python_bin
  if ! python_bin="$(find_python)"; then
    if [ "$OS" = "macos" ]; then
      warn "Python 3 introuvable. Installe-le : brew install python@3.12"
    else
      warn "Python 3 introuvable. Installe-le : sudo apt install python3 (ou équivalent)"
    fi
    return 0
  fi

  local py_version
  py_version="$("$python_bin" --version 2>&1)"
  info "Utilisation de $py_version ($python_bin)"

  "$python_bin" -m venv "$VENV_DIR" 2>/dev/null || true

  if "$VENV_DIR/bin/pip" install -q -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null; then
    ok "Paquets Python installés dans $VENV_DIR"
    PIP_OK=true
  else
    warn "Échec pip install. Pour réessayer manuellement :"
    info "  $python_bin -m venv $VENV_DIR && $VENV_DIR/bin/pip install -r requirements.txt"
  fi
}

# === Étape 5 : Vault setup ===================================================
step5_vault() {
  step 5 "Configuration du vault"

  if [ "$IS_CI" = "true" ] && [ -n "${XAIS_BRAIN_VAULT_PATH:-}" ]; then
    VAULT_PATH="$XAIS_BRAIN_VAULT_PATH"
    info "CI mode — vault path : $VAULT_PATH"
  else
    echo ""
    echo "  Où veux-tu installer ton second cerveau ?"
    info "Appuie sur Entrée pour le défaut : ~/xais-brain-vault"
    info "(ex: ~/Documents/MyVault, /Users/toi/Notes)"
    read -rp "  Chemin du vault : " VAULT_PATH
    VAULT_PATH="${VAULT_PATH:-$DEFAULT_VAULT}"
  fi
  VAULT_PATH="${VAULT_PATH/#\~/$HOME}"
  [ "${#VAULT_PATH}" -gt 1 ] && VAULT_PATH="${VAULT_PATH%/}"

  # Garde-fou : le vault ne peut pas être le repo lui-même
  local real_vault real_script
  real_vault="$(cd "$VAULT_PATH" 2>/dev/null && pwd || echo "$VAULT_PATH")"
  real_script="$(cd "$SCRIPT_DIR" 2>/dev/null && pwd)"
  if [ "$real_vault" = "$real_script" ]; then
    warn "Le vault ne peut pas être le repo lui-même. Utilisation de $DEFAULT_VAULT."
    VAULT_PATH="$DEFAULT_VAULT"
  fi

  # Garde-fou : le chemin doit être un dossier
  if [ -e "$VAULT_PATH" ] && [ ! -d "$VAULT_PATH" ]; then
    err "Ce chemin pointe sur un fichier, pas un dossier : $VAULT_PATH"
    exit 1
  fi

  # Détection vault existant
  IS_EXISTING_VAULT=false
  HAS_EXISTING_CLAUDE=false
  local has_obsidian=false
  local is_non_empty=false

  [ -d "$VAULT_PATH/.obsidian" ] && has_obsidian=true
  [ -f "$VAULT_PATH/CLAUDE.md" ] && HAS_EXISTING_CLAUDE=true
  if [ -d "$VAULT_PATH" ] && [ -n "$(ls -A "$VAULT_PATH" 2>/dev/null | grep -v '^\.DS_Store$')" ]; then
    is_non_empty=true
  fi

  if [ "$has_obsidian" = true ] || [ "$is_non_empty" = true ]; then
    IS_EXISTING_VAULT=true
    handle_existing_vault
  fi

  # Migration ancien layout : si $VAULT_PATH/skills/ existe (vieille version)
  # sans .claude/skills/, on logue un warning et laisse l'user nettoyer manuellement.
  if [ -d "$VAULT_PATH/skills" ] && [ ! -d "$VAULT_PATH/.claude/skills" ]; then
    warn "Ancien layout détecté : $VAULT_PATH/skills/"
    info "Le nouveau layout sera installé dans $VAULT_PATH/.claude/skills/"
    info "Tu peux supprimer l'ancien dossier quand tu es prêt : rm -rf \"$VAULT_PATH/skills\""
  fi

  # .obsidian/ est obligatoire : sans ce dossier, Obsidian refuse d'ouvrir
  # le path et pop "Vault not found". Vide suffit, Obsidian le remplit au
  # premier lancement (workspace.json, app.json, etc.).
  mkdir -p "$VAULT_PATH"/{inbox,daily,projects,research,archive,memory,99-Meta/Session-Debriefs,scripts/providers,.claude/skills,.claude/rules,.claude/hooks,.claude/output-styles,.obsidian}
  copy_vault_template

  if [ "$IS_EXISTING_VAULT" = true ]; then
    ok "Vault enrichi : $VAULT_PATH"
  else
    ok "Vault créé : $VAULT_PATH"
  fi
}

handle_existing_vault() {
  echo ""
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo -e "  ${CYAN}Vault existant détecté : $VAULT_PATH${RESET}"
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "  Le script va :"
  echo -e "  ${GREEN}+${RESET} Ajouter les dossiers manquants (inbox/, daily/, etc.)"
  echo -e "  ${GREEN}+${RESET} Installer 11 slash commands + 2 hooks FR"
  echo -e "  ${GREEN}+${RESET} Copier les scripts dans scripts/"
  echo -e "  ${GREEN}+${RESET} Créer vault-config.json (source de vérité structurée)"
  if [ "$HAS_EXISTING_CLAUDE" = true ]; then
    local preview="CLAUDE.md.backup-$(date +%Y-%m-%d-%H%M%S)"
    echo -e "  ${ORANGE}!${RESET} Backup ton CLAUDE.md actuel → $preview"
    echo -e "  ${ORANGE}!${RESET} Installer le nouveau template (lance /vault-setup ensuite)"
  fi
  echo ""
  echo -e "  ${WHITE}Ne touchera pas :${RESET}"
  echo "  - Tes notes existantes (dans inbox/, daily/, projects/, etc.)"
  echo "  - Tes plugins, thèmes, settings Obsidian (.obsidian/)"
  echo ""
  if [ "$IS_CI" = "true" ]; then
    ANSWER="${XAIS_BRAIN_EXISTING_VAULT:-O}"
    info "CI mode — auto-réponse vault existant : $ANSWER"
  else
    read -rp "  Continuer ? [O/n] : " ANSWER
    ANSWER="${ANSWER:-O}"
  fi
  if [[ ! "$ANSWER" =~ ^[OoYy] ]]; then
    info "Installation annulée. Ton vault est intact."
    exit 0
  fi

  if [ "$HAS_EXISTING_CLAUDE" = true ]; then
    BACKUP_NAME="CLAUDE.md.backup-$(date +%Y-%m-%d-%H%M%S)"
    cp "$VAULT_PATH/CLAUDE.md" "$VAULT_PATH/$BACKUP_NAME"
    ok "Backup → $BACKUP_NAME"
  fi
}

copy_vault_template() {
  safe_cp "$SCRIPT_DIR/vault-template/CLAUDE.md" "$VAULT_PATH/CLAUDE.md"

  # MEMORY.md : seulement si neuf, ne jamais écraser un existant
  if [ "$IS_EXISTING_VAULT" = false ] || [ ! -f "$VAULT_PATH/MEMORY.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/MEMORY.md" "$VAULT_PATH/MEMORY.md"
  fi
  if [ ! -f "$VAULT_PATH/memory/README.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/memory/README.md" "$VAULT_PATH/memory/README.md"
  fi
  if [ ! -f "$VAULT_PATH/.claude/rules/README.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/.claude/rules/README.md" "$VAULT_PATH/.claude/rules/README.md"
  fi

  # vault-config.json : source de vérité structurée. Ne jamais écraser
  # un existant (step7_llm_config le mergera plus tard).
  if [ ! -f "$VAULT_PATH/vault-config.json" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/vault-config.json" "$VAULT_PATH/vault-config.json"
  fi

  # Scripts Python (orchestrateur + providers + web clipper)
  safe_cp "$SCRIPT_DIR/scripts/file_intel.py" "$VAULT_PATH/scripts/file_intel.py"
  safe_cp "$SCRIPT_DIR/scripts/web_clip.py" "$VAULT_PATH/scripts/web_clip.py"
  for f in __init__.py base.py _prompts.py gemini_provider.py claude_provider.py openai_provider.py; do
    safe_cp "$SCRIPT_DIR/scripts/providers/$f" "$VAULT_PATH/scripts/providers/$f"
  done

  # 99-Meta/ : piste d'audit du vault (audit, fact-check log, session debriefs)
  # Ne jamais écraser si déjà existant (l'user peut avoir coché des cases dans Audit.md
  # ou ajouté des entrées manuelles dans Fact-Check-Log.md).
  if [ ! -f "$VAULT_PATH/99-Meta/README.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/99-Meta/README.md" "$VAULT_PATH/99-Meta/README.md"
  fi
  if [ ! -f "$VAULT_PATH/99-Meta/Audit.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/99-Meta/Audit.md" "$VAULT_PATH/99-Meta/Audit.md"
  fi
  if [ ! -f "$VAULT_PATH/99-Meta/Fact-Check-Log.md" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/99-Meta/Fact-Check-Log.md" "$VAULT_PATH/99-Meta/Fact-Check-Log.md"
  fi
  if [ ! -f "$VAULT_PATH/99-Meta/Session-Debriefs/.gitkeep" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/99-Meta/Session-Debriefs/.gitkeep" "$VAULT_PATH/99-Meta/Session-Debriefs/.gitkeep"
  fi
}

# === Étape 6 : Skills install ================================================
step6_skills() {
  step 6 "Installation des slash commands, hooks et output-styles"

  local skills=(vault-setup daily tldr file-intel inbox-zero memory-add humanise import-vault client project clip)
  local src="$SCRIPT_DIR/vault-template/.claude/skills"

  for skill in "${skills[@]}"; do
    # Vault local
    mkdir -p "$VAULT_PATH/.claude/skills/$skill"
    safe_cp "$src/$skill/SKILL.md" "$VAULT_PATH/.claude/skills/$skill/SKILL.md"

    # Global (utilisable depuis n'importe quel dossier)
    mkdir -p "$HOME/.claude/skills/$skill"
    safe_cp "$src/$skill/SKILL.md" "$HOME/.claude/skills/$skill/SKILL.md"
  done

  ok "${#skills[@]} skills installés dans le vault"
  ok "${#skills[@]} skills installés globalement (~/.claude/skills/)"

  # Hooks FR : session-init + skill-discovery
  mkdir -p "$VAULT_PATH/.claude/hooks"
  for hook in session-init.sh skill-discovery.sh; do
    safe_cp "$SCRIPT_DIR/vault-template/.claude/hooks/$hook" "$VAULT_PATH/.claude/hooks/$hook"
    chmod +x "$VAULT_PATH/.claude/hooks/$hook" 2>/dev/null || true
  done
  ok "2 hooks FR installés (session-init, skill-discovery)"

  # Output style Coach FR
  mkdir -p "$VAULT_PATH/.claude/output-styles"
  safe_cp "$SCRIPT_DIR/vault-template/.claude/output-styles/coach.md" "$VAULT_PATH/.claude/output-styles/coach.md"
  ok "Output style Coach FR installé"

  # settings.json du vault : on ne l'écrase jamais si l'user l'a modifié
  if [ ! -f "$VAULT_PATH/.claude/settings.json" ]; then
    safe_cp "$SCRIPT_DIR/vault-template/.claude/settings.json" "$VAULT_PATH/.claude/settings.json"
    ok "settings.json installé (permissions + hooks déclarés)"
  else
    info "settings.json existant préservé"
  fi
}

# === Étape 7 : LLM config ====================================================
step7_llm_config() {
  step 7 "Configuration du LLM pour file-intel"

  if [ "$IS_CI" = "true" ]; then
    LLM_CHOICE="${XAIS_BRAIN_LLM_PROVIDER:-4}"
    info "CI mode — LLM provider : $LLM_CHOICE"
  else
    echo ""
    echo "  Quel LLM veux-tu utiliser pour traiter tes fichiers ?"
    echo ""
    echo "  1) Gemini  — quota gratuit (selon dispo Google AI Studio)"
    echo -e "             ${DIM}https://aistudio.google.com/apikey${RESET}"
    echo "  2) Claude  — payant, qualité supérieure"
    echo -e "             ${DIM}https://console.anthropic.com/${RESET}"
    echo "  3) OpenAI  — payant"
    echo -e "             ${DIM}https://platform.openai.com/api-keys${RESET}"
    echo "  4) Skip    — configurer plus tard dans .env"
    echo ""
    read -rp "  Choix [1-4] (défaut 1) : " LLM_CHOICE
    LLM_CHOICE="${LLM_CHOICE:-1}"
  fi

  local llm_name key_var key_url
  case "$LLM_CHOICE" in
    1)
      llm_name="gemini"
      key_var="GOOGLE_API_KEY"
      key_url="https://aistudio.google.com/apikey"
      ;;
    2)
      llm_name="claude"
      key_var="ANTHROPIC_API_KEY"
      key_url="https://console.anthropic.com/"
      ;;
    3)
      llm_name="openai"
      key_var="OPENAI_API_KEY"
      key_url="https://platform.openai.com/api-keys"
      ;;
    4)
      info "Skip — édite $VAULT_PATH/.env quand tu seras prêt"
      safe_cp "$SCRIPT_DIR/.env.example" "$VAULT_PATH/.env"
      return 0
      ;;
    *)
      warn "Choix invalide, on prend Gemini par défaut"
      llm_name="gemini"
      key_var="GOOGLE_API_KEY"
      key_url="https://aistudio.google.com/apikey"
      ;;
  esac

  if [ "$IS_CI" = "true" ]; then
    API_KEY=""
    info "CI mode — skip saisie clé API"
  else
    echo ""
    echo -e "  ${CYAN}Récupère ta clé ici : $key_url${RESET}"
    info "Ta clé sera invisible pendant la saisie. C'est normal."
    echo ""
    read -rsp "  Colle ta clé $key_var (ou Entrée pour skip) : " API_KEY
    echo ""
  fi

  # Trim whitespace (le copier-coller ajoute parfois des espaces)
  API_KEY="$(echo "$API_KEY" | tr -d '[:space:]')"

  # Écriture sécurisée (printf gère les caractères spéciaux)
  {
    printf 'LLM_PROVIDER=%s\n' "$llm_name"
    printf '%s=%s\n' "$key_var" "$API_KEY"
  } > "$VAULT_PATH/.env"

  # Merge le provider dans vault-config.json (source de vérité structurée)
  if command -v python3 &>/dev/null; then
    python3 - "$VAULT_PATH" "$llm_name" <<'PYEOF' 2>/dev/null || true
import json, sys, os
from datetime import date
vault, provider = sys.argv[1], sys.argv[2]
cfg_path = os.path.join(vault, "vault-config.json")
try:
    with open(cfg_path) as f:
        cfg = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    cfg = {
        "version": "0.2",
        "folders": {
            "inbox": "inbox", "daily": "daily", "projects": "projects",
            "research": "research", "archive": "archive", "memory": "memory"
        },
        "preferences": {"coachMode": False, "autoCommit": False},
        "adoptedVault": False,
    }
cfg.setdefault("user", {"name": None, "workMode": None})
cfg.setdefault("folders", {
    "inbox": "inbox", "daily": "daily", "projects": "projects",
    "research": "research", "archive": "archive", "memory": "memory"
})
cfg.setdefault("preferences", {"coachMode": False, "autoCommit": False})
cfg["llm"] = {"provider": provider, "model": cfg.get("llm", {}).get("model")}
# setupDate uniquement si absent (preserve l'existant à chaque relance)
if not cfg.get("setupDate"):
    cfg["setupDate"] = date.today().isoformat()
with open(cfg_path, "w") as f:
    json.dump(cfg, f, indent=2)
PYEOF
  fi

  if [ -n "$API_KEY" ]; then
    ok "LLM configuré : $llm_name (clé sauvegardée, masquée)"
  else
    warn "Clé non fournie — ajoute-la dans $VAULT_PATH/.env avant /file-intel"
  fi
}

# === Étape 8 : Import fichiers ===============================================
step8_import() {
  step 8 "Import de fichiers existants (optionnel)"

  if [ "$IS_CI" = "true" ]; then
    IMPORT_FOLDER="${XAIS_BRAIN_IMPORT_FOLDER:-}"
    info "CI mode — import folder : '${IMPORT_FOLDER:-skip}'"
  else
    echo ""
    echo "  As-tu un dossier de fichiers à importer ? (PDFs, Word, etc.)"
    info "Le LLM configuré va les synthétiser en notes Markdown dans inbox/"
    echo ""
    read -rp "  Chemin du dossier (ou Entrée pour skip) : " IMPORT_FOLDER
  fi

  if [ -z "$IMPORT_FOLDER" ]; then
    return 0
  fi

  IMPORT_FOLDER="${IMPORT_FOLDER/#\~/$HOME}"
  if [ ! -d "$IMPORT_FOLDER" ]; then
    warn "Dossier introuvable : $IMPORT_FOLDER"
    return 0
  fi

  if [ "${PIP_OK:-false}" != true ]; then
    warn "Les paquets Python ne sont pas installés — import impossible"
    info "Pour le faire manuellement plus tard :"
    info "  $VENV_DIR/bin/python3 $VAULT_PATH/scripts/file_intel.py \"$IMPORT_FOLDER\" \"$VAULT_PATH/inbox\""
    return 0
  fi

  echo ""
  echo "  Traitement en cours..."
  if "$VENV_DIR/bin/python3" "$VAULT_PATH/scripts/file_intel.py" \
       "$IMPORT_FOLDER" "$VAULT_PATH/inbox"; then
    ok "Fichiers traités → $VAULT_PATH/inbox"
    info "Lance Claude Code dans le vault et tape /inbox-zero pour les trier"
  else
    warn "Échec du traitement — vérifie ta clé API et réessaie manuellement"
  fi
}

# === Étape 9 : Kepano skills =================================================
step9_kepano() {
  step 9 "Skills Obsidian de Kepano (optionnel)"

  if [ "$IS_CI" = "true" ]; then
    ANSWER="${XAIS_BRAIN_KEPANO:-n}"
    info "CI mode — Kepano skills : $ANSWER"
  else
    echo ""
    echo "  Kepano (Steph Ango), CEO d'Obsidian, publie des skills officiels"
    echo "  qui apprennent à Claude Code à naviguer dans ton vault via le CLI."
    echo ""
    info "Slash commands ajoutés : obsidian-cli, obsidian-markdown, obsidian-bases, json-canvas, defuddle"
    info "(commandes de lecture seule — rien n'est envoyé ailleurs)"
    echo ""
    read -rp "  Installer les skills Kepano ? [O/n] : " ANSWER
    ANSWER="${ANSWER:-O}"
  fi

  if [[ ! "$ANSWER" =~ ^[OoYy] ]]; then
    info "Skip — installable plus tard depuis github.com/kepano/obsidian-skills"
    return 0
  fi

  echo "  Téléchargement..."
  local tmp
  tmp="$(mktemp -d)"
  if git clone --depth=1 https://github.com/kepano/obsidian-skills.git "$tmp/obsidian-skills" &>/dev/null; then
    for skill_dir in "$tmp/obsidian-skills/skills"/*/; do
      local skill_name
      skill_name="$(basename "$skill_dir")"
      mkdir -p "$VAULT_PATH/.claude/skills/$skill_name" "$HOME/.claude/skills/$skill_name"
      cp "$skill_dir/SKILL.md" "$VAULT_PATH/.claude/skills/$skill_name/SKILL.md" 2>/dev/null || true
      cp "$skill_dir/SKILL.md" "$HOME/.claude/skills/$skill_name/SKILL.md" 2>/dev/null || true
    done
    rm -rf "$tmp"
    ok "Skills Kepano installés (vault + global)"
  else
    rm -rf "$tmp"
    warn "Impossible de joindre GitHub"
    info "Optionnel — ton vault marche sans"
  fi
}

# === Étape 10 : CLI wrapper (xb) =============================================
step10_cli() {
  step 10 "Installation du CLI wrapper (xb)"

  if [ ! -f "$SCRIPT_DIR/vault-cli.sh" ]; then
    warn "vault-cli.sh introuvable dans le repo — skip"
    return 0
  fi

  local cli_dir="$HOME/.local/bin"
  local cli_target="$cli_dir/xb"
  mkdir -p "$cli_dir"
  cp "$SCRIPT_DIR/vault-cli.sh" "$cli_target"
  chmod +x "$cli_target"
  ok "CLI installé : xb (dans $cli_dir/)"

  # Vérifier si ~/.local/bin est dans le PATH
  if ! echo "$PATH" | tr ':' '\n' | grep -qx "$cli_dir"; then
    echo ""
    warn "\$HOME/.local/bin n'est pas dans ton PATH."
    info "Ajoute cette ligne à ton ~/.zshrc (ou ~/.bashrc) :"
    echo ""
    echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${RESET}"
    echo ""
    info "Puis redémarre ton terminal ou : source ~/.zshrc"
  fi
}

# === Vérification finale =====================================================
verify_install() {
  echo ""
  echo -e "  ${WHITE}Vérification de l'installation...${RESET}"
  info "(Si quelque chose a échoué, relance setup.sh sans risque.)"
  echo ""

  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip vérifications Obsidian et Claude Code"
  else
    # Obsidian check
    case "$OS" in
      macos)
        if brew list --cask obsidian &>/dev/null 2>&1 || [ -d /Applications/Obsidian.app ]; then
          ok "Obsidian"
        else
          err "Obsidian — réinstalle : brew install --cask obsidian"
        fi
        ;;
      linux)
        if command -v obsidian &>/dev/null || (command -v flatpak &>/dev/null && flatpak list 2>/dev/null | grep -q md.obsidian.Obsidian); then
          ok "Obsidian"
        else
          warn "Obsidian non détecté — télécharge depuis obsidian.md"
        fi
        ;;
    esac

    if command -v claude &>/dev/null; then
      ok "Claude Code  $(claude --version 2>/dev/null | head -1)"
    else
      warn "Claude Code pas dans le PATH — redémarre le terminal puis : claude"
    fi
  fi

  if [ -x "$VENV_DIR/bin/python3" ]; then
    ok "$("$VENV_DIR/bin/python3" --version 2>&1) (venv)"
  elif command -v python3 &>/dev/null; then
    ok "$(python3 --version 2>&1)"
  else
    if [ "$OS" = "macos" ]; then
      err "Python 3 introuvable — brew install python@3.12"
    else
      err "Python 3 introuvable — sudo apt install python3 (ou équivalent)"
    fi
  fi

  if [ -f "$VAULT_PATH/CLAUDE.md" ]; then
    ok "Vault  $VAULT_PATH"
  else
    err "Fichiers du vault manquants à $VAULT_PATH"
  fi

  if [ -f "$VAULT_PATH/vault-config.json" ]; then
    ok "vault-config.json"
  else
    warn "vault-config.json absent"
  fi

  local skill_count
  skill_count="$(find "$VAULT_PATH/.claude/skills" -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l | tr -d ' ')"
  ok "$skill_count skills installés"

  local hook_count
  hook_count="$(find "$VAULT_PATH/.claude/hooks" -maxdepth 1 -type f -name '*.sh' 2>/dev/null | wc -l | tr -d ' ')"
  if [ "${hook_count:-0}" -ge 2 ] 2>/dev/null; then
    ok "$hook_count hooks FR installés"
  else
    warn "Hooks FR manquants"
  fi

  if command -v xb &>/dev/null; then
    ok "CLI wrapper  xb ($(xb version 2>/dev/null))"
  elif [ -x "$HOME/.local/bin/xb" ]; then
    ok "CLI wrapper  xb (installé, pas encore dans le PATH)"
  else
    warn "CLI wrapper xb non installé"
  fi
}

# === Avertissements ==========================================================
print_warnings() {
  if [ "$IS_CI" = "true" ]; then return 0; fi
  echo ""
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo -e "  ${ORANGE}IMPORTANT — À lire avant d'utiliser :${RESET}"
  echo ""
  echo -e "  ${WHITE}Si tu utilises Obsidian Sync / iCloud / Dropbox :${RESET}"
  echo "  Exclus ces dossiers de la sync (sinon boucle récursive) :"
  echo -e "  ${CYAN}.claude/${RESET}  ${CYAN}scripts/${RESET}  ${CYAN}.env${RESET}"
  echo ""
  echo "  Dans Obsidian → Settings → Sync → Excluded folders"
  echo "  Ajoute : .claude, scripts"
  echo ""
  echo -e "  ${RED}Pourquoi ?${RESET} Si .claude/ se sync, ça crée une boucle récursive qui peut"
  echo "  bloater ton vault et corrompre le contexte de Claude."
  echo ""
  echo "  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
}

# === Done ====================================================================
print_done() {
  if [ "${IS_EXISTING_VAULT:-false}" = true ]; then
    echo -e "  ${GREEN}✅ Ton vault est upgradé.${RESET}"
  else
    echo -e "  ${GREEN}✅ Ton second cerveau est prêt.${RESET}"
  fi
  echo ""
  echo -e "  ${WHITE}Ce que tu obtiens :${RESET}"
  echo "  - 11 slash commands : /vault-setup /daily /tldr /file-intel /inbox-zero /memory-add /humanise /import-vault /project /client /clip"
  echo "  - 2 hooks FR : session-init (contexte au démarrage) + skill-discovery"
  echo "  - Output style : Coach FR (tape /output-style pour l'activer)"
  echo "  - CLAUDE.md template (perso via /vault-setup)"
  echo "  - vault-config.json (source de vérité structurée)"
  echo "  - Système de mémoire indexé (MEMORY.md + memory/)"
  echo "  - Scripts Python multi-LLM (Gemini/Claude/OpenAI)"
  echo "  - CLI wrapper : xb (raccourcis depuis n'importe quel dossier)"
  if [ "${IS_EXISTING_VAULT:-false}" = true ] && [ "${HAS_EXISTING_CLAUDE:-false}" = true ]; then
    echo "  - Ton ancien CLAUDE.md sauvegardé : ${BACKUP_NAME:-}"
  fi
  echo ""
  echo -e "  ${WHITE}Vault :${RESET} $VAULT_PATH"
  echo ""
  echo -e "  ${WHITE}Prochaines étapes :${RESET}"
  echo -e "  ${CYAN}1.${RESET} Ouvre Obsidian → Open folder as vault → ${DIM}$VAULT_PATH${RESET}"
  echo -e "  ${CYAN}2.${RESET} Dans Obsidian : engrenage (bas-gauche) → General → Enable CLI"
  echo -e "  ${CYAN}3.${RESET} Dans un terminal :"
  echo -e "     ${DIM}cd \"$VAULT_PATH\" && claude${RESET}"
  echo -e "  ${CYAN}4.${RESET} Tape ${DIM}/vault-setup${RESET} — Claude t'interviewe et personnalise ton vault"
  echo -e "  ${CYAN}5.${RESET} Essaie le CLI : ${DIM}xb status${RESET} — état du vault depuis n'importe où"
  echo ""
  echo -e "  ${WHITE}Pour éditer tes clés API plus tard :${RESET}"
  if [ "$OS" = "macos" ]; then
    echo -e "     ${DIM}open -e \"$VAULT_PATH/.env\"${RESET}  ${DIM}(le fichier est caché, préfixé par un point)${RESET}"
  else
    echo -e "     ${DIM}nano \"$VAULT_PATH/.env\"${RESET}  ${DIM}(le fichier est caché, préfixé par un point)${RESET}"
  fi
  echo ""
  info "Ce script est safe à relancer — il détecte les vaults existants et n'écrase rien."
  echo ""
}

open_obsidian_app() {
  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip ouverture Obsidian"
    return 0
  fi

  case "$OS" in
    macos)
      # Enregistre le vault dans le registre Obsidian
      # (~/Library/Application Support/obsidian/obsidian.json) pour qu'il s'ouvre
      # directement au lancement, plutôt que de pop "Vault not found".
      # Safe : backup + atomic write + fallback silencieux sur open -a si ça foire.

      # Si Obsidian tourne déjà, il garde son état en RAM et écrasera notre fichier
      # au prochain quit. On prévient l'utilisateur et on n'écrit pas pour rien.
      local obsidian_running=false
      if pgrep -x Obsidian &>/dev/null; then
        obsidian_running=true
      fi

      python3 - "$VAULT_PATH" <<'PYEOF' 2>/dev/null || true
import json, os, secrets, shutil, sys, tempfile, time

vault = sys.argv[1]
config_dir = os.path.expanduser("~/Library/Application Support/obsidian")
config = os.path.join(config_dir, "obsidian.json")

try:
    with open(config) as f:
        data = json.load(f)
    shutil.copy2(config, config + ".bak")
except FileNotFoundError:
    data = {}
except Exception:
    sys.exit(0)

vaults = data.setdefault("vaults", {})

# Si déjà enregistré, on réutilise l'id au lieu d'en créer un doublon
target_id = next((vid for vid, v in vaults.items() if v.get("path") == vault), None)
if target_id is None:
    target_id = secrets.token_hex(8)
    vaults[target_id] = {"path": vault, "ts": int(time.time() * 1000)}

# Marque ce vault comme celui à ouvrir, désélectionne les autres
for vid, v in vaults.items():
    if vid == target_id:
        v["open"] = True
    else:
        v.pop("open", None)

# Atomic write : tempfile dans le même dossier puis os.replace
try:
    os.makedirs(config_dir, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=config_dir, prefix=".obsidian.json.", suffix=".tmp")
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)
    os.replace(tmp, config)
except Exception:
    if 'tmp' in dir() and os.path.exists(tmp):
        try:
            os.unlink(tmp)
        except OSError:
            pass
    sys.exit(0)
PYEOF

      if [ "$obsidian_running" = true ]; then
        echo ""
        warn "Obsidian était déjà en cours d'exécution."
        info "Quitte-le complètement (Cmd+Q) puis relance-le pour qu'il s'ouvre directement sur ton vault."
        info "Sinon, ouvre ton vault manuellement : Open folder as vault → $VAULT_PATH"
      fi

      open -a Obsidian 2>/dev/null || true
      ;;

    linux)
      # Pas de registration automatique sur Linux (pas de registre central Obsidian)
      # Juste ouvrir si Obsidian est disponible
      if command -v obsidian &>/dev/null; then
        obsidian "$VAULT_PATH" &
      elif command -v flatpak &>/dev/null && flatpak list 2>/dev/null | grep -q md.obsidian.Obsidian; then
        flatpak run md.obsidian.Obsidian "$VAULT_PATH" &
      else
        info "Ouvre Obsidian manuellement → Open folder as vault → $VAULT_PATH"
      fi
      ;;
  esac
}

# === Main ====================================================================
main() {
  bootstrap_if_needed
  trap cleanup_bootstrap EXIT

  show_banner
  detect_os
  step1_package_manager
  step2_obsidian
  step3_claude_code
  step4_python_deps
  step5_vault
  step6_skills
  step7_llm_config
  step8_import
  step9_kepano
  step10_cli
  verify_install
  print_warnings
  print_done
  open_obsidian_app
}

main "$@"
