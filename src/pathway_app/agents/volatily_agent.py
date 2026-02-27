import logging
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VolatilityConfig:
    """
    Configuration for volatility thresholds.
    """
    low_price_threshold: float = 200.0
    high_price_threshold: float = 400.0
    low_volatility: float = 0.3
    medium_volatility: float = 0.5
    high_volatility: float = 0.7


class VolatilityAgent:
    """
    Calculates market volatility score based on price thresholds.
    Designed for extensibility and clean architecture compliance.
    """

    def __init__(self, config: VolatilityConfig | None = None) -> None:
        self.config = config or VolatilityConfig()

    def calculate(self, price: float) -> float:
        """
        Compute volatility score from price.

        Args:
            price (float): Current stock price

        Returns:
            float: Volatility score (0.0 - 1.0)

        Raises:
            ValueError: If price is invalid
        """

        self._validate(price)

        volatility = self._compute_volatility(price)

        logger.debug("Calculated volatility: price=%s volatility=%s", price, volatility)

        return volatility

    def _compute_volatility(self, price: float) -> float:
        """
        Internal rule engine for volatility calculation.
        """

        if price < self.config.low_price_threshold:
            return self.config.low_volatility

        if price > self.config.high_price_threshold:
            return self.config.high_volatility

        return self.config.medium_volatility

    @staticmethod
    def _validate(price: float) -> None:
        """
        Validates input price.
        """

        if price <= 0:
            raise ValueError("Price must be greater than zero")