# Plan — Intégration patterns obsidian-god-mode dans xais-brain

**Source patterns** : `/Users/xais/Dev/PROJETS/obsidian-labo-fork/obsidian-god-mode-claude-code/PROMPT-PILOT.md` (370 lignes)
**Cible** : `xais-brain` (vault-template + skills + setup.sh + CLI `xb`)
**Auteur** : Xavier / Claude
**Date** : 2026-04-20
**Dernière mise à jour** : 2026-04-21 (pivot stratégique, voir §0)
**Statut** : **DÉCIDÉ** — prêt à `/XD-build` à partir de la piste 6B

---

## 0. Pivot stratégique — 2026-04-21

### 0.1 Positionnement adopté

> **xais-brain — Le second brain qui s'auto-audite.**
> Un vault Obsidian piloté par Claude Code, pensé dès le départ pour que l'IA puisse le lire, l'enrichir et diagnostiquer sa santé.

**Stratégie** : **A-façade + C-moteur**.
- **Axe A (façade, narrative, README)** : self-auditing second brain — score de santé, dégradation détectée, remédiation assistée. C'est ce qu'on *vend*, c'est ce qui différencie vs. Obsidian+Copilot / Reor / Khoj / templates "Claude+Obsidian".
- **Axe C (moteur, implémentation)** : AI-native by design — frontmatter enrichi, skills dédiés, CLAUDE.md vault optimisé LLM. C'est ce qui *rend l'audit possible* : sans ce moteur, rien à scorer.

### 0.2 Conséquence sur l'ordre des pistes

`/vault-audit` passe de **4e** à **2e** position : c'est la feature différenciante, elle doit tomber tôt pour qu'on itère dessus. L'ordre final **6B → 6E → 6D → 6F → 6C → 6G (→ 6H)** — détail §5.

### 0.3 Décisions sur les 8 questions ouvertes (§8)

| # | Question | Décision |
|---|----------|----------|
| Q1 | Ordre des pistes | **6B → 6E → 6D → 6F → 6C → 6G → (6H)** (ré-orienté Axe A : `/vault-audit` tôt) |
| Q2 | Rétrocompat frontmatter | **Additif uniquement** + migration opt-in via `xb audit --migrate`. Jamais de champ renommé. |
| Q3 | `/vault-audit` skill vs CLI | **Les deux** : skill `/vault-audit` (UX conversationnelle) + CLI `xb audit` (scripting, cron futurs) |
| Q4 | Frontmatter incomplet dans `xb audit` | **Warning non bloquant** (rapport uniquement, exit code 0). On veut qu'un vault existant garde un score même imparfait. |
| Q5 | Density rule (6H) | **GO** — renforce l'Axe A (détection notes anémiques / sous-liées). Planifiée, pas en MVP. |
| Q6 | Pricing JSON (6F) | **Fichier config séparé** `.claude/pricing.json` — maj sans toucher au code. |
| Q7 | Exclusion `99-Meta/` dans graphe Obsidian | **Doc manuelle d'abord** (README de `99-Meta/` existant). Config auto via `.obsidian/app.json` = v2. |
| Q8 | `GUIDE.md` vs `CLAUDE.md` | **Séparation validée** — `CLAUDE.md` pour Claude, `GUIDE.md` didactique pour l'user. |

### 0.4 Impact sur la narrative marketing (README)

À la fin de la piste 6E, le README sera refait autour du score d'audit (héro visuel) et non plus autour de la liste des 11 skills. La piste 5 (demo GIF, `specs/todo/05-demo-gif-readme.md`) devra montrer **un audit qui tourne**, pas un setup.

---

## 1. Problème & objectif

### 1.1 Problème

