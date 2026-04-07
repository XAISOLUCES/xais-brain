"""Prompts partagés entre tous les providers LLM."""
from __future__ import annotations

from datetime import date


def build_summarization_prompt(content: str, source_filename: str) -> str:
    """Construit le prompt complet pour résumer un fichier.

    Le prompt instruit le LLM de générer un Markdown structuré avec
    frontmatter Obsidian, TL;DR, points clés, concepts, et actions.
    """
    today = date.today().isoformat()

    return f"""Tu es un assistant de prise de notes pour un vault Obsidian.
Tu reçois le contenu brut d'un fichier (PDF, doc, slides, etc.) et tu génères
une note Markdown synthétique prête à intégrer un second cerveau.

Format de sortie OBLIGATOIRE :

---
source: {source_filename}
date: {today}
tags: [tag1, tag2, tag3]
type: résumé
---

# (Titre court inspiré du contenu)

## TL;DR

(2-3 phrases qui résument l'essentiel)

## Points clés

- ...
- ...
- ...

## Concepts importants

- **(concept)** : (explication courte)

## À retenir / actions

- [ ] ...

## Notes brutes

(Sections détaillées si pertinent — sous-titres ## ou ###)

Règles :
- Toujours en français (sauf si la source est dans une autre langue, alors traduire)
- Tags pertinents et spécifiques (3-7 max), en kebab-case, sans dièse
- Pas de remplissage ni de blabla générique
- Si le contenu est court ou trivial, fais une note courte
- Si le contenu est dense, structure-le avec des sections claires
- Donne directement le Markdown — n'inclus PAS de bloc ```markdown autour
- Le frontmatter (---) doit être la PREMIÈRE ligne de ta réponse

Contenu source ({source_filename}) :

{content}
"""
