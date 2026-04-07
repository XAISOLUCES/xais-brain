# xais-brain

> Ton second cerveau — Obsidian + Claude Code, prêt en une commande.

**xais-brain** est un installateur tout-en-un qui transforme un dossier vide en vault Obsidian piloté par Claude Code. Tu déposes tes fichiers (PDFs, docs, slides) dans `inbox/`, Claude les digère, les organise, et les retrouve quand tu en as besoin.

---

## Installation rapide

```bash
curl -fsSL https://raw.githubusercontent.com/xais/xais-brain/main/setup.sh | bash
```

Le script installe :

- **Obsidian** (via Homebrew)
- **Claude Code CLI** (l'IA qui lit et écrit dans ton vault)
- **Dépendances Python** (dans un venv isolé, pas de pollution système)
- **Template de vault** (CLAUDE.md, structure de dossiers)
- **Skills slash commands** : `/vault-setup`, `/daily`, `/tldr`, `/file-intel`

> Rien n'est uploadé. Ton vault reste sur ta machine.

---

## Ce que tu obtiens

- Un vault Obsidian structuré et personnalisable
- Claude Code qui connaît ton vault et l'utilise comme mémoire long terme
- Un système de capture (`inbox/`) qui digère tes fichiers via LLM
- Des notes journalières, des projets, de la recherche, et un système d'archive

---

## Plateformes supportées

- macOS uniquement (pour l'instant)

---

## Multi-LLM

Par défaut, `/file-intel` utilise **Gemini** (gratuit). Tu peux changer dans `.env` :

```bash
LLM_PROVIDER=gemini   # ou claude, openai
```

---

## Licence

[MIT](LICENSE) — fais-en ce que tu veux.
