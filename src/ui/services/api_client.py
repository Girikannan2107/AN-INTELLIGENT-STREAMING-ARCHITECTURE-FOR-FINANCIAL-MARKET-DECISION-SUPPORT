import logging
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


class APIClient:
    """
    Handles communication with backend services.
    """

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def get_latest_prediction(self) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(f"{self.base_url}/latest", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("Failed to fetch latest prediction: %s", e)
            return None

    def query_rag(self, text: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.post(
                f"{self.base_url}/query",
                json={"text": text},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning("Failed to query RAG: %s", e)
            return None