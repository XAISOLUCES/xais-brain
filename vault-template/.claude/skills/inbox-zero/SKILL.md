---
name: inbox-zero
description: Trie automatiquement le contenu de inbox/ dans les bons dossiers du vault (projects, research, daily, archive, memory). Utiliser quand l'utilisateur dit inbox-zero, trie l'inbox, range mes fichiers, ou vide ma boîte de réception.
user-invocable: true
disable-model-invocation: false
model: sonnet
---

# inbox-zero

Vide `inbox/` en distribuant chaque fichier dans le bon dossier du vault.

## Étapes

### 1. Lister inbox/

- Lire tous les fichiers de `inbox/` (récursif)
- Si vide → annoncer *"Inbox déjà vide ✓"* et stopper

### 2. Pour chaque fichier

Lire le fichier (ou son frontmatter + premières lignes si gros), puis classifier selon ces règles :

| Critère | Destination |
|---|---|
| Concerne un projet existant dans `projects/[nom]/` | `projects/[nom]/notes/` |
| Idée brute, brainstorm, recherche | `research/[topic-slug].md` |
| Note datée d'une journée précise | `daily/YYYY-MM-DD.md` |
| Travail terminé, document de référence | `archive/[année]/` |
| Mémoire long terme (décision, leçon) | `memory/[catégorie].md` (append + index) |
| Ambigu | Garder dans `inbox/` et flagger |

### 3. Mode interactif vs batch

**Par défaut** (interactif) : pour chaque fichier, propose la destination et demande confirmation rapide (`[Y/n/skip]`).

**Si l'utilisateur dit "tout d'un coup", "batch", ou "trie tout"** : exécute en batch et liste les déplacements à la fin.

### 4. Déplacer (jamais copier)

Utilise `mv` pour préserver l'historique git si le vault est versionné.

Crée les dossiers cibles s'ils n'existent pas (ex: `projects/[nom]/notes/`).

**Règle de préservation du frontmatter (piste 6B — god-mode patterns)**
Les fichiers clippés par `/clip` ou résumés par `/file-intel` contiennent un frontmatter YAML enrichi (`source`, `source_url`/`source_file`, `source_knowledge`, `verification_date`, `statut`, `importance`, `tags`, …). `/inbox-zero` **ne doit JAMAIS** :

- réécrire ou renommer ces champs,
- normaliser la casse,
- supprimer des champs inconnus,
- modifier l'ordre des clés YAML existantes.

Le skill ne fait que **déplacer** le fichier. Si tu veux enrichir un frontmatter, utilise `/vault-audit --migrate` (skill dédié, piste 6E).

Tu peux lire le frontmatter pour **classifier** la destination (par exemple `source: pdf` + `importance: core` → `research/`), mais tu n'en modifies jamais la valeur.

### 5. Récap final

```
✓ 12 fichiers triés
  → 4 vers projects/xais-brain/notes/
  → 5 vers research/
  → 2 vers archive/2026/
  → 1 vers memory/learnings.md (+ index MEMORY.md)
✗ 1 fichier ambigu : note-sans-titre.md (resté dans inbox/)
```

### 6. Si fichiers ambigus

Propose une seconde passe interactive pour les fichiers laissés dans `inbox/`, avec contexte supplémentaire si nécessaire.
