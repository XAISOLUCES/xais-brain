## HANDOFF — xais-brain — 2026-04-08

### État du projet
- Branch: `main`
- Dernier commit: `e4c80b1` — fix(setup): crée .obsidian/ dans le vault + warning si Obsidian tourne
- Commits non pushés: 0 (tout est sur `origin/main`)
- Fichiers en cours (non commités): aucun (working tree clean sauf `specs/` non tracké — ce handoff)
- Remote: `origin` = https://github.com/XAISOLUCES/xais-brain (PUBLIC)
- Repo path: `/Users/xais/Dev/XAIS_2ND_BRAIN/xais-brain/`

### Contexte & décisions

**Problème traité** : Le handoff 002 listait comme seul "TODO critique" le test du one-liner `curl | bash` qui n'avait jamais été testé en réel. Cette session a fait ce test et a découvert **3 bugs en cascade**, tous fixés et poussés.

**Approche choisie** : Fix-test-fix incrémental, un commit par bug, plutôt qu'un seul gros commit ou une attente d'un test final monolithique. Rejeté :
- **Tester d'abord puis fixer en batch** — raison : chaque bug en cachait un autre, il fallait dépiler progressivement
- **Pkill Obsidian dans le script pour forcer le quit** — raison : trop intrusif pour un installateur first-run, l'utilisateur peut perdre du travail non sauvegardé. Préféré : warning + instructions claires

**Décisions d'architecture** :
- **Pour le bug stdin TTY** : fix dans `bootstrap_if_needed()` uniquement (un seul `exec bash ... < /dev/tty`), pas d'ajout de `< /dev/tty` sur chaque `read` individuel. Raison : un seul point de contrôle plus simple à maintenir, et c'est exactement ce que font rustup/nvm/oh-my-zsh.
- **Pour le bug obsidian.json registration** : éditer directement le fichier en Python plutôt qu'utiliser un URL scheme. Raison : `obsidian://vault?path=...` n'enregistre PAS un nouveau vault, il essaie d'en ouvrir un déjà connu — c'était une fausse piste héritée du handoff 002.
- **Garde-fous obsidian.json** : backup `.bak` avant écriture + atomic write via `tempfile.mkstemp` + `os.replace` + try/except large avec fallback silencieux. Raison : c'est un fichier de config global de l'utilisateur, le corrompre serait grave.
- **Pour le bug `.obsidian/` manquant** : créer un dossier vide via `mkdir -p` plutôt que d'y mettre des fichiers de config par défaut. Raison : Obsidian remplit le dossier lui-même au premier lancement (workspace.json, app.json, etc.), pas la peine de réinventer ses templates.
- **Pour le bug "Obsidian déjà ouvert"** : ne pas tuer le processus, juste détecter via `pgrep -x Obsidian` et afficher un warning expliquant `Cmd+Q + relance`. Raison : less is more pour un installateur tiers.

### Findings critiques

- **Bug stdin** : avec `set -e` actif (ligne 6 de setup.sh), un `read` qui retourne 1 à cause d'un stdin fermé (pipe de curl) **stoppe net le script**. Tous les installateurs `curl | bash` doivent rediriger vers `/dev/tty` après le re-exec.
- **`obsidian://vault?path=...` ne fait QUE naviguer vers un vault déjà enregistré**, contrairement à ce que disait le handoff 002. Si le vault n'est pas dans le registre, popup "Vault not found. Unable to find a vault for the URL ...".
- **Format de `~/Library/Application Support/obsidian/obsidian.json`** :
  ```json
  {
    "vaults": {
      "<id_hex_16>": {"path": "...", "ts": <unix_ms>, "open": true}
    },
    "cli": true
  }
  ```
  L'`id` est 16 caractères hex (64 bits), généré aléatoirement. Le `ts` est un timestamp Unix en millisecondes. Le flag `open: true` indique le vault à ouvrir au démarrage — UN seul vault peut l'avoir.
- **Obsidian garde son état en RAM et écrase `obsidian.json` à chaque quit**. Si on modifie le fichier pendant qu'Obsidian tourne, les changements sont **perdus** au prochain quit. Il faut soit fermer Obsidian avant, soit vivre avec cette limitation et avertir l'utilisateur.
- **Obsidian REFUSE d'ouvrir un dossier comme vault s'il ne contient pas un sous-dossier `.obsidian/`**, même vide. Sans ce dossier, popup "Vault not found" même si l'enregistrement dans obsidian.json est correct. C'était LE bug fondamental qu'on ratait depuis 2 sessions.
- **`tempfile.mkstemp()` crée par défaut en mode 0600** — donc `os.replace(tmp, config)` durcit les perms du fichier d'origine de 644 → 600. Inoffensif (et même plus sécurisé), pas fixé.
- **Comportement de re-run du setup sur un vault existant** : `step5_vault` détecte le vault non-vide, affiche "Vault existant détecté", demande confirmation, fait un backup `CLAUDE.md.backup-YYYY-MM-DD-HHMMSS`, et réinstalle. Vu en pratique pendant cette session (Xavier a re-run sur `~/xais-brain-vault`).
- **Test à blanc Python pur** : on peut extraire un heredoc Python d'un script bash et le tester en isolation avec `python3 -c "import re; m = re.search(r\"<<'PYEOF'.*?\\n(.*?)\\nPYEOF\", open('setup.sh').read(), re.DOTALL); open('/tmp/test.py', 'w').write(m.group(1))"` puis `python3 /tmp/test.py <args>`. Très utile pour valider la logique sans relancer tout le setup.

