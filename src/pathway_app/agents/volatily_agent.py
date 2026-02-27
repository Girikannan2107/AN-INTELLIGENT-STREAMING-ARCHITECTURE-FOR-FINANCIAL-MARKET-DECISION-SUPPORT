import json
import logging
import time
from dataclasses import dataclass, asdict
from typing import Optional

import requests
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from pathway_app.config import (
    KAFKA_BOOTSTRAP,
    MARKET_TOPIC,
    ALPHA_VANTAGE_KEY,
    MARKET_FETCH_INTERVAL,
)

logger = logging.getLogger(__name__)


# ----------------------------------------
# Domain Model
# ----------------------------------------

@dataclass(frozen=True)
class MarketEvent:
    symbol: str
    price: float
    timestamp: float


# ----------------------------------------
# Alpha Vantage Client
# ----------------------------------------

class AlphaVantageClient:
    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str, symbol: str = "AAPL") -> None:
        self.api_key = api_key
        self.symbol = symbol

    def fetch_price(self) -> Optional[MarketEvent]:
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_KEY not configured")

        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": self.symbol,
            "apikey": self.api_key,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=10)
        data = response.json()

        quote = data.get("Global Quote")

        if not quote or "05. price" not in quote:
            logger.warning("Invalid API response: %s", data)
            return None

        return MarketEvent(
            symbol=self.symbol,
            price=float(quote["05. price"]),
            timestamp=time.time(),
        )


# ----------------------------------------
# Kafka Producer Wrapper
# ----------------------------------------

class KafkaMarketProducer:
    def __init__(self, bootstrap_servers: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.producer = self._connect()

    def _connect(self) -> KafkaProducer:
        retry_delay = 5
        max_retries = 5

        for attempt in range(max_retries):
            try:
                producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                )
                logger.info("✅ Connected to Kafka")
                return producer
            except NoBrokersAvailable:
                logger.warning(
                    "Kafka unavailable (attempt %s/%s). Retrying in %s seconds...",
                    attempt + 1,
                    max_retries,
                    retry_delay,
                )
                time.sleep(retry_delay)

        raise ConnectionError("Unable to connect to Kafka after retries")

    def send(self, topic: str, event: MarketEvent) -> None:
        self.producer.send(topic, asdict(event))
        logger.info("Sent market event: %s", event)

    def close(self) -> None:
        self.producer.close()


# ----------------------------------------
# Main Service
# ----------------------------------------

class MarketProducerService:
    """
    Coordinates fetching market data and sending to Kafka.
    """

    def __init__(
        self,
        client: AlphaVantageClient,
        producer: KafkaMarketProducer,
        topic: str,
        interval: int,
    ) -> None:
        self.client = client
        self.producer = producer
        self.topic = topic
        self.interval = interval
        self._running = True

    def run_once(self) -> None:
        """
        Executes a single fetch-send cycle (testable).
        """

        event = self.client.fetch_price()

        if event:
            self.producer.send(self.topic, event)

    def start(self) -> None:
        """
        Starts continuous market streaming.
        """

        logger.info("🚀 Market Producer Service Started")

        try:
            while self._running:
                self.run_once()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("🛑 Market Producer Stopped")

        finally:
            self.producer.close()

    def stop(self) -> None:
        self._running = False
