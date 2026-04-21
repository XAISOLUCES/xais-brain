# Architecture xais-brain

> Documentation technique : arborescence exacte du repo et du vault installé,
> diagrammes de composants, et flux d'exécution. Pour le quickstart utilisateur,
> voir [README.md](README.md).

---

## Vue d'ensemble

`xais-brain` est un installateur idempotent qui transforme un dossier vide (ou un vault Obsidian existant) en second cerveau piloté par Claude Code. Le repo contient trois couches :

1. **Orchestrateur** — `setup.sh` : 9 étapes séquentielles, détecte les vaults existants, ne casse rien
2. **Source canonique** — `vault-template/` : tout ce qui est copié dans le vault de l'utilisateur (CLAUDE.md, skills, hooks, output-styles, config)
3. **Moteur Python** — `scripts/file_intel.py` + `scripts/providers/` : pipeline LLM multi-provider pour `/file-intel`

Le vault installé est un dossier Obsidian standard (avec `.obsidian/`) augmenté d'un dossier `.claude/` qui contient les slash commands, hooks, output styles et permissions.

---

## Arborescence du repo

```
xais-brain/
│
├── README.md                          ← Quickstart utilisateur
├── ARCHITECTURE.md                    ← Ce fichier
├── LICENSE                            ← MIT
├── .gitignore
├── .env.example                       ← Template des clés API
├── requirements.txt                   ← pypdf, python-docx, google-genai, anthropic, openai, python-dotenv
│
├── setup.sh                           ← Orchestrateur d'install (9 étapes)
│
├── scripts/                           ← Moteur Python /file-intel
│   ├── file_intel.py                  ← Extracteurs PDF/DOCX/TXT/MD + main
│   └── providers/
│       ├── __init__.py                ← get_provider() — factory selon LLM_PROVIDER
│       ├── base.py                    ← LLMProvider (interface ABC)
│       ├── _prompts.py                ← Prompt FR partagé pour summarization
│       ├── gemini_provider.py         ← Implémentation Gemini
│       ├── claude_provider.py         ← Implémentation Anthropic
│       └── openai_provider.py         ← Implémentation OpenAI
│
├── vault-template/                    ← Source canonique copiée dans chaque vault
│   ├── CLAUDE.md                      ← Template d'instructions pour Claude
│   ├── MEMORY.md                      ← Index du système de mémoire
│   ├── vault-config.json              ← Source de vérité structurée (user, llm, folders)
│   │
│   ├── inbox/.gitkeep                 ← Drop zone — fichiers en attente
│   ├── daily/.gitkeep                 ← Notes journalières (YYYY-MM-DD.md)
│   ├── projects/.gitkeep              ← Projets actifs
│   ├── research/.gitkeep              ← Notes de recherche
│   ├── archive/.gitkeep               ← Travail terminé (jamais supprimé)
│   ├── memory/
│   │   └── README.md                  ← Pattern mémoire long terme
│   ├── 99-Meta/                       ← Piste d'audit du vault (hors contenu)
│   │   ├── README.md                  ← Rôle + instructions exclusion du graphe Obsidian
│   │   ├── Audit.md                   ← Dernier rapport /vault-audit
│   │   ├── Fact-Check-Log.md          ← Log append-only des sources (alimenté par /clip, /file-intel)
│   │   └── Session-Debriefs/          ← Rétrospectives (alimenté par /tldr)
│   │       └── .gitkeep
│   │
│   └── .claude/
│       ├── settings.json              ← Permissions + déclaration des hooks
│       │
│       ├── skills/                    ← 11 slash commands canoniques
│       │   ├── vault-setup/SKILL.md   ← Interview utilisateur → personnalise CLAUDE.md
│       │   ├── daily/SKILL.md         ← Démarre la journée avec contexte vault
│       │   ├── tldr/SKILL.md          ← Sauvegarde résumé de session
│       │   ├── file-intel/SKILL.md    ← Wrapper du script Python file_intel.py
│       │   ├── inbox-zero/SKILL.md    ← Trie inbox/ vers les bons dossiers
│       │   ├── memory-add/SKILL.md    ← Ajoute une mémoire long terme
│       │   ├── humanise/SKILL.md      ← Nettoie un texte AI-ifié
│       │   ├── import-vault/SKILL.md  ← Adopte un vault existant (BYOV)
│       │   ├── project/SKILL.md       ← Charge contexte d'un side-project
│       │   ├── client/SKILL.md        ← Charge contexte d'un client en prod
│       │   └── clip/SKILL.md          ← Web clipper URL → Markdown inbox/
│       │
│       ├── hooks/
│       │   ├── session-init.sh        ← SessionStart : surface daily/inbox
│       │   └── skill-discovery.sh     ← UserPromptSubmit : liste skills sur trigger FR
│       │
│       ├── output-styles/
│       │   └── coach.md               ← Mode coach challengeant FR
│       │
│       └── rules/
│           └── README.md              ← Pattern règles modulaires (importables via @import)
│
└── specs/                             ← Méta : plans + handoffs (pas installé chez l'user)
    ├── done/
    │   └── enrich-xais-brain-pkm-best-of.md
    └── handoffs/
        ├── 001-2026-04-07-xais-brain-from-scratch.md
        ├── 002-2026-04-08-publication-github-fixes-post-test.md
        ├── 003-2026-04-08-fixes-curl-bash-et-obsidian.md
        ├── 004-2026-04-09-enrich-pkm-bestof-build.md
        └── 005-2026-04-09-import-vault-v2-et-coach-hardening.md
```

