## Case facts
- **Branch** : `main`
- **Last commit** : `fb0d8e0` — feat: add 99-Meta/ audit trail folder to vault template
- **Open PRs** : none
- **Blocking issue** : none
- **Next concrete step** : `/XD-build specs/todo/06-integration-god-mode-patterns.md` sur la **piste 6B** (frontmatter enrichi `/clip` + `/file-intel` + `/inbox-zero`)

## HANDOFF — xais-brain — 2026-04-20

### État du projet
- Branch: `main`
- Dernier commit: `fb0d8e0` — feat: add 99-Meta/ audit trail folder to vault template
- Commits non pushés: 0 (tout pushé, CI verte)
- Fichiers en cours (non commités) :
  - `specs/handoffs/007-2026-04-12-5-gaps-session1-cli-ci-linux.md` (untracked, hérité handoff 008)
  - `specs/handoffs/008-2026-04-12-5-gaps-session2-web-clipper.md` (untracked, hérité handoff 008)
  - `specs/todo/06-integration-god-mode-patterns.md` (untracked, plan produit cette session)
- Remote: `origin` = https://github.com/XAISOLUCES/xais-brain (PUBLIC)

### Contexte & décisions

**Problème traité** : Xavier a partagé un fork `obsidian-god-mode-claude-code` (LE LABO IA) — générateur one-shot de vault Obsidian dense (30-50 pages, wikilinks, fact-checks WebSearch, pattern Karpathy). Objectif : extraire les patterns transférables vers xais-brain.

**Approche choisie** :
- **Analyse approfondie via `explore-codebase` agent** → rapport structuré (essence, points forts, patterns, à éviter, verdict)
- **Verdict** : cherry-picking, pas intégration. Les deux projets sont orthogonaux (god-mode = one-shot generator, xais-brain = second brain continu)
- **Plan `/XD-plan`** décomposé en 8 pistes atomiques (6A → 6H), 13-19h sur 4-5 sessions
- **Piste 6A** implémentée cette session (la plus safe, débloque 6B/6D/6E)
- **Rejeté** : importer le prompt monolithique PROMPT-PILOT.md (370 lignes) — non-maintenable, architecture skills xais-brain reste souveraine

**Décisions d'architecture clés** :
- Frontmatter enrichi (pistes 6B) = **additif uniquement**, aucun champ renommé, rétrocompat garantie
- Migration notes existantes = **opt-in** via `xb audit --migrate` (pas de migration forcée)
- `XAIS_BRAIN_CI=1` doit **bypasser tous les checkpoints humains** (sinon CI pend)
- `/vault-audit` = **skill Claude + CLI `xb audit`** (les deux, mêmes 7 détections)
- MVP `/vault-audit` **sans embeddings** (titre exact + word count pour doublons)

### Findings critiques

- **Piste 6A validée** — tests bash 47 passed, tests Python 12/12, CI macOS + Linux vertes (run `24687487275`)
- **Commit `fb0d8e0`** : 7 fichiers, +167 lignes (vault-template/99-Meta/ + ARCHITECTURE + setup.sh + tests/test_setup.sh)
- **`safe_cp` idempotent** dans setup.sh : ne jamais écraser les fichiers 99-Meta/ existants (préserver cases cochées + entrées manuelles)
- **Pattern Karpathy** (wiki sémantique compilé vs re-RAG) — source d'inspiration du repo god-mode, hors scope direct pour xais-brain
- **Consolidation dream** : 3 nouveaux fichiers mémoire (`preferences.md`, `decisions.md`, `patterns.md`) + `MEMORY.md` reconverti en index pur (2026-04-20)
- **Warning Node.js 20 deprecated** en CI (non bloquant) — `actions/checkout@v4` + `actions/setup-python@v5`, deadline juin 2026

### Terminé