### Terminé

- **Fix #1 — TTY redirect pour curl | bash** (commit `296ab82`) : dans `bootstrap_if_needed()`, redirige stdin vers `/dev/tty` au moment du `exec bash` quand on détecte que stdin n'est pas un TTY ([setup.sh:55-60](setup.sh#L55-L60)).
- **Fix #2 — Enregistrement direct dans obsidian.json** (commit `000ba88`) : réécriture complète de `open_obsidian_app()` avec un heredoc Python qui fait backup + atomic write + fallback ([setup.sh:578-636](setup.sh#L578-L636)). Idempotent : si le vault est déjà enregistré, réutilise son id.
- **Fix #3 — Création de `.obsidian/` + warning Obsidian running** (commit `e4c80b1`) :
  - Ajout de `.obsidian` à la liste `mkdir -p` de `step5_vault` ([setup.sh:250-253](setup.sh#L250-L253))
  - Détection de `pgrep -x Obsidian` au début de `open_obsidian_app()` ([setup.sh:585-589](setup.sh#L585-L589))
  - Warning à la fin si Obsidian tournait, expliquant Cmd+Q + relance ([setup.sh:638-644](setup.sh#L638-L644))
- **Test grandeur réelle du curl | bash réussi** : Xavier a lancé `cd /tmp && curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash` dans Warp à 19:11 → 9/9 étapes en 2m04s, vault créé à `~/xais-brain-vault/` avec 6 skills + CLAUDE.md + .env + structure complète. **Le bootstrap auto-clone marche, le TTY redirect marche, les 6 prompts interactifs ont fonctionné.**
- **Validation manuelle du fix #2 en isolation** : extraction du Python heredoc + run sur le obsidian.json réel → vault correctement ajouté, 3 vaults existants préservés, `.bak` identique à l'original octet pour octet, JSON valide.
- **État local de Xavier réparé** : `~/xais-brain-vault/.obsidian/` créé manuellement (avant le fix #3), `obsidian.json` réécrit avec `xais-brain-vault` en `open: true` après que Xavier ait fait Cmd+Q sur Obsidian. Au relance d'Obsidian, **plus de popup, ouverture directe sur xais-brain-vault confirmée par Xavier**.
- **3 commits poussés sur `origin/main`** : 296ab82, 000ba88, e4c80b1.

### Prochaine étape immédiate

**Action concrète à faire en premier au pickup** : choisir parmi 3 options dans cet ordre de priorité décroissante :

1. **Re-test final du curl | bash sur un vault tout neuf** (`~/xais-brain-vault-2`) avec **Obsidian fermé d'abord** pour valider les 3 fixes ensemble dans le scénario nominal. Commande :
   ```bash
   pkill -x Obsidian 2>/dev/null ; sleep 2 ; cd /tmp && curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash
   ```
   Réponses aux prompts : chemin = `~/xais-brain-vault-2`, LLM = `1` (Claude), API key = Entrée (skip), import = Entrée (skip), Kepano = Entrée (oui). Critère de succès : Obsidian s'ouvre directement sur xais-brain-vault-2 sans popup, sans warning "Obsidian était déjà en cours d'exécution".

2. **Ajouter les topics GitHub** pour la discoverabilité (30s) :
   ```bash
   gh repo edit XAISOLUCES/xais-brain --add-topic obsidian,claude-code,second-brain,french,llm,macos
   ```

3. **Tester les providers Gemini et OpenAI** de `/file-intel` (jamais testés en réel, seul Claude l'a été dans le test interactif d'hier).

### Risques identifiés

- **Re-test du curl | bash en mode "Obsidian fermé" pas fait dans cette session** — on a testé chaque fix individuellement (TTY en grandeur réelle, obsidian.json en isolation Python, .obsidian/ via diagnostic manuel) mais jamais les 3 ensemble dans une seule run propre. Risque résiduel faible mais non nul.
- **Comportement avec Obsidian Sync activé** : pas testé. Si l'utilisateur a Obsidian Sync, et que `xais-brain-vault` se sync, alors `.claude/` se sync aussi → boucle récursive. Le `print_warnings` mentionne déjà ça mais après l'install, donc trop tard si l'utilisateur a un sync auto.
- **Modification de `obsidian.json` côté utilisateur final** : on touche à un fichier de config global. Si une version future d'Obsidian change le format JSON (ex: ajout d'un champ obligatoire, schéma versionné), notre code peut produire un fichier invalide. Mitigé par le `.bak` mais pas idéal. À surveiller dans les release notes Obsidian.
- **`pgrep -x Obsidian` est macOS-only** — sur Linux ça marche aussi, mais le binaire peut s'appeler `obsidian` (lowercase) selon la distrib. Pas un problème vu que le script entier est macOS-first et `check_os()` filtre ça en step 0, mais à garder en tête si on veut supporter Linux un jour.
- **Bug subtil possible** : si l'utilisateur a 2 vaults au même path (impossible normalement, mais edge case), notre `next((vid for vid, v in vaults.items() if v.get("path") == vault), None)` prend le premier. Pas grave.
- **Vault `~/xais-brain-vault` a un `CLAUDE.md.backup-2026-04-08-192523`** dans le dossier — résidu d'un re-run du setup pendant le diagnostic. Non critique, à supprimer ou laisser, ne gêne pas.
- **Lacunes connues du repo qui restent** : pas de CI, pas de tests auto, pas de test des providers Gemini/OpenAI en réel. Acceptable pour v0.1 solo.

### Prêt pour la prod ?

- [x] Syntaxe Bash validée (`bash -n setup.sh`) après chaque fix
- [x] Syntaxe Python validée (extraction du heredoc + `ast.parse`)
- [x] Fix #1 (TTY) testé en grandeur réelle via curl | bash → 9/9 étapes OK
- [x] Fix #2 (obsidian.json) testé en isolation Python → JSON valide, vaults préservés, .bak intact
- [x] Fix #3 (`.obsidian/`) validé empiriquement → création manuelle a fait disparaître la popup
- [x] Vault de Xavier (`~/xais-brain-vault`) opérationnel : Obsidian s'ouvre dessus directement
- [x] 3 commits poussés sur `origin/main` (296ab82, 000ba88, e4c80b1)
- [ ] **Re-test complet du curl | bash avec Obsidian fermé sur un vault neuf** (option 1 du pickup) — pas fait dans cette session
- [ ] Topics GitHub pas encore ajoutés
- [ ] Providers Gemini/OpenAI toujours pas testés en réel

**Décision : OUI pour le partage** — le repo est solide, les 3 bugs que le test grandeur réelle a révélés sont fixés et poussés. Le re-test final est rassurant mais marginal — chaque fix a été validé individuellement.

### Fichiers clés

- [setup.sh](setup.sh) — installateur, ~640 lignes maintenant (vs 593 au handoff 002, +47 lignes via les 3 fixes). Points d'intérêt :
  - [setup.sh:42-62](setup.sh#L42-L62) — `bootstrap_if_needed()` avec TTY redirect
  - [setup.sh:250-253](setup.sh#L250-L253) — `mkdir -p` avec `.obsidian` ajouté
  - [setup.sh:578-644](setup.sh#L578-L644) — `open_obsidian_app()` complet (Python heredoc + warning Obsidian running)
- `~/xais-brain-vault/` — vault opérationnel de Xavier après les fixes, avec `.obsidian/` créé à la main pendant le diagnostic. Contient les 6 skills, CLAUDE.md, MEMORY.md, .env, structure complète.
- `~/Library/Application Support/obsidian/obsidian.json` — registre Obsidian de Xavier. Contient maintenant 4 vaults dont `xais-brain-vault` (id `1c09c412cff8a6c4`) avec `open: true`.
- `~/Library/Application Support/obsidian/obsidian.json.bak` — backup créé par notre script Python lors de la réparation manuelle.

**Repo GitHub** :
- https://github.com/XAISOLUCES/xais-brain — public, 11 commits (3 ajoutés cette session), `main` à `e4c80b1`

**Repos parallèles à connaître** (inchangés) :
- `/Users/xais/Dev/XAIS_2ND_BRAIN/second-brain/` — clone de Mark, intact, NE PAS toucher
- `/Users/xais/second-brain` — vault perso opérationnel de Xavier, indépendant
- `~/xais-brain-test/` — vault de test du test interactif d'hier, toujours sur disque
- `~/.xais-brain-venv/` — venv Python 3.12.12

### État du contexte

- Utilisation : ~75-80% au moment du handoff (estimation — session avec beaucoup de read/edit/diff sur setup.sh, plusieurs runs de validation Python, 3 commits successifs avec messages détaillés)