Le repo `obsidian-god-mode-claude-code` a mûri des patterns audit-friendly (frontmatter YAML structuré, piste d'audit `99-Meta/`, anti-hallucination hardcodé, checkpoints humains forcés) que `xais-brain` n'a pas encore. Aujourd'hui dans xais-brain :

- `/clip`, `/file-intel`, `/inbox-zero` produisent des notes **sans frontmatter uniforme** → pas auditable.
- Aucune **piste d'audit** des sources WebSearch ni des décisions de tri.
- Les skills batch (`/file-intel` sur 20 PDFs, `/inbox-zero` sur 50 fichiers) **n'ont pas de checkpoint** → risque de brûler du budget LLM sur une mauvaise trajectoire.
- Pas de skill de **santé du vault** (orphelines, doublons, anémiques, frontmatter cassé).
- Pas de **budget annoncé** avant batch → Xavier découvre le coût après coup.

### 1.2 Objectif

Cherry-picker les 8 patterns transférables de god-mode et les intégrer dans xais-brain **sans** :

- casser les vaults existants (rétrocompat frontmatter impératif),
- importer le prompt monolithique (architecture skills reste souveraine),
- alourdir le workflow quotidien (checkpoints opt-in sur batch seulement).

### 1.3 Contraintes

- **Git-first** : tout passe par une branche + worktree + commit atomique.
- **CI verte** : macOS + Linux (`setup.sh`, `tests/`).
- **Rétrocompat** : frontmatter nouveau = **additif uniquement**, jamais de champ renommé.
- **Mode CI** : `XAIS_BRAIN_CI=1` doit bypasser tous les checkpoints humains (sinon la CI pend).
- **Français** : tous les nouveaux skills, docs, frontmatter → FR.

### 1.4 Non-objectifs

- PAS de génération one-shot de 50 pages sur un sujet (hors scope xais-brain).
- PAS d'obligation de density rule 7 wikilinks (trop strict pour un second brain quotidien).
- PAS de migration forcée des notes existantes (opt-in via `xb audit --migrate`).

---

## 2. Les 8 patterns et leur transférabilité

| # | Pattern god-mode | Transférabilité | Piste |
|---|------------------|-----------------|-------|
| 1 | Checkpoints humains forcés | Oui, sur skills batch | 6C |
| 2 | YAML frontmatter audit-friendly | Oui, additif | 6B |
| 3 | Anti-hallucination hardcodé | Partiel (via `/clip` + `/file-intel`) | 6D |
| 4 | Dossier `99-Meta/` (piste d'audit) | Oui | 6A |
| 5 | Density rule wikilinks (min 7) | Assouplie (min 3, opt-in) | 6H |
| 6 | Phases avec livrables explicites | Implicite via skills existants | — |
| 7 | Budget + wall-time transparent | Oui, sur skills batch | 6F |
| 8 | GUIDE.md didactique | Oui | 6G |

Pattern 6 n'a pas de piste dédiée : il est déjà exprimé par l'architecture des skills (chaque skill = une phase avec un livrable).

---

## 3. Architecture cible

### 3.1 Arborescence cible du vault-template

```
vault-template/
├── CLAUDE.md
├── GUIDE.md                              ← NOUVEAU (piste 6G)
├── MEMORY.md
├── vault-config.json
│
├── inbox/
├── daily/
├── projects/
├── research/
├── archive/
├── memory/
│
├── 99-Meta/                              ← NOUVEAU (piste 6A)
│   ├── README.md                         ← Rôle du dossier
│   ├── Audit.md                          ← Template rapport d'audit
│   ├── Fact-Check-Log.md                 ← Append-only, alimenté par /clip et /file-intel
│   └── Session-Debriefs/
│       └── .gitkeep                      ← Alimenté par /tldr
│
└── .claude/
    ├── skills/
    │   ├── ... (11 existants, modifiés pistes 6B/6C/6D/6F)
    │   └── vault-audit/                  ← NOUVEAU (piste 6E)
    │       └── SKILL.md
    └── settings.json
```

### 3.2 Frontmatter cible (piste 6B)

```yaml
---
source: web | pdf | docx | txt | md | manual | import | session
source_url: https://...                   # optionnel, si source=web
source_file: ./path/to.pdf                # optionnel, si source=pdf|docx
source_knowledge: internal | web-checked | mixed
verification_date: 2026-04-20             # ISO YYYY-MM-DD
statut: draft | verified | to-verify | archived
importance: low | medium | high | core
tags: [ai, alignment, controverse]
created: 2026-04-20
---
```

Champs **additifs** : aucun champ existant renommé. Migration = `xb audit --migrate` qui complète les champs manquants avec des valeurs par défaut (`statut: draft`, `source_knowledge: internal`, `verification_date: <aujourd'hui>`).

### 3.3 Script Python nouveau : `scripts/vault_audit.py`

Appelé par le skill `/vault-audit` ET par la commande CLI `xb audit`.

Signature :

```bash
python3 scripts/vault_audit.py <vault_path> [--output <path>] [--migrate] [--json]
```

Sorties :

- `99-Meta/Audit-YYYY-MM-DD.md` (humain lisible, checklist)
- Optionnellement JSON pour scripting (`--json`)

---

## 4. Décomposition en 8 pistes atomiques

Chaque piste = une branche + worktree + commit atomique + spec finale rangée dans `specs/done/`.

### Piste 6A — `99-Meta/` dans vault-template

**Taille** : S (1-2h)
**Dépendances** : aucune
**Débloque** : 6D, 6E

**Livrables** :

1. `vault-template/99-Meta/README.md` (~40 lignes) — explique le rôle du dossier, renvoie vers `/vault-audit`.
2. `vault-template/99-Meta/Audit.md` — template vide avec les sections (orphelines, anémiques, doublons, frontmatter incomplet, tags incohérents).
3. `vault-template/99-Meta/Fact-Check-Log.md` — template append-only avec en-tête.
4. `vault-template/99-Meta/Session-Debriefs/.gitkeep`.
5. `setup.sh` : vérifier que le dossier est bien copié (il l'est déjà par `cp -R vault-template/*` mais confirmer).
6. `ARCHITECTURE.md` : ajouter le dossier dans l'arbo.
7. `tests/test_setup.sh` : assert `[ -d "$VAULT/99-Meta" ]` après install.

**Spec du README.md de `99-Meta/`** :

```markdown
# 99-Meta — Piste d'audit du vault

Ce dossier trace l'hygiène et la fiabilité du vault.
Il n'est pas conçu pour être lu comme du contenu : c'est la "boîte noire"
du second brain.

## Fichiers

- `Audit.md` — dernier rapport du skill `/vault-audit` (orphelines, anémiques, doublons).
- `Fact-Check-Log.md` — log append-only des sources vérifiées (alimenté par `/clip`, `/file-intel`).
- `Session-Debriefs/` — rétrospectives de session (alimenté par `/tldr`).

## Ignorer dans le graphe Obsidian

Ajoute `99-Meta/` dans les "Files & Links → Excluded files" d'Obsidian
pour que ces fichiers ne polluent pas la graph view.
```

**Critère de succès** :

- Après `bash setup.sh`, le vault contient `99-Meta/` avec les 4 fichiers template.
- CI verte.

---

### Piste 6B — Frontmatter enrichi (`/clip` + `/file-intel` + `/inbox-zero`)

**Taille** : M (2-3h)
**Dépendances** : 6A (pour que `verification_date` soit cohérent avec Fact-Check-Log)
**Débloque** : 6E (l'audit détecte les frontmatter incomplets)

**Livrables** :

1. **`scripts/web_clip.py`** — ajouter dans le frontmatter généré :
   ```yaml
   source: web
   source_url: <url>
   source_knowledge: web-checked
   verification_date: <today ISO>
   statut: draft
   importance: medium
   ```
2. **`scripts/file_intel.py`** (et `scripts/providers/_prompts.py`) — ajouter :
   ```yaml
   source: pdf | docx | txt | md
   source_file: <original path>
   source_knowledge: internal
   verification_date: <today ISO>
   statut: to-verify
   importance: medium
   ```
3. **`/inbox-zero` SKILL.md** — règle explicite : **préserver** tout frontmatter existant lors du tri, ne pas réécrire les champs déjà présents.
4. **Tests** :
   - `tests/test_web_clip.py` — assert que le frontmatter contient `source: web`, `source_url`, `statut: draft`.
   - `tests/test_file_intel.py` — assert frontmatter PDF avec `source: pdf`, `source_file`, `statut: to-verify`.
5. **Doc** : `ARCHITECTURE.md` section "Frontmatter standard" (nouvelle, ~20 lignes).

**Risque** : casser la CI si les tests actuels vérifient un frontmatter figé → vérifier avant codage (grep sur les tests).

**Critère de succès** :

- Les 3 skills produisent un frontmatter conforme au schéma §3.2.
- Tests verts macOS + Linux.
- Notes existantes non modifiées.

---

### Piste 6C — Checkpoints humains dans skills batch

**Taille** : M (2-3h)
**Dépendances** : aucune (mais gagne à être fait après 6F pour afficher le budget au checkpoint)
**Débloque** : rien

**Livrables** :

1. **`/inbox-zero` SKILL.md** — ajouter section "Checkpoint humain" :
   - Phase 1 : lister les fichiers inbox et proposer un plan de tri numéroté (fichier → dossier).
   - **STOP** et attendre confirmation ("ok", "go", "modif X→Y").
   - Phase 2 : exécuter le tri.
   - Phase 3 : afficher récap + proposer `/vault-audit`.
2. **`/file-intel` SKILL.md** — ajouter 2 checkpoints :
   - Checkpoint 1 : après listing des fichiers + estimation budget (cf. 6F) → attendre "ok".
   - Checkpoint 2 : après traitement des 2-3 premiers fichiers → montrer un résumé → attendre "ok" avant le reste.
3. **Mode CI** : les deux skills doivent détecter `$XAIS_BRAIN_CI=1` et bypasser les checkpoints en assumant "ok" par défaut.
4. **Tests** :
   - `tests/test_file_intel.py` — vérifier que `XAIS_BRAIN_CI=1` ne bloque pas.
   - Test manuel macOS (non automatisable car checkpoint interactif).

**Spec du pattern checkpoint** (à répéter dans chaque skill concerné) :

```markdown
## Checkpoint humain

Avant de lancer le traitement batch :

1. Affiche le plan numéroté (X fichiers → Y actions).
2. Affiche le budget estimé (tokens, temps, €).
3. Demande : **"OK pour lancer ? (oui / modif / non)"**
4. Si `XAIS_BRAIN_CI=1` → skip et assume "oui".
5. Sinon, attendre une réponse explicite avant de continuer.
```

**Critère de succès** :

- Lancer `/file-intel` sur un dossier de 10 PDFs → s'arrête et demande validation avant de traiter.
- `XAIS_BRAIN_CI=1 /file-intel` → bypass sans input.

---

### Piste 6D — Fact-Check-Log.md auto-alimenté

**Taille** : M (2h)
**Dépendances** : 6A (dossier 99-Meta/), 6B (frontmatter avec `source_knowledge`)
**Débloque** : 6E (l'audit peut cross-référencer)

**Livrables** :

1. **`scripts/web_clip.py`** — après génération de la note, **append** dans `99-Meta/Fact-Check-Log.md` :
   ```markdown
   ## 2026-04-20 — [[<note-title>]]
   - **Source** : web (`<url>`)
   - **Skill** : /clip
   - **Statut** : draft (à vérifier)
   ```
2. **`scripts/file_intel.py`** — même append avec `source: pdf|docx|...`.
3. **Format standard** : date ISO → note liée wikilink → source → skill → statut.
4. **Header du Fact-Check-Log.md** (en piste 6A) :
   ```markdown
   # Fact-Check Log

   Log append-only des sources utilisées par les skills xais-brain.
   Alimenté par /clip et /file-intel. Ne PAS éditer à la main — utiliser /vault-audit pour nettoyer.

   ---
   ```
5. **Tests** :
   - `tests/test_web_clip.py` — assert que `Fact-Check-Log.md` contient une entrée après clip.
   - `tests/test_file_intel.py` — idem.

**Edge case** : le fichier `Fact-Check-Log.md` peut devenir énorme → prévoir rotation annuelle dans une future piste (hors scope ici).

**Critère de succès** :

- Après `xb clip <url>`, `99-Meta/Fact-Check-Log.md` contient une nouvelle entrée datée.
- Après `xb file-intel <dir>`, une entrée par fichier traité.

---

### Piste 6E — Skill `/vault-audit` + script Python

**Taille** : L (4-6h)
**Dépendances** : 6A, 6B, 6D (pour auditer ce que les autres pistes ont mis en place)
**Débloque** : rien

**Livrables** :

1. **`scripts/vault_audit.py`** — CLI Python autonome :
   ```bash
   python3 scripts/vault_audit.py <vault_path> [--output <path>] [--migrate] [--json]
   ```
   Détections **MVP** :
   - Notes orphelines : 0 backlinks ET 0 wikilinks sortants.
   - Notes anémiques : `< 100` mots (excluant frontmatter).
   - Doublons **titre exact** (MVP — pas d'embeddings).
   - Frontmatter incomplet : manque `statut` OU `source_knowledge`.
   - Notes `statut: to-verify` depuis > 30 jours (via `verification_date`).
   - Tags incohérents : détection casse/variantes (`#ai`, `#AI`, `#ia`).
   - Wikilinks cassés : `[[X]]` où `X.md` n'existe pas.
2. **`vault-template/.claude/skills/vault-audit/SKILL.md`** — wrapper du script :
   ```markdown
   ---
   name: vault-audit
   description: Scanne le vault et génère un rapport d'hygiène (orphelines, anémiques, doublons, frontmatter, tags, liens cassés). Utiliser quand l'utilisateur dit audit vault, hygiène vault, santé vault, vault-audit.
   user-invocable: true
   model: haiku
   ---
   ```
3. **Output** : `99-Meta/Audit-YYYY-MM-DD.md` avec sections checklist actionnable.
4. **CLI `xb audit`** — ajouter dans `vault-cli.sh` un sous-commande `audit` qui appelle le script.
5. **Flag `--migrate`** — complète les frontmatter manquants avec valeurs par défaut (sans écraser l'existant).
6. **Tests** :
   - `tests/test_vault_audit.py` — 6-8 fixtures (note orpheline, anémique, doublon, frontmatter incomplet, lien cassé) et asserts sur chaque détection.
7. **Doc** : `ARCHITECTURE.md` + `README.md` section "Audit vault".

**Détail du schéma d'Audit.md généré** :

```markdown
# Vault Audit — 2026-04-20

**Vault** : /Users/xais/vault
**Notes scannées** : 142
**Temps** : 0.8s

## Notes orphelines (3)

- [ ] [[inbox/vieille-note]] — 0 backlinks, 0 wikilinks sortants
- [ ] [[archive/tmp-note]] — ...

## Notes anémiques (< 100 mots) (7)

- [ ] [[daily/2025-12-03]] — 42 mots

## Doublons titre exact (1)

- [ ] [[inbox/article.md]] ≈ [[research/article.md]]

## Frontmatter incomplet (12)

- [ ] [[research/foo]] — manque `statut`, `source_knowledge`
- ...

## Notes `to-verify` depuis > 30 jours (2)

- [ ] [[research/bar]] — verification_date: 2026-03-01

## Tags incohérents (2 groupes)

- `#ai` (14 notes), `#AI` (3 notes), `#ia` (1 note) → unifier ?

## Wikilinks cassés (5)

- [[inbox/note-x]] → [[note-inexistante]] ligne 42
```

**Critère de succès** :

- `xb audit` génère `99-Meta/Audit-YYYY-MM-DD.md` avec les 7 sections.
- Tests unitaires verts sur 6 fixtures.
- `xb audit --migrate` complète les frontmatter sans écraser.

---

### Piste 6F — Budget annoncé avant batch

**Taille** : S (1h)
**Dépendances** : aucune (mais gagne à être fait avant 6C pour afficher dans le checkpoint)
**Débloque** : 6C (plus riche)

**Livrables** :

1. **`scripts/file_intel.py`** — avant de lancer le traitement :
   - compter les fichiers,
   - estimer les pages totales (PDF : somme pages, DOCX : len(paragraphes)/30),
   - afficher :
     ```
     /file-intel va traiter 12 PDFs (~487 pages).
     Estimation : 8-15 min, ~$0.50-$1.20 en tokens (provider: gemini).
     ```
   - Si `$XAIS_BRAIN_CI=1` → afficher mais ne pas attendre.
2. **`/inbox-zero` SKILL.md** — si `> 20` fichiers, afficher un warning budget (estimation grossière).
3. **Table des estimations** (à documenter dans `scripts/file_intel.py`) :
   | Provider | $/1k tokens input | $/1k tokens output |
   |----------|-------------------|--------------------|
   | gemini   | $0.00             | $0.00 (free tier)  |
   | claude   | $0.003            | $0.015             |
   | openai   | $0.005            | $0.015             |
4. **Tests** :
   - `tests/test_file_intel.py` — vérifier que l'estimation s'affiche.

**Critère de succès** :

- Lancer `xb file-intel ./dossier` → affiche "X fichiers, ~Y pages, ~$Z" avant exécution.

---

### Piste 6G — GUIDE.md utilisateur final

**Taille** : S (1-2h)
**Dépendances** : toutes les autres (pour documenter l'état final)
**Débloque** : rien

**Livrables** :

1. **`vault-template/GUIDE.md`** (~200 lignes) — 10 sections :
   1. **Bienvenue** — 3 phrases sur xais-brain
   2. **Quand utiliser quel skill** — tableau situation → skill
   3. **Workflow quotidien type** — matin `/daily`, travail, `/tldr` soir
   4. **Traiter des nouveaux fichiers** — `/clip`, `/file-intel`, `/inbox-zero`
   5. **Mémoire long terme** — `/memory-add` + `MEMORY.md`
   6. **Projets et clients** — `/project`, `/client`
   7. **Hygiène du vault** — `/vault-audit` mensuel
   8. **Personnalisation** — `CLAUDE.md`, `.claude/rules/`
   9. **CLI `xb`** — commandes disponibles
   10. **FAQ** — 8-10 questions courantes
2. **`CLAUDE.md`** — ajouter un lien en tête : `> Guide utilisateur : voir [GUIDE.md](GUIDE.md)`.

**Distinction** : `CLAUDE.md` = instructions pour Claude / `GUIDE.md` = didactique pour Xavier.

**Critère de succès** :

- Nouveau vault installé → `GUIDE.md` présent, lisible, auto-suffisant.
- Xavier peut expliquer le système à quelqu'un en lui donnant juste `GUIDE.md`.

---

### Piste 6H — Density rule wikilinks (OPTIONNEL)

**Taille** : S (1h)
**Dépendances** : 6B
**Débloque** : rien
**Statut** : **À décider avec Xavier (§8 Q5)**

**Livrables** (si on la fait) :

1. `/file-intel` prompt (`scripts/providers/_prompts.py`) — ajouter ligne :
   > "Inclus **au moins 3 wikilinks sortants** `[[Concept]]` vers des pages pertinentes, chacun justifié par une phrase."
2. Frontmatter enrichi (piste 6B étendu) — ajouter optionnellement :
   ```yaml
   liens_forts: [[Page1]], [[Page2]]
   liens_opposition: [[Page3]]
   ```
3. `/vault-audit` — nouveau check : notes avec 0 wikilinks sortants.

**Décision recommandée** : **SKIP au MVP**. Ajouter quand le pattern émerge naturellement dans l'usage de Xavier.

---

## 5. Ordre d'implémentation (révisé 2026-04-21, Axe A)

**Principe directeur** : `/vault-audit` est la feature différenciante (Axe A). Elle arrive **le plus tôt possible** après le minimum technique qui la rend possible (frontmatter enrichi). Les autres pistes nourrissent ou polissent l'audit.

### Phase 1 — Moteur AI-native (condition technique)

1. **6A** ✅ **FAIT** (commit `fb0d8e0`) — `99-Meta/` folder
2. **6B** Frontmatter enrichi — ~2-3h — débloque l'audit

### Phase 2 — Feature différenciante

3. **6E** Skill `/vault-audit` + script + CLI `xb audit` — ~4-6h — **pivot business**

### Phase 3 — Enrichissement de l'audit

4. **6D** Fact-Check-Log auto — ~2h — complète la traçabilité
5. **6F** Budget annoncé — ~1h — UX batch + config `.claude/pricing.json`

### Phase 4 — UX & docs

6. **6C** Checkpoints humains — ~2-3h — bénéficie de 6F
7. **6G** GUIDE.md — ~1-2h — reflète l'état final (dont audit)

### Phase 5 — Renforcement Axe A

8. **6H** Density rule — ~1h — **planifiée** (décision §0.3 : GO)

**Total temps restant estimé (6B à 6H)** : 13-18h sur 4-5 sessions.

### Commits cibles (ordre chronologique révisé)

```
✅ feat(vault): add 99-Meta/ audit trail folder (piste 6A)           ← fb0d8e0
→  feat(skills): enrich frontmatter for clip, file-intel, inbox-zero (piste 6B)
   feat(skills): add /vault-audit skill + xb audit CLI (piste 6E)
   feat(skills): auto-populate Fact-Check-Log.md from clip & file-intel (piste 6D)
   feat(skills): announce batch budget from .claude/pricing.json (piste 6F)
   feat(skills): add human checkpoints to batch skills (piste 6C)
   docs: add user-facing GUIDE.md (piste 6G)
   feat(skills): density rule wikilinks (piste 6H)
   docs: rebrand README around vault audit score (Axe A narrative)
```

---

## 6. Stratégie de test

### 6.1 Tests unitaires Python

- `tests/test_web_clip.py` — frontmatter enrichi + Fact-Check-Log append.
- `tests/test_file_intel.py` — frontmatter + Fact-Check-Log + budget + checkpoint CI bypass.
- `tests/test_vault_audit.py` — **nouveau**, 6-8 fixtures couvrant chaque détection.

### 6.2 Tests d'intégration bash

- `tests/test_setup.sh` — `99-Meta/` présent après install.
- Nouveau : `tests/test_audit.sh` — `xb audit` génère bien `99-Meta/Audit-YYYY-MM-DD.md`.

### 6.3 Tests manuels (non-automatisables)

- Checkpoints humains sur `/file-intel` en mode interactif macOS.
- Lecture visuelle de `GUIDE.md` (est-ce didactique ?).

### 6.4 CI

Toutes les pistes doivent passer la CI `macos-latest` + `ubuntu-latest`. Flag `XAIS_BRAIN_CI=1` = bypass checkpoints.

### 6.5 Test de rétrocompat frontmatter

Créer une fixture `tests/fixtures/vault-legacy/` avec des notes **sans** les nouveaux champs → vérifier :

- `/inbox-zero` ne casse pas,
- `/vault-audit` les détecte comme "frontmatter incomplet" mais ne plante pas,
- `xb audit --migrate` les complète proprement.

---

## 7. Risques & mitigations

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Breaking change frontmatter | Haute | Haut | Additif uniquement + flag `--migrate` opt-in |
| CI pend sur checkpoint humain | Moyenne | Haut | Flag `XAIS_BRAIN_CI=1` testé explicitement |
| `99-Meta/` pollue graph Obsidian | Moyenne | Bas | Documenter l'exclusion dans README du dossier |
| `/vault-audit` lent sur gros vaults | Basse | Moyen | MVP sans embeddings (titre exact) + progress bar |
| `Fact-Check-Log.md` devient énorme | Basse | Moyen | Rotation annuelle prévue hors scope |
| Users existants surpris par nouveaux fichiers | Moyenne | Bas | Release notes claires + GUIDE.md |
| Détection doublons faux-positifs | Haute | Bas | MVP = titre exact seulement, heuristique améliorable |
| Checkpoints cassent les scripts automatisés | Basse | Haut | `XAIS_BRAIN_CI=1` documenté dans README |

---

## 8. Questions ouvertes pour Xavier — **TRANCHÉES 2026-04-21 (voir §0.3)**

_Conservées pour historique. Les réponses font foi en §0.3._

1. **Q1 — Ordre** : OK avec Phase 1 → 2 → 3 → 4 ci-dessus ? Ou préfères-tu commencer par `/vault-audit` (6E) en standalone ?
2. **Q2 — Rétrocompat** : OK pour ajouter les nouveaux champs frontmatter en additif + flag `xb audit --migrate` opt-in pour compléter les notes existantes ? (vs migration auto au prochain `setup.sh`)
3. **Q3 — `/vault-audit`** : skill dédié OU simple commande `xb audit` OU les deux ? (je propose **les deux** : skill pour l'UX conversationnelle, CLI pour cron futurs)
4. **Q4 — Checkpoints** : bloque vraiment sur stdin ("oui/non") ou affiche juste un warning 5 secondes avant de lancer ? (je propose **stdin bloquant** car c'est le cœur du pattern god-mode)
5. **Q5 — Density rule (6H)** : on la skip au MVP comme recommandé, ou on la fait quand même ?
6. **Q6 — Budget** : on monte un tableau hardcodé des prix LLM (piste 6F) OU on le charge depuis un fichier `scripts/pricing.json` pour faciliter les updates ? (je propose **JSON** pour éviter de toucher le code quand les prix bougent)
7. **Q7 — `99-Meta/` dans Obsidian** : on ajoute automatiquement l'exclusion dans `.obsidian/app.json` ou on laisse Xavier le faire manuellement via le README ? (manuel = plus safe, auto = meilleure UX)
8. **Q8 — GUIDE.md vs README.md** : le README actuel fait déjà quickstart. GUIDE.md = approfondissement. OK avec cette séparation ?

---

## 9. Ce qu'on NE reprend PAS (explicitement)

1. **Prompt monolithique 370 lignes** : l'architecture skills xais-brain est supérieure.
2. **Phase autonome longue sans checkpoint** : risque hallucination cumulative.
3. **Mono-subagent imposé** : on veut pouvoir paralléliser (`/file-intel` sur N PDFs).
4. **Vault sans git** : xais-brain reste git-first.
5. **Génération one-shot de 50 pages sur un sujet** : hors scope — si un jour utile → skill séparé `/vault-generate`, pas dans le workflow principal.
6. **WebSearch obligatoire dans chaque skill** : on le rend **encouragé mais pas bloquant** via le flag `source_knowledge: web-checked`.
7. **Density rule stricte 7 wikilinks** : assouplie à 3, et **opt-in** via piste 6H.

---

## 10. Critères de succès globaux

À la fin des 7 pistes non-optionnelles (6A à 6G hors 6H) :

- [ ] `bash setup.sh` installe un vault avec `99-Meta/`, `GUIDE.md`, skill `/vault-audit`.
- [ ] `xb clip <url>` produit une note avec frontmatter enrichi ET une entrée dans `Fact-Check-Log.md`.
- [ ] `xb file-intel ./docs` annonce le budget, attend un go, traite 2-3 fichiers, attend un go, finit.
- [ ] `xb audit` génère `99-Meta/Audit-YYYY-MM-DD.md` avec 7 sections checklist.
- [ ] CI macOS + Linux verte.
- [ ] Vaults existants (sans `99-Meta/`) ne cassent pas.
- [ ] `GUIDE.md` permet à un tiers de comprendre xais-brain sans autre ressource.

---

## 11. Références

- Source patterns : `/Users/xais/Dev/PROJETS/obsidian-labo-fork/obsidian-god-mode-claude-code/PROMPT-PILOT.md`
- Guide source : `/Users/xais/Dev/PROJETS/obsidian-labo-fork/obsidian-god-mode-claude-code/GUIDE.md`
- Architecture xais-brain : `ARCHITECTURE.md`
- Plan 5 gaps : `specs/todo/00-plan-5-gaps-critiques.md`
- Handoffs récents : `specs/handoffs/007`, `specs/handoffs/008`
- Pattern Karpathy (wiki sémantique compilé vs RAG) — source originelle du god-mode

---

## 12. Prochaine action

1. ✅ Les 8 questions sont tranchées (§0.3).
2. ✅ Piste 6A livrée (commit `fb0d8e0`).
3. ✅ Piste 6B livrée — frontmatter enrichi pour `/clip`, `/file-intel`, `/inbox-zero`.
4. ✅ Piste 6E livrée — skill `/vault-audit` + `scripts/vault_audit.py` + `xb audit` CLI (22 tests verts).
5. ✅ Piste 6D livrée — Fact-Check-Log auto-alimenté par `/clip` (existant) et `/file-intel` (ajout 2026-04-22, 31 tests verts).
6. ✅ Piste 6F livrée — budget annoncé avant batch via `.claude/pricing.json` (ajout 2026-04-22, 74 tests Python + 56 asserts bash verts).
7. → **Piste 6C** — Checkpoints humains (bénéficie du budget de 6F).
8. Chaque piste = 1 commit atomique. Worktree optionnel si piste longue.
9. Déplacement de ce fichier vers `specs/done/` quand **toutes** les pistes non-optionnelles (6C-6G) sont mergées.
