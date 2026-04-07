"""Providers LLM disponibles pour file-intel.

Le provider à utiliser est choisi via la variable d'environnement LLM_PROVIDER.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import LLMProvider


def get_provider(name: str | None = None) -> "LLMProvider":
    """Récupère le provider LLM configuré.

    Args:
        name: Nom explicite du provider (gemini, claude, openai).
              Si None, lit LLM_PROVIDER depuis l'environnement (défaut: gemini).

    Returns:
        Instance d'un LLMProvider initialisé avec sa clé API.

    Raises:
        ValueError: Si le nom de provider est inconnu.
        RuntimeError: Si la clé API correspondante manque dans l'environnement.
    """
    name = (name or os.getenv("LLM_PROVIDER", "gemini")).lower()

    if name == "gemini":
        from .gemini_provider import GeminiProvider

        key = os.getenv("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("GOOGLE_API_KEY manquante dans .env")
        return GeminiProvider(api_key=key)

    if name == "claude":
        from .claude_provider import ClaudeProvider

        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY manquante dans .env")
        return ClaudeProvider(api_key=key)

    if name == "openai":
        from .openai_provider import OpenAIProvider

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY manquante dans .env")
        return OpenAIProvider(api_key=key)

    raise ValueError(
        f"Provider inconnu : {name}. Choix possibles : gemini, claude, openai"
    )