- **Pickup session 008** — handoff lu et assimilé
- **Analyse repo obsidian-god-mode-claude-code** via `explore-codebase` agent — rapport complet (essence, 5 points forts, 6 patterns transférables, 6 à éviter, verdict cherry-picking)
- **Plan `/XD-plan`** écrit dans `specs/todo/06-integration-god-mode-patterns.md` — 8 pistes (6A-6H), 13-19h, questions ouvertes §8
- **Piste 6A implémentée** — `vault-template/99-Meta/` complet (README + Audit.md + Fact-Check-Log.md + Session-Debriefs/.gitkeep), setup.sh mis à jour avec `safe_cp` idempotent, ARCHITECTURE.md à jour (2 sections), tests/test_setup.sh +6 assertions
- **Validate + commit + push** — commit `fb0d8e0`, CI verte sur les 2 jobs

### Prochaine étape immédiate

**1. `chore(specs): track handoffs 007-008 and god-mode plan`** (30 sec)
- Commit des 3 fichiers untracked :
  - `specs/handoffs/007-2026-04-12-5-gaps-session1-cli-ci-linux.md`
  - `specs/handoffs/008-2026-04-12-5-gaps-session2-web-clipper.md`
  - `specs/todo/06-integration-god-mode-patterns.md`

**2. `/XD-build specs/todo/06-integration-god-mode-patterns.md` piste 6B** (2-3h)
- Frontmatter enrichi additif pour `/clip`, `/file-intel`, `/inbox-zero`
- Champs : `source`, `source_url`, `source_file`, `source_knowledge`, `verification_date`, `statut`, `importance`
- Rétrocompat : aucun champ existant renommé

**Ordre pistes validé** : 6B → 6D → 6F → 6E → 6C → 6G (+ 6H optionnel)

### Risques identifiés

- **Piste 6B — breaking change potentiel sur vaults existants** : mitigation = additif uniquement + migration opt-in `xb audit --migrate`
- **Piste 6E — complexité détection doublons** : MVP = titre exact + word count, pas d'embeddings
- **Piste 6F — pricing tokens hardcodé vs config** : **à trancher** (question ouverte §8)
- **Piste 6C — checkpoints en CI** : bypass `XAIS_BRAIN_CI=1` **doit être testé explicitement**
- **Dettes techniques héritées** :
  - Migration GitHub Actions → Node.js 24 (deadline **juin 2026**, bloquant à terme)
  - `$XAIS_BRAIN_REPO` toujours non fixée (hérité handoff 005, bloqueur silencieux)
  - Skills `/client` et `/project` non testés en runtime (hérité handoff 006)
  - `setup.sh` ~900+ lignes — refactoring conseillé après toutes les pistes
- **Piste 5 (demo GIF) toujours reportée** — nécessite VHS installé (`brew install vhs`)

### Prêt pour la prod ?

- [x] Tests bash OK (47 passed)
- [x] Tests Python OK (12 passed)
- [x] Bash syntax OK (setup.sh, vault-cli.sh, test_setup.sh)
- [x] CI macOS + Linux verte (run `24687487275`)
- [x] Tous les commits pushés
- [x] Piste 6A dans `specs/todo/06-integration-god-mode-patterns.md` (à déplacer dans `specs/done/` après toutes les pistes)
- [ ] **chore(specs) des 3 untracked** — PAS FAIT (30 sec pour la prochaine session)
- [ ] **Pistes 6B-6H** — PAS FAIT (planifiées, ~12-17h restantes)

**Décision : PARTIEL** — Piste 6A terminée, testée, commitée et pushée. 7 pistes restantes avec ordre clair. CI verte.

### Fichiers clés

