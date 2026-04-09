## HANDOFF — xais-brain — 2026-04-09

### État du projet
- Branch: `main`
- Dernier commit: `e4c80b1` — fix(setup): crée .obsidian/ dans le vault + warning si Obsidian tourne
- Commits non pushés: 0
- Fichiers en cours (non commités) :
  - **Modifiés** : `README.md`, `setup.sh`, `vault-template/CLAUDE.md`
  - **Renommés via git mv** : `skills/{daily,file-intel,inbox-zero,memory-add,tldr,vault-setup}/SKILL.md` → `vault-template/.claude/skills/.../SKILL.md` (6 fichiers)
  - **Untracked (nouveaux)** :
    - `vault-template/.claude/hooks/{session-init.sh,skill-discovery.sh}`
    - `vault-template/.claude/output-styles/coach.md`
    - `vault-template/.claude/settings.json`
    - `vault-template/.claude/skills/humanise/SKILL.md`
    - `vault-template/.claude/skills/import-vault/SKILL.md`
    - `vault-template/vault-config.json`
    - `specs/` (plans + handoffs, incluant ce fichier)
- Remote: `origin` = https://github.com/XAISOLUCES/xais-brain (PUBLIC)
- Repo path: `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/`

### Contexte & décisions

**Problème traité** : Après avoir fermé les 3 fixes cascade du handoff 003 (curl|bash, obsidian.json, .obsidian/), la session s'est ouverte sur le **reste du TODO** : re-test sur vault neuf + topics GitHub. Puis Xavier a demandé une **analyse concurrentielle approfondie** du marché Obsidian+Claude Code sur GitHub, suivie d'une analyse détaillée des 2 leaders (claudesidian 2.1k stars + obsidian-claude-pkm 1.3k stars), puis un `/XD-plan` + `/XD-build` complet pour porter leurs meilleures idées dans xais-brain.

**Approche choisie** : Fork Explore → Plan → Build séquentiel, avec garde-fous anti-dérive explicites (liste de "À NE PAS copier") dans le plan pour éviter de cloner les erreurs des concurrents (init-bootstrap 854 lignes, cascade 3Y→Y→M→W→D, emojis partout).

**Décisions d'architecture clés** :

