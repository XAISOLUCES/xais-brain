# Plan 07 — Health Audit Fixes (post-plan-06)

> **Source** : audit `/XD-health` du 2026-04-22 (30 findings : 6 OWASP + 24 structurels). Handoff 011 documente la session plan 06 complet.
> **Status** : TODO — aucun batch livré.
> **Ordre recommandé** : Batch 1 → 3 → 2 → 4 → 5. Batch 6 = backlog séparé.

---

## §0 Contexte

L'audit `/XD-health` a révélé 3 findings structurels graves qui étaient masqués par la vitesse de livraison du plan 06 :

1. **CI menteuse** : `ci.yml` ne run que `tests/test_file_intel.py` → 65 tests sur 83 (78 %) n'ont jamais tourné en CI. Chaque "CI green" depuis 2 semaines est un faux positif pour `test_budget.py`, `test_vault_audit.py`, `test_web_clip.py`.
2. **Sécu HAUTE** : `.env` créé sans `chmod 600` → clés API lisibles par tout UID local.
3. **Bug prod `detect_stale_to_verify`** : connu depuis handoff 010, toujours non fixé. Pollue les rapports d'audit des users.

Plus 27 findings structurels (docs périmées, dead code, dette review 6C/6F, permissions lax, etc.) cumulatifs mais non bloquants.

### Décisions actées

- **Pas de breaking change** : tous les fixes sont additifs ou corrigent des comportements buggés. Pas de renommage, pas de suppression de feature publique.
- **Batch 6 (refacto setup.sh + vault_audit.py)** = spec séparée (08) à créer plus tard. Pas mélanger refacto et fix bugs.
- **Ordre 1 → 3 → 2 → 4 → 5** : Batch 1 d'abord (révèle tests cachés), Batch 3 ensuite (docs synchrones = moins de confusion), Batch 2 après (dette review ciblée), Batch 4 (sécu P1), Batch 5 (fondations dev).

---

## §1 Batch 1 — P0 bloquants (~30 min, 1 commit `fix(critical)`)

### Fichiers touchés
- `.github/workflows/ci.yml`
- `setup.sh`
- `scripts/vault_audit.py`
- `README.md`
- `ARCHITECTURE.md`

### Étapes

**1.1 — CI run tous les tests**
`.github/workflows/ci.yml:46,87` : remplacer `pytest tests/test_file_intel.py -v` par `pytest tests/ -v` (2 occurrences : macOS + Linux jobs). Fixer aussi le `pip install pytest` si besoin d'une version (`pytest>=7.0`).

**1.2 — `.env` chmod 600**
`setup.sh:586-590` (step7_llm_config, bloc écriture .env avec clé) :
```bash
umask 077
{
  printf 'LLM_PROVIDER=%s\n' "$llm_name"
  printf '%s=%s\n' "$key_var" "$API_KEY"
} > "$VAULT_PATH/.env"
chmod 600 "$VAULT_PATH/.env"
```
Appliquer aussi au cas skip (`safe_cp .env.example .env`) : `chmod 600 "$VAULT_PATH/.env"` après la copie.

**1.3 — Bug `detect_stale_to_verify`**
`scripts/vault_audit.py:220-237` : modifier la condition de skip pour inclure `archived` :
```python
# Avant : if statut == "verified": continue
# Après :
if statut in {"verified", "archived"}:
    continue
```
Ajouter 1 test dans `tests/test_vault_audit.py` qui crée une note `statut: archived` avec `verification_date` > 30j et vérifie qu'elle n'apparaît PAS dans `detect_stale_to_verify`.

