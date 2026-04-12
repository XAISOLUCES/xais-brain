# Piste 2 — CI, tests et mode non-interactif

> Priorite : HAUTE | Effort : ~2h | Dependances : aucune (parallelisable avec Piste 1)

## Probleme

Aucun test automatise dans le repo. `setup.sh` est entierement interactif (9 `read -rp`). Impossible de valider les changements avant un push. Aucun CI. Les bugs de docs (skill count "8" au lieu de "10", formats fictifs dans file-intel) ont ete decouverts manuellement apres coup.

## Objectif

1. Rendre `setup.sh` executable en mode non-interactif (CI/scripting)
2. Creer une suite de tests bash pour valider le setup sur un vault frais
3. Configurer GitHub Actions pour lancer ces tests a chaque push/PR

---

## Phase A : Mode non-interactif pour `setup.sh`

### Approche

Ajouter un flag `--non-interactive` (ou detecter `CI=true`) qui fournit des reponses par defaut a tous les `read -rp`.

### Variables d'environnement CI

```bash
# Si definis, setup.sh skip les prompts interactifs
XAIS_BRAIN_CI=true              # Active le mode non-interactif
XAIS_BRAIN_VAULT_PATH=/tmp/test-vault  # Path du vault (pas de read)
XAIS_BRAIN_LLM_PROVIDER=skip   # Skip config LLM (pas de cle en CI)
XAIS_BRAIN_IMPORT_FOLDER=""     # Skip import
XAIS_BRAIN_KEPANO=no            # Skip Kepano
XAIS_BRAIN_EXISTING_VAULT=yes   # Auto-accepter vault existant
```

### Modifications `setup.sh`

Wrapper autour de chaque `read -rp` :

```bash
# Ajouter en haut du script, apres les constantes
IS_CI="${XAIS_BRAIN_CI:-false}"

# Helper pour les prompts conditionnels
prompt_or_default() {
  local prompt="$1"
  local default="$2"
  local var_name="$3"  # nom de la var d'env override

  if [ "$IS_CI" = "true" ] && [ -n "${!var_name:-}" ]; then
    echo "${!var_name}"
    return 0
  fi
  read -rp "$prompt" REPLY
  echo "${REPLY:-$default}"
}
```

**Points de modification specifiques dans setup.sh :**

| Ligne actuelle | Variable CI | Defaut CI |
|----------------|-------------|-----------|
| `read -rp "Chemin du vault"` (step5, ~L220) | `XAIS_BRAIN_VAULT_PATH` | `/tmp/xais-brain-test` |
| `read -rp "Continuer ? [O/n]"` (handle_existing_vault, ~L299) | `XAIS_BRAIN_EXISTING_VAULT` | `O` |
| `read -rp "Choix [1-4]"` (step7, ~L396) | `XAIS_BRAIN_LLM_PROVIDER` | `4` (skip) |
| `read -rsp "Colle ta cle"` (step7, ~L433) | skip si provider=4 | - |
| `read -rp "Chemin du dossier"` (step8, ~L494) | `XAIS_BRAIN_IMPORT_FOLDER` | `""` (skip) |
| `read -rp "Installer Kepano"` (step9, ~L534) | `XAIS_BRAIN_KEPANO` | `n` |

### Garde-fou `open_obsidian_app`

En CI, ne pas tenter d'ouvrir Obsidian :

```bash
open_obsidian_app() {
  if [ "$IS_CI" = "true" ]; then
    info "CI mode — skip ouverture Obsidian"
    return 0
  fi
  # ... code existant
}
```

Idem pour `show_banner` (skip `clear` en CI qui corrompt les logs).

---

## Phase B : Suite de tests bash

### Fichier : `tests/test_setup.sh` (nouvelle creation)

Framework minimaliste : fonctions `assert_*` + compteur pass/fail.

```bash
#!/bin/bash
# Tests d'integration pour setup.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_VAULT="/tmp/xais-brain-test-$$"
PASS=0
FAIL=0

# Helpers
assert_file() { [ -f "$1" ] && ((PASS++)) || { echo "FAIL: fichier absent: $1"; ((FAIL++)); }; }
assert_dir()  { [ -d "$1" ] && ((PASS++)) || { echo "FAIL: dossier absent: $1"; ((FAIL++)); }; }
assert_exec() { [ -x "$1" ] && ((PASS++)) || { echo "FAIL: pas executable: $1"; ((FAIL++)); }; }
assert_json() { python3 -m json.tool "$1" >/dev/null 2>&1 && ((PASS++)) || { echo "FAIL: JSON invalide: $1"; ((FAIL++)); }; }
assert_contains() { grep -q "$2" "$1" && ((PASS++)) || { echo "FAIL: '$2' absent de $1"; ((FAIL++)); }; }

cleanup() { rm -rf "$TEST_VAULT"; }
trap cleanup EXIT
```

