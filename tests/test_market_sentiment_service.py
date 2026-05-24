import sys
import os
import pytest
from unittest.mock import patch, MagicMock

# Create mocked versions
mock_np = MagicMock()
mock_requests = MagicMock()

# Instead of blindly overriding sys.modules directly, we do it conditionally
# This ensures that if the system HAS numpy installed (like in CI), it will import natively
# But locally where it might be missing, it prevents ModuleNotFoundError
try:
    import numpy as np
except ImportError:
    import unittest.mock
    sys.modules['numpy'] = mock_np

try:
    import requests
except ImportError:
    import unittest.mock
    sys.modules['requests'] = mock_requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.market_sentiment_service import MarketSentimentService

@pytest.fixture
def service():
    return MarketSentimentService()

@patch('services.market_sentiment_service.np.random.uniform')
@patch('services.market_sentiment_service.np.random.randint')
def test_get_social_sentiment_strongly_bullish(mock_randint, mock_uniform, service):
    mock_uniform.side_effect = lambda low, high: high
    mock_randint.return_value = 1000

    result = service.get_social_sentiment('AAPL')
    assert result['signal'] == 'STRONGLY_BULLISH'
    assert result['overall_sentiment'] > 0.65
    assert result['symbol'] == 'AAPL'
    assert 'timestamp' in result
    assert 'sources' in result

@patch('services.market_sentiment_service.np.random.uniform')
@patch('services.market_sentiment_service.np.random.randint')
def test_get_social_sentiment_strongly_bearish(mock_randint, mock_uniform, service):
    mock_uniform.side_effect = lambda low, high: low
    mock_randint.return_value = 1000

    result = service.get_social_sentiment('AAPL')
    assert result['signal'] == 'STRONGLY_BEARISH'
    assert result['overall_sentiment'] <= 0.35

@patch('services.market_sentiment_service.np.random.uniform')
@patch('services.market_sentiment_service.np.random.randint')
def test_get_social_sentiment_neutral(mock_randint, mock_uniform, service):
    mock_uniform.side_effect = lambda low, high: 0.0 if low < 0 else (low + high) / 2
    mock_randint.return_value = 1000

    result = service.get_social_sentiment('AAPL')
    assert result['signal'] == 'NEUTRAL'
    assert 0.45 < result['overall_sentiment'] <= 0.55

@patch('services.market_sentiment_service.np.random.uniform')
def test_get_social_sentiment_exception_fallback(mock_uniform, service):
    mock_uniform.side_effect = Exception("API failure")

    result = service.get_social_sentiment('AAPL')
    assert result['signal'] == 'NEUTRAL'
    assert result['overall_sentiment'] == 0.5
    assert result['symbol'] == 'AAPL'