**Note** : le dossier `specs/` est versionné dans le repo mais **n'est pas copié** dans le vault de l'utilisateur. C'est un historique de développement (plans + handoffs de session) destiné aux contributeurs.

---

## Arborescence du vault installé

Voici ce que l'utilisateur obtient après `setup.sh` :

```
~/mon-vault/                           ← Choisi par l'user (défaut ~/xais-brain-vault)
│
├── CLAUDE.md                          ← Personnalisable via /vault-setup
├── MEMORY.md                          ← Index de la mémoire (auto-mis à jour)
├── vault-config.json                  ← Source de vérité (user, llm, folders, preferences)
├── .env                               ← Clés API LLM (gitignoré, jamais commité)
│
├── .obsidian/                         ← Créé par Obsidian au 1er lancement
│   ├── workspace.json                 ← État UI (panels, tabs ouverts)
│   ├── app.json
│   ├── core-plugins.json
│   └── appearance.json
│
├── inbox/                             ← Drop zone pour /file-intel et imports
├── daily/                             ← YYYY-MM-DD.md
├── projects/                          ← Projets actifs (1 dossier par projet)
├── research/                          ← Notes de recherche, snippets
├── archive/                           ← Travail terminé
├── memory/                            ← Mémoire sémantique (user, projects, decisions...)
│   └── README.md
├── 99-Meta/                           ← Piste d'audit du vault (à exclure du graphe Obsidian)
│   ├── README.md                      ← Rôle + instructions d'exclusion
│   ├── Audit.md                       ← Dernier rapport /vault-audit
│   ├── Fact-Check-Log.md              ← Log append-only des sources (/clip, /file-intel)
│   └── Session-Debriefs/              ← Rétrospectives (/tldr)
│
├── scripts/                           ← Copié depuis xais-brain/scripts/
│   ├── file_intel.py
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       ├── _prompts.py
│       ├── gemini_provider.py
│       ├── claude_provider.py
│       └── openai_provider.py
│
└── .claude/                           ← Tout ce qui est lu par Claude Code
    ├── settings.json                  ← Permissions + hooks déclarés
    │
    ├── skills/                        ← 10 canoniques + 5 Kepano si activé
    │   ├── vault-setup/SKILL.md
    │   ├── daily/SKILL.md
    │   ├── tldr/SKILL.md
    │   ├── file-intel/SKILL.md
    │   ├── inbox-zero/SKILL.md
    │   ├── memory-add/SKILL.md
    │   ├── humanise/SKILL.md
    │   ├── import-vault/SKILL.md
    │   ├── project/SKILL.md
    │   ├── client/SKILL.md
    │   │
    │   └── (si Kepano installé via setup.sh étape 9)
    │   ├── obsidian-cli/SKILL.md      ← CLI Obsidian officiel
    │   ├── obsidian-markdown/SKILL.md ← Wikilinks, callouts, embeds
    │   ├── obsidian-bases/SKILL.md    ← Vues table/card sur les notes
    │   ├── json-canvas/SKILL.md       ← Canvas visuels Obsidian
    │   └── defuddle/SKILL.md          ← Extraction markdown propre depuis URLs
    │
    ├── hooks/
    │   ├── session-init.sh            ← Exécutable (chmod +x)
    │   └── skill-discovery.sh         ← Exécutable (chmod +x)
    │
    ├── output-styles/
    │   └── coach.md                   ← Activable via /output-style
    │
    └── rules/
        └── README.md                  ← User crée ses règles ici, importe via @import
```

