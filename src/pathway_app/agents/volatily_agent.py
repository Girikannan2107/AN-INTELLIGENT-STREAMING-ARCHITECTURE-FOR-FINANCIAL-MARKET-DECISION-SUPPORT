import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


# =====================================================
# Configuration Layer (Immutable Strategy Parameters)
# =====================================================
@dataclass(frozen=True)
class VolatilityConfig:
    """
    Immutable configuration object for volatility thresholds.

    Design Decisions:
    -----------------
    - frozen=True ensures immutability → prevents accidental mutation
    - Separates configuration from business logic
    - Makes unit testing easier (inject custom configs)
    - Supports environment-based overrides

    This allows:
    - Strategy tuning without modifying core logic
    - Clean dependency injection
    """

    # Price boundaries
    low_price_threshold: float = 200.0
    high_price_threshold: float = 400.0

    # Volatility scores mapped to price ranges
    low_volatility: float = 0.3
    medium_volatility: float = 0.5
    high_volatility: float = 0.7


# =====================================================
# Volatility Agent (Business Logic Layer)
# =====================================================
class VolatilityAgent:
    """
    VolatilityAgent computes a deterministic volatility score
    from the given stock price.

    Architecture Principles:
    ------------------------
    - Single Responsibility: Only calculates volatility
    - Dependency Injection: Accepts external configuration
    - Encapsulation: Internal rule engine hidden from API
    - Deterministic Rule-Based System (replaceable with ML)

    Future Upgrade Path:
    --------------------
    - Replace rule engine with statistical volatility model
    - Integrate rolling window variance calculation
    - Connect to real-time streaming market engine
    """

    def __init__(self, config: VolatilityConfig | None = None) -> None:
        """
        Initializes agent with injected configuration.

        If no configuration is provided,
        a default immutable configuration is used.

        This pattern improves:
        - Testability
        - Flexibility
        - Strategy customization
        """
        self.config = config or VolatilityConfig()

    # =====================================================
    # Public API Method
    # =====================================================
    def calculate(self, price: float) -> float:
        """
        Computes normalized volatility score.

        Workflow:
        ---------
        1. Validate input
        2. Apply rule engine
        3. Log computation for observability

        Args:
            price (float): Current stock price

        Returns:
            float: Volatility score (0.0 - 1.0)

        Raises:
            ValueError: If price is invalid
        """

        # Defensive programming ensures system stability
        self._validate(price)

        # Delegating computation to internal rule engine
        volatility = self._compute_volatility(price)

        # Debug-level logging keeps production logs clean
        # while allowing deep inspection during development
        logger.debug(
            "Volatility calculated | Price=%.2f | Score=%.2f",
            price,
            volatility,
        )

        return volatility

    # =====================================================
    # Internal Rule Engine
    # =====================================================
    def _compute_volatility(self, price: float) -> float:
        """
        Applies threshold-based volatility logic.

        Rule Logic:
        ----------
        - Price < low threshold  → Low volatility
        - Price > high threshold → High volatility
        - Otherwise              → Medium volatility

        This function is intentionally private
        to protect internal business logic.
        """

        if price < self.config.low_price_threshold:
            return self.config.low_volatility

        if price > self.config.high_price_threshold:
            return self.config.high_volatility

        return self.config.medium_volatility

    # =====================================================
    # Validation Layer
    # =====================================================
    @staticmethod
    def _validate(price: float) -> None:
        """
        Validates input price before processing.

        Why Static?
        ----------
        - Does not depend on instance state
        - Clearly indicates utility behavior

        Raises:
            ValueError: If price is not positive
        """

        if price <= 0:
            raise ValueError("Price must be greater than zero")
