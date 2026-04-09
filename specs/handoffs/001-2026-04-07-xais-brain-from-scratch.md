## HANDOFF — xais-brain — 2026-04-07

### État du projet
- Branch: `main`
- Dernier commit: `46079f7` — docs: README solide v0.1
- Commits non pushés: 7 (tous, aucun remote configuré — repo local-only)
- Fichiers en cours (non commités): aucun (working tree clean) sauf ce handoff
- Repo path: `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/`

### Contexte & décisions

**Problème traité** : Recréer from scratch le repo `second-brain` de Mark (cloné dans `/Users/xais/Dev/XAIS_2ND_BRAIN/second-brain/`, owner GitHub `earlyaidopters/second-brain`, sans LICENSE) pour avoir une version 100% à Xavier, sans ambiguïté juridique, en français, et avec améliorations. Trigger initial : bug `brew install --cask --adopt obsidian` qui a cassé l'install d'Obsidian dans le repo de Mark.

**Approche choisie** : Recréation complète (option 4 sur 4 que j'avais proposées). Les autres options rejetées :
- Rejeté : **Demander à Mark d'ajouter MIT License + collaborator** — raison : Xavier veut "son" projet à lui, pas du co-ownership
- Rejeté : **Fork officiel via GitHub** — raison : forking garde le credit de Mark visible et limite à GitHub ToS
- Rejeté : **Renommer le clone local** — raison : ne change rien, reste juridiquement le code de Mark

**Décisions d'architecture structurantes** :
- **Nom** : `xais-brain` (vs `cerveau`, `mon-second-cerveau`, etc.)
- **Licence** : MIT, copyright XAIS 2026
- **Plateforme** : macOS uniquement (`setup.sh` seul, pas de `.ps1` Windows)
- **Langue** : 100% français partout (UI script, prompts, README, commentaires code)
- **Vault structure** : identique à Mark (inbox/daily/projects/research/archive) — pattern standard, pas de raison de casser
- **Système de mémoire** : **upgrade** vs Mark — on a séparé `MEMORY.md` (index racine) et `memory/` (fichiers sémantiques user.md/projects.md/decisions.md/learnings.md). Match le pattern natif Claude Code.
- **Skills** : 4 originaux de Mark + 2 nouveaux (`/inbox-zero` pour trier l'inbox, `/memory-add` pour la mémoire) = 6 skills total
- **`.claude/rules/`** : pattern modulaire ajouté pour règles avancées importables dans CLAUDE.md (vs Mark qui a tout en un seul fichier)
- **Multi-LLM** : abstraction Pattern Provider (`scripts/providers/`) avec `gemini` (défaut), `claude`, `openai`. Choix via `LLM_PROVIDER` dans `.env`. Lazy imports pour ne pas charger les SDK non utilisés.
- **Setup.sh** : architecture en fonctions par étape (`step1_brew` à `step9_kepano`), 9 étapes numérotées, helpers d'affichage uniformes (`step/ok/warn/err/info`).
- **Fix bug --adopt** : détecte `/Applications/Obsidian.app` AVANT `brew install`, skip si présent. Évite le bug qui a déclenché toute la session.
- **LLM provider à l'install** : choix interactif (1-4) au moment du setup.sh, plutôt que Gemini hardcodé chez Mark.

### Findings critiques

- **Mark's repo n'a pas de LICENSE** — `git log --format='%an' | sort -u` → un seul committer `promptadvisers`. Sans license, "tous droits réservés" par défaut. Justification juridique de la recréation from scratch.
- **google-genai SDK** (vs ancien `google-generativeai`) : on utilise le nouveau SDK (`from google import genai`, `client.models.generate_content(model=..., contents=...)`).
- **Modèles par défaut configurés dans le code** :
  - Gemini : `gemini-2.0-flash` (override via `GEMINI_MODEL`)
  - Claude : `claude-haiku-4-5-20251001` (override via `ANTHROPIC_MODEL`)
  - OpenAI : `gpt-4o-mini` (override via `OPENAI_MODEL`)
- **Renommage** : les fichiers providers sont `gemini_provider.py` / `claude_provider.py` / `openai_provider.py` (pas `openai.py`) pour éviter conflit d'import avec le package `openai`.
- **Test bout-en-bout réussi** : `bash setup.sh` lancé sur `/tmp/xais-brain-test`, les 9 étapes ont passé (Gemini skip, Kepano skip). Vault créé avec structure complète, 6 skills installés vault + global. Vérification : `find /tmp/xais-brain-test -type f` montre tous les fichiers attendus.
- **Skills globaux confirmés actifs** : les 6 nouveaux skills (`vault-setup`, `daily`, `tldr`, `file-intel`, `inbox-zero`, `memory-add`) sont visibles dans la liste globale Claude Code (en français), preuve qu'ils sont chargés depuis `~/.claude/skills/`.
- **Vault de test toujours sur disque** : `/tmp/xais-brain-test/` existe, pas encore nettoyé. À supprimer avec `rm -rf /tmp/xais-brain-test` quand plus besoin.

### Terminé

- **Phase 2** — Squelette du repo : `LICENSE` MIT, `.gitignore`, `.env.example` multi-LLM, `README.md` initial. Commit `310ed72`.
- **Phase 3** — Template de vault : `vault-template/` avec `CLAUDE.md` minimaliste, `MEMORY.md` index, `memory/README.md`, `.claude/rules/README.md`, 5 dossiers de base + .gitkeep. Commit `a1e3c78`.
- **Phase 4** — 6 skills slash commands en français : `vault-setup`, `daily`, `tldr`, `file-intel`, `inbox-zero` (nouveau), `memory-add` (nouveau). Commit `3aa9e67`.
- **Phase 5** — Scripts Python multi-LLM : `file_intel.py` orchestrateur + `providers/` (base, _prompts, gemini, claude, openai, __init__). Validé avec `python3 -m py_compile`. Commit `9978f87`.
- **Phase 6** — `setup.sh` from scratch : 571 lignes, 9 étapes en français, fix bug --adopt, choix LLM interactif, bootstrap auto-clone. Validé avec `bash -n`. Commit `057e495`.
- **Phase 7** — README solide v0.1 : badges, quick start, table des 6 commands, structure vault, multi-LLM, customization, install manuelle (collapsed), section Pourquoi. 195 lignes. Commit `46079f7`.
- **Test bout-en-bout** : `bash setup.sh` sur `/tmp/xais-brain-test` → 9/9 étapes passées, structure du vault validée, skills installés vault + global.

### Prochaine étape immédiate

**Décider de la stratégie de publication GitHub**, parmi :

1. **Publier en public** sur `github.com/xais/xais-brain` (compte GitHub à confirmer — le username `xais` est utilisé dans le README et le `REPO_URL` du `setup.sh`, mais c'est un placeholder qui doit matcher le vrai compte). Commande prête :
   ```bash
   gh repo create xais/xais-brain --public \
     --source=/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain \
     --remote=origin --push
   ```
   Action publique irréversible — demander confirmation explicite avant de lancer.

2. **Tester d'abord en interactif** : ouvrir Obsidian sur `/tmp/xais-brain-test`, lancer Claude Code dedans, jouer avec `/vault-setup`, `/daily`, `/inbox-zero`, etc. pour valider que les skills se déclenchent correctement et font ce qu'on attend.

3. **Ajuster avant publication** : si le test interactif révèle des problèmes dans les skills ou le script.

**Action concrète à faire en premier au pickup** : demander à Xavier laquelle des 3 options ci-dessus il veut attaquer, et **vérifier le vrai username GitHub** (le placeholder `xais` est probablement faux) avant tout `gh repo create`.

### Risques identifiés

- **Username GitHub `xais` est un placeholder** dans `README.md` (ligne 17 quick install URL, lignes manual install et issues) et dans `setup.sh` (`REPO_URL="https://github.com/xais/xais-brain.git"`). Si Xavier publie sous un autre username, il faut un find/replace global avant le push. Sinon le one-liner `curl | bash` du README sera cassé.
- **Pas de tests automatisés** : aucun test unitaire sur les providers Python ni sur les extracteurs PDF/DOCX. Si une lib change d'API, on le verra à l'exécution. Acceptable pour un v0.1, à ajouter si le projet grossit.
- **`/file-intel` non testé en réel** : le script Python a passé `py_compile` mais aucun appel LLM réel n'a été fait (Xavier a choisi "skip" à l'étape 7 du setup). Risque mineur : un bug d'API SDK pourrait casser le premier appel réel. Mitigation : tester avec un PDF de test après la publication.
- **`scripts/file_intel.py` dans le vault utilise `sys.path.insert`** pour trouver `providers/`. Marche si le venv `~/.xais-brain-venv/` est utilisé, mais peut casser si l'utilisateur lance le script avec un autre Python. Acceptable car `setup.sh` configure le venv.
- **`/tmp/xais-brain-test/` non nettoyé** : ce vault de test existe encore. Pas un risque, juste à ne pas oublier de `rm -rf` quand on n'en a plus besoin.
- **MIT License protège juridiquement** la recréation, mais Mark pourrait quand même mal le prendre si Xavier ne le prévient pas. **Recommandation perso** (pas un risque code) : envoyer un message court à Mark *"j'ai recodé une version de mon côté en français pour mon propre usage, voici le repo"* — par courtoisie.

### Prêt pour la prod ?

- [x] Syntaxe Bash validée (`bash -n setup.sh`)
- [x] Syntaxe Python validée (`python3 -m py_compile` sur les 7 fichiers)
- [x] Test setup.sh bout-en-bout réussi sur `/tmp/xais-brain-test`
- [x] Structure du vault de test conforme à l'attendu
- [x] 6 skills installés et visibles globalement dans Claude Code
- [ ] Test d'un appel réel `/file-intel` avec un PDF + clé API LLM (non fait)
- [ ] Publication GitHub (en attente de décision Xavier)
- [ ] Username GitHub réel substitué au placeholder `xais` (si différent)

**Décision : PARTIEL** — le code est solide et testé en intégration. Manque juste le test réel d'un appel LLM et la publication GitHub. Safe à utiliser tel quel localement.

### Fichiers clés

- [setup.sh](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/setup.sh) — installateur principal, 571 lignes, 9 étapes, fix --adopt aux lignes 117-122, choix LLM aux lignes 312-380
- [scripts/file_intel.py](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/scripts/file_intel.py) — orchestrateur Python, extracteurs PDF/DOCX/TXT/MD inline
- [scripts/providers/__init__.py](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/scripts/providers/__init__.py) — factory `get_provider()` lit `LLM_PROVIDER` env
- [scripts/providers/_prompts.py](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/scripts/providers/_prompts.py) — prompt FR partagé entre les 3 providers (frontmatter Obsidian)
- [vault-template/CLAUDE.md](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/vault-template/CLAUDE.md) — template minimaliste, à personnaliser via `/vault-setup`
- [vault-template/MEMORY.md](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/vault-template/MEMORY.md) — index racine du système de mémoire
- [skills/inbox-zero/SKILL.md](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/skills/inbox-zero/SKILL.md) — skill nouveau (vs Mark)
- [skills/memory-add/SKILL.md](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/skills/memory-add/SKILL.md) — skill nouveau (vs Mark)
- [README.md](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/README.md) — 195 lignes, badges, quick start, table 6 commands, multi-LLM
- [requirements.txt](/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/requirements.txt) — dotenv, pypdf, python-docx, google-genai, anthropic, openai

**Repos parallèles à connaître** :
- `/Users/xais/Dev/XAIS_2ND_BRAIN/second-brain/` — clone de Mark (`earlyaidopters/second-brain`, intact, dernier commit `72efde2`). NE PAS toucher.
- `/Users/xais/second-brain` — vault de Xavier installé via le script de Mark plus tôt dans la session (vault perso opérationnel, indépendant de xais-brain).
- `/tmp/xais-brain-test/` — vault de test du setup.sh, à nettoyer.

### État du contexte

- Utilisation : ~60% au moment du handoff (estimation — beaucoup de file writes en série, prompts longs, conversation continue depuis le début de session)
