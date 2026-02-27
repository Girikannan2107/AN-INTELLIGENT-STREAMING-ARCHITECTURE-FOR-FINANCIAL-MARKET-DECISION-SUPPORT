from dataclasses import dataclass
from enum import Enum


class Recommendation(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class MarketData:
    symbol: str
    price: float
    timestamp: float


@dataclass(frozen=True)
class Prediction:
    symbol: str
    price: float
    recommendation: Recommendation
    confidence: float
    brokerage_cost: float
    timestamp: float