"""Provider OpenAI via le SDK openai."""
from __future__ import annotations

import os

from ._prompts import build_summarization_prompt
from .base import LLMProvider


class OpenAIProvider(LLMProvider):
    """Provider OpenAI.

    Modèle par défaut : gpt-4o-mini (rapide et économique).
    Override possible via la variable d'env OPENAI_MODEL.
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", self.DEFAULT_MODEL)

    def summarize(self, content: str, source_filename: str) -> str:
        prompt = build_summarization_prompt(
            content=content, source_filename=source_filename
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
