import logging
from dataclasses import dataclass
from typing import List

from rag_service.embedding_service import EmbeddingService
from rag_service.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


# -----------------------------------------
# Domain Models
# -----------------------------------------

@dataclass(frozen=True)
class Document:
    content: str


@dataclass(frozen=True)
class RAGResponse:
    query: str
    context: List[str]
    answer: str


# -----------------------------------------
# Retriever
# -----------------------------------------

class SimpleRetriever:
    """
    In-memory retriever (replace with vector DB in production).
    """

    def __init__(self, documents: List[Document]) -> None:
        self.documents = documents

    def retrieve(self, query: str, top_k: int = 2) -> List[Document]:
        # Simple keyword match scoring
        scored = []

        for doc in self.documents:
            score = sum(word in doc.content.lower() for word in query.lower().split())
            scored.append((score, doc))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [doc for _, doc in scored[:top_k]]


# -----------------------------------------
# RAG Pipeline
# -----------------------------------------

class RAGPipeline:
    """
    Production-style RAG pipeline.
    """

    def __init__(
        self,
        retriever: SimpleRetriever,
        generator: OpenAIClient,
    ) -> None:
        self.retriever = retriever
        self.generator = generator

    def query(self, text: str) -> RAGResponse:
        self._validate(text)

        documents = self.retriever.retrieve(text)
        context = [doc.content for doc in documents]

        answer = self.generator.generate(text, context)

        logger.info("RAG query completed")

        return RAGResponse(
            query=text,
            context=context,
            answer=answer,
        )

    @staticmethod
    def _validate(text: str) -> None:
        if not text or not text.strip():
            raise ValueError("Query cannot be empty")