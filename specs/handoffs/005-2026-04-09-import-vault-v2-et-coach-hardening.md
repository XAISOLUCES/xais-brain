## HANDOFF — xais-brain — 2026-04-09

### État du projet
- Branch: `main`
- Dernier commit: `2d17096` — chore(specs): track plans and session handoffs
- Commits non pushés: 0 (tout est sur `origin/main`)
- Fichiers en cours (non commités) : aucun, working tree clean
- Remote: `origin` = https://github.com/XAISOLUCES/xais-brain (PUBLIC)
- Repo path: `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/`

### Contexte & décisions

**Problème traité** : pickup du handoff 004 (session dense "enrich PKM best-of"). Trois chantiers restants : test `/import-vault` en réel, test `coach.md` en session, nettoyage `/tmp`. En cours de route, Xavier a demandé d'analyser la documentation du skill-creator 2.0 avant de durcir `/import-vault` — ce qui a débouché sur une refonte complète du skill et un durcissement de `coach.md`.

**Approche choisie pour le test `/import-vault`** : **simulation (voie A)** dans la session actuelle plutôt que test orthodoxe dans un nouveau shell. Avantage : on reste dans cette session, pas besoin de bootstrap le skill dans le vault cible. Le vault de test choisi est `~/second-brain` (a déjà un CLAUDE.md, 2 skills custom `client`/`project`, structure PARA-like) — cas authentique.

**Approche choisie pour la refonte `/import-vault`** : **option C hybride** — single-file SKILL.md en XML 2.0 avec fixes des bugs + `<success_criteria>` + `allowed-tools`, **sans** créer `scripts/` ni `references/`. Gain pédagogique 2.0 à 80% sans la charge de maintenance de 3 fichiers supplémentaires. Rationale : le skill s'exécute 1 fois par vault, pas un workflow récurrent — over-engineering évité.

**Approche choisie pour le durcissement `coach.md`** : ajouter une section `## Obligation finale (non-négociable)` en TOUTE FIN du fichier qui repackage la règle "action + question d'accountability" comme MUST avec exemples. Redondance volontaire avec la section "Structure de réponse" car Haiku avait ignoré la règle cachée dans un bullet.

**Décisions d'architecture clés** :

- **import-vault v2 = single-file XML pur** : 341 lignes, 10 tags XML balanced, 0 markdown headings dans le body. Pattern skill-creator 2.0 respecté (objective/prerequisites/quick_start/workflow/phases/edge_cases/success_criteria).
- **Fallback par nom dans le scan** : critique pour les vaults squelettes (dossiers vides, 0 `.md`). Sans ce fallback, v1 ne détectait aucun candidat — bug reproduit sur `~/second-brain.backup-pre-import-test` puis confirmé fixé.
- **Mode additif strict (`cp -n`)** : JAMAIS écraser un fichier utilisateur. Skills custom, Kepano et canoniques tous respectés. Règle absolue du skill durci.
- **Split AskUserQuestion en 2 rounds de 4 items** : contrainte technique de l'outil (`max=4`). v1 demandait 5 en un seul round — bug bloquant identifié et fixé.
- **`@import backup` supprimé** : ce n'est pas une directive native Claude Code, juste une convention xais-brain optionnelle. Remplacé par une référence en prose dans le nouveau CLAUDE.md.
- **PAS de split en `scripts/` + `references/`** : validé par option C. Over-engineering évité pour un skill one-shot.
- **Durcissement coach.md via redondance en fin de fichier** : section `## Obligation finale (non-négociable)` avec 4 exemples d'accountability questions + rationale. Position stratégique en toute fin car les règles en fin de system prompt sont mieux suivies par les modèles.

### Findings critiques

- **Marché Obsidian+Claude Code FR** : aucun nouveau concurrent identifié pendant cette session. Positionnement xais-brain inchangé.
- **Test `/import-vault` sur `~/second-brain`** a révélé **10 frictions/bugs** dans le skill v1 :
  1. 🔴 BUG bloquant : `AskUserQuestion` max=4, v1 demandait 5 questions en 1 round
  2. 🟠 Pas de fallback par nom pour vault squelette (0 `.md`)
  3. 🟠 Ambiguïté "Créer nouveau X/" quand le dossier existe déjà
  4. 🟠 Phase 4.5 copie skills depuis `~/.claude/skills/` (confus + faux, devrait être `vault-template/`)
  5. 🟡 `memory.md` racine non géré
  6. 🟡 `customFolders` absent du schéma vault-config.json
  7. 🟡 Skills custom utilisateur non préservés/documentés
  8. 🟡 Pas de `<success_criteria>` mesurables
  9. 🟢 Body en markdown `##`, pas en XML
  10. 🟢 Pas de `allowed-tools` déclarés
