from rag_service.rag_pipeline import (
    RAGPipeline,
    SimpleRetriever,
    Document,
)
from rag_service.openai_client import OpenAIClient

if __name__ == "__main__":

    docs = [
        Document(content="Apple stock surged after earnings."),
        Document(content="Tech rally boosted market sentiment."),
        Document(content="Federal Reserve policy impacted markets."),
    ]

    retriever = SimpleRetriever(docs)
    generator = OpenAIClient(model="gpt-4o-mini")

    pipeline = RAGPipeline(
        retriever=retriever,
        generator=generator,
    )

    response = pipeline.query("Why did Apple stock increase?")

    print("Answer:\n", response.answer)