Les skills sont **aussi** installés dans `~/.claude/skills/` (global) pour être disponibles depuis n'importe quel dossier — pas seulement dans le vault.

---

## Diagramme de composants

```
┌──────────────────────────────────────────────────────────────────────────┐
│                            UTILISATEUR                                   │
└────────────────────┬─────────────────────────────────────────────────────┘
                     │ curl | bash
                     ▼
       ┌─────────────────────────────┐
       │      setup.sh (9 étapes)    │
       │   bootstrap → install →     │
       │   vault → skills → LLM      │
       └──────────────┬──────────────┘
                      │ copie depuis
                      ▼
   ┌──────────────────────────────────────┐         ┌──────────────────────┐
   │           vault-template/            │         │       scripts/       │
   │  CLAUDE.md, MEMORY.md, .claude/...   │────────▶│  file_intel.py +     │
   │  11 skills + 2 hooks + coach + cfg   │         │  providers/{3 LLMs}  │
   └──────────────────┬───────────────────┘         └──────────┬───────────┘
                      │                                        │
                      ▼                                        ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                      ~/mon-vault/   (Obsidian + Claude Code)             │
│                                                                          │
│   ┌──────────────┐   ┌─────────────────┐   ┌──────────────────────────┐  │
│   │  Obsidian    │   │  Claude Code    │   │   Python venv            │  │
│   │  (.obsidian) │   │  (.claude)      │   │  ~/.xais-brain-venv/     │  │
│   │              │   │                 │   │                          │  │
│   │  - Vault UI  │◀─▶│  - 11 skills    │──▶│  scripts/file_intel.py   │  │
│   │  - Markdown  │   │  - 2 hooks      │   │  → providers/{LLM}       │  │
│   │  - Plugins   │   │  - coach.md     │   │  → résumé Markdown       │  │
│   │              │   │  - settings.json│   │                          │  │
│   └──────────────┘   └────────┬────────┘   └──────────────┬───────────┘  │
│                               │                           │              │
│                               ▼                           ▼              │
│                     ┌──────────────────────────────────────────┐         │
│                     │   inbox/ daily/ projects/ research/      │         │
│                     │   archive/ memory/                       │         │
│                     │   CLAUDE.md  MEMORY.md  vault-config.json│         │
│                     └──────────────────────────────────────────┘         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Flux : `setup.sh` (9 étapes)

```
┌─────────────────────────────────────────────────────────────────┐
│  curl ... | bash                                                │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐  bootstrap_if_needed()
│   Bootstrap     │  Si lancé via curl|bash, clone le repo dans /tmp
│   (auto-clone)  │  puis re-exec setup.sh avec stdin redirigé sur /dev/tty
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 1        │  brew install (si absent)
│  Homebrew       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 2        │  brew install --cask obsidian
│  Obsidian       │  (avec fix --adopt si déjà présent hors brew)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 3        │  curl claude.ai/install.sh | sh
│  Claude Code    │
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 4        │  python3 -m venv ~/.xais-brain-venv
│  Python venv    │  pip install -r requirements.txt
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 5        │  Demande le chemin du vault
│  Vault setup    │  Détecte si vault existant → demande confirmation
│                 │  Crée la structure de dossiers
│                 │  Copie vault-template/ → $VAULT_PATH/
│                 │  Copie scripts/file_intel.py + providers/ → $VAULT_PATH/scripts/
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 6        │  Boucle sur la liste hardcodée de 11 skills :
│  Skills install │  Copie vault-template/.claude/skills/$skill/SKILL.md
│                 │   → $VAULT_PATH/.claude/skills/$skill/
│                 │   → ~/.claude/skills/$skill/   (global)
│                 │  Installe les 2 hooks (chmod +x)
│                 │  Installe coach.md
│                 │  Installe settings.json (préserve si existant)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 7        │  Demande LLM préféré (gemini/claude/openai/skip)
│  LLM config     │  Demande la clé API correspondante (saisie masquée)
│                 │  Écrit .env (LLM_PROVIDER + clé)
│                 │  Met à jour vault-config.json (merge llm.provider + setupDate)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 8        │  Demande optionnellement un dossier de fichiers
│  Import         │  Lance file_intel.py [source] $VAULT_PATH/inbox
│  (optionnel)    │  → notes Markdown dans inbox/
└────────┬────────┘
         ▼