**1.4 — Install manuel README**
`README.md:343` : le `cp` actuel oublie `scripts/budget.py` (sans lui, `file_intel.py` crash à l'import L32) :
```bash
# Avant : cp scripts/file_intel.py scripts/web_clip.py scripts/vault_audit.py ...
# Après : cp scripts/file_intel.py scripts/web_clip.py scripts/vault_audit.py scripts/budget.py ...
```

**1.5 — ARCHITECTURE cohérence setup.sh**
`ARCHITECTURE.md` :
- 4 occurrences "9 étapes" → "10 étapes" : lignes 13, 33, 212, 249
- Ligne 31 : retirer `pyyaml` de la liste requirements.txt (jamais importé nulle part)

### Critères de succès
- [ ] CI run 83 tests (au lieu de 18) sur macOS **et** Linux
- [ ] Fresh install : `ls -la $VAULT/.env` → `-rw-------`
- [ ] Test `test_vault_audit.py::test_stale_ignores_archived` vert
- [ ] README install manuel copié-collé → `file_intel.py --help` marche sans ImportError
- [ ] `grep -c "9 étapes" ARCHITECTURE.md` → 0

### Risques
- **CI va devenir rouge** au premier push si un des 65 tests précédemment masqués fail. Mitigation : lancer `pytest tests/ -v` en local avant le push pour identifier.
- **Impact user** : aucun — tous les changements sont internes ou correctifs.

---

## §2 Batch 3 — Docs désynchronisées (~15 min, 1 commit `docs: sync`)

> **Pourquoi avant Batch 2** : peu risqué, renforce cohérence du chiffre "8" (détections audit) partout, réduit la confusion pendant les autres batches.

### Fichiers touchés
- `vault-template/GUIDE.md`
- `vault-template/99-Meta/README.md`
- `vault-template/99-Meta/Audit.md`
- `vault-template/.claude/skills/vault-audit/SKILL.md`
- `vault-template/.claude/skills/import-vault/SKILL.md`

### Étapes

**3.1 — GUIDE.md 8 symptômes**
`vault-template/GUIDE.md:177` : "7 symptômes" → "8 symptômes". Lignes 179-187 : ajouter une ligne dans la table pour "Notes peu liées" (< 3 wikilinks sortants, exclut daily/).

**3.2 — 99-Meta/README.md**
`vault-template/99-Meta/README.md:19` : mettre à jour la liste de catégories de 7 → 8 (ajouter "Notes peu liées").

**3.3 — Template Audit.md**
`vault-template/99-Meta/Audit.md` : ajouter une section vide "## Notes peu liées (0)" pour cohérence avec `render_report()`. Ce template est le fallback quand aucun audit n'a encore tourné.

**3.4 — vault-audit SKILL.md description**
`vault-template/.claude/skills/vault-audit/SKILL.md:3` : la description frontmatter liste les détections mais oublie "notes peu liées". Ajouter à la liste.

**3.5 — import-vault SKILL.md cohérence 12 skills**
`vault-template/.claude/skills/import-vault/SKILL.md` lignes 73, 191, 222 : le skill liste 8 skills xais-brain core. Les remplacer par les 12 canoniques actuels. Ligne 296 : le résumé "4 skills xais-brain manquants" est faux — recompter.

### Critères de succès
- [ ] `grep -rn "7 symptômes\|7 catégories\|7 détections" vault-template/` → 0
- [ ] `grep -c "Notes peu liées" vault-template/99-Meta/Audit.md` → ≥ 1
- [ ] `import-vault/SKILL.md` liste bien 12 skills : clip, daily, client, file-intel, humanise, import-vault, inbox-zero, memory-add, project, tldr, vault-audit, vault-setup

---

## §3 Batch 2 — Dette review piste 6C/6F (~20 min, 1 commit `fix(review-debt)`)

> Les 3 warnings du commit 6F (`c2c3829`) + 2 warnings du commit 6C (`663d4e7`) documentés dans handoff 011 §Risques.

### Fichiers touchés
- `scripts/budget.py`
- `scripts/file_intel.py`
- `vault-template/.claude/pricing.json`
- `tests/test_file_intel.py`

### Étapes

**2.1 — Formule DOCX 40% sous-estimée**
`scripts/budget.py:140-142` : actuellement `pages * per_page * per_para // 10` → ~450 tokens/page vs PDF à 750. Décision : aligner sur PDF (`tokens_per_pdf_page` directement, car un DOCX a une densité similaire). Retirer les clés `tokens_per_docx_page` et `tokens_per_paragraph` de `pricing.json` si inutilisées, sinon corriger la formule.

**2.2 — `format_inbox_warning` dead code**
Décision : **supprimer** (le SKILL.md `inbox-zero` explique déjà textuellement le checkpoint). Retirer :
- `scripts/budget.py:256-265` (la fonction elle-même)
- `tests/test_budget.py` tests associés (à identifier par `grep format_inbox_warning`)

**2.3 — `seconds_per_file_avg` dead config**
- `scripts/budget.py:47` (dataclass field) — retirer
- `vault-template/.claude/pricing.json:30` (clé `seconds_per_file_avg`) — retirer des 3 providers

**2.4 — Docstring `announce_budget`**
`scripts/file_intel.py:172-175` : la docstring mentionne un comportement CI (`XAIS_BRAIN_CI=1`) non implémenté dans cette fonction (seul `prompt_checkpoint` le supporte). Retirer la mention ou la déplacer vers `prompt_checkpoint`.

**2.5 — `except Exception` large**
`scripts/file_intel.py:180` : actuellement swallow silencieux. Remplacer par :
```python
except Exception as exc:
    print(f"  ⚠ budget estimate failed: {type(exc).__name__}", file=sys.stderr)
```
Pour garder le côté non-bloquant **et** avoir une trace en cas de bug.

**2.6 — `prompt_checkpoint` comportement inattendu**
`scripts/file_intel.py:161-162` : actuellement retourne `default_yes` sur réponse non reconnue (surprenant pour `[Y/n]`). Changer pour retourner `False` (abort safe) si la réponse n'est ni yes/no/empty. Mettre à jour le test correspondant.

### Critères de succès
- [ ] `grep -n format_inbox_warning scripts/` → 0
- [ ] `grep -n seconds_per_file_avg scripts/ vault-template/` → 0
- [ ] `grep -n "XAIS_BRAIN_CI" scripts/file_intel.py:170-180` → 0 (ou seulement dans `prompt_checkpoint`)
- [ ] Tests verts après modifications (97 → 95 si 2 tests format_inbox_warning supprimés)

---

## §4 Batch 4 — Sécurité P1 (~40 min, 1 commit `fix(security)`)

> Les 3 MOYENNE + 2 BASSE OWASP. Non-bloquants mais actionnables.

### Fichiers touchés
- `scripts/web_clip.py`
- `vault-cli.sh`
- `scripts/file_intel.py`
- `setup.sh`
- `tests/test_web_clip.py`

### Étapes

**4.1 — SSRF web_clip filtrage**
`scripts/web_clip.py:72-86` (fonction `fetch_and_extract`) : ajouter validation avant `httpx.get` :
```python
from urllib.parse import urlparse
import ipaddress, socket

_ALLOWED_SCHEMES = {"http", "https"}

def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    return True
```
Lever `ValueError` si `not _is_safe_url(url)`. +2 tests : scheme `file://` rejeté, IP `127.0.0.1` rejetée.

**4.2 — Injection vault-cli (4 invocations)**
`vault-cli.sh:83, 104-106, 167` : toutes les `python3 -c "... '$cfg' ..."` → passer `$cfg` en argv :
```bash
# Avant
inbox_dir=$(python3 -c "import json; print(json.load(open('$cfg'))...)")
# Après
inbox_dir=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))...)' "$cfg")
```
4 invocations à mettre à jour. Vérifier avec paths contenant une apostrophe après fix.

**4.3 — Exception leak dans logs**
`scripts/file_intel.py:259, 279-281, 326` : remplacer `{exc}` par `{type(exc).__name__}` dans les `print(..., file=sys.stderr)` (sinon les SDK LLM peuvent embarquer headers `Authorization` dans leur repr).

**4.4 — `unset API_KEY`**
`setup.sh` fin de `step7_llm_config` : ajouter `unset API_KEY` après l'écriture du .env (évite que la clé reste en mémoire shell si l'user Ctrl+C entre step 7 et 8).