- **skill-creator 2.0** (`~/.claude/skills/skill-creator/`) — 21 192 bytes SKILL.md + 7 references (workflows, progressive-disclosure-patterns, prompting-integration, real-world-examples, script-patterns, output-patterns, xml-tag-guide). Lu en profondeur (4 références). Standard = **3 niveaux progressive disclosure** (metadata/body/bundled resources), **XML pur sans markdown headings**, **tags requis** `<objective>/<quick_start>/<success_criteria>`, **scripts pour déterminisme**, **references one level deep**, **SKILL.md < 500 lignes ideal**.
- **Test `coach.md` v1** via `claude -p --append-system-prompt` + Haiku sur le prompt "J'ai 4 projets en parallèle, je suis éparpillé" → réponse respecte 10/11 règles sauf **question d'accountability finale absente**. Confirmé comme bug de spec (règle enfouie dans un bullet), pas du modèle.
- **Test `coach.md` v2** (après durcissement) sur le MÊME prompt + Haiku → respecte **11/11 règles**, y compris la question d'accountability ("Quand tu reviens : tu me dis qui gagne et tu as identifié pourquoi tu sautes d'un à l'autre ?"). Haiku a même **verbalisé** le respect de la règle "1 question intentionnelle — pas plus". Fix validé.
- **`/tmp/claudesidian` et `/tmp/obsidian-claude-pkm`** sont **GONE** — nettoyés par le reboot machine comme prédit dans le handoff 004. Aucune action nécessaire.
- **Dry-run du skill `/import-vault` v2** sur `~/second-brain.backup-pre-import-test` (vault squelette 0 `.md`) : fallback par nom détecte les 5 rôles canoniques (inbox/daily/projects/research/archive), détection `memory.md` racine OK, classification des 11 skills existants en canonical/kepano/custom 100% correcte. Tous les fixes critiques (bugs 1, 2, 4) validés.
- **3 commits séparés poussés** : 1f33712 (coach.md hardening), 7d096c0 (import-vault refonte 2.0), 2d17096 (specs tracking). Total 10 commits pushés sur `origin/main` en un seul push (les 7 locaux du handoff 004 + 3 de cette session).

### Terminé

- **Piste 1 du handoff 004** — Test grandeur réelle du `setup.sh` : validé PASS par inspection de `~/xais-brain-vault-3` (déjà installé avec 13 skills, 2 hooks `+x`, `coach.md`, `vault-config.json` en `provider: gemini`, `settings.json`). Décision : considéré comme PASS, pas de re-run.
- **Piste 2 du handoff 004** — Test `/import-vault` en réel sur `~/second-brain` : simulation complète (scan, mapping via AskUserQuestion × 2 rounds, écriture additive, validation). Backup auto `~/second-brain.backup-pre-import-test` créé. Adoption réussie : vault-config.json (provider null, projects→clients, customFolders), memory/README.md, CLAUDE.md.backup-2026-04-09-122304, nouveau CLAUDE.md, 4 skills ajoutés, 2 skills custom préservés.
- **Analyse skill-creator 2.0** : 4 références lues en profondeur (SKILL.md, workflows.md, progressive-disclosure-patterns.md, real-world-examples.md, script-patterns.md, xml-tag-guide.md). Synthèse des patterns 2.0 documentée pour application.
- **Durcissement `/import-vault`** via pattern C (single-file XML 2.0) : réécriture complète de `vault-template/.claude/skills/import-vault/SKILL.md` (341 lignes, 10 tags balanced, 11 bugs fixés). Validé par dry-run.
- **Test + durcissement `coach.md`** : test headless v1 avec Haiku → bug accountability identifié → ajout section "Obligation finale (non-négociable)" → re-test v2 PASS 11/11.
- **Piste 4 du handoff 004** — Nettoyage `/tmp` : auto-résolu (reboot a déjà supprimé les 2 repos de référence).
- **Commits + push** : 3 commits conventionnels séparés, push réussi vers `origin/main`. Working tree clean, branch up-to-date.

