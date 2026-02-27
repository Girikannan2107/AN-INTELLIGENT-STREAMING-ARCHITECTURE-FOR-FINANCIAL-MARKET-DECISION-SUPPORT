import logging
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from rag_service.embedding_service import EmbeddingService, EmbeddingResult

# ---------------------------------------
# Logging Setup
# ---------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("EmbeddingAPI")

# ---------------------------------------
# FastAPI App
# ---------------------------------------

app = FastAPI(
    title="Embedding Service",
    description="High-performance embedding microservice",
    version="1.0.0",
)

embedding_service = EmbeddingService()


# ---------------------------------------
# Request / Response Models
# ---------------------------------------

class EmbeddingRequest(BaseModel):
    text: str


class EmbeddingResponse(BaseModel):
    text: str
    vector: List[float]


# ---------------------------------------
# Routes
# ---------------------------------------

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/embed", response_model=EmbeddingResponse)
def embed(request: EmbeddingRequest) -> EmbeddingResponse:
    """
    Generate embedding vector for given text.
    """

    try:
        result: EmbeddingResult = embedding_service.embed(request.text)
        return EmbeddingResponse(text=result.text, vector=result.vector)

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Embedding error")
        raise HTTPException(status_code=500, detail="Internal server error")