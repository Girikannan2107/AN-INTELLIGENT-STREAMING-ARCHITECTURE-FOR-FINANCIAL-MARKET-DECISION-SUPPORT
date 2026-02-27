import logging
from dataclasses import asdict

import pathway as pw

from pathway_app.config import STREAM_FILE
from pathway_app.agents.news_agent import NewsAgent
from pathway_app.models import MarketData, Prediction

logger = logging.getLogger(__name__)


# ----------------------------------------
# Schema Definition
# ----------------------------------------

class StockSchema(pw.Schema):
    symbol: str
    title: str
    price: float
    timestamp: float


# ----------------------------------------
# Streaming Service
# ----------------------------------------

class StreamingService:
    """
    Handles Pathway streaming pipeline.
    Responsible only for orchestration.
    """

    def __init__(self, agent: NewsAgent) -> None:
        self.agent = agent

    # -------------------------------------

    def _transform(self, symbol: str, title: str, price: float, timestamp: float) -> dict:
        """
        Converts raw stream input into Prediction output.
        This method is isolated for testability.
        """

        market_data = MarketData(
            symbol=symbol,
            price=price,
            timestamp=timestamp,
        )

        prediction: Prediction = self.agent.predict(market_data)

        logger.info("Prediction Generated: %s", prediction)

        return asdict(prediction)

    # -------------------------------------

    def start(self) -> None:
        """
        Starts the Pathway streaming pipeline.
        """

        logger.info("📡 Pathway Streaming Started")

        table = pw.io.jsonlines.read(
            STREAM_FILE,
            schema=StockSchema,
            mode="streaming",
        )

        result = table.select(
            prediction=pw.apply(
                self._transform,
                pw.this.symbol,
                pw.this.title,
                pw.this.price,
                pw.this.timestamp,
            )
        )

        pw.io.print(result)
        pw.run()