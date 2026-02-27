import json
import logging
import random
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from pathway_app.config import STREAM_FILE, STREAM_INTERVAL

# -----------------------------------------
# Logging Configuration
# -----------------------------------------

logger = logging.getLogger(__name__)


# -----------------------------------------
# Domain Model
# -----------------------------------------

@dataclass(frozen=True)
class MarketEvent:
    symbol: str
    title: str
    price: float
    timestamp: float


# -----------------------------------------
# Live Generator
# -----------------------------------------

class LiveGenerator:
    """
    Generates simulated live stock market events
    and appends them to a streaming file.
    """

    DEFAULT_SYMBOLS: List[str] = ["AAPL", "TSLA", "GOOG", "MSFT", "AMZN"]

    def __init__(
        self,
        stream_file: str = STREAM_FILE,
        interval: int = STREAM_INTERVAL,
        symbols: List[str] | None = None,
    ) -> None:
        self.stream_path = Path(stream_file)
        self.interval = interval
        self.symbols = symbols or self.DEFAULT_SYMBOLS

    # -------------------------------------

    def start(self) -> None:
        """
        Starts continuous event generation.
        """

        self._initialize_stream()

        logger.info("🚀 Live Producer Started")

        try:
            while True:
                event = self.generate_once()
                self._append_to_stream(event)
                logger.info("Generated event: %s", event)
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("🛑 Live Producer Stopped")

    # -------------------------------------

    def generate_once(self) -> MarketEvent:
        """
        Generates a single market event.
        Useful for unit testing.
        """

        return MarketEvent(
            symbol=random.choice(self.symbols),
            title="Tech rally",
            price=round(random.uniform(100, 500), 2),
            timestamp=round(time.time(), 2),
        )

    # -------------------------------------

    def _initialize_stream(self) -> None:
        """
        Clears previous stream file.
        """

        if self.stream_path.exists():
            self.stream_path.unlink()

    # -------------------------------------

    def _append_to_stream(self, event: MarketEvent) -> None:
        """
        Appends event to JSON lines stream file.
        """

        with self.stream_path.open("a") as file:
            file.write(json.dumps(asdict(event)) + "\n")