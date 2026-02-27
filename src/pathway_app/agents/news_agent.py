import logging
from pathway_app.config import BROKERAGE_RATE
from pathway_app.models import MarketData, Prediction, Recommendation

logger = logging.getLogger(__name__)


class NewsAgent:
    """
    NewsAgent applies trading rules to market data
    and produces structured Prediction output.
    """

    BUY_THRESHOLD: float = 250.0
    SELL_THRESHOLD: float = 400.0

    def predict(self, data: MarketData) -> Prediction:
        """
        Generates trading recommendation from market data.

        Args:
            data (MarketData): Incoming market information

        Returns:
            Prediction: Structured trading prediction
        """

        self._validate(data)

        recommendation, confidence = self._generate_signal(data.price)

        brokerage_cost = round(data.price * BROKERAGE_RATE, 2)

        prediction = Prediction(
            symbol=data.symbol,
            price=data.price,
            recommendation=recommendation,
            confidence=confidence,
            brokerage_cost=brokerage_cost,
            timestamp=data.timestamp,
        )

        logger.info("Generated prediction: %s", prediction)

        return prediction

    def _generate_signal(self, price: float) -> tuple[Recommendation, float]:
        """
        Determines trading signal based on price thresholds.
        """

        if price < self.BUY_THRESHOLD:
            return Recommendation.BUY, 0.82
        elif price > self.SELL_THRESHOLD:
            return Recommendation.SELL, 0.88
        return Recommendation.HOLD, 0.75

    @staticmethod
    def _validate(data: MarketData) -> None:
        """
        Validates incoming market data.
        """

        if data.price <= 0:
            raise ValueError("Price must be positive")

        if not data.symbol:
            raise ValueError("Symbol cannot be empty")