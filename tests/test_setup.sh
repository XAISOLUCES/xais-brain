#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  Tests d'intégration pour setup.sh (mode CI)
#  Usage : bash tests/test_setup.sh
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEST_VAULT="/tmp/xais-brain-test-$$"
PASS=0
FAIL=0

# === Helpers =================================================================
# Note : on utilise PASS=$((PASS+1)) au lieu de ((PASS++)) car ((0)) retourne
# exit code 1 en bash, ce qui pose problème avec set -e.
assert_file() {
  if [ -f "$1" ]; then
    PASS=$((PASS+1))
  else
    echo "FAIL: fichier absent: $1"
    FAIL=$((FAIL+1))
  fi
}

assert_dir() {
  if [ -d "$1" ]; then
    PASS=$((PASS+1))
  else
    echo "FAIL: dossier absent: $1"
    FAIL=$((FAIL+1))
  fi
}

assert_exec() {
  if [ -x "$1" ]; then
    PASS=$((PASS+1))
  else
    echo "FAIL: pas executable: $1"
    FAIL=$((FAIL+1))
  fi
}

assert_json() {
  if python3 -m json.tool "$1" >/dev/null 2>&1; then
    PASS=$((PASS+1))
  else
    echo "FAIL: JSON invalide: $1"
    FAIL=$((FAIL+1))
  fi
}

assert_contains() {
  if grep -q "$2" "$1" 2>/dev/null; then
    PASS=$((PASS+1))
  else
    echo "FAIL: '$2' absent de $1"
    FAIL=$((FAIL+1))
  fi
}

cleanup() {
  if [ -d "$TEST_VAULT" ]; then
    # Supprimer le vault de test (dossier temporaire /tmp)
    find "$TEST_VAULT" -delete 2>/dev/null || true
  fi
}
trap cleanup EXIT

# === Test 1 : Installation fraîche ==========================================
test_fresh_install() {
  echo "=== Test : installation fraîche ==="
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

  # Compteur dynamique de skills
  local skill_count
  skill_count=$(find "$TEST_VAULT/.claude/skills" -maxdepth 1 -type d | tail -n +2 | wc -l | tr -d ' ')
  if [ "$skill_count" -eq 10 ]; then
    PASS=$((PASS+1))
  else
    echo "FAIL: $skill_count skills au lieu de 10"
    FAIL=$((FAIL+1))
  fi
}

# === Test 2 : Idempotence (2e run) ==========================================
test_idempotent_rerun() {
  echo "=== Test : idempotence (2e run) ==="
  export XAIS_BRAIN_CI=true
  export XAIS_BRAIN_VAULT_PATH="$TEST_VAULT"
  export XAIS_BRAIN_LLM_PROVIDER=4
  export XAIS_BRAIN_IMPORT_FOLDER=""
  export XAIS_BRAIN_KEPANO=n
  export XAIS_BRAIN_EXISTING_VAULT=O

  # Modifier CLAUDE.md pour vérifier que le script ne crash pas
  echo "# Custom content" >> "$TEST_VAULT/CLAUDE.md"

  bash "$SCRIPT_DIR/setup.sh"

  # Le script ne doit pas crasher et les fichiers doivent rester valides
  assert_file "$TEST_VAULT/CLAUDE.md"
  assert_json "$TEST_VAULT/vault-config.json"
}

# === Test 3 : Scripts Python copiés =========================================
test_scripts_python() {
  echo "=== Test : scripts Python copiés ==="
  assert_file "$TEST_VAULT/scripts/file_intel.py"
  assert_file "$TEST_VAULT/scripts/providers/__init__.py"
  assert_file "$TEST_VAULT/scripts/providers/base.py"
  assert_file "$TEST_VAULT/scripts/providers/_prompts.py"
  assert_file "$TEST_VAULT/scripts/providers/gemini_provider.py"
  assert_file "$TEST_VAULT/scripts/providers/claude_provider.py"
  assert_file "$TEST_VAULT/scripts/providers/openai_provider.py"
}

# === Test 4 : file_intel.py dry import check ================================
test_file_intel_dry() {
  echo "=== Test : file_intel.py import check ==="

  local python_bin="$HOME/.xais-brain-venv/bin/python3"
  if [ ! -x "$python_bin" ]; then
    python_bin="python3"
  fi

  if "$python_bin" -c "
import sys; sys.path.insert(0, '$TEST_VAULT/scripts')
from file_intel import slugify, discover_files
assert slugify('Mon Document (v2).pdf') == 'mon-document-v2', f'Got: {slugify(\"Mon Document (v2).pdf\")}'
assert slugify('') == 'untitled', f'Got: {slugify(\"\")}'
print('OK slugify + discover_files importables')
" 2>&1; then
    PASS=$((PASS+1))
  else
    echo "FAIL: file_intel.py import"
    FAIL=$((FAIL+1))
  fi
}

# === Test 5 : session-init.sh ===============================================
test_hook_session_init() {
  echo "=== Test : session-init.sh ==="
  local output
  output=$(cd "$TEST_VAULT" && bash .claude/hooks/session-init.sh 2>&1)
  if echo "$output" | grep -q "Vault"; then
    PASS=$((PASS+1))
  else
    echo "FAIL: session-init pas de sortie Vault"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
  fi
}

# === Test 6 : skill-discovery.sh ============================================
test_hook_skill_discovery() {
  echo "=== Test : skill-discovery.sh ==="
  local output
  output=$(cd "$TEST_VAULT" && echo "quels skills ?" | bash .claude/hooks/skill-discovery.sh 2>&1)
  if echo "$output" | grep -q "/daily"; then
    PASS=$((PASS+1))
  else
    echo "FAIL: skill-discovery pas de /daily"
    echo "  Output: $output"
    FAIL=$((FAIL+1))
  fi
}

# === Exécution ===============================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  xais-brain — Tests d'intégration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

test_fresh_install
test_idempotent_rerun
test_scripts_python
test_file_intel_dry
test_hook_session_init
test_hook_skill_discovery

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Résultats : $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
