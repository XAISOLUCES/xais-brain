---
name: humanise
description: Nettoyer un texte AI-ifié pour restaurer une voix naturelle française. Enlève les tics IA (« moreover », « il est important de noter », « exploitons »), les transitions mécaniques, et les listes à rallonge. Utiliser pour humanise, dé-IA-ifier, nettoyer ce texte, rendre plus humain.
user-invocable: true
disable-model-invocation: true
model: sonnet
---

# humanise

Restaure une voix humaine dans un texte marqué IA. Produit un fichier `<nom>-humanise.md` et un changelog des modifs.

## Entrée

Chemin d'un fichier `.md` ou `.txt`. Si l'utilisateur ne précise pas, demander.

## Ce qu'on enlève

### 1. Transitions mécaniques

- « De plus », « Par ailleurs », « En outre », « Néanmoins », « Toutefois » (en excès)
- Ouvertures « Bien que X, Y »
- « Il convient de noter que »

### 2. Clichés IA

- « Dans un monde en constante évolution »
- « Plongeons au cœur de »
- « Libérer ton potentiel »
- « Exploiter la puissance de »
- « C'est crucial de comprendre »

### 3. Verbes corporate

- `utiliser` (en excès) → `prendre`, `se servir de`
- `optimiser` → `améliorer`
- `faciliter` → `aider`
- `exploiter` → `utiliser`
- `tirer parti de` → `utiliser`
- `implémenter` → `mettre en place`

### 4. Quantificateurs vagues

- « divers », « plusieurs », « de multiples », « une myriade »
- « relativement », « généralement » (quand l'auteur connaît la réponse)

### 5. Motifs robotiques

- Questions rhétoriques suivies de leurs réponses immédiates
- Parallélismes obsessionnels (toujours exactement 3 exemples)
- Annonces d'emphase (« Il est crucial de comprendre que... »)
- Conclusions qui paraphrasent l'intro

## Ce qu'on garde ou ajoute

- Phrases de longueurs variées
- Ton direct, affirmatif
- Exemples concrets à la place de généralités
- Rythme naturel (pas de structure « 3 bullets + conclusion »)
- Le « je » si l'original l'utilisait

## Process

1. Lire le fichier source.
2. Appliquer les transformations (pattern par pattern).
3. Écrire le résultat dans `<nom>-humanise.md` dans le même dossier.
4. Logger un changelog : combien de tics enlevés, combien de phrases reformulées, et marquer les passages qui gagneraient un exemple concret (à compléter par l'user).

## Exemple

**Avant (IA)** :
> Dans l'écosystème numérique actuel en constante évolution, il est crucial de comprendre que tirer parti de l'intelligence artificielle de manière efficace n'est pas simplement une question d'utiliser des technologies de pointe — c'est exploiter son potentiel transformateur pour libérer des opportunités sans précédent.

**Après (humain)** :
> L'IA marche mieux quand tu l'utilises pour des tâches précises. Écris du code, analyse des données, réponds à des questions. Le reste est du marketing.

## Cas d'erreur

- **Fichier introuvable** → demande un path valide.
- **Fichier vide** → warning, pas d'écriture.
- **Fichier déjà humanisé** (`-humanise.md` existe) → demande écrasement.

## Sortie finale

- Fichier `<nom>-humanise.md` créé
- Changelog affiché dans le chat : « 12 tics IA enlevés, 4 phrases reformulées, 2 passages à enrichir d'un exemple concret »
