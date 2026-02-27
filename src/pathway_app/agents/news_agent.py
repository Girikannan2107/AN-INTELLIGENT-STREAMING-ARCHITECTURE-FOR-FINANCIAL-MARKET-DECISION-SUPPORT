"""
Comprehensive tests for NewsAgent with patterns demonstration.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from pathway_app.news_agent import (
    NewsAgent,
    ThresholdStrategy,
    VolatilityAdjustedStrategy,
    ValidationError,
    Result,
    TradingStrategyFactory,
    PriceValidator,
    SymbolValidator,
)
from pathway_app.models import MarketData, Prediction, Recommendation


class TestThresholdStrategy:
    """Unit tests for ThresholdStrategy."""
    
    @pytest.fixture
    def strategy(self):
        return ThresholdStrategy(
            buy_threshold=250.0,
            sell_threshold=400.0,
            buy_confidence=0.82,
            sell_confidence=0.88,
            hold_confidence=0.75,
        )
    
    def test_buy_signal(self, strategy):
        data = Mock(spec=MarketData, price=200.0)
        signal = strategy.generate_signal(200.0, data)
        
        assert signal.recommendation == Recommendation.BUY
        assert signal.confidence == 0.82
        assert "threshold" in signal.metadata
    
    def test_sell_signal(self, strategy):
        data = Mock(spec=MarketData, price=450.0)
        signal = strategy.generate_signal(450.0, data)
        
        assert signal.recommendation == Recommendation.SELL
        assert signal.confidence == 0.88
    
    def test_hold_signal(self, strategy):
        data = Mock(spec=MarketData, price=300.0)
        signal = strategy.generate_signal(300.0, data)
        
        assert signal.recommendation == Recommendation.HOLD
        assert 0.75 <= signal.confidence <= 0.95
    
    def test_invalid_threshold_configuration(self):
        with pytest.raises(Exception):  # ConfigurationError
            ThresholdStrategy(
                buy_threshold=500.0,  # Invalid: buy > sell
                sell_threshold=400.0,
                buy_confidence=0.82,
                sell_confidence=0.88,
                hold_confidence=0.75,
            )


class TestNewsAgent:
    """Integration tests for NewsAgent."""
    
    @pytest.fixture
    def valid_market_data(self):
        return MarketData(
            symbol="AAPL",
            price=150.0,
            timestamp=datetime.now(timezone.utc),
        )
    
    @pytest.fixture
    def agent(self):
        return NewsAgent()
    
    def test_successful_prediction(self, agent, valid_market_data):
        result = agent.predict(valid_market_data)
        
        assert result.is_success
        prediction = result.value
        assert isinstance(prediction, Prediction)
        assert prediction.symbol == "AAPL"
        assert prediction.price == 150.0
        assert isinstance(prediction.confidence, float)
    
    def test_validation_failure_empty_symbol(self, agent):
        invalid_data = MarketData(
            symbol="",
            price=150.0,
            timestamp=datetime.now(timezone.utc),
        )
        
        result = agent.predict(invalid_data)
        
        assert result.is_failure
        assert isinstance(result.error, ValidationError)
        assert result.error.field == "symbol"
    
    def test_validation_failure_negative_price(self, agent):
        invalid_data = MarketData(
            symbol="AAPL",
            price=-10.0,
            timestamp=datetime.now(timezone.utc),
        )
        
        result = agent.predict(invalid_data)
        
        assert result.is_failure
        assert result.error.field == "price"
    
    def test_batch_processing(self, agent, valid_market_data):
        data_points = [valid_market_data, valid_market_data]
        results = agent.predict_batch(data_points)
        
        assert len(results) == 2
        assert all(r.is_success for r in results)
    
    def test_dependency_injection(self):
        mock_strategy = Mock()
        mock_strategy.generate_signal.return_value = Mock(
            recommendation=Recommendation.BUY,
            confidence=0.95,
            signal_type=Mock(name="STRONG_BUY"),
            metadata={},
        )
        
        agent = NewsAgent(strategy=mock_strategy)
        result = agent.predict(
            MarketData(
                symbol="TEST",
                price=100.0,
                timestamp=datetime.now(timezone.utc),
            )
        )
        
        assert result.is_success
        mock_strategy.generate_signal.assert_called_once()


class TestResultPattern:
    """Tests for Result monad."""
    
    def test_success_result(self):
        result = Result.success(42)
        assert result.is_success
        assert not result.is_failure
        assert result.value == 42
    
    def test_failure_result(self):
        error = ValueError("test error")
        result = Result.failure(error)
        
        assert result.is_failure
        assert not result.is_success
        assert result.error == error
    
    def test_result_map(self):
        result = Result.success(5).map(lambda x: x * 2)
        assert result.value == 10
    
    def test_result_map_on_failure(self):
        result = Result.failure[int, ValueError](ValueError("error"))
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_failure


class TestVolatilityAdjustedStrategy:
    """Tests for volatility decorator."""
    
    def test_volatility_adjustment(self):
        base_strategy = ThresholdStrategy(
            buy_threshold=250.0,
            sell_threshold=400.0,
            buy_confidence=0.82,
            sell_confidence=0.88,
            hold_confidence=0.75,
        )
        vol_strategy = VolatilityAdjustedStrategy(base_strategy)
        
        data = Mock(spec=MarketData)
        
        # Feed multiple prices to establish volatility
        for price in [300.0, 310.0, 290.0, 305.0, 295.0]:
            signal = vol_strategy.generate_signal(price, data)
        
        # Volatility should now affect confidence
        assert "volatility" in signal.metadata
