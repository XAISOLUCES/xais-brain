# Piste 1 — vault-cli.sh : CLI wrapper pour xais-brain

> Priorite : HAUTE | Effort : ~1h | Dependances : aucune

## Probleme

L'utilisateur doit aujourd'hui `cd ~/mon-vault && claude` puis taper des slash commands. Aucun raccourci CLI pour les operations courantes. Pas de moyen de lancer `/daily` ou `/inbox-zero` en one-shot depuis n'importe ou.

## Objectif

Creer un script `vault-cli.sh` (installe comme `xb` dans le PATH) qui sert de point d'entree unique pour toutes les operations vault courantes, sans ouvrir une session Claude interactive.

## Approche technique

### Fichier : `vault-cli.sh` (nouvelle creation, racine du repo)

```bash
#!/bin/bash
# xb — CLI wrapper pour xais-brain
# Usage : xb <commande> [args...]

set -e

# Resoudre le vault path
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
  # 3. Defaut
  if [ -f "$HOME/xais-brain-vault/vault-config.json" ]; then
    echo "$HOME/xais-brain-vault"
    return 0
  fi
  echo "Erreur : vault introuvable. Definis XAIS_BRAIN_VAULT ou cd dans ton vault." >&2
  return 1
}
```

### Commandes a implementer

| Commande | Action | Implementation |
|----------|--------|----------------|
| `xb daily` | Lance `/daily` en one-shot | `claude -p "/daily" --cwd $VAULT` |
| `xb inbox` | Lance `/inbox-zero` en one-shot | `claude -p "/inbox-zero" --cwd $VAULT` |
| `xb intel <dossier>` | Lance file-intel sur un dossier | Appel direct Python (pas besoin de Claude) |
| `xb status` | Affiche l'etat du vault (inbox count, daily, dernier MEMORY) | Script bash pur |
| `xb open` | Ouvre Obsidian sur le vault | `open -a Obsidian "$VAULT"` (macOS) / `xdg-open` (Linux) |
| `xb shell` | `cd $VAULT && claude` (session interactive) | exec |
| `xb help` | Affiche l'aide | heredoc |

### `xb status` (bash pur, pas de Claude)

```bash
cmd_status() {
  local vault="$(resolve_vault)"
  local cfg="$vault/vault-config.json"
  local today=$(date +%Y-%m-%d)

  # Lire les noms de dossiers depuis vault-config.json
  local inbox_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")
  local daily_dir=$(python3 -c "import json; print(json.load(open('$cfg')).get('folders',{}).get('daily','daily'))" 2>/dev/null || echo "daily")

  local inbox_count=$(find "$vault/$inbox_dir" -maxdepth 1 -type f 2>/dev/null | wc -l | tr -d ' ')
  local has_daily="non"
  [ -f "$vault/$daily_dir/$today.md" ] && has_daily="oui"

  echo "Vault    : $(basename "$vault")"
  echo "Inbox    : $inbox_count fichier(s)"
  echo "Daily    : $has_daily ($today)"
  echo "Provider : $(python3 -c "import json; print(json.load(open('$cfg')).get('llm',{}).get('provider','non configure'))" 2>/dev/null || echo "?")"
}
```

### `xb intel` (appel Python direct)

```bash
cmd_intel() {
  local vault="$(resolve_vault)"
  local source_dir="$1"
  if [ -z "$source_dir" ]; then
    echo "Usage : xb intel <dossier_source>" >&2
    return 1
  fi
  source_dir="${source_dir/#\~/$HOME}"
  local inbox_dir=$(python3 -c "import json; print(json.load(open('$vault/vault-config.json')).get('folders',{}).get('inbox','inbox'))" 2>/dev/null || echo "inbox")
  "$HOME/.xais-brain-venv/bin/python3" "$vault/scripts/file_intel.py" "$source_dir" "$vault/$inbox_dir"
}
```

## Installation

### Modification de `setup.sh`

Ajouter une etape (ou l'integrer dans step6) :

```bash
# Installer le CLI wrapper
if [ -f "$SCRIPT_DIR/vault-cli.sh" ]; then
  local cli_target="$HOME/.local/bin/xb"
  mkdir -p "$HOME/.local/bin"
  cp "$SCRIPT_DIR/vault-cli.sh" "$cli_target"
  chmod +x "$cli_target"
  # Ecrire le vault path par defaut
  # (l'utilisateur peut override via XAIS_BRAIN_VAULT)
  ok "CLI installe : xb (dans ~/.local/bin/)"
  info "Si 'xb' n'est pas trouve, ajoute ~/.local/bin a ton PATH"
fi
```

### PATH warning

Verifier si `~/.local/bin` est dans le PATH. Si non, afficher un warning avec la commande a ajouter dans `.zshrc` / `.bashrc`.

## Fichiers a creer/modifier

| Fichier | Action |
|---------|--------|
| `vault-cli.sh` | **CREER** — script principal (~120 lignes) |
| `setup.sh` | **MODIFIER** — ajouter installation du CLI dans step6 ou step finale |
| `README.md` | **MODIFIER** — ajouter section "CLI rapide" avec exemples `xb` |

## Cas limites

- **Pas de Claude Code installe** : `xb status`, `xb intel`, `xb open` marchent sans. Seuls `xb daily/inbox/shell` echouent proprement.
- **Plusieurs vaults** : `XAIS_BRAIN_VAULT` permet de choisir. Sans variable, le vault du cwd est utilise, sinon le defaut.
- **Linux** : `xb open` doit detecter l'OS et utiliser `xdg-open` (voir Piste 2).

## Criteres de succes

- [ ] `xb status` affiche l'etat du vault depuis n'importe quel dossier
- [ ] `xb intel ~/Documents` lance file-intel sans session Claude
- [ ] `xb daily` lance une session Claude one-shot avec `/daily`
- [ ] `xb help` affiche toutes les commandes disponibles
- [ ] `setup.sh` installe `xb` dans `~/.local/bin/`
- [ ] README documente les commandes `xb`
