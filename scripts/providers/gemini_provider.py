"""Provider Gemini via le SDK google-genai."""
from __future__ import annotations

import os

from ._prompts import build_summarization_prompt
from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Provider Gemini (Google AI Studio).

    Modèle par défaut : gemini-2.0-flash (gratuit, rapide).
    Override possible via la variable d'env GEMINI_MODEL.
    """

    DEFAULT_MODEL = "gemini-2.0-flash"

    def __init__(self, api_key: str) -> None:
        from google import genai

        self.client = genai.Client(api_key=api_key)
        self.model = os.getenv("GEMINI_MODEL", self.DEFAULT_MODEL)

    def summarize(self, content: str, source_filename: str) -> str:
        prompt = build_summarization_prompt(
            content=content, source_filename=source_filename
        )
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text or ""
