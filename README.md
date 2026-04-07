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
curl -fsSL https://raw.githubusercontent.com/xais/xais-brain/main/setup.sh | bash
```

Une seule commande, ~3 minutes. Le script t'interroge sur :

- Le chemin où installer ton vault
- Le LLM à utiliser pour traiter tes fichiers (Gemini gratuit / Claude / OpenAI)
- Un dossier de fichiers existants à importer (optionnel)

---

## Ce qui est installé

| Composant | Rôle |
|---|---|
| **Obsidian** | App de notes locale, fichiers Markdown |
| **Claude Code CLI** | L'IA qui lit et écrit dans ton vault |
| **Python venv** (`~/.xais-brain-venv/`) | Isolé du système, pas de pollution |
| **6 slash commands** | `/vault-setup` `/daily` `/tldr` `/file-intel` `/inbox-zero` `/memory-add` |
| **Skills Kepano** *(optionnel)* | CLI Obsidian officiel pour navigation native |

Les skills sont installés à la fois dans le vault et globalement (`~/.claude/skills/`) — tu peux les utiliser depuis n'importe quel dossier.

---

## Les 6 slash commands

| Commande | Ce qu'elle fait |
|---|---|
| `/vault-setup` | T'interviewe en 4 questions et personnalise ton `CLAUDE.md` |
| `/daily` | Démarre la journée avec contexte vault complet (continuité, inbox, projets) |
| `/tldr` | Sauvegarde un résumé de la session courante au bon endroit |
| `/file-intel` | Traite un dossier de fichiers (PDF, DOCX, TXT, MD) via LLM |
| `/inbox-zero` | Trie automatiquement `inbox/` dans `projects/`, `research/`, etc. |
| `/memory-add` | Ajoute une mémoire long terme et met à jour l'index `MEMORY.md` |

Tape n'importe laquelle dans Claude Code pour la déclencher.

---

## Structure du vault

```
mon-vault/
├── CLAUDE.md          ← instructions pour Claude (perso via /vault-setup)
├── MEMORY.md          ← index de la mémoire long terme
├── memory/            ← fichiers de mémoire sémantique (user, projects, decisions...)
├── inbox/             ← nouveaux fichiers en attente de tri
├── daily/             ← notes journalières (YYYY-MM-DD.md)
├── projects/          ← projets actifs et briefs
├── research/          ← notes de recherche, synthèses, idées
├── archive/           ← travail terminé (jamais supprimé)
├── scripts/           ← file_intel.py + providers LLM
└── .claude/
    ├── skills/        ← les 6 slash commands
    └── rules/         ← règles avancées (importables dans CLAUDE.md)
```

Le **système de mémoire** suit le pattern natif Claude Code : `MEMORY.md` est l'index, `memory/` contient les fichiers détaillés organisés sémantiquement (`user.md`, `projects.md`, `decisions.md`, `learnings.md`, etc.).

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

## Personnalisation

### Ajouter ta propre skill

```bash
mkdir -p ~/.claude/skills/ma-commande
cat > ~/.claude/skills/ma-commande/SKILL.md << 'EOF'
---
name: ma-commande
description: Ce que fait ma commande, et quand l'utiliser.
---

# ma-commande

[Instructions pour Claude quand cette commande est appelée]
EOF
```

### Ajouter des règles avancées

Crée un fichier dans `[ton-vault]/.claude/rules/` puis importe-le dans ton `CLAUDE.md` :

```markdown
@import .claude/rules/voice.md
@import .claude/rules/naming.md
```

Le pattern modulaire garde `CLAUDE.md` léger et charge les règles spécialisées uniquement quand pertinent.

---

## Installation manuelle

<details>
<summary>Si tu préfères ne pas lancer le one-liner</summary>

```bash
git clone https://github.com/xais/xais-brain.git
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
mkdir -p ~/mon-vault/{inbox,daily,projects,research,archive,memory,scripts/providers,.claude/skills,.claude/rules}
cp vault-template/CLAUDE.md ~/mon-vault/
cp vault-template/MEMORY.md ~/mon-vault/
cp -r skills/* ~/mon-vault/.claude/skills/
cp -r skills/* ~/.claude/skills/
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

Les PRs sont bienvenues. Pour ajouter une nouvelle skill, suivre la structure de [skills/vault-setup/SKILL.md](skills/vault-setup/SKILL.md) et ouvrir une PR.

Pour signaler un bug : [GitHub Issues](https://github.com/xais/xais-brain/issues).

---

## Licence

[MIT](LICENSE) — fais-en ce que tu veux.
