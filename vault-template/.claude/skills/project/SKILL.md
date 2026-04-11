---
name: project
description: Charge le contexte complet d'un side-project. Lit le README, les notes récentes, surface le statut, les décisions récentes et les next actions. Utiliser quand on reprend le travail sur un projet.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# project

Use when the user runs `/project [name]` or asks to "work on [project]" / "reprendre [projet]".

## What to do

1. **Find the project**
   - Look for `projects/[name]/` (fuzzy match on the name if exact match fails)
   - If multiple matches → list them and ask which one
   - If no match → list all projects in `projects/` and ask which one, or propose to create it

2. **Load the context**
   Read in this order:
   - `projects/[name]/README.md` — statut, description, stack, next actions
   - `projects/[name]/notes/` — les 3 notes les plus récentes (par date de modification)
   - Any file named `DECISIONS.md`, `ARCHITECTURE.md`, or `ROADMAP.md` if present

3. **Surface the context**
   Present a short briefing:
   ```
   📦 [Project name]

   Statut: [active / paused / blocked / ...]
   Stack: [...]

   Dernière activité: [date de la dernière note]

   Décisions récentes:
   - ...

   Next actions:
   - [ ] ...

   Sur quoi tu veux avancer ?
   ```

4. **Offer to start**
   Wait for the user's direction before reading code or touching files.

## If the project doesn't exist yet

Propose to bootstrap it:
```
projects/[name]/
├── README.md        ← Statut + description + stack + next actions
├── DECISIONS.md     ← Log des choix techniques et architecturaux
└── notes/           ← Sessions notes (YYYY-MM-DD-slug.md)
```

Ask for confirmation before creating.

## README template for new projects

```markdown
# [Project name]

**Statut:** active | paused | blocked | done
**Stack:** [...]
**Repo:** [url if applicable]
**Démarré:** YYYY-MM-DD

## Description
[1-2 phrases — c'est quoi, pour qui, pourquoi]

## Next actions
- [ ]

## Contexte
[Notes sur le projet, liens utiles, etc.]
```

## Rules
- Français par défaut
- Ne pas charger tout le code source du projet — juste les fichiers de contexte du vault
- Si le projet est marqué `paused` ou `blocked`, mentionner la raison avant tout
