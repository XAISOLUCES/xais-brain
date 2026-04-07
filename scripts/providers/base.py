"""Interface abstraite pour les providers LLM."""
from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface commune pour tous les providers LLM."""

    @abstractmethod
    def __init__(self, api_key: str) -> None:
        """Initialise le client avec une clé API."""

    @abstractmethod
    def summarize(self, content: str, source_filename: str) -> str:
        """Génère un résumé Markdown structuré du contenu fourni.

        Args:
            content: Texte brut extrait du fichier source.
            source_filename: Nom du fichier source (utilisé dans le prompt
                             et pour le frontmatter Obsidian).

        Returns:
            Markdown brut contenant frontmatter, résumé, sections et tags.
            Le format de sortie est défini par providers/_prompts.py.
        """
