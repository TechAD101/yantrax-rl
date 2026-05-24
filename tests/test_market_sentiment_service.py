import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Mock dependencies to avoid ModuleNotFoundError in restricted environments
import unittest.mock

mock_np = MagicMock()
mock_np.random.uniform.return_value = 0.5
mock_np.random.randint.return_value = 1000

mock_requests = MagicMock()

mocks = {
    'numpy': mock_np,
    'requests': mock_requests
}

with unittest.mock.patch.dict(sys.modules, mocks):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from services.market_sentiment_service import MarketSentimentService

@pytest.fixture
def service():
    with unittest.mock.patch.dict(sys.modules, mocks):
        return MarketSentimentService()

def test_get_social_sentiment_strongly_bullish(service):
    with patch.dict(sys.modules, mocks):
        # In this context, mock_np.random.uniform returns 0.5 which corresponds to STRONGLY_BULLISH
        mock_np.random.uniform.side_effect = lambda low, high: high
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')
        assert result['signal'] == 'STRONGLY_BULLISH'
        assert result['overall_sentiment'] > 0.65
        assert result['symbol'] == 'AAPL'
        assert 'timestamp' in result
        assert 'sources' in result

def test_get_social_sentiment_strongly_bearish(service):
    with patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = lambda low, high: low
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')
        assert result['signal'] == 'STRONGLY_BEARISH'
        assert result['overall_sentiment'] <= 0.35

def test_get_social_sentiment_neutral(service):
    with patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = lambda low, high: 0.0 if low < 0 else (low + high) / 2
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')
        assert result['signal'] == 'NEUTRAL'
        assert 0.45 < result['overall_sentiment'] <= 0.55

def test_get_social_sentiment_exception_fallback(service):
    with patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = Exception("API failure")

        result = service.get_social_sentiment('AAPL')
        assert result['signal'] == 'NEUTRAL'
        assert result['overall_sentiment'] == 0.5
        assert result['symbol'] == 'AAPL'

        # Reset side effect for subsequent tests
        mock_np.random.uniform.side_effect = None
