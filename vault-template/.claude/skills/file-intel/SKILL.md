---
name: file-intel
description: Traite un dossier de fichiers (PDF, DOCX, TXT, MD) via LLM et génère des résumés Markdown prêts pour Obsidian. Utiliser quand l'utilisateur dit file-intel, résume ce dossier, traite ces fichiers, ou veut digérer des PDFs.
user-invocable: true
disable-model-invocation: false
model: sonnet
---

# file-intel

Traite un dossier de fichiers et génère des notes Markdown synthétiques dans `inbox/`.

## Étapes

### 1. Identifier le dossier source

- Si l'utilisateur a fourni un chemin → l'utiliser
- Sinon → demander : *"Quel dossier veux-tu traiter ?"*
- Vérifier que le chemin existe et contient au moins un fichier supporté

### 2. Vérifier la config LLM

Lire `.env` à la racine du vault :

- `LLM_PROVIDER` (gemini | claude | openai)
- La clé API correspondante :
  - `gemini` → `GOOGLE_API_KEY`
  - `claude` → `ANTHROPIC_API_KEY`
  - `openai` → `OPENAI_API_KEY`

Si la clé manque → expliquer comment l'obtenir et stopper.

### 3. Lancer le script Python

```bash
"$HOME/.xais-brain-venv/bin/python3" \
  "$VAULT_PATH/scripts/file_intel.py" \
  "[dossier source]" \
  "$VAULT_PATH/inbox"
```

Le script :

- Lit chaque fichier du dossier (PDF, DOCX, TXT, MD)
- **Affiche une estimation de budget avant exécution** (piste 6F) — nombre de fichiers, pages, durée attendue, coût estimé en USD selon `LLM_PROVIDER`. Les tarifs sont lus depuis `.claude/pricing.json` (modifiable sans toucher au code).
- **Demande deux checkpoints humains** (piste 6C) :
  - **Checkpoint 1** — juste après le budget, avant de bruler des tokens : `OK pour lancer le traitement ? [Y/n]`. Réponse vide = oui par défaut, `non` annule tout.
  - **Checkpoint 2** — après les 3 premiers fichiers traités (seulement si le batch contient 6 fichiers ou plus) : permet d'inspecter les notes générées avant d'attaquer le reste. `Continuer avec les N restant(s) ? [Y/n]`. Un `non` arrête le batch proprement.
- Envoie au LLM configuré via `LLM_PROVIDER`
- Génère un fichier Markdown par source dans `inbox/`
- Frontmatter automatique avec source, date, tags

**Mode CI** : si `XAIS_BRAIN_CI=1` ou `CI=1`, le budget et les checkpoints sont affichés mais **aucun prompt interactif n'est bloquant** — le script assume "oui" et enchaîne directement. Idem si stdin n'est pas un TTY (pipe, redirection).

### 4. Confirmation

Une fois terminé :

- Compter les fichiers générés dans `inbox/`
- Afficher un récap : *"X notes créées dans inbox/. Veux-tu lancer `/inbox-zero` pour les trier ?"*

### 5. Erreurs courantes

- **Clé API manquante** → guider vers `.env` et l'URL d'obtention
- **venv pas trouvé** → relancer `setup.sh`
- **Aucun fichier supporté** → lister les extensions supportées (pdf, docx, txt, md)
- **Quota LLM atteint** → suggérer de changer `LLM_PROVIDER` dans `.env`