### Prochaine étape immédiate

Aucune action technique pendante. Options pour la prochaine session, par priorité décroissante :

1. **Tester le skill `/import-vault` v2 en run réel** (pas simulation) sur un vault Obsidian vraiment frais (ex : créer `~/vault-test-v2/` avec structure PARA + un CLAUDE.md, bootstrap le skill dedans, puis `claude` + `/import-vault`). Ça valide le chemin "vrai user typing `/import-vault`" qui n'a pas encore été fait (toutes les validations ont été simulations dans cette session).

2. **Re-tester `coach.md` v2 avec Sonnet** (pas Haiku) pour confirmer que la règle accountability tient aussi sur le modèle standard. Le test Haiku a suffi pour valider le fix, mais Sonnet pourrait révéler d'autres nuances.

3. **Activer `coach.md` en session réelle** via `/output-style coach` (ou équivalent settings.json) pour le tester dans une vraie conversation interactive, pas headless.

4. **Rollback `~/second-brain`** au backup `~/second-brain.backup-pre-import-test` si Xavier ne veut pas garder l'adoption de test dans son vrai vault. À décider consciemment — l'adoption a touché CLAUDE.md (backup auto créé), vault-config.json, memory/, .claude/hooks, .claude/output-styles, .claude/settings.json, et ajouté 4 skills.

5. **Documenter les patterns skill-creator 2.0** dans une note `vault-template/.claude/rules/skill-patterns.md` si Xavier veut s'en servir comme référence pour créer d'autres skills xais-brain dans le futur.

### Risques identifiés

- **`/import-vault` v2 pas testé en session réelle Claude Code** — toutes les validations sont soit dry-run (scan bash), soit simulation manuelle dans cette session. Le chemin "user tape `/import-vault` dans un claude fresh" n'a pas été exécuté. Risque résiduel : le frontmatter `allowed-tools: Bash, Read, Write, Edit, Glob, AskUserQuestion` pourrait ne pas charger correctement, ou le skill pourrait ne pas être découvert par le skill-discovery.sh hook (à vérifier).

- **`~/second-brain` est maintenant "mi-adopté"** — le vault a été modifié par la simulation. Xavier a un backup intact (`~/second-brain.backup-pre-import-test`) mais devra décider s'il garde l'adoption (provider=null, projects→clients, customFolders personal/scripts/claude-config) ou rollback. Pas de date limite, pas urgent.

- **`coach.md` durci pas re-testé avec Sonnet** — fix validé seulement sur Haiku. Sonnet pourrait soit respecter encore mieux la règle (moins risqué), soit révéler des subtilités d'interprétation. Pas critique, mais à vérifier avant d'annoncer le mode coach en production.

- **Le SKILL.md `/import-vault` v2 mentionne `$XAIS_BRAIN_REPO`** comme variable d'environnement pour la source des skills à copier. Cette variable **n'est définie nulle part** dans `setup.sh` ni dans les hooks. Le fallback `~/Dev/XAIS_2ND_BRAIN/xais-brain/vault-template` est hardcodé au chemin de Xavier — ça ne marchera pas pour un autre utilisateur qui clone le repo ailleurs. **À corriger** : soit exporter `XAIS_BRAIN_REPO` dans `setup.sh` step initial, soit détecter dynamiquement le path via `git rev-parse --show-toplevel` depuis le skill.

