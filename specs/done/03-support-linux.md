# Piste 3 — Support Linux

> Priorite : MOYENNE | Effort : ~1.5h | Dependances : Piste 2 (CI) pour validation automatisee

## Probleme

`setup.sh` est macOS-only (`check_os` exit 1 sur tout sauf `darwin`). Brew, Obsidian via cask, `open -a`, `date -v`, `pgrep -x Obsidian`, la registration dans `~/Library/Application Support/obsidian/` — tout est macOS-specifique. Pourtant le coeur de xais-brain (vault structure, skills, hooks, Python scripts) est 100% portable.

## Objectif

Rendre `setup.sh` compatible Linux (Ubuntu/Debian et Fedora/Arch en priorite) tout en gardant le flow macOS intact. Les utilisateurs Linux representent une part significative des devs utilisant Claude Code en CLI.

---

## Approche : branches conditionnelles par OS

### Detection OS (remplacer `check_os`)

```bash
detect_os() {
  case "$OSTYPE" in
    darwin*)  OS="macos" ;;
    linux*)   OS="linux" ;;
    *)
      err "OS non supporte : $OSTYPE"
      info "xais-brain supporte macOS et Linux."
      exit 1
      ;;
  esac
  export OS
}
```

### Etape 1 : Package manager (remplacer `step1_brew`)

```bash
step1_package_manager() {
  step 1 "Verification du gestionnaire de paquets"
  case "$OS" in
    macos)
      if ! command -v brew &>/dev/null; then
        echo "  Installation de Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        ok "Homebrew installe"
      else
        ok "Homebrew deja installe"
      fi
      ;;
    linux)
      # Detecter le package manager
      if command -v apt-get &>/dev/null; then
        PKG_MGR="apt"
        ok "apt detecte (Debian/Ubuntu)"
      elif command -v dnf &>/dev/null; then
        PKG_MGR="dnf"
        ok "dnf detecte (Fedora/RHEL)"
      elif command -v pacman &>/dev/null; then
        PKG_MGR="pacman"
        ok "pacman detecte (Arch)"
      else
        warn "Gestionnaire de paquets non detecte"
        info "Installe les dependances manuellement (voir README)"
      fi
      ;;
  esac
}
```

### Etape 2 : Obsidian (adaptation Linux)

```bash
step2_obsidian() {
  step 2 "Installation d'Obsidian"
  case "$OS" in
    macos)
      # Code actuel : brew install --cask obsidian (inchange)
      ;;
    linux)
      if command -v obsidian &>/dev/null || [ -f /usr/bin/obsidian ]; then
        ok "Obsidian deja installe"
        return 0
      fi
      # Flatpak est le moyen le plus universel sur Linux
      if command -v flatpak &>/dev/null; then
        echo "  Installation d'Obsidian via Flatpak..."
        if flatpak install -y flathub md.obsidian.Obsidian; then
          ok "Obsidian installe (Flatpak)"
        else
          warn "Echec Flatpak — telecharge manuellement depuis obsidian.md"
        fi
      elif [ "$PKG_MGR" = "pacman" ]; then
        warn "Obsidian disponible via AUR : yay -S obsidian"
        info "Installe-le manuellement puis relance ce script"
      else
        warn "Obsidian non installe — telecharge l'AppImage depuis obsidian.md"
        info "https://obsidian.md/download"
      fi
      ;;
  esac
}
```

### Etape 3 : Claude Code (identique, deja portable)

Le script `curl -fsSL https://claude.ai/install.sh | sh` fonctionne deja sur Linux. Aucune modification.

### Corrections date BSD vs GNU

`session-init.sh` utilise `date -v-1d` (BSD/macOS). Le fallback GNU existe deja :

```bash
# Ligne 7 actuelle — deja correct :
export YESTERDAY=$(date -v-1d +%Y-%m-%d 2>/dev/null || date -d "yesterday" +%Y-%m-%d 2>/dev/null || echo "")
```

Verifier que tous les autres usages de `date` dans le repo sont compatibles.

### `open_obsidian_app` (adaptation Linux)

