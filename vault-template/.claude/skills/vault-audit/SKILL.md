---
name: vault-audit
description: Scanne le vault et genere un rapport d'hygiene (orphelines, anemiques, notes peu liees, doublons, frontmatter, tags, liens casses, notes to-verify > 30j). Utiliser quand l'utilisateur dit audit vault, hygiene vault, sante vault, vault-audit, scan du vault.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# vault-audit

Scanne le vault et produit un rapport d'hygiene actionnable dans `99-Meta/Audit-YYYY-MM-DD.md`.

## Detections

- **Orphelines** : 0 backlinks ET 0 wikilinks sortants
- **Anemiques** : notes < 100 mots
- **Doublons** : meme titre exact dans differents dossiers
- **Frontmatter incomplet** : manque `statut` ou `source_knowledge`
- **Notes `to-verify` > 30j** : via `verification_date`
- **Tags incoherents** : variantes de casse (`#ai` vs `#AI`)
- **Wikilinks casses** : `[[X]]` ou `X.md` n'existe pas
- **Notes peu liees** : note >= 100 mots avec moins de 3 wikilinks sortants
  (piste 6H — density rule). Daily notes exclues par convention.

## Workflow

### 1. Lancer le script

```bash
~/.xais-brain-venv/bin/python3 scripts/vault_audit.py "$PWD"
```

Ou via le CLI :

```bash
xb audit
```

Le rapport est ecrit dans `99-Meta/Audit-YYYY-MM-DD.md`.

### 2. Lire le rapport

Ouvrir le fichier genere, resumer a l'utilisateur :

- Nombre de notes scannees
- Les 3 categories avec le plus d'items
- Proposer les actions prioritaires (ex : "12 frontmatter incomplets — tu veux que je les complete avec `xb audit --migrate` ?")

### 3. Actions suggerees

Selon ce qui ressort :

- **Frontmatter incomplet eleve** : proposer `xb audit --migrate` (complete avec defaults).
- **Beaucoup d'orphelines dans `inbox/`** : proposer `/inbox-zero`.
- **Beaucoup d'anemiques dans `daily/`** : normal, ne pas alerter.
- **Wikilinks casses** : lister les 5 premiers et proposer de les renommer.
- **Notes peu liees (< 3 wikilinks)** : suggerer d'ouvrir la note et d'ajouter
  2-3 liens `[[Concept]]` vers les concepts centraux. Utile pour les notes
  issues de `/file-intel` sans injection automatique de liens.

## Options

- `--migrate` : complete les champs `statut`, `source_knowledge`, `verification_date` manquants (sans ecraser).
- `--json` : imprime le rapport en JSON sur stdout (scripting).
- `--output <path>` : ecrit le rapport ailleurs que dans `99-Meta/`.

## Edge cases

- Vault sans `99-Meta/` → le dossier est cree automatiquement.
- Vault vide → rapport avec 0 notes, toutes sections vides (pas d'erreur).
- Note avec frontmatter casse → parser tolerant, note comptee quand meme.