┌─────────────────┐
│  Étape 9        │  Propose d'installer 5 skills Kepano (CEO Obsidian)
│  Kepano skills  │  git clone github.com/kepano/obsidian-skills
│  (optionnel)    │  Copie chaque SKILL.md → vault + global
└────────┬────────┘
         ▼
┌─────────────────┐
│  verify_install │  Check Obsidian, Claude, Python, vault, vault-config,
│                 │  count skills, count hooks
└────────┬────────┘
         ▼
┌─────────────────┐
│  print_warnings │  ⚠ Si Obsidian Sync : exclure .claude/, scripts/, .env
│  print_done     │  ✅ Récap + prochaines étapes
│  open_obsidian  │  Enregistre le vault dans obsidian.json + open -a Obsidian
└─────────────────┘
```

**Le script est idempotent** : `safe_cp` ne casse rien si le fichier existe, `vault-config.json` est mergé (pas écrasé), `settings.json` existant est préservé, `MEMORY.md` n'est jamais écrasé. Tu peux relancer `setup.sh` autant de fois que tu veux.

---

## Flux : `SessionStart` hook (`session-init.sh`)

```
┌──────────────────────────────────────┐
│  L'user lance `claude` dans le vault │
└────────┬─────────────────────────────┘
         ▼
┌──────────────────────────────────────────┐
│  .claude/settings.json déclenche le hook │
│  SessionStart → .claude/hooks/session-init.sh
└────────┬─────────────────────────────────┘
         ▼
┌──────────────────────────────────────┐
│  Lit vault-config.json (si présent)  │
│  → exporte VAULT_INBOX_DIR, etc.     │
│  Fallback sur les noms canoniques    │
│  si vault-config absent ou corrompu  │
└────────┬─────────────────────────────┘
         ▼
┌──────────────────────────────────────────────────────┐
│  Affiche en stdout (lu par Claude Code au démarrage) │
│                                                      │
│  Vault  : mon-vault  |  Aujourd'hui : 2026-04-11    │
│  Inbox  : 3 fichiers en attente  → /inbox-zero      │
│  Note du jour absente  → /daily                     │
└──────────────────────────────────────────────────────┘
```

Si `CLAUDE.md` absent → message « ce dossier ne ressemble pas à un vault xais-brain » + suggère le one-liner d'install.

---

## Flux : `UserPromptSubmit` hook (`skill-discovery.sh`)

```
┌──────────────────────────────────────┐
│  L'user envoie un message à Claude   │
└────────┬─────────────────────────────┘
         ▼
┌──────────────────────────────────────────────┐
│  Hook lit le prompt depuis stdin             │
│  Cherche un mot-clé déclencheur (regex FR) : │
│  skill | commande | que peux-tu | aide-moi |│
│  quoi faire | slash                          │
└────────┬─────────────────────────────────────┘
         │
         ├── pas de match → exit 0 (silencieux)
         │
         └── match → liste les skills :
             │
             ▼
