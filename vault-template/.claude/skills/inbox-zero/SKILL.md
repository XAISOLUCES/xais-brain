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
- **Warning budget (piste 6F)** : si plus de 20 fichiers, annoncer *"⚠ inbox/ contient X fichiers. Le tri risque d'être long — utilise 'trie tout' pour le mode batch, ou traite par lots."* avant de continuer.

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

**Si l'utilisateur dit "tout d'un coup", "batch", ou "trie tout"** : passe en mode batch avec **checkpoint humain** avant de déplacer quoi que ce soit (piste 6C).

### 3.bis Checkpoint humain (mode batch — piste 6C)

Avant tout `mv`, même en mode batch :

1. **Plan numéroté** — affiche un plan du tri proposé sous forme de tableau :
   ```
   Plan de tri (12 fichiers) :
    1. inbox/note-xai.md          → projects/xais-brain/notes/
    2. inbox/article-karpathy.md  → research/
    3. inbox/draft-post.md        → inbox/ (ambigu)
    ...
   ```
2. **STOP** — demande explicitement : **"OK pour lancer le tri ? (oui / modif X→Y / non)"**
3. **Attendre une réponse explicite** :
   - `oui` / vide → exécuter.
   - `modif 3 → research/` → ajuster la ligne 3 du plan puis redemander.
   - `non` → annuler, ne rien déplacer.
4. **Mode CI** : si `XAIS_BRAIN_CI=1` ou `CI=1` est défini dans l'environnement, assume "oui" et exécute sans attendre. Même chose si le tri est lancé depuis un script non interactif.
5. Après exécution, passer à l'étape 5 (récap final).

Ne jamais sauter ce checkpoint tant que le mode batch est actif — c'est le garde-fou principal contre un `mv` massif accidentel.

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