**Créés cette session** :
- [specs/todo/06-integration-god-mode-patterns.md](specs/todo/06-integration-god-mode-patterns.md) — Plan complet 8 pistes (untracked)
- [vault-template/99-Meta/README.md](vault-template/99-Meta/README.md) — Rôle + instructions exclusion graphe Obsidian
- [vault-template/99-Meta/Audit.md](vault-template/99-Meta/Audit.md) — Template 7 sections (orphelines, anémiques, doublons, frontmatter, tags, wikilinks, to-verify)
- [vault-template/99-Meta/Fact-Check-Log.md](vault-template/99-Meta/Fact-Check-Log.md) — Log append-only des sources vérifiées
- [vault-template/99-Meta/Session-Debriefs/.gitkeep](vault-template/99-Meta/Session-Debriefs/.gitkeep) — Alimenté par `/tldr`

**Modifiés cette session** :
- [setup.sh](setup.sh) — `mkdir -p` du dossier + 4 blocs `safe_cp` idempotents
- [ARCHITECTURE.md](ARCHITECTURE.md) — 2 sections mises à jour (arbo repo + arbo vault installé)
- [tests/test_setup.sh](tests/test_setup.sh) — 6 nouvelles assertions sur `99-Meta/`

**Références** :
- Source patterns : `/Users/xais/Dev/PROJETS/obsidian-labo-fork/obsidian-god-mode-claude-code/PROMPT-PILOT.md`
- Guide source : `/Users/xais/Dev/PROJETS/obsidian-labo-fork/obsidian-god-mode-claude-code/GUIDE.md`

**Specs restantes (todo)** :
- [specs/todo/00-plan-5-gaps-critiques.md](specs/todo/00-plan-5-gaps-critiques.md) — Plan maître 5 gaps (partiellement fait, piste 5 restante)
- [specs/todo/05-demo-gif-readme.md](specs/todo/05-demo-gif-readme.md) — Piste 5 (nécessite VHS)
- [specs/todo/06-integration-god-mode-patterns.md](specs/todo/06-integration-god-mode-patterns.md) — 7 pistes restantes (6B-6H)

**Commits de cette session** :
- `fb0d8e0` — feat: add 99-Meta/ audit trail folder to vault template

### 8 questions ouvertes à trancher avant prochain `/XD-build`

1. **Ordre pistes** : 6B → 6D → 6F → 6E → 6C → 6G (+ 6H) — confirmé ?
2. **Rétrocompat frontmatter** : additif uniquement + `xb audit --migrate` opt-in — confirmé ?
3. **`/vault-audit`** : skill Claude **et** commande `xb audit` (les deux) — confirmé ?
4. **Frontmatter incomplet** dans `xb audit` : warning ou blocker ?
5. **Density rule (6H)** : go ou skip ?
6. **Pricing JSON (6F)** : hardcodé dans le code ou fichier config séparé ?
7. **Exclusion 99-Meta/ dans Obsidian graph** : uniquement doc manuelle, ou tentative de config auto via `.obsidian/app.json` ?
8. **GUIDE.md (humain) vs CLAUDE.md (Claude)** : séparation validée ✅

### État du contexte
- Utilisation : ~45% estimée au moment du handoff. Session dense : pickup + analyse fork + `/XD-plan` 8 pistes + build/validate/commit/push piste 6A + handoff. Bonne marge pour la suite.

### Build en cours (specs/state.json)
(pas de build en cours)

### État git (au moment du handoff)
```
?? specs/handoffs/007-2026-04-12-5-gaps-session1-cli-ci-linux.md
?? specs/handoffs/008-2026-04-12-5-gaps-session2-web-clipper.md
?? specs/todo/06-integration-god-mode-patterns.md
```
(ce handoff 009 s'ajoutera à la liste au prochain `git status`)

### Derniers commits
```
fb0d8e0 feat: add 99-Meta/ audit trail folder to vault template
e327ee9 feat: add web clipper (URL → Markdown in inbox/)
a1d0f56 feat: add Linux support (Ubuntu/Debian, Fedora, Arch)
925ae97 chore(specs): track handoffs 005-006 and 5-gaps plan
625733a feat: add vault CLI wrapper (xb) with 7 commands
```
