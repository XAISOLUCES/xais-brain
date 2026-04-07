# memory/

Mémoire long terme du vault — fichiers Markdown indexés par `MEMORY.md` (à la racine).

## Comment ça marche

Chaque fichier ici représente **une catégorie de mémoire**. Tu en crées autant que tu veux, organisés sémantiquement (pas chronologiquement).

Exemples typiques :

- `user.md` — qui tu es, rôle, préférences, contexte
- `projects.md` — projets en cours, statut, deadlines
- `decisions.md` — décisions importantes, avec le pourquoi
- `learnings.md` — leçons apprises, patterns récurrents
- `people.md` — collaborateurs, mentors, contacts clés

## Format d'un fichier mémoire

```markdown
---
name: User profile
description: Qui je suis et comment je préfère bosser
type: user
---

[Contenu de la mémoire en Markdown libre.]
```

Le frontmatter aide Claude à juger la pertinence en contexte. Plus la `description` est précise, mieux Claude saura quand charger cette mémoire.

## Indexation

Chaque fichier que tu crées doit avoir une ligne dans `MEMORY.md` (à la racine du vault) :

```markdown
- [User profile](memory/user.md) — qui je suis et comment je préfère bosser
```

`MEMORY.md` est l'**index uniquement** — pas de contenu lourd dedans. Le contenu vit ici dans `memory/`.

## Pour démarrer

Ce dossier est vide au départ. Crée ton premier fichier quand tu en as besoin — pas avant. Tu peux aussi laisser Claude écrire ici automatiquement (skills `/dream`, `/tldr`, etc.).
