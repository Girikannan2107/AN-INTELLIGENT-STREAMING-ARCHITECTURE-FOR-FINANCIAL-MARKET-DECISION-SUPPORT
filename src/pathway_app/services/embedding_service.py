import logging
from dataclasses import dataclass
from typing import List

import hashlib

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EmbeddingResult:
    text: str
    vector: List[float]


class EmbeddingService:
    """
    Responsible for generating embeddings.
    Designed for clean architecture and easy provider swap.
    """

    def embed(self, text: str) -> EmbeddingResult:
        """
        Generate deterministic pseudo-embedding vector.

        Args:
            text (str): Input text

        Returns:
            EmbeddingResult
        """

        self._validate(text)

        vector = self._generate_embedding(text)

        logger.info("Generated embedding for text length=%s", len(text))

        return EmbeddingResult(text=text, vector=vector)

    @staticmethod
    def _generate_embedding(text: str) -> List[float]:
        """
        Simple deterministic hash-based embedding (replace with real model).
        """

        hash_digest = hashlib.sha256(text.encode()).hexdigest()

        # Convert hash to numeric vector
        vector = [
            int(hash_digest[i:i + 4], 16) / 65535
            for i in range(0, 64, 4)
        ]

        return vector

    @staticmethod
    def _validate(text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")