```bash
open_obsidian_app() {
  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip ouverture Obsidian"
    return 0
  fi

  case "$OS" in
    macos)
      # Code actuel : registration obsidian.json + open -a Obsidian
      ;;
    linux)
      # Pas de registration automatique sur Linux
      # Juste ouvrir si Obsidian est disponible
      if command -v obsidian &>/dev/null; then
        obsidian "$VAULT_PATH" &
      elif command -v flatpak &>/dev/null && flatpak list | grep -q md.obsidian.Obsidian; then
        flatpak run md.obsidian.Obsidian "$VAULT_PATH" &
      else
        info "Ouvre Obsidian manuellement → Open folder as vault → $VAULT_PATH"
      fi
      ;;
  esac
}
```

### Verification finale (adaptation Linux)

`verify_install` utilise `brew list --cask` pour checker Obsidian. Ajouter la branche Linux :

```bash
# Obsidian check
case "$OS" in
  macos)
    if brew list --cask obsidian &>/dev/null 2>&1 || [ -d /Applications/Obsidian.app ]; then
      ok "Obsidian"
    else
      err "Obsidian — reinstalle : brew install --cask obsidian"
    fi
    ;;
  linux)
    if command -v obsidian &>/dev/null || (command -v flatpak &>/dev/null && flatpak list 2>/dev/null | grep -q md.obsidian.Obsidian); then
      ok "Obsidian"
    else
      warn "Obsidian non detecte — telecharge depuis obsidian.md"
    fi
    ;;
esac
```

### `xb open` (Piste 1, adaptation Linux)

```bash
cmd_open() {
  local vault="$(resolve_vault)"
  case "$OSTYPE" in
    darwin*) open -a Obsidian "$vault" ;;
    linux*)
      if command -v obsidian &>/dev/null; then
        obsidian "$vault" &
      elif command -v xdg-open &>/dev/null; then
        xdg-open "$vault" &
      else
        echo "Ouvre Obsidian manuellement sur : $vault"
      fi
      ;;
  esac
}
```

---

## Fichiers a modifier

| Fichier | Modification |
|---------|-------------|
| `setup.sh` | Remplacer `check_os` par `detect_os`, adapter steps 1/2/9 et `open_obsidian_app`/`verify_install` avec branches `case "$OS"` |
| `vault-cli.sh` | Adapter `cmd_open` pour Linux (si Piste 1 implementee) |
| `README.md` | Retirer le badge "macOS only", ajouter "macOS + Linux" |
| `.github/workflows/ci.yml` | Activer le job `test-linux` (si Piste 2 implementee) |

## Ce qui ne change PAS

- `session-init.sh` : deja compatible (fallback GNU date present)
- `skill-discovery.sh` : bash pur, portable
- `file_intel.py` + `providers/` : Python pur, portable
- `vault-config.json`, `settings.json`, tous les SKILL.md : JSON/Markdown, portable
- `coach.md` : Markdown, portable

## Tests specifiques Linux

Ajouter dans `tests/test_setup.sh` :

```bash
test_linux_specific() {
  if [ "$OS" != "linux" ]; then
    echo "SKIP: test Linux uniquement"
    return 0
  fi
  # Verifier que le script n'appelle pas de commandes macOS
  ! grep -q "brew " "$TEST_VAULT/.claude/hooks/session-init.sh" && ((PASS++)) || ((FAIL++))
  # Verifier que date GNU fonctionne
  date -d "yesterday" +%Y-%m-%d >/dev/null 2>&1 && ((PASS++)) || ((FAIL++))
}
```

## Criteres de succes

- [ ] `setup.sh` termine sans erreur sur Ubuntu 22.04+ (CI ou VM)
- [ ] Obsidian est detecte (ou installe via Flatpak) sans Homebrew
- [ ] Les hooks fonctionnent sans `date -v` BSD
- [ ] `open_obsidian_app` ne crash pas sur Linux (fallback silencieux)
- [ ] Le badge README passe de "macOS" a "macOS + Linux"
- [ ] Le CI GitHub Actions passe sur `ubuntu-latest`