┌────────────────────────────────────────────────┐
│  Pour chaque .claude/skills/*/SKILL.md         │
│  Parse le frontmatter (awk) :                  │
│    - description                               │
│    - user-invocable                            │
│  Si user-invocable=true →                      │
│    /nom-skill — description                    │
│                                                │
│  → Output injecté dans le contexte de Claude   │
└────────────────────────────────────────────────┘
```

---

## Flux : `/file-intel` (pipeline LLM)

```
┌─────────────────────────────────────────────┐
│  L'user tape /file-intel ou mentionne       │
│  « traite ce dossier »                      │
└────────┬────────────────────────────────────┘
         ▼
┌──────────────────────────────────────────────┐
│  SKILL.md file-intel/ (sonnet)               │
│  1. Demande le chemin source                 │
│  2. Vérifie .env (LLM_PROVIDER + clé API)    │
│  3. Lance le script Python via Bash          │
└────────┬─────────────────────────────────────┘
         ▼
┌────────────────────────────────────────────────────────────┐
│  ~/.xais-brain-venv/bin/python3 \                          │
│    $VAULT_PATH/scripts/file_intel.py \                     │
│    [dossier_source] \                                      │
│    $VAULT_PATH/inbox                                       │
└────────┬───────────────────────────────────────────────────┘
         ▼
┌──────────────────────────────────────────────┐
│  file_intel.py main()                        │
│  1. load_env() → lit .env du vault           │
│  2. get_provider() → instancie LLMProvider   │
│     selon LLM_PROVIDER                       │
│  3. discover_files() → liste pdf/docx/txt/md │
└────────┬─────────────────────────────────────┘
         ▼
┌──────────────────────────────────────────────┐  Pour chaque fichier :
│  process_file()                              │
│                                              │
│  ┌──────────────────────┐                    │
│  │  Extracteur          │  pdf  → pypdf      │
│  │  selon extension     │  docx → python-docx│
│  └──────────┬───────────┘  txt/md → read     │
│             ▼                                │
│  ┌──────────────────────┐                    │
│  │  provider.summarize()│                    │
│  │  → Markdown FR       │                    │
│  │  (frontmatter,       │                    │
│  │   TL;DR, points clés,│                    │
│  │   actions)           │                    │
│  └──────────┬───────────┘                    │
│             ▼                                │
│  ┌──────────────────────┐                    │
│  │  Écrit               │                    │
│  │  inbox/[slug].md     │                    │
│  └──────────────────────┘                    │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│  ✓ N/N fichier(s) traité(s) → inbox/         │
│  Le SKILL propose alors /inbox-zero          │
└──────────────────────────────────────────────┘
```

**Multi-LLM via factory** :

```
LLM_PROVIDER=gemini → gemini_provider.GeminiProvider(GOOGLE_API_KEY)
LLM_PROVIDER=claude → claude_provider.ClaudeProvider(ANTHROPIC_API_KEY)
LLM_PROVIDER=openai → openai_provider.OpenAIProvider(OPENAI_API_KEY)

Tous implémentent l'interface base.LLMProvider :
    summarize(content, source_filename) → Markdown FR

Le prompt FR partagé est dans providers/_prompts.py
```

---

## Composants détaillés

### `vault-config.json` — Source de vérité structurée

Schéma utilisé par `session-init.sh`, `setup.sh` et les skills pour résoudre les noms de dossiers, le LLM configuré, et les préférences utilisateur.

```json
{
  "version": "0.2",
  "setupDate": "2026-04-11",
  "user": {
    "name": null,
    "workMode": null
  },
  "llm": {
    "provider": "gemini",
    "model": null
  },
  "folders": {
    "inbox": "inbox",
    "daily": "daily",
    "projects": "projects",
    "research": "research",
    "archive": "archive",
    "memory": "memory"
  },
  "preferences": {
    "coachMode": false,
    "autoCommit": false
  },
  "adoptedVault": false
}
```

**Pourquoi c'est utile** : si tu lances `/import-vault` sur un vault existant qui utilise `clients/` au lieu de `projects/`, le mapping est sauvegardé dans `folders.projects = "clients"`. `session-init.sh` lira ce mapping et exportera `VAULT_PROJECTS_DIR=clients`. Toutes les skills résoudront le bon dossier sans hardcoder.

### `.claude/settings.json` — Permissions et hooks

Déclare ce que Claude Code a le droit de faire dans ton vault, et quels hooks lancer.

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Write(inbox/**)", "Write(daily/**)", "Write(projects/**)",
      "Write(research/**)", "Write(archive/**)", "Write(memory/**)",
      "Edit(inbox/**)", "Edit(daily/**)", "Edit(projects/**)",
      "Edit(research/**)", "Edit(memory/**)",
      "Edit(CLAUDE.md)", "Edit(MEMORY.md)", "Edit(vault-config.json)",
      "Glob", "Grep",
      "Bash(ls:*)", "Bash(date:*)", "Bash(find:*)",
      "Bash(git:*)", "Bash(python3:*)",
      "Bash(~/.xais-brain-venv/bin/python3:*)"
    ],
    "deny": [
      "Edit(.claude/**)",
      "Write(.git/**)",
      "Bash(rm -rf:*)"
    ]
  },
  "env": { "VAULT_PATH": "${cwd}" },
  "hooks": {
    "SessionStart":     [{ "hooks": [{ "type": "command", "command": ".claude/hooks/session-init.sh" }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command", "command": ".claude/hooks/skill-discovery.sh", "timeout": 5000 }] }]
  }
}
```

### Système de mémoire

`MEMORY.md` est l'index, `memory/` contient les fichiers détaillés organisés sémantiquement (`user.md`, `projects.md`, `decisions.md`, `learnings.md`...). C'est le pattern natif Claude Code (les conventions globales `~/.claude/CLAUDE.md` font la même chose).

Le skill `/memory-add` est l'interface pour ajouter une nouvelle entrée et mettre à jour `MEMORY.md` automatiquement.

### Mode Coach FR

`coach.md` est un output style activable via `/output-style coach`. Il transforme Claude en coach de productivité : challenge les hypothèses, refuse la planification stérile, force l'action.

**Règle non-négociable** : chaque réponse se termine par (1) une action concrète faisable dans l'heure, et (2) une question d'accountability. Pas d'exception, même sur une question factuelle. Si Claude oublie ces deux éléments, la réponse est considérée comme incomplète.

### Frontmatter standard (piste 6B — god-mode patterns)

Depuis la piste 6B, toute note générée par `/clip` et `/file-intel` porte un frontmatter YAML enrichi, auditable par `/vault-audit` (piste 6E) :

```yaml
---
source: web | pdf | docx | txt | md | manual | import | session
source_url: https://...             # uniquement si source=web (clip)
source_file: ./path/to.pdf          # uniquement si source=pdf|docx|txt|md (file-intel)
source_knowledge: internal | web-checked | mixed
verification_date: 2026-04-21       # ISO YYYY-MM-DD
statut: draft | verified | to-verify | archived
importance: low | medium | high | core
tags: [...]
---
```

**Règle d'or** : ces champs sont **additifs**. Les notes existantes ne sont jamais modifiées automatiquement ; seul `xb audit --migrate` (piste 6E) peut compléter les champs manquants, et uniquement en append (jamais en renommage).

**Cartographie skill → valeurs** :

| Skill | `source` | `source_knowledge` | `statut` initial |
|-------|----------|--------------------|------------------|
| `/clip` | `web` | `web-checked` | `draft` |
| `/file-intel` (pdf) | `pdf` | `internal` | `to-verify` |
| `/file-intel` (docx) | `docx` | `internal` | `to-verify` |
| `/file-intel` (txt/md) | `txt` ou `md` | `internal` | `to-verify` |

`/inbox-zero` **ne modifie jamais** le frontmatter ; il ne fait que déplacer les fichiers. Pour enrichir/migrer un frontmatter, utiliser `xb audit --migrate` (piste 6E, pas encore livré).

### Skills canoniques (10) vs Skills Kepano (5 optionnels)

| Catégorie | Source | Activé par défaut |
|---|---|---|
| **xais-brain core** (10) | `vault-template/.claude/skills/` | ✅ Oui |
| **Kepano** (5) | `github.com/kepano/obsidian-skills` | ❌ Demandé en étape 9 |

Les skills Kepano (CEO d'Obsidian) sont des compagnons de navigation : `obsidian-cli` (CLI Obsidian officiel), `obsidian-markdown` (wikilinks/callouts/embeds), `obsidian-bases` (vues table/card), `json-canvas` (canvas visuels), `defuddle` (extraction markdown propre depuis URLs).

---

## Spécifications versionnées (`specs/`)

Le dossier `specs/` est versionné dans le repo mais **n'est pas copié** dans le vault de l'utilisateur. Il sert d'historique de développement :

- `specs/done/` — plans d'implémentation terminés
- `specs/handoffs/` — résumés de session pour la continuité (un par session significative, numérotés `NNN-YYYY-MM-DD-slug.md`)

C'est un pattern interne à xais-brain pour documenter les décisions et permettre la reprise de travail entre sessions Claude Code via `/XD-pickup`.