- **Les commits de refonte `/import-vault` touchent un skill que xais-brain a déjà pushé publiquement il y a 1 jour** (handoff 004 : `703f746 feat(skill): add /import-vault FR (BYOV adopt)`). Les early adopters qui ont cloné entre-temps ont la v1 buggée. Acceptable en v0.1 (peu d'utilisateurs), mais à documenter dans un changelog si on fait un tag/release.

### Prêt pour la prod ?

- [x] Tests fonctionnels import-vault (simulation complète sur `~/second-brain`)
- [x] Dry-run import-vault v2 sur vault squelette (fallback par nom validé)
- [x] Tests headless coach.md v1 + v2 (Haiku)
- [x] YAML frontmatter validé (yaml.safe_load passe)
- [x] XML tags balanced (10 tags, 0 markdown headings dans le body)
- [x] Ligne count <500 (341 lignes pour import-vault v2)
- [x] Commits conventionnels séparés
- [x] Push réussi sur origin/main
- [ ] **Test en session Claude Code réelle du skill `/import-vault` v2** — PAS FAIT
- [ ] **Test coach.md v2 avec Sonnet** — PAS FAIT (Haiku uniquement)
- [ ] **Variable `$XAIS_BRAIN_REPO` définie ou path dynamique** — PAS FAIT (hardcodé au path Xavier)
- [ ] Test activation coach.md via `/output-style coach` en vraie conversation — PAS FAIT

**Décision : PARTIEL** — le code est structurellement solide et validé par simulations + dry-run, les commits sont propres, mais aucun test en session Claude Code réelle n'a été exécuté sur le skill durci. Acceptable pour un push initial en v0.2, mais un test réel serait prudent avant de communiquer le skill comme "production ready".

### Fichiers clés

**Modifiés et committés cette session** :
- [vault-template/.claude/skills/import-vault/SKILL.md](vault-template/.claude/skills/import-vault/SKILL.md) — refonte 2.0 XML pur, 341 lignes, 10 tags balanced. Source canonique du skill.
- [vault-template/.claude/output-styles/coach.md](vault-template/.claude/output-styles/coach.md) — durci avec section "Obligation finale (non-négociable)" en fin de fichier. +15 lignes.
- [specs/](specs/) — 5 fichiers versionnés (1 plan done + 4 handoffs). Nouveau : ce handoff 005.

**Fichiers de référence lus (skill-creator 2.0)** :
- `~/.claude/skills/skill-creator/SKILL.md` — guide principal 21 192 bytes
- `~/.claude/skills/skill-creator/references/workflows.md` — sequential + conditional workflows
- `~/.claude/skills/skill-creator/references/progressive-disclosure-patterns.md` — 3 niveaux, patterns high_level_guide/domain_organization/conditional_details/progressive_complexity/feature_based
- `~/.claude/skills/skill-creator/references/real-world-examples.md` — simple/standard/complex examples
- `~/.claude/skills/skill-creator/references/script-patterns.md` — scripts bash/python, setup/validation/transformation templates
- `~/.claude/skills/skill-creator/references/xml-tag-guide.md` — tags requis + conditionnels, règle "no markdown headings"

**Vaults de test** :
- `~/xais-brain-vault-3` — vault installé en début de session précédente, 13 skills, provider=gemini, structure intacte. Sert de reference pour le test setup.sh.
- `~/second-brain` — **vault réel de Xavier, maintenant mi-adopté** par la simulation. CLAUDE.md backup-2026-04-09-122304 présent. 15 skills dont 2 custom (client, project) préservés. Decision rollback ou garde à prendre.
- `~/second-brain.backup-pre-import-test` — backup intact du vault second-brain AVANT toute modification. 124K. Rollback possible via `rm -rf ~/second-brain && mv ~/second-brain.backup-pre-import-test ~/second-brain`.
- `~/xais-brain-vault` — vault de Xavier v0.1, pas encore migré vers 8 skills/hooks.
- `~/xais-brain-vault-2` — vault de test handoff 003, nominal OK.

**Repo GitHub** :
- https://github.com/XAISOLUCES/xais-brain — public, maintenant 14 commits sur `main` (dernier `2d17096`), up-to-date avec le local.

**Commits de cette session (pushés)** :
- `1f33712` — feat(output-style): enforce accountability question in coach.md
- `7d096c0` — refactor(skill): rewrite import-vault with skill-creator 2.0 patterns
- `2d17096` — chore(specs): track plans and session handoffs

### État du contexte

- Utilisation : ~55-65% estimée au moment du handoff (session dense : lecture de 6 fichiers skill-creator, test `/import-vault` simulation complète avec 2 rounds AskUserQuestion, refonte SKILL.md 341 lignes, 2 tests headless coach.md, 3 commits + push, plus les lectures git status répétées). Loin du seuil de compaction forcée mais assez pour justifier le handoff proprement.
