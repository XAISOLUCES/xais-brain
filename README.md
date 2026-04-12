# xais-brain

> Ton second cerveau — Obsidian + Claude Code, prêt en une commande.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#)

**xais-brain** est un installateur tout-en-un qui transforme un dossier vide en vault Obsidian piloté par Claude Code. Tu déposes tes fichiers dans `inbox/`, Claude les digère, les organise dans les bons dossiers, et les retrouve quand tu en as besoin.

> Rien n'est uploadé. Ton vault reste sur ta machine.

---

## Installation rapide

```bash
curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash
```

Une seule commande, ~3 minutes. Le script t'interroge sur :

- Le chemin où installer ton vault
- Le LLM à utiliser pour traiter tes fichiers (Gemini gratuit / Claude / OpenAI)
- Un dossier de fichiers existants à importer (optionnel)

---

## CLI rapide (`xb`)

Le setup installe `xb` dans `~/.local/bin/` — un raccourci pour les opérations courantes, utilisable depuis n'importe quel dossier.

```bash
xb status                     # État du vault (inbox, daily, provider)
xb daily                      # Lance /daily en one-shot
xb inbox                      # Lance /inbox-zero en one-shot
xb intel ~/Documents/PDFs     # Traite des fichiers via LLM (sans session Claude)
xb open                       # Ouvre Obsidian sur le vault
xb shell                      # Session Claude Code interactive dans le vault
xb help                       # Liste toutes les commandes
```

