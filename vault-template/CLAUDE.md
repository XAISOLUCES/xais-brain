# Mon Second Cerveau

> Vault Obsidian piloté par Claude Code.
> Lance `/vault-setup` pour personnaliser ce fichier (rôle, projets, objectifs).

## Qui je suis

[À remplir via `/vault-setup` — Claude t'interviewera et complétera cette section automatiquement.]

## Structure du vault

```
inbox/              ← Nouveaux fichiers non triés. Claude les sortira plus tard.
daily/              ← Notes journalières (YYYY-MM-DD.md)
projects/           ← Projets actifs et briefs
research/           ← Notes de recherche, synthèses, idées sauvegardées
archive/            ← Travail terminé. Jamais supprimé, juste archivé.
memory/             ← Mémoire long terme (voir MEMORY.md pour l'index)
vault-config.json   ← Source de vérité structurée (nom, provider LLM, mapping dossiers)
```

## Règles de chargement de contexte

**En début de journée**
→ Lire `daily/[date du jour].md` s'il existe
→ Vérifier `inbox/` pour les fichiers non traités

**En travaillant sur un projet**
→ Lire `projects/[nom]/` avant de démarrer

**Avant d'écrire quelque chose**
→ Lire les notes récentes pour calibrer le ton et le contexte
→ Consulter `MEMORY.md` pour les références mémoire pertinentes

## Comment maintenir ce vault

- Nouveaux fichiers de l'extérieur → `inbox/` d'abord, tri ensuite
- Notes journalières → `daily/YYYY-MM-DD.md`
- Travail terminé → `archive/` (jamais supprimé)
- Mets ce fichier à jour quand tes conventions changent

## Slash commands disponibles

- `/vault-setup`  — Personnalise ce vault selon ton rôle
- `/daily`        — Démarre la journée avec le contexte du vault
- `/tldr`         — Sauvegarde un résumé de cette session dans le vault
- `/file-intel`   — Traite n'importe quel dossier de fichiers via LLM, génère des résumés Markdown
- `/inbox-zero`   — Trie `inbox/` dans les bons dossiers (projects, research, archive…)
- `/memory-add`   — Ajoute une mémoire long terme et met à jour `MEMORY.md`
- `/humanise`     — Nettoie un texte AI-ifié pour restaurer une voix naturelle FR
- `/import-vault` — Adopte un vault Obsidian existant sans casser sa structure

## Règles avancées

Pour des règles plus poussées (ton de voix, conventions de nommage, workflow custom), voir `.claude/rules/`.

Tu peux les importer dans ce fichier via :

```
@import .claude/rules/[nom-du-fichier].md
```