**4.5 — Supply chain Kepano pin**
`setup.sh:704` : `git clone https://github.com/kepano/obsidian-skills.git ...` → pinner un commit SHA connu pour éviter qu'un compromis futur des skills Kepano affecte les futurs installs :
```bash
git clone https://github.com/kepano/obsidian-skills.git "$tmp/obsidian-skills" &>/dev/null
(cd "$tmp/obsidian-skills" && git checkout <SHA-A-CHOISIR>)
```
À choisir : le HEAD actuel au moment du fix.

### Critères de succès
- [ ] `python3 -c "from scripts.web_clip import _is_safe_url; print(_is_safe_url('file:///etc/passwd'))"` → `False`
- [ ] Vault path avec apostrophe (`/tmp/foo'bar`) : `xb status` ne crashe plus
- [ ] Test intentionnel : inject une exception dans provider → stderr ne contient pas `sk-`, `AIza`, `sk-ant-`
- [ ] `grep -A2 "kepano/obsidian-skills" setup.sh` → contient un `git checkout <SHA>`

---

## §5 Batch 5 — Fondations dev (~15 min, 1 commit `chore(dev)`)

### Fichiers touchés
- `tests/conftest.py` (nouveau)
- 4× `tests/test_*.py`
- `requirements.txt`
- `vault-template/.claude/settings.json`