**Résolution du vault** : `xb` cherche dans cet ordre :
1. `$XAIS_BRAIN_VAULT` (variable d'env)
2. `vault-config.json` dans le répertoire courant
3. `~/xais-brain-vault/` (défaut)

Pour utiliser plusieurs vaults : `XAIS_BRAIN_VAULT=~/autre-vault xb status`

> `xb status`, `xb intel` et `xb open` marchent sans Claude Code installé. Seuls `xb daily`, `xb inbox` et `xb shell` nécessitent Claude Code.

---

## Ce qui est installé

| Composant | Rôle |
|---|---|
| **Obsidian** | App de notes locale, fichiers Markdown |
| **Claude Code CLI** | L'IA qui lit et écrit dans ton vault |
| **Python venv** (`~/.xais-brain-venv/`) | Isolé du système, pas de pollution |
| **10 slash commands** | `/vault-setup` `/daily` `/tldr` `/file-intel` `/inbox-zero` `/memory-add` `/humanise` `/import-vault` `/project` `/client` |
| **2 hooks FR** | SessionStart (contexte vault au démarrage) + UserPromptSubmit (liste les skills sur trigger FR) |
| **Output style Coach FR** | Mode coach challengeant activable via `/output-style` |
| **Permissions cadrées** | `settings.json` : écritures scopées aux dossiers du vault, `.git/` et `.claude/` protégés, `rm -rf` refusé |
| **CLI wrapper** (`xb`) | Raccourcis vault depuis n'importe quel dossier (`xb daily`, `xb status`, etc.) |
| **Skills Kepano** *(optionnel)* | `obsidian-cli` `obsidian-markdown` `obsidian-bases` `json-canvas` `defuddle` |

Les skills sont installés à la fois dans le vault et globalement (`~/.claude/skills/`) — tu peux les utiliser depuis n'importe quel dossier.

---

## Les 10 slash commands

| Commande | Ce qu'elle fait |
|---|---|
| `/vault-setup` | T'interviewe en 4 questions et personnalise ton `CLAUDE.md` |
| `/daily` | Démarre la journée avec contexte vault complet (continuité, inbox, projets) |
| `/tldr` | Sauvegarde un résumé de la session courante au bon endroit |
| `/file-intel` | Traite un dossier de fichiers (PDF, DOCX, TXT, MD) via LLM |
| `/inbox-zero` | Trie automatiquement `inbox/` dans `projects/`, `research/`, etc. |
| `/memory-add` | Ajoute une mémoire long terme et met à jour l'index `MEMORY.md` |
| `/humanise` | Nettoie un texte AI-ifié pour restaurer une voix naturelle FR |
| `/import-vault` | Adopte un vault Obsidian existant sans casser sa structure |
| `/project` | Charge le contexte complet d'un side-project (`projects/[nom]/`) |
| `/client` | Charge le contexte complet d'un client en prod (`clients/[nom]/`) |

Tape n'importe laquelle dans Claude Code pour la déclencher.

> **Tu as déjà un vault Obsidian ?** Lance `claude` depuis sa racine puis tape `/import-vault` — xais-brain s'installe par-dessus sans casser ta structure existante.

---

## Structure du vault

```
mon-vault/
├── CLAUDE.md              ← instructions pour Claude (perso via /vault-setup)
├── MEMORY.md              ← index de la mémoire long terme
├── vault-config.json      ← source de vérité structurée (user, llm, folders)
├── .env                   ← clés API LLM (gitignoré)
├── memory/                ← fichiers de mémoire sémantique (user, projects, decisions...)
├── inbox/                 ← nouveaux fichiers en attente de tri
├── daily/                 ← notes journalières (YYYY-MM-DD.md)
├── projects/              ← projets actifs et briefs
├── research/              ← notes de recherche, synthèses, idées
├── archive/               ← travail terminé (jamais supprimé)
├── scripts/
│   ├── file_intel.py      ← extracteurs PDF/DOCX/TXT/MD + orchestrateur
│   └── providers/         ← gemini, claude, openai (interface commune)
└── .claude/
    ├── skills/            ← les 10 slash commands (+ Kepano si activé)
    ├── hooks/             ← session-init.sh + skill-discovery.sh
    ├── output-styles/     ← coach.md (mode coach FR activable)
    ├── rules/             ← règles avancées (importables dans CLAUDE.md)
    └── settings.json      ← permissions + déclaration des hooks
```

Le **système de mémoire** suit le pattern natif Claude Code : `MEMORY.md` est l'index, `memory/` contient les fichiers détaillés organisés sémantiquement (`user.md`, `projects.md`, `decisions.md`, `learnings.md`, etc.).

Pour l'arborescence complète du repo (code source) et les diagrammes ASCII de flux, voir [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Multi-LLM

`/file-intel` supporte trois providers, configurables via `.env` :

```bash
# Quel LLM utiliser ?
LLM_PROVIDER=gemini   # ou claude, openai

# Une seule clé suffit (selon LLM_PROVIDER)
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

| Provider | Modèle par défaut | Coût | Override modèle |
|---|---|---|---|
| `gemini` | `gemini-2.0-flash` | gratuit | `GEMINI_MODEL=...` |
| `claude` | `claude-haiku-4-5-20251001` | payant | `ANTHROPIC_MODEL=...` |
| `openai` | `gpt-4o-mini` | payant | `OPENAI_MODEL=...` |

Changer de provider = modifier une ligne dans `.env`. Aucun code à toucher.

---

## Hooks et permissions

Deux hooks tournent automatiquement dans chaque vault xais-brain.

**`SessionStart` → `.claude/hooks/session-init.sh`**
S'exécute au lancement de Claude Code. Affiche en 3 lignes max : nom du vault, date du jour, fichiers en attente dans `inbox/`, et signale si la note daily du jour n'existe pas. Lit `vault-config.json` pour résoudre les noms de dossiers (utile si tu as remappé `projects/` → `clients/` via `/import-vault`).

**`UserPromptSubmit` → `.claude/hooks/skill-discovery.sh`**
S'exécute à chaque message envoyé à Claude. Si ton message contient un mot-clé FR (`skill`, `commandes`, `que peux-tu`, `aide-moi`, `quoi faire`, `slash`), liste automatiquement les slash commands disponibles avec leur description. Sinon : silencieux.

**Permissions par défaut (`.claude/settings.json`)**
- ✅ Écriture autorisée dans : `inbox/`, `daily/`, `projects/`, `research/`, `archive/`, `memory/`, `CLAUDE.md`, `MEMORY.md`, `vault-config.json`
- ✅ Bash limité à : `ls`, `date`, `find`, `git`, `python3`, `~/.xais-brain-venv/bin/python3`
- ❌ Refusé : `Edit(.claude/**)`, `Write(.git/**)`, `Bash(rm -rf:*)`

Tu peux étendre ou restreindre ces permissions en éditant `.claude/settings.json` à la main.

---

## Personnalisation

### Ajouter ta propre skill

```bash
mkdir -p ~/.claude/skills/ma-commande
cat > ~/.claude/skills/ma-commande/SKILL.md << 'EOF'
---
name: ma-commande
description: Ce que fait ma commande, et quand l'utiliser. Mentionne les mots-clés FR qui doivent la déclencher (ex. "mots-clés magiques").
user-invocable: true
disable-model-invocation: false
model: haiku
---

# ma-commande

[Instructions pour Claude quand cette commande est appelée]
EOF
```

| Champ frontmatter | Rôle |
|---|---|
| `user-invocable` | `true` rend la skill disponible via slash command (`/ma-commande`) |
| `disable-model-invocation` | `false` autorise Claude à la déclencher seul si la description matche |
| `model` | `haiku` (rapide, lectures simples) ou `sonnet` (raisonnement, transformations) |

### Ajouter des règles avancées

Crée un fichier dans `[ton-vault]/.claude/rules/` puis importe-le dans ton `CLAUDE.md` :

```markdown
@import .claude/rules/voice.md
@import .claude/rules/naming.md
```

Le pattern modulaire garde `CLAUDE.md` léger et charge les règles spécialisées uniquement quand pertinent.

### Activer le mode Coach FR

Un output style `coach.md` est livré par défaut. Pour l'activer dans une session Claude Code :

```
/output-style
```

Puis sélectionne **Coach FR**. Claude passera en mode coaching : questions challengeantes, accountability, focus sur l'action plutôt que la planification. Chaque réponse se termine **obligatoirement** par une action faisable dans l'heure et une question d'accountability — pas d'exception. Pour revenir au mode normal, re-lance `/output-style` et choisis « default ».

---

## Installation manuelle

<details>
<summary>Si tu préfères ne pas lancer le one-liner</summary>

```bash
git clone https://github.com/XAISOLUCES/xais-brain.git
cd xais-brain
bash setup.sh
```

Ou étape par étape :

```bash
# 1. Dépendances
brew install --cask obsidian
curl -fsSL https://claude.ai/install.sh | sh

# 2. Python venv
python3 -m venv ~/.xais-brain-venv
~/.xais-brain-venv/bin/pip install -r requirements.txt

# 3. Vault
mkdir -p ~/mon-vault/{inbox,daily,projects,research,archive,memory,scripts/providers,.claude/skills,.claude/hooks,.claude/output-styles,.claude/rules}
cp vault-template/CLAUDE.md ~/mon-vault/
cp vault-template/MEMORY.md ~/mon-vault/
cp vault-template/vault-config.json ~/mon-vault/
cp -r vault-template/.claude/skills/* ~/mon-vault/.claude/skills/
cp -r vault-template/.claude/skills/* ~/.claude/skills/
cp vault-template/.claude/hooks/*.sh ~/mon-vault/.claude/hooks/
chmod +x ~/mon-vault/.claude/hooks/*.sh
cp vault-template/.claude/output-styles/coach.md ~/mon-vault/.claude/output-styles/
cp vault-template/.claude/settings.json ~/mon-vault/.claude/
cp scripts/file_intel.py ~/mon-vault/scripts/
cp scripts/providers/* ~/mon-vault/scripts/providers/

# 4. Config LLM
cp .env.example ~/mon-vault/.env
# Édite ~/mon-vault/.env pour ajouter ta clé API
```

</details>

---

## Pourquoi xais-brain

- **Local-first** : ton vault est sur ton disque, en Markdown plain text. Pas de cloud, pas de lock-in, pas d'abonnement.
- **Multi-LLM** : tu choisis ton provider (gratuit ou payant), tu peux changer en une ligne.
- **Modulaire** : les skills, les rules et la mémoire sont des fichiers séparés que tu peux versionner, partager, étendre.
- **Idempotent** : `setup.sh` est safe à relancer — il détecte les vaults existants, ne casse rien.
- **Français-first** : prompts, slash commands et messages d'erreur sont tous en français.

---

## Contribution

Les PRs sont bienvenues. Pour ajouter une nouvelle skill, suivre la structure de [vault-template/.claude/skills/vault-setup/SKILL.md](vault-template/.claude/skills/vault-setup/SKILL.md) et ouvrir une PR.

Pour signaler un bug : [GitHub Issues](https://github.com/XAISOLUCES/xais-brain/issues).

---

## Licence

[MIT](LICENSE) — fais-en ce que tu veux.
