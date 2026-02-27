import logging
from pathway_app.config import BROKERAGE_RATE
from pathway_app.models import MarketData, Prediction, Recommendation

logger = logging.getLogger(__name__)


class NewsAgent:
    """
    NewsAgent is responsible for translating raw market data
    into structured trading predictions.

    Design Principles:
    ------------------
    - Single Responsibility: Handles only prediction logic
    - Encapsulation: Internal signal logic is private
    - Config-Driven: Brokerage rate is injected via config
    - Deterministic Logic: Rule-based threshold system

    This agent can later be replaced with:
    - ML-based model
    - Reinforcement learning policy
    - External AI microservice
    """

    # =====================================================
    # Strategy Configuration (Class-Level Constants)
    # =====================================================
    # These thresholds define trading decision boundaries.
    # Keeping them as class attributes:
    # - Makes tuning easy
    # - Avoids magic numbers inside logic
    # - Supports subclass override if needed
    BUY_THRESHOLD: float = 250.0
    SELL_THRESHOLD: float = 400.0

    # =====================================================
    # Public API Method
    # =====================================================
    def predict(self, data: MarketData) -> Prediction:
        """
        Generates a structured trading prediction.

        Workflow:
        ---------
        1. Validate input market data
        2. Generate trading signal
        3. Compute brokerage cost
        4. Construct Prediction object

        Args:
            data (MarketData): Validated market snapshot

        Returns:
            Prediction: Fully structured output model

        Raises:
            ValueError: If market data fails validation
        """

        # Defensive validation ensures data integrity
        self._validate(data)

        # Encapsulated signal generation logic
        recommendation, confidence = self._generate_signal(data.price)

        # Brokerage cost calculation is externalized via config
        # This makes the agent environment-agnostic
        brokerage_cost = round(data.price * BROKERAGE_RATE, 2)

        # Create immutable structured output
        prediction = Prediction(
            symbol=data.symbol,
            price=data.price,
            recommendation=recommendation,
            confidence=confidence,
            brokerage_cost=brokerage_cost,
            timestamp=data.timestamp,
        )

        # Structured logging for monitoring and observability
        logger.info(
            "Prediction generated | Symbol=%s | Price=%.2f | Action=%s",
            prediction.symbol,
            prediction.price,
            prediction.recommendation,
        )

        return prediction

    # =====================================================
    # Internal Strategy Logic
    # =====================================================
    def _generate_signal(self, price: float) -> tuple[Recommendation, float]:
        """
        Applies deterministic rule-based strategy.

        Strategy Logic:
        --------------
        - Below BUY_THRESHOLD  -> BUY
        - Above SELL_THRESHOLD -> SELL
        - Otherwise            -> HOLD

        Returns:
            tuple:
                Recommendation enum
                Confidence score (0.0 - 1.0)

        Note:
            Confidence values are static placeholders.
            In ML systems, this would represent model probability.
        """

        if price < self.BUY_THRESHOLD:
            return Recommendation.BUY, 0.82

        if price > self.SELL_THRESHOLD:
            return Recommendation.SELL, 0.88

        return Recommendation.HOLD, 0.75

    # =====================================================
    # Input Validation Layer
    # =====================================================
    @staticmethod
    def _validate(data: MarketData) -> None:
        """
        Validates incoming market data before processing.

        Validation Rules:
        -----------------
        - Price must be positive
        - Symbol must not be empty

        Raises:
            ValueError: If validation fails

        Why Static?
        -----------
        Validation does not depend on instance state,
        so it is marked static for clarity and intent.
        """

        if data.price <= 0:
            raise ValueError("Price must be positive")

        if not data.symbol:
            raise ValueError("Symbol cannot be empty")
