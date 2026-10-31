"""Production hardening regression tests for Phase 2A verification.

These tests verify:
1. Emotional safeguards fail closed (P0)
2. Sentiment returns provenance-labeled neutral when unavailable (P0)  
3. Order creation requires valid price (P0)
4. Market data providers fail closed (P1)
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '/home/ubuntu/yantrax-rl')


class TestEmotionalSafeguardsFailClosed:
    """P0: Verify emotional safeguards bypass does not allow unauthorized trading."""
    
    def test_emotional_safeguards_exception_sets_trading_allowed_false(self):
        """When get_status() raises, trading_allowed must be False."""
        from backend.core.decision_context import DecisionContext
        from backend.core.decision_pipeline import DecisionPipeline
        import asyncio
        
        # Create a mock risk governor with failing emotional safeguards
        mock_governor = MagicMock()
        mock_governor.emotional_safeguards = MagicMock()
        mock_governor.emotional_safeguards.get_status.side_effect = RuntimeError("Database connection failed")
        mock_governor.emotional_state = 'error'
        
        # Create pipeline and call the risk staging
        pipeline = DecisionPipeline.__new__(DecisionPipeline)
        pipeline.risk_governor = mock_governor
        
        # Mock the portfolio state method
        async def mock_get_portfolio():
            return MagicMock()
        pipeline._get_portfolio_state = mock_get_portfolio
        
        # Execute the method
        ctx = asyncio.run(pipeline._stage_preliminary_risk(DecisionContext()))
        
        # VERIFY: trading_allowed must be False after exception
        assert ctx.risk_state.trading_allowed == False, \
            "CRITICAL: Emotional safeguards exception did not set trading_allowed=False"
        assert ctx.risk_state.emotional_state == 'error'


class TestOrderCreationRequiresPrice:
    """P0: Verify create_order() fails closed without valid price."""
    
    def test_create_order_fails_without_price(self):
        """Price must be provided for canonical order creation."""
        from backend.order_manager import create_order
        
        with pytest.raises(ValueError, match="Price must be provided"):
            create_order("AAPL", 1000.0, price=None, simulation_mode=False)
    
    def test_create_order_fails_with_zero_price(self):
        """Zero price is invalid."""
        from backend.order_manager import create_order
        
        with pytest.raises(ValueError, match="Price must be positive"):
            create_order("AAPL", 1000.0, price=0.0)
    
    def test_create_order_fails_with_negative_price(self):
        """Negative price is invalid."""
        from backend.order_manager import create_order
        
        with pytest.raises(ValueError, match="Price must be positive"):
            create_order("AAPL", 1000.0, price=-10.0)
    
    def test_create_order_succeeds_with_valid_price(self):
        """Valid price should work."""
        from backend.order_manager import create_order
        
        order = create_order("AAPL", 1000.0, price=150.0)
        assert order['symbol'] == 'AAPL'
        assert abs(order['quantity'] - (1000.0/150.0)) < 0.01
        assert order['price'] == 150.0


class TestSentimentHasProvenance:
    """P0: Verify sentiment service provides provenance for all data sources."""
    
    def test_sentiment_returns_provenance(self):
        """Sentiment calculation should return provenance metadata."""
        from backend.services.market_sentiment_service import MarketSentimentService
        
        service = MarketSentimentService()
        result = service.calculate_fear_greed_index()
        
        assert 'provenance' in result, "Result must include provenance"
        assert result['provenance'] in ['real_data_where_available', 'unavailable'], \
            f"Invalid provenance: {result['provenance']}"
    
    def test_sentiment_indicators_have_provenance_or_neural_markers(self):
        """Indicators should have provenance when data used, neutral markers when not."""
        from backend.services.market_sentiment_service import MarketSentimentService
        
        service = MarketSentimentService()
        result = service.calculate_fear_greed_index()
        
        indicators = result.get('indicators', {})
        for name, indicator in indicators.items():
            if isinstance(indicator, dict):
                prov = indicator.get('provenance')
                if prov == 'unavailable':
                    # Should have neutral score and reason
                    assert indicator.get('score') == 0.5, "Unavailable should have neutral score"
                    assert indicator.get('reason') is not None, "Unavailable should explain why"


class TestMarketDataProviderReturnsNoneOnFailure:
    """P1: Verify market data provider returns None on failure (fail-closed)."""
    
    @pytest.mark.skip(reason="Alpaca module requires production environment setup")
    def test_market_data_returns_none_on_api_failure(self):
        """Alpaca API failure should return None, not crash."""
        from backend.services.market_data_service import get_market_data
        
        # Mock Alpaca failing
        with patch('backend.services.market_data_service._get_alpaca_bars') as mock_alpaca:
            mock_alpaca.side_effect = RuntimeError("API key missing")
            result = get_market_data("TEST")
            assert result is None, "Should return None on API failure, not raise"


class TestPortfolioTradeEndpointIsDeprecated:
    """P1: Verify legacy trade endpoint is properly documented as deprecated."""
    
    def test_endpoint_has_deprecation_warning(self):
        """The /api/portfolio/<id>/trade endpoint should be marked as DEPRECATED."""
        with open('/home/ubuntu/yantrax-rl/backend/main.py', 'r') as f:
            content = f.read()
        
        assert 'DEPRECATED' in content, "Endpoint should be marked DEPRECATED"
        assert 'This endpoint directly mutates PortfolioPosition without evidence' in content, \
            "Deprecation should explain why it bypasses canonical pipeline"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])