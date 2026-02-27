import logging
import os
from typing import List

from openai import OpenAI

logger = logging.getLogger(__name__)


class OpenAIClient:
    """
    Wrapper around OpenAI GPT model.
    Clean abstraction layer for generation.
    """

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, query: str, context: List[str]) -> str:
        """
        Generate response using GPT model.
        """

        prompt = self._build_prompt(query, context)

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content
        logger.info("OpenAI response generated")

        return answer

    @staticmethod
    def _build_prompt(query: str, context: List[str]) -> str:
        context_text = "\n".join(context)

        return f"""
Use the following context to answer the question.

Context:
{context_text}

Question:
{query}

Answer:
"""