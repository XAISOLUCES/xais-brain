"""Provider Anthropic Claude via le SDK anthropic."""
from __future__ import annotations

import os

from ._prompts import build_summarization_prompt
from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    """Provider Anthropic Claude.

    Modèle par défaut : claude-haiku-4-5 (rapide et économique).
    Override possible via la variable d'env ANTHROPIC_MODEL.
    """

    DEFAULT_MODEL = "claude-haiku-4-5-20251001"
    MAX_TOKENS = 4096

    def __init__(self, api_key: str) -> None:
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = os.getenv("ANTHROPIC_MODEL", self.DEFAULT_MODEL)

    def summarize(self, content: str, source_filename: str) -> str:
        prompt = build_summarization_prompt(
            content=content, source_filename=source_filename
        )
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        # La réponse Claude est une liste de ContentBlock — on récupère le texte
        text_parts = [
            block.text for block in message.content if hasattr(block, "text")
        ]
        return "\n".join(text_parts)
