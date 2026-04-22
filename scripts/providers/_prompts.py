"""Prompts partagés entre tous les providers LLM."""
from __future__ import annotations

from datetime import date
from pathlib import Path


# Extensions supportees par file-intel (doit matcher EXTRACTORS dans file_intel.py)
_EXT_TO_SOURCE = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "txt",
    ".md": "md",
}


def source_type_from_filename(source_filename: str) -> str:
    """Retourne la categorie de source (pdf|docx|txt|md) pour le frontmatter.

    Fallback sur 'import' si l'extension n'est pas reconnue.
    """
    ext = Path(source_filename).suffix.lower()
    return _EXT_TO_SOURCE.get(ext, "import")


def build_summarization_prompt(content: str, source_filename: str) -> str:
    """Construit le prompt complet pour résumer un fichier.

    Le prompt instruit le LLM de générer un Markdown structuré avec
    frontmatter Obsidian enrichi (piste 6B — god-mode patterns),
    TL;DR, points clés, concepts, et actions.
    """
    today = date.today().isoformat()
    source_type = source_type_from_filename(source_filename)

    return f"""Tu es un assistant de prise de notes pour un vault Obsidian.
Tu reçois le contenu brut d'un fichier (PDF, doc, slides, etc.) et tu génères
une note Markdown synthétique prête à intégrer un second cerveau.

Format de sortie OBLIGATOIRE :

---
source: {source_type}
source_file: {source_filename}
source_knowledge: internal
verification_date: {today}
statut: to-verify
importance: medium
date: {today}
tags: [tag1, tag2, tag3]
liens_forts: ["[[Concept1]]", "[[Concept2]]"]
liens_opposition: ["[[ContreIdee]]"]
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
- Inclus **au moins 3 wikilinks sortants** `[[Concept]]` vers des pages
  pertinentes du vault (concepts, personnes, projets, théories évoquées).
  Chaque wikilink doit être justifié par la phrase qui l'entoure — pas de
  lien décoratif. Préfère les noms de concepts en PascalCase ou Title Case
  (`[[AlignmentProblem]]`, `[[Karl Popper]]`). Si vraiment aucun concept
  ne se prête au lien, tu peux en mettre moins — mais c'est rare.
- Dans le frontmatter, `liens_forts` liste 2-5 wikilinks vers les concepts
  centraux traités par la note. `liens_opposition` est optionnel : liste
  les concepts avec lesquels la note est en tension ou qu'elle contredit.
  Laisse ces champs vides (`liens_forts: []`) si rien de pertinent.
- Donne directement le Markdown — n'inclus PAS de bloc ```markdown autour
- Le frontmatter (---) doit être la PREMIÈRE ligne de ta réponse
- Ne modifie PAS les valeurs de `source`, `source_file`, `source_knowledge`,
  `verification_date`, `statut`, `importance` dans le frontmatter : recopie-les
  telles quelles. Seuls `tags`, `liens_forts`, `liens_opposition` et le corps
  de la note sont à adapter.

Contenu source ({source_filename}) :

{content}
"""
