## HANDOFF — xais-brain — 2026-04-11

### État du projet
- Branch: `main`
- Dernier commit: `308dda3` — docs: add ARCHITECTURE.md and expand README with hooks and permissions
- Commits non pushés: 0 (tout est sur `origin/main`)
- Fichiers en cours (non commités) : `specs/handoffs/005-2026-04-09-import-vault-v2-et-coach-hardening.md` (laissé volontairement untracked depuis le pickup, décision Xavier)
- Remote: `origin` = https://github.com/XAISOLUCES/xais-brain (PUBLIC)
- Repo path: `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/`

### Contexte & décisions

**Problème traité** : pickup du handoff 005, suivi de 4 chantiers consécutifs déclenchés par Xavier au fil de la session :
1. Audit des dossiers de test traînants dans `~`
2. Extraction des patterns intéressants depuis `~/second-brain` avant suppression
3. Audit complet de toutes les fonctionnalités du repo
4. Mise à jour du README + création d'une doc ARCHITECTURE.md avec arborescence et diagrammes ASCII

**Approche choisie pour le cleanup `~/`** : 6 dossiers identifiés (`second-brain`, `second-brain.backup-pre-import-test`, `xais-brain-vault`, `xais-brain-vault-2`, `xais-brain-test`, `xais-brain-vault-3`). 4 supprimés via `trash` (jamais `rm -rf` — bloqué par hook Xavier) :
- `xais-brain-vault`, `xais-brain-vault-2`, `xais-brain-test` — obsolètes (validation Xavier)
- `second-brain.backup-pre-import-test` — backup obsolète après extraction
- `second-brain` — supprimé après extraction des patterns (validation Xavier)
- **Restant** : `~/xais-brain-vault-3` (test actif, modifié aujourd'hui à 18:50 par Obsidian — `.obsidian/workspace.json`, benign)

**Approche choisie pour l'extraction `second-brain`** : option **1A + 2A + 3 jeter** (validée par Xavier).
- 1A = skills `client`/`project` → `vault-template/.claude/skills/` (canoniques pour tous les users)
- 2A = scripts Python → bundled dans `file-intel/scripts/` ❌ **ABANDONNÉ après inspection**
- 3 jeter = CLAUDE.md adopté → pas de valeur de référence

**Pivot inattendu sur les scripts Python** : `process_docs_to_obsidian.py` et `process_files_with_gemini.py` (datés du 7 avril 17:00) sont en réalité les **prototypes obsolètes** de `scripts/file_intel.py` (refactoré le 7 avril 22:51 avec architecture providers gemini/claude/openai). Le repo a déjà la version améliorée et `setup.sh` la copie déjà dans chaque vault. **Rien à extraire** pour les scripts. Tâche #3 supprimée.

**Approche choisie pour la promotion canonique de `client`/`project`** : ajout au tableau hardcodé de `setup.sh` (skills list 8 → 10) pour qu'ils soient installés par défaut chez tous les users. Pas un patch optionnel. Rationale : les patterns "load context d'un client" et "load context d'un side-project" sont génériques pour tout dev freelance, pas juste Xavier.

**Modifications appliquées aux skills extraits** :
- Ajout du frontmatter canonique : `user-invocable: true`, `disable-model-invocation: false`, `model: haiku` (alignement avec daily/tldr qui sont aussi des "context loaders")
- Remplacement de "Xavier" par "l'utilisateur" / "the user" dans le body (généralisation)
- Heading H1 simplifié de "# Client — Load a client's full context" → "# client" (cohérence avec daily/tldr)

**Approche choisie pour l'audit** : audit complet en 8 tâches parallèles (TaskCreate × 8). Lecture exhaustive de :
- Tous les SKILL.md (10 + frontmatter)
- setup.sh (steps 1-9 + helpers)
- vault-template/CLAUDE.md, MEMORY.md, vault-config.json
- 2 hooks (.sh)
- coach.md (output style)
- settings.json (permissions)
- file_intel.py + 3 providers + base.py + _prompts.py
- requirements.txt + .env.example + .gitignore
- README.md actuel

**Décisions d'architecture clés** :

- **2 commits atomiques séparés** pour les corrections d'audit (validation Xavier en fin de session) : `4af5cda` (fix bugs setup.sh + file-intel) puis `308dda3` (README + ARCHITECTURE.md). Rationale : séparer les fixes des additions docs pour git log lisible.
- **ARCHITECTURE.md à la racine** (pas dans `docs/` ni `specs/`). Convention : doc d'architecture top-level pour visibilité maximale comme dans les repos OSS standards.
- **README garde sa focale "user discovery"**, ARCHITECTURE.md prend le deep dive technique. Pas de duplication — README link vers ARCHITECTURE.md sous la section "Structure du vault".
- **3 commits pushés en un seul `git push`** : `b9e2dd6` + `4af5cda` + `308dda3`.

### Findings critiques

- **Bug fix #1** : `vault-template/.claude/skills/file-intel/SKILL.md` description annonçait support `PPTX, XLSX, CSV, JSON` mais le `EXTRACTORS` dict dans `scripts/file_intel.py:60-65` ne contient que `pdf, docx, txt, md`. **Faux marketing** sur 4 formats. Fixed dans le commit `4af5cda` (description + body lignes 44 et 60).
- **Bug fix #2** : `setup.sh:286` (existing-vault prompt) et `setup.sh:644` (final summary) disaient encore "8 slash commands". Inconsistance avec mon commit `b9e2dd6` qui a déjà passé la liste à 10. Fixed dans `4af5cda`.
- **README inaccuracies** corrigées :
  - Ligne 81 (vault structure tree) : "8 slash commands" → "10 slash commands"
  - Section "Ajouter ta propre skill" : exemple frontmatter outdated (manquait `user-invocable`, `disable-model-invocation`, `model`) — mis à jour avec tableau explicatif des champs
  - Tableau "Ce qui est installé" : ajouté ligne "Permissions cadrées" + nommé les 5 skills Kepano (`obsidian-cli`, `obsidian-markdown`, `obsidian-bases`, `json-canvas`, `defuddle`)
- **Section README manquante** : aucune explication du comportement réel des hooks. Ajoutée nouvelle section "Hooks et permissions" avec 3 sous-sections (SessionStart, UserPromptSubmit, settings.json allow/deny).
- **Mode Coach FR** : section README ne mentionnait pas la règle "Obligation finale (non-négociable)" ajoutée dans le handoff 005. Précisée maintenant.
- **`scripts/providers/_prompts.py:6-64`** : prompt Gemini partagé entre tous les providers. Format de sortie OBLIGATOIRE = frontmatter Obsidian + TL;DR + Points clés + Concepts + Actions + Notes brutes. Sortie en français par défaut.
- **`vault-template/.claude/settings.json:24-26`** : `Bash(rm -rf:*)` est explicitement dans la deny list. Plus `Edit(.claude/**)` et `Write(.git/**)`. Cohérent avec le hook Xavier qui bloque `rm -rf` (j'ai été bloqué une fois cette session, j'ai dû passer par `trash`).
- **Compteur skills `setup.sh:601-603`** : utilise `find $VAULT_PATH/.claude/skills -maxdepth 1 -type d` pour compter dynamiquement, donc affichera correctement 10 (ou 15 avec Kepano) à l'install. Robuste.
- **`session-init.sh:13-23`** : parse `vault-config.json` via Python inline (sans dep `jq`) pour exporter `VAULT_INBOX_DIR`, etc. Permet aux skills de résoudre les noms de dossiers même après un `/import-vault` qui aurait remappé `projects/` → `clients/`.
- **`skill-discovery.sh:20-35`** : parse le frontmatter SKILL.md via `awk` (pas `sed`, plus portable BSD/GNU). Liste seulement les skills `user-invocable: true`. Triggers FR : `skills?, commandes?, que peux[- ]tu, aide[ -]moi, quoi faire, slash`.

### Terminé

- **Cleanup vault-3 mystery** : `~/xais-brain-vault-3` modifié 04-11 18:50 → enquête `find -mtime -2` → c'est `.obsidian/{workspace,app,core-plugins,appearance}.json` → Obsidian a touché à la config UI. Benign, vault non modifié manuellement.
- **Cleanup `~/` test folders** : 4 dossiers supprimés via `trash` (récupérables 30 jours dans corbeille macOS). 332K libérés sur les 3 obsolètes + 124K du backup + ~172K de second-brain.
- **Extraction `second-brain`** : 2 skills custom (`client`, `project`) copiés dans `vault-template/.claude/skills/`, généralisés (Xavier → user), frontmatter canonique ajouté. `setup.sh` étendu : skills list 8 → 10. `vault-template/CLAUDE.md` + `README.md` mis à jour avec les 2 nouvelles commandes.
- **Audit complet** : 8 tâches TaskCreate exécutées (map repo, inventory skills, audit setup.sh, audit hooks/output-styles, audit scripts/providers, compare README, update README, create ARCHITECTURE.md).
- **3 bugs de docs corrigés** : `setup.sh × 2` lignes (286, 644) + `file-intel SKILL.md × 3` (description + 2 lignes body listant les formats fictifs).
- **README.md enrichi** : nouvelle section "Hooks et permissions", arborescence vault à jour (10 skills, .env, scripts/ détaillé), exemple "Ajouter ta propre skill" avec frontmatter à jour + tableau, mention obligation Coach FR, lien vers ARCHITECTURE.md.
- **ARCHITECTURE.md créé** : 541 lignes. 10 sections incluant arborescence repo complète, arborescence vault installé, diagramme de composants ASCII, 4 flux d'exécution (setup.sh 9 étapes, SessionStart hook, UserPromptSubmit hook, /file-intel pipeline), schémas vault-config.json + settings.json, doc du méta-layer specs/.
- **3 commits propres pushés sur `origin/main`** : `b9e2dd6` (feat skills), `4af5cda` (fix bugs), `308dda3` (docs).

### Prochaine étape immédiate

Aucune action technique pendante de cette session. Options pour la prochaine session, par priorité décroissante :

1. **Lecture critique de `ARCHITECTURE.md`** par Xavier (engagement pris en fin de session) → soit thumbs-up, soit corrections précises. Xavier doit identifier ce qui est flou ou ce qui manque dans la doc avant qu'elle dorme dans le repo.

2. **Test réel de `/client` et `/project` post-push** dans un vault frais. Bootstrap un vault, lancer `claude`, tester `/project` (devrait demander quel projet, lister `projects/` vide ou proposer de bootstrap), puis `/client`. Vérifier que le frontmatter `model: haiku` charge correctement.

3. **Décider du sort du handoff 005 untracked** — Xavier l'a explicitement laissé untracked au début de cette session. À committer dans un futur `chore(specs)` ou à supprimer si il ne veut plus de cette trace.

4. **Reprendre les pistes du handoff 005 toujours en attente** :
   - Test `/import-vault` v2 en session Claude Code réelle (pas simulation)
   - Re-test `coach.md` v2 avec Sonnet (pas Haiku)
   - Activer `coach.md` en session réelle via `/output-style`
   - Fix variable `$XAIS_BRAIN_REPO` (mentionnée dans le skill mais définie nulle part — bloqueur silencieux pour les early adopters qui clonent ailleurs que `~/Dev/XAIS_2ND_BRAIN/xais-brain`)

### Risques identifiés

- **`/client` et `/project` non testés en session réelle Claude Code** — copiés depuis `~/second-brain/.claude/skills/` (où ils existaient et fonctionnaient), généralisés (Xavier → user), frontmatter ajouté, mais aucun test post-extraction. Risque résiduel : le `model: haiku` pourrait ne pas être suffisant pour certains cas d'usage (haiku gère bien la lecture/présentation mais pas le raisonnement complexe). À monitorer.

- **`setup.sh` skills list hardcodée** : ajouter un nouveau skill canonique demande d'éditer 4 endroits (la liste `setup.sh:344`, `setup.sh:93` "10 skills", `setup.sh:286` prompt, `setup.sh:644` summary). Pas de single source of truth. Si on rajoute un 11e skill, il faudra penser à tout. Risque de drift documentation/réalité (déjà arrivé entre le commit b9e2dd6 et aujourd'hui — les lignes 286 et 644 étaient restées à "8" jusqu'à 4af5cda). Refactor possible : compter dynamiquement via `find vault-template/.claude/skills -maxdepth 1 -type d`.

- **README + ARCHITECTURE.md non relus par Xavier au moment du push** — engagement pris pour plus tard. Si quelque chose est faux ou pas clair, ça part en prod public sur GitHub avant la review. Acceptable car xais-brain est en alpha et le risque d'impact est faible (pas de breaking change), mais à corriger dès que Xavier identifie un problème.

- **Commits poussés mais non testés sur un vault frais** : les 3 commits modifient `setup.sh`, `vault-template/`, et la doc. Personne n'a relancé `setup.sh` après ces changements. Le compteur dynamique `verify_install` devrait afficher `10 skills` correctement, mais ça reste théorique.

- **Le mystère "vault-3 modifié à 18:50"** est résolu (Obsidian touche workspace.json) mais pourrait re-apparaître et créer de la confusion à chaque session. Pas de fix nécessaire — c'est le comportement normal d'Obsidian qui sauvegarde son state UI à chaque interaction.

### Prêt pour la prod ?

- [x] Fix bugs documentation (file-intel formats + setup.sh counts)
- [x] Skills `/client` et `/project` extraits, frontmatter canonique, généralisés
- [x] `setup.sh` étendu pour installer les nouveaux skills
- [x] README.md cohérent avec la réalité du code (10 skills, hooks expliqués, settings.json documenté, Kepano nommés)
- [x] `ARCHITECTURE.md` complet avec arborescences ASCII et 4 flux d'exécution
- [x] Commits conventionnels séparés (3 commits atomiques)
- [x] Push réussi sur `origin/main`
- [ ] **Test fresh install avec setup.sh sur un vault vide** — PAS FAIT (théoriquement OK car compteur dynamique)
- [ ] **Test runtime des skills `/client` et `/project`** — PAS FAIT
- [ ] **Review humaine de `ARCHITECTURE.md`** — PAS FAIT (Xavier a engagé de regarder plus tard)
- [ ] **Fix variable `$XAIS_BRAIN_REPO`** (héritage du handoff 005) — PAS FAIT

**Décision : PARTIEL** — toutes les modifications sont commitées et pushées proprement, le code est cohérent, les bugs identifiés sont fixés. Mais aucun test runtime n'a été exécuté sur les nouveaux skills ni sur le setup.sh modifié. Acceptable pour un push de doc+refactor sur un projet alpha, mais une session de validation runtime serait prudente avant de communiquer xais-brain v0.3 publiquement.

### Fichiers clés

**Modifiés et committés cette session** :

- [vault-template/.claude/skills/client/SKILL.md](vault-template/.claude/skills/client/SKILL.md) — nouveau skill canonique, 89 lignes, frontmatter `model: haiku`, généralisé pour tout user
- [vault-template/.claude/skills/project/SKILL.md](vault-template/.claude/skills/project/SKILL.md) — nouveau skill canonique, 83 lignes, frontmatter `model: haiku`, généralisé pour tout user
- [vault-template/.claude/skills/file-intel/SKILL.md](vault-template/.claude/skills/file-intel/SKILL.md) — bug fix description (PDF/DOCX/TXT/MD seulement, plus de PPTX/XLSX/CSV/JSON fictifs)
- [vault-template/CLAUDE.md](vault-template/CLAUDE.md) — slash commands list 8 → 10 (ajout `/project` et `/client`)
- [setup.sh](setup.sh) — skills list line 344 (8 → 10), banner line 93 (8 → 10), prompt line 286 (8 → 10), final summary line 644 (8 → 10 + ajout `/project /client`)
- [README.md](README.md) — section Hooks et permissions ajoutée, vault tree updated, frontmatter example fixé, Kepano nommés, mention coach obligation finale, lien ARCHITECTURE.md
- [ARCHITECTURE.md](ARCHITECTURE.md) — **NOUVEAU**, 541 lignes, doc technique complète

**Commits de cette session (pushés)** :
- `b9e2dd6` — feat(skills): add /client and /project skills
- `4af5cda` — fix(docs): correct outdated skill count and file-intel format claims
- `308dda3` — docs: add ARCHITECTURE.md and expand README with hooks and permissions

**Fichier untracked laissé volontairement** :
- [specs/handoffs/005-2026-04-09-import-vault-v2-et-coach-hardening.md](specs/handoffs/005-2026-04-09-import-vault-v2-et-coach-hardening.md) — décision Xavier de le laisser intracked (pas de raison explicite donnée)

**Vaults sur disque (état final)** :
- `~/xais-brain-vault-3` — seul vault restant, 168K, 13 skills (snapshot pré-extraction client/project), `vault-config.json provider=gemini`, ouvert dans Obsidian
- Tous les autres dossiers `xais-brain-vault*` et `second-brain*` sont dans la corbeille macOS (récupérables 30 jours)

**Repo GitHub** :
- https://github.com/XAISOLUCES/xais-brain — public, maintenant 17 commits sur `main` (dernier `308dda3`), up-to-date avec le local

### État du contexte

- Utilisation : ~70-80% estimée au moment du handoff. Session très dense : pickup 005 + 4 chantiers consécutifs avec lectures multiples (10 SKILL.md, setup.sh complet, hooks, output-styles, scripts Python, README), création d'un fichier de 541 lignes (ARCHITECTURE.md), 3 commits + push, 13 tâches TaskCreate complétées dont 12 marquées completed (1 deleted suite au pivot scripts Python). Plusieurs lectures git status répétées entre les commits. Bien au-delà du seuil idéal de handoff précoce.