- **Migration `skills/` → `vault-template/.claude/skills/`** : raison — toutes les bibs concurrentes utilisent `.claude/skills/` (standard Claude Code), et le hook `skill-discovery.sh` attend ce path. Alternative rejetée : garder `skills/` au root pour compat — trop de friction pour les hooks.
- **Frontmatter skills enrichi** (`user-invocable`, `disable-model-invocation`, `model`) : `haiku` sur `daily`+`tldr` (rapides), `sonnet` sur le reste. `disable-model-invocation: true` sur `humanise` et `import-vault` (actions lourdes, trigger explicite uniquement).
- **Parse YAML via `awk` et non `sed`** : raison — BSD sed macOS ne supporte pas la syntaxe multi-ligne du plan original. Découvert pendant le build, corrigé et testé.
- **`vault-config.json`** comme source de vérité structurée au root du vault (et PAS dans `.claude/`) : raison — pattern PKM, lisible par tous les skills, path prévisible. Merge Python non-destructif dans `step7_llm_config` (préserve l'existant).
- **Permissions strictes dans `settings.json`** : `deny Edit(.claude/**)` + `deny Bash(rm -rf:*)` comme garde-fous. Alternative rejetée : tout autoriser — contraire à la philo "safe by default".
- **Hooks non-bloquants** : `exit 0` systématique même en cas d'erreur. Jamais planter une session Claude Code à cause d'un hook.
- **PAS de marker `FIRST_RUN`** (contrairement à claudesidian et PKM) : raison — trop de state à gérer pour un gain marginal dans une philo one-liner.
- **PAS de cascade goals 3Y→Y→M→W→D** : raison — xais-brain = "2nd brain", pas "système GTD complet". Scope creep évité.
- **PAS de traduction des skills Kepano** : raison — déjà référencés via install optionnelle, les traduire créerait de la dette de maintenance.

### Findings critiques

- **Le marché FR est quasi-vide** : 1 seul concurrent FR identifié — **Frutzmann/obsidian-claude-code** (7 stars, créé le 5 avril 2026, soit **3 jours avant** xais-brain). Approche minimaliste sans installer, accompagne une vidéo YouTube. xais-brain est probablement le **premier installer FR `curl | bash` avec skills custom + auto-register `obsidian.json`**.
- **Kepano obsidian-skills = 21 717 stars** — c'est LE standard de facto. Tous les vaults sérieux vendorent ses skills. xais-brain a l'option d'installation Kepano minimale (skills Obsidian CLI) mais ne force pas.
- **Les 3 leaders** : claudesidian (2.1k, PARA numéroté + `/init-bootstrap` 854 lignes), obsidian-claude-pkm (1.3k, cascade PKM + rules scopées par path), COG-second-brain (307, multi-agents .claude/.gemini/.kiro). xais-brain s'inspire principalement de PKM (approche hooks + output-styles).
- **Obsidian MCP bridge** : [iansinnott/obsidian-claude-code-mcp](https://github.com/iansinnott/obsidian-claude-code-mcp) (236 stars) permet à Claude Code d'accéder à un vault SANS être dans son cwd. Opportunité future pour xais-brain mais out of scope pour cette session.
- **Hook `skill-discovery.sh` testé à blanc** : vault factice avec 8 skills, prompt `"quels skills sont disponibles"` → liste les 8 avec descriptions FR. Prompt `"bonjour"` → silence (non-invasif). Parfait.
- **Hook `session-init.sh` testé à blanc** : vault sans CLAUDE.md → message d'accueil "Ce dossier ne ressemble pas à un vault xais-brain" + suggestion du curl|bash.
- **Re-test `curl | bash` nominal RÉUSSI** (début de session, piste 1 du handoff 003) : vault `~/xais-brain-vault-2` créé en 2m env, `.obsidian/` auto-peuplé par Obsidian au 1er lancement, `obsidian.json` merge OK (id `e6b9a325a7b13984`, path correct, `open: True`), 4 vaults précédents préservés. Les 3 fixes du handoff 003 fonctionnent **ensemble** dans le scénario nominal.
- **Topics GitHub ajoutés** : `claude-code, french, llm, macos, obsidian, second-brain` — repo discoverable via GitHub search.
- **8 slash commands FR au total** (6 existants + 2 nouveaux `/humanise` et `/import-vault`). Avec les 2 hooks, le vault devient "intelligent dès le 1er lancement" (session-init surface le contexte sans que l'utilisateur tape quoi que ce soit).

### Terminé

- **Piste 1 du handoff 003** — Re-test `curl | bash` nominal sur `~/xais-brain-vault-2` : 9/9 étapes OK, Obsidian s'ouvre direct sans popup, `obsidian.json` correct, 3 fixes validés ensemble. ✅
- **Piste 2 du handoff 003** — Topics GitHub ajoutés : `gh repo edit XAISOLUCES/xais-brain --add-topic obsidian,claude-code,second-brain,french,llm,macos`. ✅
- **Analyse concurrentielle** — 15 repos GitHub analysés, 10 articles de blog référencés, positionnement clarifié ("le claudesidian français, mais en une commande"). 2 repos clonés localement dans `/tmp/claudesidian` et `/tmp/obsidian-claude-pkm` pour référence.
- **Analyse détaillée `.claude/`** — Structure comparative 3 colonnes, top 10 idées à piquer, patterns d'architecture, liste "à NE PAS copier". Output des 2 leaders analysés.
- **Plan `/XD-plan`** — `specs/todo/enrich-xais-brain-pkm-best-of.md` créé, 8 phases, décisions clés documentées, non-scope explicite. Déplacé dans `specs/done/` après build.
- **Build `/XD-build` complet** (20 fichiers touchés) :
  - Phase 1 : Migration `skills/` → `vault-template/.claude/skills/` via `git mv`, dossier `skills/` racine supprimé, frontmatter enrichi (user-invocable/disable-model-invocation/model) sur les 6 skills existants
  - Phase 2 : `vault-template/vault-config.json` créé + merge Python non-destructif dans `step7_llm_config`
  - Phase 3 : Hooks FR `session-init.sh` et `skill-discovery.sh` via `awk` (BSD-compat), `chmod +x`, non-bloquants. `vault-template/.claude/settings.json` avec permissions strictes + déclaration des hooks
  - Phase 4 : Skill `/humanise` FR (patterns IA français : "par ailleurs", "il convient de noter", "exploiter", "tirer parti", clichés IA, verbes corporate)
  - Phase 5 : Skill `/import-vault` FR (BYOV — scan structure, mapping interactif 5 dossiers, écriture vault-config.json, backup CLAUDE.md existant, pas de merge auto — trop fragile)
  - Phase 6 : Output style `coach.md` FR (challenge, accountability, questions > affirmations, bannissement tics IA)
  - Phase 7 : Update `setup.sh` (step5_vault crée `.claude/hooks` et `.claude/output-styles`, détecte ancien layout avec warning ; `copy_vault_template` copie `vault-config.json` ; `step6_skills` installe 8 skills + 2 hooks + coach + settings ; `verify_install` check les nouveaux fichiers ; bannière "8 skills" + "Hooks FR"), `vault-template/CLAUDE.md` (mention `vault-config.json`, liste des 8 slash commands), `README.md` (tableau 8 skills, structure vault enrichie, section "Activer le mode Coach FR", install manuelle corrigée)
  - Phase 8 : Validation syntaxe bash + JSON + hooks testés à blanc avec vault factice
- **`/XD-validate`** complet : 27/27 checks OK (bash syntax × 3, JSON × 3, Python × 7, frontmatter skills × 8, permissions hooks × 2, hook runtime session-init × 1, hook runtime skill-discovery trigger+no-trigger × 2, setup.sh executable × 1).

### Prochaine étape immédiate

**Action concrète à faire en premier au pickup** : choisir entre 2 options par priorité décroissante :

1. **Tester en grandeur réelle le setup.sh local sur un 3e vault neuf** avant de committer. Commande :
   ```bash
   pkill -x Obsidian 2>/dev/null ; sleep 2 ; bash /Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/setup.sh
   ```
   Réponses prompts : chemin = `~/xais-brain-vault-3`, LLM = `1` (Claude), API key = Entrée, import = Entrée, Kepano = Entrée. Critères de succès : 9/9 étapes OK, Obsidian s'ouvre direct sans popup, `.claude/skills/` contient les **8 skills**, `.claude/hooks/` contient les 2 `.sh` exécutables, `.claude/output-styles/coach.md` présent, `vault-config.json` mergé avec `provider: claude`, `.claude/settings.json` présent. Note : le `setup.sh` n'appelle PAS `bootstrap_if_needed` car il détecte `vault-template/CLAUDE.md` localement — donc il utilise bien les templates locaux modifiés, pas la version GitHub.

2. **Committer directement avec `/XD-commit`** puis tester via `curl | bash` (workflow "propre" mais on pousse avant validation grandeur réelle). Si cette voie est choisie : plusieurs commits suggérés (1 par phase logique) plutôt qu'un gros monolithe :
   - `refactor(skills): migrate to vault-template/.claude/skills/ with enriched frontmatter`
   - `feat(vault): add vault-config.json as structured source of truth`
   - `feat(hooks): add session-init.sh and skill-discovery.sh in FR`
   - `feat(skill): add /humanise FR (de-AI-ify text)`
   - `feat(skill): add /import-vault FR (BYOV adopt)`
   - `feat(output-style): add coach.md FR`
   - `chore(setup): update setup.sh + CLAUDE.md + README for new layout`

   Ou un seul commit `feat: enrich vault with 2 new skills + hooks + coach + vault-config.json` si on préfère un bloc cohérent.

### Risques identifiés

- **Build pas encore testé en grandeur réelle** — validation syntaxe + hooks à blanc OK, mais pas de run complet du `setup.sh` avec les nouveaux templates. Risque résiduel : un chemin pas créé, un skill qui ne se copie pas, une permission loupée. À fixer par le test piste 1 du pickup.
- **`vault-config.json` n'est pas utilisé ailleurs qu'au setup** — on l'écrit mais AUCUN skill actuel ne le lit pour personnaliser son comportement. C'est du "préparer le terrain pour v2" plus qu'un gain immédiat. Risque : fichier orphelin qui diverge de la réalité du vault avec le temps.
- **Migration `skills/` → `vault-template/.claude/skills/` breaking pour les utilisateurs early adopters** — si quelqu'un a installé xais-brain avant aujourd'hui, son vault a les skills au root `skills/`. Le `setup.sh` détecte ça avec un warning mais ne migre pas automatiquement. Acceptable pour v0.1 (on n'a quasi aucun utilisateur) mais à documenter dans le changelog si on fait une release.
- **Output style `coach.md` non-testé** — pas lancé en session Claude Code réelle, seulement validé comme fichier. À tester au pickup.
- **`/import-vault` pas testé** — skill ambitieux (scan + mapping interactif + backup), aucune validation en réel. Potentiel de bugs.
- **Hooks macOS-specific subtils** : `date -v-1d` est BSD (macOS), le fallback `date -d "yesterday"` est GNU (Linux). Testé localement (macOS) mais pas sur Linux. Vu que xais-brain est macOS-first, acceptable.
- **Les 2 repos concurrents dans `/tmp`** (`claudesidian`, `obsidian-claude-pkm`) **seront nettoyés au prochain reboot** — si on veut les garder pour référence future, les déplacer dans un dossier stable. Pas critique.

### Prêt pour la prod ?

- [x] Syntaxe bash validée (`bash -n`) sur setup.sh + 2 hooks
- [x] JSON valide (`python3 -m json.tool`) sur vault-config.json + settings.json
- [x] Frontmatter skills validés (8/8 skills avec tous les champs attendus)
- [x] Hooks testés à blanc dans un vault factice (session-init + skill-discovery avec et sans trigger)
- [x] Python syntax validée (file_intel.py + 6 providers)
- [x] Permissions hooks `chmod +x` OK
- [ ] **Test grandeur réelle du setup.sh local sur un vault neuf** — PAS FAIT (option 1 du pickup)
- [ ] `/XD-commit` puis push — PAS FAIT (option 2 du pickup)
- [ ] Test `/import-vault` en réel sur un vault existant — PAS FAIT (ambitieux, à planifier)
- [ ] Test output style `coach.md` en session réelle — PAS FAIT

**Décision : PARTIEL** — le code est syntaxiquement solide et les hooks ont été testés à blanc, mais le run complet du setup.sh avec les nouveaux templates n'a pas eu lieu. Pickup obligatoire sur l'option 1 avant tout commit.

### Fichiers clés

**Modifiés** :
- [setup.sh](setup.sh) — installateur, ~830 lignes maintenant (vs ~640 au handoff 003). Points d'intérêt :
  - `step5_vault` : création `.claude/hooks`, `.claude/output-styles`, détection ancien layout avec warning
  - `copy_vault_template` : copie `vault-config.json` si absent
  - `step6_skills` : installe 8 skills + 2 hooks (chmod +x) + coach.md + settings.json
  - `step7_llm_config` : snippet Python inline qui merge provider + setupDate dans vault-config.json (non-destructif)
  - `verify_install` : check `vault-config.json` et hooks
  - `show_banner` : "8 skills" + "Hooks FR"
- [README.md](README.md) — tableau 8 skills, structure vault enrichie, section "Mode Coach FR", install manuelle corrigée (paths `.claude/skills/`)
- [vault-template/CLAUDE.md](vault-template/CLAUDE.md) — mention `vault-config.json`, liste des 8 slash commands

**Créés** :
- [vault-template/vault-config.json](vault-template/vault-config.json) — schéma structuré (name, provider, folders, setupDate, ...)
- [vault-template/.claude/settings.json](vault-template/.claude/settings.json) — permissions + déclaration des hooks
- [vault-template/.claude/hooks/session-init.sh](vault-template/.claude/hooks/session-init.sh) — SessionStart hook (contexte vault)
- [vault-template/.claude/hooks/skill-discovery.sh](vault-template/.claude/hooks/skill-discovery.sh) — UserPromptSubmit hook (liste skills sur trigger FR/EN)
- [vault-template/.claude/output-styles/coach.md](vault-template/.claude/output-styles/coach.md) — mode coach challengeant FR
- [vault-template/.claude/skills/humanise/SKILL.md](vault-template/.claude/skills/humanise/SKILL.md) — dé-IA-ification FR
- [vault-template/.claude/skills/import-vault/SKILL.md](vault-template/.claude/skills/import-vault/SKILL.md) — BYOV scan + mapping

**Renommés via `git mv`** (6 fichiers) :
- `skills/daily/SKILL.md` → `vault-template/.claude/skills/daily/SKILL.md`
- `skills/file-intel/SKILL.md` → `vault-template/.claude/skills/file-intel/SKILL.md`
- `skills/inbox-zero/SKILL.md` → `vault-template/.claude/skills/inbox-zero/SKILL.md`
- `skills/memory-add/SKILL.md` → `vault-template/.claude/skills/memory-add/SKILL.md`
- `skills/tldr/SKILL.md` → `vault-template/.claude/skills/tldr/SKILL.md`
- `skills/vault-setup/SKILL.md` → `vault-template/.claude/skills/vault-setup/SKILL.md`

**Frontmatter enrichi sur les 6 skills existants** : ajout de `user-invocable: true`, `disable-model-invocation: false`, `model: sonnet` (ou `haiku` pour daily + tldr).

**Specs** :
- `specs/done/enrich-xais-brain-pkm-best-of.md` — plan complet 8 phases (déplacé depuis `todo/` après build)
- `specs/handoffs/003-2026-04-08-fixes-curl-bash-et-obsidian.md` — handoff précédent (les 3 fixes cascade)

**Repos de référence locaux** (dans `/tmp`, potentiellement nettoyés au reboot) :
- `/tmp/claudesidian` — fork shallow de heyitsnoah/claudesidian (2.1k stars)
- `/tmp/obsidian-claude-pkm` — fork shallow de ballred/obsidian-claude-pkm (1.3k stars)

**Vaults de test sur disque** :
- `~/xais-brain-vault` — vault de Xavier (version handoff 003, pas encore migré vers 8 skills/hooks)
- `~/xais-brain-vault-2` — vault de test créé en début de session (test piste 1), validation du nominal, opérationnel
- `~/xais-brain-vault-3` — **à créer au pickup** pour le test grandeur réelle du nouveau setup.sh

**Repo GitHub** :
- https://github.com/XAISOLUCES/xais-brain — public, 11 commits sur `main` (dernier `e4c80b1`, rien de cette session encore pushé), topics ajoutés cette session : `obsidian, claude-code, second-brain, french, llm, macos`

### État du contexte

- Utilisation : ~80-85% au moment du handoff (session très dense : analyse concurrentielle, analyse détaillée, plan, build, validate, read README, plusieurs invocations d'agents en forked execution)
