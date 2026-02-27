import json
import logging
import random
import time
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, List

from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable

from pathway_app.config import KAFKA_BOOTSTRAP

logger = logging.getLogger(__name__)


# ----------------------------------------
# Domain Models
# ----------------------------------------

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


@dataclass(frozen=True)
class NewsEvent:
    symbol: str
    title: str
    sentiment: Sentiment
    price: float
    timestamp: float


# ----------------------------------------
# Kafka Wrapper
# ----------------------------------------

class KafkaNewsProducer:
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
                logger.info("✅ Connected to Kafka (News Producer)")
                return producer
            except NoBrokersAvailable:
                logger.warning(
                    "Kafka unavailable (%s/%s). Retrying in %s sec...",
                    attempt + 1,
                    max_retries,
                    retry_delay,
                )
                time.sleep(retry_delay)

        raise ConnectionError("Unable to connect to Kafka")

    def send(self, topic: str, event: NewsEvent) -> None:
        self.producer.send(topic, asdict(event))
        logger.info("Sent news event: %s", event)

    def close(self) -> None:
        self.producer.close()


# ----------------------------------------
# Service Layer
# ----------------------------------------

class NewsProducerService:
    DEFAULT_HEADLINES: List[str] = [
        "Market crashes",
        "Stock surges",
        "Tech rally",
        "Economic slowdown",
    ]

    def __init__(
        self,
        producer: KafkaNewsProducer,
        topic: str = "news_topic",
        interval: int = 5,
        symbol: str = "AAPL",
    ) -> None:
        self.producer = producer
        self.topic = topic
        self.interval = interval
        self.symbol = symbol
        self._running = True

    def generate_news(self) -> NewsEvent:
        """
        Generate a simulated news event.
        """

        sentiment = random.choice(list(Sentiment))

        return NewsEvent(
            symbol=self.symbol,
            title=random.choice(self.DEFAULT_HEADLINES),
            sentiment=sentiment,
            price=round(random.uniform(250, 280), 2),
            timestamp=time.time(),
        )

    def run_once(self) -> None:
        """
        Single execution cycle (unit-test friendly).
        """

        event = self.generate_news()
        self.producer.send(self.topic, event)

    def start(self) -> None:
        """
        Continuous streaming loop.
        """

        logger.info("🚀 News Producer Service Started")

        try:
            while self._running:
                self.run_once()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("🛑 News Producer Stopped")

        finally:
            self.producer.close()

    def stop(self) -> None:
        self._running = False