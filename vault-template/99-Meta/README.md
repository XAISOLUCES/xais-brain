# 99-Meta — Piste d'audit du vault

Ce dossier trace l'hygiène et la fiabilité du vault.
Il n'est pas conçu pour être lu comme du contenu : c'est la "boîte noire"
du second brain.

## Rôle

Séparer clairement :

- Le **contenu** du vault (notes, projets, recherche) → `inbox/`, `daily/`, `projects/`, `research/`, `archive/`, `memory/`.
- La **méta-donnée** sur ce contenu (santé, sources vérifiées, historique de session) → `99-Meta/`.

Le préfixe `99-` garantit que le dossier apparaît en bas dans l'explorateur
de fichiers d'Obsidian, pour ne pas parasiter la navigation quotidienne.

## Fichiers

- `Audit.md` — dernier rapport du skill `/vault-audit` (orphelines, anémiques, peu liées, doublons, frontmatter incomplet, tags incohérents, wikilinks cassés, notes `to-verify` > 30j).
- `Fact-Check-Log.md` — log append-only des sources vérifiées (alimenté par `/clip` et `/file-intel`).
- `Session-Debriefs/` — rétrospectives de session courte (alimenté par `/tldr`).

## Ignorer dans le graphe Obsidian

Ces fichiers sont du bruit pour la graph view. Pour les exclure :

1. Obsidian → **Settings** → **Files & links** → **Excluded files**.
2. Ajouter `99-Meta/` dans la liste.

Les notes du dossier ne s'afficheront plus ni dans le graphe, ni dans les
suggestions de wikilinks, ni dans la recherche par défaut.

## Ne pas éditer à la main

`Fact-Check-Log.md` et `Audit.md` sont générés automatiquement par les skills.
Édite-les uniquement pour cocher des cases d'action (`[ ]` → `[x]`) pendant
une revue d'hygiène.