### Tests a implementer

```bash
test_fresh_install() {
  echo "=== Test : installation fraiche ==="
  export XAIS_BRAIN_CI=true
  export XAIS_BRAIN_VAULT_PATH="$TEST_VAULT"
  export XAIS_BRAIN_LLM_PROVIDER=4  # skip
  export XAIS_BRAIN_IMPORT_FOLDER=""
  export XAIS_BRAIN_KEPANO=n

  bash "$SCRIPT_DIR/setup.sh"

  # Structure vault
  assert_dir  "$TEST_VAULT"
  assert_dir  "$TEST_VAULT/inbox"
  assert_dir  "$TEST_VAULT/daily"
  assert_dir  "$TEST_VAULT/projects"
  assert_dir  "$TEST_VAULT/research"
  assert_dir  "$TEST_VAULT/archive"
  assert_dir  "$TEST_VAULT/memory"
  assert_dir  "$TEST_VAULT/.obsidian"

  # Fichiers core
  assert_file "$TEST_VAULT/CLAUDE.md"
  assert_file "$TEST_VAULT/MEMORY.md"
  assert_file "$TEST_VAULT/vault-config.json"
  assert_file "$TEST_VAULT/.env"
  assert_json "$TEST_VAULT/vault-config.json"

  # Skills (10 canoniques)
  local expected_skills=(vault-setup daily tldr file-intel inbox-zero memory-add humanise import-vault client project)
  for skill in "${expected_skills[@]}"; do
    assert_file "$TEST_VAULT/.claude/skills/$skill/SKILL.md"
  done

  # Hooks
  assert_exec "$TEST_VAULT/.claude/hooks/session-init.sh"
  assert_exec "$TEST_VAULT/.claude/hooks/skill-discovery.sh"

  # Output style
  assert_file "$TEST_VAULT/.claude/output-styles/coach.md"

  # Settings
  assert_file "$TEST_VAULT/.claude/settings.json"
  assert_json "$TEST_VAULT/.claude/settings.json"

  # Compteur dynamique
  local skill_count
  skill_count=$(find "$TEST_VAULT/.claude/skills" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
  [ "$skill_count" -eq 10 ] && ((PASS++)) || { echo "FAIL: $skill_count skills au lieu de 10"; ((FAIL++)); }
}

test_idempotent_rerun() {
  echo "=== Test : idempotence (2e run) ==="
  # Modifier CLAUDE.md pour verifier qu'il n'est pas ecrase silencieusement
  echo "# Custom content" >> "$TEST_VAULT/CLAUDE.md"
  local md5_before=$(md5sum "$TEST_VAULT/vault-config.json" | cut -d' ' -f1)

  bash "$SCRIPT_DIR/setup.sh"

  # CLAUDE.md est ecrase (comportement actuel de safe_cp)
  # vault-config.json ne doit PAS etre ecrase (step5 check)
  # Ici on verifie juste que le script ne crash pas
  assert_file "$TEST_VAULT/CLAUDE.md"
  assert_json "$TEST_VAULT/vault-config.json"
}

test_scripts_python() {
  echo "=== Test : scripts Python copies ==="
  assert_file "$TEST_VAULT/scripts/file_intel.py"
  assert_file "$TEST_VAULT/scripts/providers/__init__.py"
  assert_file "$TEST_VAULT/scripts/providers/base.py"
  assert_file "$TEST_VAULT/scripts/providers/_prompts.py"
  assert_file "$TEST_VAULT/scripts/providers/gemini_provider.py"
  assert_file "$TEST_VAULT/scripts/providers/claude_provider.py"
  assert_file "$TEST_VAULT/scripts/providers/openai_provider.py"
}

test_file_intel_dry() {
  echo "=== Test : file_intel.py --help (import check) ==="
  # Verifier que le script est importable (pas de syntax error)
  "$HOME/.xais-brain-venv/bin/python3" -c "
import sys; sys.path.insert(0, '$TEST_VAULT/scripts')
from file_intel import slugify, discover_files
assert slugify('Mon Document (v2).pdf') == 'mon-document-v2'
assert slugify('') == 'untitled'
print('OK slugify')
" && ((PASS++)) || { echo "FAIL: file_intel.py import"; ((FAIL++)); }
}

test_hook_session_init() {
  echo "=== Test : session-init.sh ==="
  local output
  output=$(cd "$TEST_VAULT" && bash .claude/hooks/session-init.sh 2>&1)
  echo "$output" | grep -q "Vault" && ((PASS++)) || { echo "FAIL: session-init pas de sortie Vault"; ((FAIL++)); }
}

test_hook_skill_discovery() {
  echo "=== Test : skill-discovery.sh ==="
  local output
  output=$(cd "$TEST_VAULT" && echo "quels skills ?" | bash .claude/hooks/skill-discovery.sh 2>&1)
  echo "$output" | grep -q "/daily" && ((PASS++)) || { echo "FAIL: skill-discovery pas de /daily"; ((FAIL++)); }
}
```

