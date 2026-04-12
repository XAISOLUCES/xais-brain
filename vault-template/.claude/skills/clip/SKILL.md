---
name: clip
description: Clippe une page web dans inbox/ en note Markdown propre. Utiliser quand l'utilisateur dit clip, sauvegarde cette page, clippe cette URL, web clip, ou donne une URL a sauvegarder.
user-invocable: true
disable-model-invocation: false
model: haiku
---

# clip

Clippe une URL web en note Markdown propre dans inbox/.

## Workflow

1. Demander l'URL si pas fournie
2. Lancer le script Python :
   ```bash
   ~/.xais-brain-venv/bin/python3 scripts/web_clip.py "<url>" "<inbox_dir>"
   ```
3. Lire le fichier genere pour confirmer le contenu
4. Proposer /inbox-zero pour trier

## Edge cases

- Si l'URL est un PDF → rediriger vers /file-intel
- Si l'extraction est vide → warning, proposer de copier-coller manuellement
- Si le fichier existe deja → le script ajoute la date au nom
