---
name: memory-add
description: Ajoute une nouvelle entrée au système de mémoire long terme du vault et met à jour l'index MEMORY.md automatiquement. Utiliser quand l'utilisateur dit memory-add, ajoute à la mémoire, retiens ça, sauvegarde ce souvenir, ou veut capturer une décision/leçon importante.
user-invocable: true
disable-model-invocation: false
model: sonnet
---

# memory-add

Ajoute une mémoire au système `memory/` et indexe dans `MEMORY.md`.

## Étapes

### 1. Identifier le contenu

Si l'utilisateur a fourni le contenu directement → l'utiliser.
Sinon → demander : *"Qu'est-ce que tu veux retenir ? Donne-moi le contexte et le pourquoi."*

### 2. Classifier le type

Détermine le type parmi :

- **user** — qui est l'utilisateur, son rôle, ses préférences
- **project** — état d'un projet, deadline, stakeholders
- **decision** — choix important pris, avec son pourquoi
- **learning** — leçon apprise, pattern récurrent
- **reference** — pointer vers une ressource externe
- **people** — info sur un collaborateur, mentor, contact

Si ambigu → propose 2 options max à l'utilisateur.

### 3. Choisir le fichier cible

| Type | Fichier |
|---|---|
| user | `memory/user.md` |
| project | `memory/projects.md` |
| decision | `memory/decisions.md` |
| learning | `memory/learnings.md` |
| reference | `memory/references.md` |
| people | `memory/people.md` |

Si le fichier n'existe pas → le créer avec frontmatter :

```markdown
---
name: [Nom catégorie]
description: [Description courte de ce que contient ce fichier]
type: [type]
---
```

### 4. Ajouter l'entrée

Format d'une entrée :

```markdown
## [YYYY-MM-DD] — [Titre court]

[Contenu de la mémoire en 2-5 phrases]

**Pourquoi** : [Raison/contexte]
**Quand l'utiliser** : [Situation où cette mémoire devient pertinente]
```

### 5. Mettre à jour MEMORY.md

Si la ligne d'index n'existe pas encore, l'ajouter :

```markdown
- [Decisions](memory/decisions.md) — choix importants pris avec leur contexte
```

Garde l'index sous 200 lignes — si trop long, propose un nettoyage.

### 6. Confirmation

```
✓ Mémoire ajoutée à memory/decisions.md
✓ Index MEMORY.md à jour
```
