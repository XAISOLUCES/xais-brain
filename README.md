# xais-brain

> **Le second brain qui s'auto-audite.**
> Un vault Obsidian piloté par Claude Code, pensé dès le départ pour que l'IA puisse le lire, l'enrichir et diagnostiquer sa santé.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux-lightgrey.svg)](#)
[![Status](https://img.shields.io/badge/status-alpha-orange.svg)](#)

Tous les PKM rouillent en silence : notes orphelines, doublons, liens cassés, frontmatter incomplet. Obsidian ne te le dit pas. **xais-brain** scanne ton vault, détecte les problèmes, et te propose des actions concrètes — sans rien uploader.

```
$ xb audit

Audit termine : 142 notes scannees, 18 points d'attention.
Rapport : ~/vault/99-Meta/Audit-2026-04-21.md
```

<details>
<summary>Aperçu du rapport généré</summary>

```markdown
# Vault Audit — 2026-04-21

**Notes scannées** : 142
**Temps** : 0.8s

## Notes orphelines (2)
- [ ] [[inbox/a-lire.md]] — 0 backlinks, 0 wikilinks sortants
- [ ] [[inbox/vieille-note-oubliee.md]] — 0 backlinks, 0 wikilinks sortants

## Notes anémiques (< 100 mots) (7)
- [ ] [[daily/2026-04-15.md]] — 11 mots
- [ ] [[research/bert-vs-gpt.md]] — 52 mots
...

## Doublons (titre exact) (1)
- [ ] [[archive/bert-vs-gpt.md]] ≈ [[research/bert-vs-gpt.md]]

## Frontmatter incomplet (3)
- [ ] [[daily/2026-04-15.md]] — manque `statut`, `source_knowledge`

## Notes `to-verify` depuis > 30 jours (2)
- [ ] [[research/transformers-architecture.md]] — verification_date: 2026-01-15

## Tags incohérents (1 groupe)
- [ ] `#ai` (4 notes), `#AI` (1 note) → unifier ?

## Wikilinks cassés (2)
- [ ] [[daily/2026-04-15.md]] → [[quelque-chose-de-disparu]]
```

</details>

---

## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/XAISOLUCES/xais-brain/main/setup.sh | bash
```

Une seule commande, ~3 minutes. Le script t'interroge sur :

- Le chemin où installer ton vault
- Le LLM à utiliser (Gemini gratuit / Claude / OpenAI)
- Un dossier de fichiers existants à importer (optionnel)

> Rien n'est uploadé. Ton vault reste sur ta machine.

---

## Pourquoi xais-brain

Trois différences concrètes vs. un Obsidian nu ou les templates "Claude + PKM" existants.

### 1. Self-auditing

`xb audit` scanne 8 symptômes de dégradation : **orphelines, anémiques, doublons, frontmatter incomplet, `to-verify` stale, tags incohérents, wikilinks cassés, notes peu liées** (< 3 wikilinks sortants). Output : un rapport Markdown checklist dans `99-Meta/Audit-YYYY-MM-DD.md`.

`xb audit --migrate` complète automatiquement les frontmatter manquants des notes existantes, sans jamais écraser une valeur.

### 2. AI-native by design

Chaque note produite par `/clip` ou `/file-intel` porte un frontmatter structuré lisible par Claude :

```yaml
---
source: web | pdf | docx | txt | md
source_url: https://...
source_knowledge: web-checked | internal
verification_date: 2026-04-21
statut: draft | verified | to-verify | archived
importance: low | medium | high | core
tags: [tag1, tag2]
liens_forts: ["[[Concept1]]", "[[Concept2]]"]
liens_opposition: ["[[ContreIdee]]"]
---
```

C'est ce moteur qui rend l'audit mesurable et les réponses de Claude pertinentes.

**Auto-discipline intégrée** :
- `/clip` et `/file-intel` loguent chaque note produite dans `99-Meta/Fact-Check-Log.md` (append-only — traçabilité des sources)
- `/file-intel` annonce le budget tokens estimé avant le batch (provider, coût, durée) depuis `.claude/pricing.json`
- Sur un batch ≥ 6 fichiers, un checkpoint humain s'affiche après les 3 premiers (bypass auto en CI)

### 3. Local-first, multi-LLM

Vault en Markdown brut sur ton disque. Pas de cloud, pas de lock-in. Change de provider LLM en éditant une ligne dans `.env` (Gemini, Claude, OpenAI).

---

## CLI rapide (`xb`)

Le setup installe `xb` dans `~/.local/bin/` — raccourcis utilisables depuis n'importe où.

```bash
xb audit                      # Scanne et génère le rapport d'hygiène
xb audit --migrate            # Complète les frontmatter manquants
xb audit --json               # Sortie JSON sur stdout (CI / scripting)
xb audit --output <path>      # Écrit le rapport ailleurs que dans 99-Meta/
xb status                     # État du vault (inbox, daily, provider)
xb daily                      # Lance /daily en one-shot
xb inbox                      # Lance /inbox-zero en one-shot
xb intel ~/Documents/PDFs     # Traite des fichiers via LLM
xb clip https://example.com   # Clippe une page web dans inbox/
xb open                       # Ouvre Obsidian sur le vault
xb shell                      # Session Claude Code interactive
xb help                       # Liste toutes les commandes
```

**Résolution du vault** : `xb` cherche dans cet ordre :
1. `$XAIS_BRAIN_VAULT` (variable d'env)
2. `vault-config.json` dans le répertoire courant
3. `~/xais-brain-vault/` (défaut)

Multi-vaults : `XAIS_BRAIN_VAULT=~/autre-vault xb status`

---

## Les 12 slash commands

| Commande | Ce qu'elle fait |
|---|---|
| `/vault-audit` | **Scanne le vault** et génère un rapport d'hygiène dans `99-Meta/Audit-YYYY-MM-DD.md` |
| `/vault-setup` | T'interviewe en 4 questions et personnalise ton `CLAUDE.md` |
| `/daily` | Démarre la journée avec contexte vault complet |
| `/tldr` | Sauvegarde un résumé de la session courante |
| `/file-intel` | Traite un dossier de fichiers (PDF, DOCX, TXT, MD) via LLM |
| `/inbox-zero` | Trie automatiquement `inbox/` dans les bons dossiers |
| `/clip` | Clippe une page web en note Markdown propre dans `inbox/` |
| `/memory-add` | Ajoute une mémoire long terme et met à jour l'index `MEMORY.md` |
| `/humanise` | Nettoie un texte AI-ifié pour restaurer une voix naturelle FR |
| `/import-vault` | Adopte un vault Obsidian existant sans casser sa structure |
| `/project` | Charge le contexte complet d'un side-project (`projects/[nom]/`) |
| `/client` | Charge le contexte complet d'un client en prod (`clients/[nom]/`) |

Tape n'importe laquelle dans Claude Code pour la déclencher.

> **Tu as déjà un vault Obsidian ?** Lance `claude` depuis sa racine puis `/import-vault` — xais-brain s'installe par-dessus sans casser ta structure.

---

## Ce qui est installé

| Composant | Rôle |
|---|---|
| **Obsidian** | App de notes locale, fichiers Markdown |
| **Claude Code CLI** | L'IA qui lit et écrit dans ton vault |
| **Python venv** (`~/.xais-brain-venv/`) | Isolé du système |
| **12 slash commands** | Voir table ci-dessus |
| **Guide utilisateur** (`GUIDE.md`) | Didactique 10 sections + FAQ, copié dans le vault |
| **2 hooks FR** | SessionStart (contexte vault) + UserPromptSubmit (liste skills sur trigger FR) |
| **Output style Coach FR** | Mode coach challengeant via `/output-style` |
| **Permissions cadrées** | Écritures scopées, `.git/`/`.claude/` protégés, `rm -rf` refusé |
| **CLI `xb`** | Raccourcis depuis n'importe quel dossier |
| **Skills Kepano** *(optionnel)* | `obsidian-cli` `obsidian-markdown` `obsidian-bases` `json-canvas` `defuddle` |

Les skills sont installés à la fois dans le vault et globalement (`~/.claude/skills/`).

---

## Structure du vault

```
mon-vault/
├── CLAUDE.md              ← instructions pour Claude (perso via /vault-setup)
├── MEMORY.md              ← index de la mémoire long terme
├── vault-config.json      ← source de vérité structurée (user, llm, folders)
├── .env                   ← clés API LLM (gitignoré)
├── memory/                ← mémoire sémantique (user, projects, decisions...)
├── inbox/                 ← nouveaux fichiers en attente de tri
├── daily/                 ← notes journalières (YYYY-MM-DD.md)
├── projects/              ← projets actifs et briefs
├── research/              ← notes de recherche, synthèses, idées
├── archive/               ← travail terminé (jamais supprimé)
├── 99-Meta/               ← piste d'audit (à exclure du graphe Obsidian)
│   ├── Audit.md           ← dernier rapport /vault-audit
│   ├── Fact-Check-Log.md  ← log append-only (alimenté par /clip, /file-intel)
│   └── Session-Debriefs/  ← rétrospectives (alimenté par /tldr)
├── scripts/
│   ├── file_intel.py      ← extracteurs PDF/DOCX/TXT/MD + orchestrateur
│   ├── web_clip.py        ← web clipper URL → Markdown (inbox/)
│   ├── vault_audit.py     ← audit hygiène vault
│   └── providers/         ← gemini, claude, openai (interface commune)
└── .claude/
    ├── skills/            ← les 12 slash commands (+ Kepano si activé)
    ├── hooks/             ← session-init.sh + skill-discovery.sh
    ├── output-styles/     ← coach.md (mode coach FR activable)
    ├── rules/             ← règles avancées (importables dans CLAUDE.md)
    └── settings.json      ← permissions + déclaration des hooks
```

Le **système de mémoire** suit le pattern natif Claude Code : `MEMORY.md` est l'index, `memory/` contient les fichiers détaillés (`user.md`, `projects.md`, `decisions.md`, etc.).

Pour l'arborescence complète du repo (code source) et les diagrammes de flux : [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Multi-LLM

`/file-intel` supporte trois providers via `.env` :

```bash
LLM_PROVIDER=gemini   # ou claude, openai
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

| Provider | Modèle par défaut | Coût | Override |
|---|---|---|---|
| `gemini` | `gemini-2.0-flash` | gratuit | `GEMINI_MODEL=...` |
| `claude` | `claude-haiku-4-5-20251001` | payant | `ANTHROPIC_MODEL=...` |
| `openai` | `gpt-4o-mini` | payant | `OPENAI_MODEL=...` |

Changer de provider = modifier une ligne dans `.env`. Aucun code à toucher.

---

## Hooks et permissions

**`SessionStart` → `.claude/hooks/session-init.sh`** — affiche en 3 lignes max : nom du vault, date du jour, fichiers inbox, signale la daily manquante. Lit `vault-config.json` pour gérer les remappages (ex. `projects/` → `clients/`).

**`UserPromptSubmit` → `.claude/hooks/skill-discovery.sh`** — si ton message contient un mot-clé FR (`skill`, `commandes`, `que peux-tu`, `aide-moi`, `quoi faire`, `slash`), liste automatiquement les slash commands. Sinon : silencieux.

**Permissions par défaut (`.claude/settings.json`)** :
- ✅ Écriture dans : `inbox/`, `daily/`, `projects/`, `research/`, `archive/`, `memory/`, `CLAUDE.md`, `MEMORY.md`, `vault-config.json`
- ✅ Bash limité à : `ls`, `date`, `find`, `git`, `python3`, `~/.xais-brain-venv/bin/python3`
- ❌ Refusé : `Edit(.claude/**)`, `Write(.git/**)`, `Bash(rm -rf:*)`

Tu peux étendre ou restreindre ces permissions en éditant `.claude/settings.json`.

---

## Personnalisation

### Ajouter ta propre skill

```bash
mkdir -p ~/.claude/skills/ma-commande
cat > ~/.claude/skills/ma-commande/SKILL.md << 'EOF'
---
name: ma-commande
description: Ce que fait ma commande, et quand l'utiliser (mots-clés FR de déclenchement).
user-invocable: true
disable-model-invocation: false
model: haiku
---

# ma-commande

[Instructions pour Claude quand cette commande est appelée]
EOF
```

| Champ | Rôle |
|---|---|
| `user-invocable` | `true` rend la skill disponible via `/ma-commande` |
| `disable-model-invocation` | `false` autorise Claude à la déclencher seul |
| `model` | `haiku` (rapide) ou `sonnet` (raisonnement) |

### Ajouter des règles avancées

Crée un fichier dans `[vault]/.claude/rules/` puis importe-le dans `CLAUDE.md` :

```markdown
@import .claude/rules/voice.md
@import .claude/rules/naming.md
```

### Activer le mode Coach FR

```
/output-style
```

Puis sélectionne **Coach FR**. Claude passe en mode coaching : questions challengeantes, accountability, focus action. Chaque réponse se termine par une action faisable dans l'heure et une question. Pour revenir : re-lance `/output-style` → « default ».

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
# macOS :
brew install --cask obsidian
# Linux (Flatpak) :
# flatpak install flathub md.obsidian.Obsidian
curl -fsSL https://claude.ai/install.sh | sh

# 2. Python venv
python3 -m venv ~/.xais-brain-venv
~/.xais-brain-venv/bin/pip install -r requirements.txt

# 3. Vault
mkdir -p ~/mon-vault/{inbox,daily,projects,research,archive,memory,99-Meta/Session-Debriefs,scripts/providers,.claude/skills,.claude/hooks,.claude/output-styles,.claude/rules}
cp vault-template/CLAUDE.md ~/mon-vault/
cp vault-template/GUIDE.md ~/mon-vault/
cp vault-template/MEMORY.md ~/mon-vault/
cp vault-template/vault-config.json ~/mon-vault/
cp -r vault-template/99-Meta/README.md vault-template/99-Meta/Audit.md vault-template/99-Meta/Fact-Check-Log.md ~/mon-vault/99-Meta/
cp -r vault-template/.claude/skills/* ~/mon-vault/.claude/skills/
cp -r vault-template/.claude/skills/* ~/.claude/skills/
cp vault-template/.claude/hooks/*.sh ~/mon-vault/.claude/hooks/
chmod +x ~/mon-vault/.claude/hooks/*.sh
cp vault-template/.claude/output-styles/coach.md ~/mon-vault/.claude/output-styles/
cp vault-template/.claude/settings.json ~/mon-vault/.claude/
cp scripts/file_intel.py scripts/web_clip.py scripts/vault_audit.py ~/mon-vault/scripts/
cp scripts/providers/* ~/mon-vault/scripts/providers/

# 4. Config LLM
cp .env.example ~/mon-vault/.env
# Édite ~/mon-vault/.env pour ajouter ta clé API
```

</details>

---

## Contribution

Les PRs sont bienvenues. Pour ajouter une skill : suivre la structure de [vault-template/.claude/skills/vault-audit/SKILL.md](vault-template/.claude/skills/vault-audit/SKILL.md) et ouvrir une PR.

Bug : [GitHub Issues](https://github.com/XAISOLUCES/xais-brain/issues).

---

## Licence

[MIT](LICENSE) — fais-en ce que tu veux.
