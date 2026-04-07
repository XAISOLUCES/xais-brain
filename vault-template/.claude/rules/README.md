# .claude/rules/

Règles avancées pour personnaliser le comportement de Claude Code dans ce vault.

## Comment ça marche

Crée un fichier `.md` par règle/domaine. Chaque fichier peut être importé depuis ton `CLAUDE.md` via :

```markdown
@import .claude/rules/[nom-du-fichier].md
```

## Exemples de règles à créer

- `voice.md` — ton de voix pour l'écriture de notes (formel, casual, bilingue, etc.)
- `naming.md` — conventions de nommage de fichiers et dossiers
- `workflow.md` — comment utiliser les slash commands en séquence
- `tags.md` — taxonomie de tags Obsidian
- `daily-template.md` — structure attendue d'une note journalière

## Pourquoi modulariser

Au lieu de tout entasser dans `CLAUDE.md`, tu sépares chaque domaine dans son propre fichier. Avantages :

- `CLAUDE.md` reste léger et toujours chargé
- Les règles spécialisées sont chargées **uniquement quand pertinent**
- Plus facile à maintenir, à versionner, à partager

## Pour démarrer

Ce dossier est vide. Crée ton premier fichier quand tu en ressens le besoin — pas avant.