### Étapes

**5.1 — `conftest.py`**
Créer `tests/conftest.py` avec :
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
```
Retirer les 4 `sys.path.insert(...)` dans :
- `tests/test_budget.py:7`
- `tests/test_file_intel.py:6`
- `tests/test_vault_audit.py:13`
- `tests/test_web_clip.py:6`

**5.2 — `pytest` dans requirements**
Ajouter `pytest>=7.0` à `requirements.txt`. Alternative : créer `requirements-dev.txt` séparé avec pytest + dev tools. Choix par défaut : tout dans `requirements.txt` (plus simple pour contributeur).

**5.3 — Permissions `settings.json`**
`vault-template/.claude/settings.json:21-26` : allow list, ajouter :
```json
"Bash(mkdir:*)", "Bash(mv:*)", "Bash(chmod:*)", "Bash(cp:*)"
```
Ligne 29 (deny) : ajouter `"Bash(rm:*)"` (pour deny `rm` sans `-rf` aussi, seulement `rm -rf` est deny actuellement).

### Critères de succès
- [ ] `pytest tests/ -v` vert sans les 4 `sys.path.insert`
- [ ] `cat requirements.txt | grep pytest` → ligne présente
- [ ] Claude Code dans le vault : `/inbox-zero` n'ouvre pas de prompt de confirmation pour `mv`/`mkdir`

---

## §6 Batch 6 — Refacto structurel (SPEC SÉPARÉE, ne pas lancer ici)

Backlog pour une future spec `08-refacto-setup-vault-audit.md` :
- Découpage `setup.sh` (1008 LOC) → `scripts/install/step-0N-*.sh` sourcés depuis un orchestrateur court
- Découpage `vault_audit.py` (660 LOC) → `scripts/audit/{detectors,report}.py`
- Découpage `tests/test_vault_audit.py` (563 LOC) par detector
- Logger structuré JSON pour `file_intel.py` et `vault_audit.py`
- CI lint : `ruff check scripts/ tests/` + hook pre-commit
- CI coverage : `pytest --cov=scripts --cov-fail-under=80`

**Pas dans ce plan** — nécessite conception séparée + risque de régression plus élevé. À créer quand les batches 1-5 seront livrés.

---

## §7 Récap critères globaux

Au bout des 5 batches (1-5), le projet doit satisfaire :

| Métrique | Avant | Après |
|---|---|---|
| Tests tournant en CI | 18/83 | **83/83** |
| Findings OWASP HAUTE | 1 | **0** |
| Findings OWASP MOYENNE | 3 | **0** |
| Findings OWASP BASSE | 2 | **0** |
| Bugs prod documentés | 1 (`detect_stale_to_verify`) | **0** |
| Dead code prod | 2 fonctions / 1 config | **0** |
| Docs incohérences comptées | 8 | **≤ 1** (tolérance hygiène) |
| Dépendances manquantes déclarées | 1 (pytest) | **0** |
| Verdict `/XD-health` | NEEDS ATTENTION | **HEALTHY** |

---

## §8 État

- [ ] Batch 1 — P0 bloquants
- [ ] Batch 3 — Docs désync
- [ ] Batch 2 — Dette review 6C/6F
- [ ] Batch 4 — Sécu P1
- [ ] Batch 5 — Fondations dev
- [ ] (Optionnel) Batch 6 — Refacto → spec séparée 08

**Prochaine action** : `/XD-build specs/todo/07-health-audit-fixes.md` pour attaquer Batch 1.
