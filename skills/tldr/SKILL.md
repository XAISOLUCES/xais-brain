---
name: tldr
description: Sauvegarde un résumé de la session courante dans le vault — décisions clés, choses à retenir, prochaines actions. Choisit automatiquement le bon dossier de destination. Utiliser quand l'utilisateur dit tldr, résume cette session, sauvegarde, ou en fin de conversation.
---

# tldr

Sauvegarde un résumé condensé de la session courante dans le vault.

## Étapes

### 1. Analyser la session

Identifie depuis le contexte conversationnel :

- **Sujet principal** : de quoi on a parlé
- **Décisions prises** : choix techniques, validations, rejets
- **Actions effectuées** : fichiers créés/modifiés, commandes lancées
- **À retenir** : insights, leçons apprises, patterns
- **Prochaines actions** : ce qu'il reste à faire

### 2. Choisir la destination

| Sujet | Destination |
|---|---|
| Travail sur un projet existant | `projects/[nom-projet]/sessions/YYYY-MM-DD.md` |
| Recherche, exploration, brainstorming | `research/[topic-slug].md` |
| Réflexion personnelle, journal | `daily/YYYY-MM-DD.md` (append) |
| Décision importante long terme | `memory/decisions.md` (append + index) |
| Apprentissage technique | `memory/learnings.md` (append + index) |

Si ambigu → demande à l'utilisateur en proposant 2 options max.

### 3. Format du résumé

```markdown
---
date: YYYY-MM-DD
tags: [tldr, ...]
session: [titre court]
---

# [Titre]

## Contexte

[1-2 phrases sur le pourquoi de cette session]

## Décisions

- ...

## Actions

- ...

## À retenir

- ...

## Prochaines actions

- [ ] ...
```

### 4. Confirmation

Confirme le chemin de sauvegarde et propose à l'utilisateur de relire/ajuster avant de finaliser.

### 5. Mise à jour d'index si pertinent

Si la destination est `memory/` → mettre aussi à jour `MEMORY.md` avec une ligne d'index.