### Tests Python unitaires

### Fichier : `tests/test_file_intel.py` (nouvelle creation)

```python
"""Tests unitaires pour file_intel.py."""
import sys
from pathlib import Path

# Ajouter scripts/ au path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from file_intel import slugify, discover_files, EXTRACTORS


def test_slugify_normal():
    assert slugify("Mon Document.pdf") == "mon-document"

def test_slugify_special_chars():
    assert slugify("rapport_Q1 (2026).docx") == "rapport_q1-2026"

def test_slugify_empty():
    assert slugify("") == "untitled"

def test_slugify_accents():
    assert slugify("resume-etude.txt") == "resume-etude"

def test_extractors_keys():
    assert set(EXTRACTORS.keys()) == {".pdf", ".docx", ".txt", ".md"}

def test_discover_files_empty(tmp_path):
    assert discover_files(tmp_path) == []

def test_discover_files_mixed(tmp_path):
    (tmp_path / "doc.pdf").touch()
    (tmp_path / "notes.md").touch()
    (tmp_path / "image.png").touch()  # pas supporte
    files = discover_files(tmp_path)
    assert len(files) == 2
    names = {f.name for f in files}
    assert names == {"doc.pdf", "notes.md"}
```

---

## Phase C : GitHub Actions CI

### Fichier : `.github/workflows/ci.yml` (nouvelle creation)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-setup:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python deps
        run: |
          python3 -m venv ~/.xais-brain-venv
          ~/.xais-brain-venv/bin/pip install -r requirements.txt

      - name: Run setup.sh (non-interactive)
        env:
          XAIS_BRAIN_CI: "true"
          XAIS_BRAIN_VAULT_PATH: /tmp/xais-brain-ci
          XAIS_BRAIN_LLM_PROVIDER: "4"
          XAIS_BRAIN_IMPORT_FOLDER: ""
          XAIS_BRAIN_KEPANO: "n"
        run: bash setup.sh

      - name: Run integration tests
        run: bash tests/test_setup.sh

      - name: Run Python unit tests
        run: |
          ~/.xais-brain-venv/bin/pip install pytest
          ~/.xais-brain-venv/bin/pytest tests/test_file_intel.py -v

  test-linux:
    runs-on: ubuntu-latest
    needs: [test-setup]
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install Python deps
        run: |
          python3 -m venv ~/.xais-brain-venv
          ~/.xais-brain-venv/bin/pip install -r requirements.txt

      - name: Run setup.sh (non-interactive, Linux)
        env:
          XAIS_BRAIN_CI: "true"
          XAIS_BRAIN_VAULT_PATH: /tmp/xais-brain-ci
          XAIS_BRAIN_LLM_PROVIDER: "4"
          XAIS_BRAIN_IMPORT_FOLDER: ""
          XAIS_BRAIN_KEPANO: "n"
        run: bash setup.sh

      - name: Run Python unit tests
        run: |
          ~/.xais-brain-venv/bin/pip install pytest
          ~/.xais-brain-venv/bin/pytest tests/test_file_intel.py -v
```

---

## Fichiers a creer/modifier

| Fichier | Action |
|---------|--------|
| `setup.sh` | **MODIFIER** — ajouter mode CI (`XAIS_BRAIN_CI`), wrapper prompts, skip banner/obsidian en CI |
| `tests/test_setup.sh` | **CREER** — tests d'integration bash (~150 lignes) |
| `tests/test_file_intel.py` | **CREER** — tests unitaires Python (~40 lignes) |
| `.github/workflows/ci.yml` | **CREER** — pipeline CI GitHub Actions |

## Dependances avec les autres pistes

- **Piste 2 (Linux)** : le job `test-linux` dans le CI ne passera qu'apres l'implementation du support Linux. En attendant, commenter le job ou le marquer `continue-on-error: true`.
- **Piste 1 (vault-cli)** : ajouter des tests pour `xb` dans `test_setup.sh` une fois le CLI cree.

## Criteres de succes

- [ ] `XAIS_BRAIN_CI=true bash setup.sh` termine sans input interactif
- [ ] `tests/test_setup.sh` valide la structure complete d'un vault frais
- [ ] `tests/test_file_intel.py` passe avec pytest
- [ ] Les hooks sont testables en isolation (stdin pipe)
- [ ] GitHub Actions passe au vert sur macOS
- [ ] Le setup est idempotent (2e run ne crash pas)
