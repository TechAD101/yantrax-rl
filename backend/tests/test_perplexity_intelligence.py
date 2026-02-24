import pytest
import asyncio
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure backend path is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock modules that might be missing or problematic
sys.modules['chromadb'] = MagicMock()
sys.modules['pysqlite3'] = MagicMock()
# Mock httpx completely
sys.modules['httpx'] = MagicMock()

from services.perplexity_intelligence import PerplexityIntelligenceService, MarketSentiment

@pytest.fixture
def service():
    return PerplexityIntelligenceService(api_key="test_key")

def test_get_market_sentiment_success(service):
    """Test get_market_sentiment when comprehensive data is returned successfully."""
    # Mock get_comprehensive_market_data to return dummy data
    service.get_comprehensive_market_data = MagicMock()
    async def mock_get_comp_data(*args, **kwargs):
        return {
            'comprehensive_data': {
                'market_sentiment': 'bullish',
                'confidence': 0.9,
                'risk_factors': ['None'],
            }
        }
    service.get_comprehensive_market_data.side_effect = mock_get_comp_data

    async def run_test():
        result = await service.get_market_sentiment("AAPL")
        assert isinstance(result, MarketSentiment)
        assert result.mood == 'bullish'
        assert result.confidence == 0.9

    asyncio.run(run_test())

def test_get_market_sentiment_failure(service):
    """Test get_market_sentiment fallback when comprehensive data fails."""
    # Mock get_comprehensive_market_data to raise an exception
    service.get_comprehensive_market_data = MagicMock()
    async def mock_fail(*args, **kwargs):
        raise Exception("API Error")
    service.get_comprehensive_market_data.side_effect = mock_fail

    # Reset cache to force new call
    service._cache = {}
    service._cache_timestamps = {}

    async def run_test():
        result = await service.get_market_sentiment("AAPL")
        assert isinstance(result, MarketSentiment)
        assert result.mood == 'neutral'
        # Check for fallback message indicating limited data
        assert "Limited data" in result.summary or "API unavailable" in result.summary or "Rate limit active" in result.summary or "Fallback" in result.sources

    asyncio.run(run_test())
