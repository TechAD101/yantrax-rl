import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Check if numpy is available. In CI it is, locally it isn't.
# If it's not available, we MUST mock it in sys.modules BEFORE importing the service.
_mocked_numpy = False
try:
    import numpy
except ImportError:
    import unittest.mock
    mock_np = MagicMock()
    sys.modules['numpy'] = mock_np
    _mocked_numpy = True

try:
    import requests
except ImportError:
    import unittest.mock
    sys.modules['requests'] = MagicMock()

from services.market_sentiment_service import MarketSentimentService

@pytest.fixture
def service():
    return MarketSentimentService()

def test_get_social_sentiment_strongly_bullish(service):
    # Depending on whether numpy was mocked via sys.modules or exists natively,
    # we patch differently to ensure it works in both environments.
    if _mocked_numpy:
        with patch.dict(sys.modules, {'numpy': sys.modules['numpy']}):
            sys.modules['numpy'].random.uniform.side_effect = lambda low, high: high
            sys.modules['numpy'].random.randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')
    else:
        with patch('services.market_sentiment_service.np.random.uniform') as mock_uniform, \
             patch('services.market_sentiment_service.np.random.randint') as mock_randint:
            mock_uniform.side_effect = lambda low, high: high
            mock_randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')

    assert result['signal'] == 'STRONGLY_BULLISH'
    assert result['overall_sentiment'] > 0.65
    assert result['symbol'] == 'AAPL'
    assert 'timestamp' in result
    assert 'sources' in result

def test_get_social_sentiment_strongly_bearish(service):
    if _mocked_numpy:
        with patch.dict(sys.modules, {'numpy': sys.modules['numpy']}):
            sys.modules['numpy'].random.uniform.side_effect = lambda low, high: low
            sys.modules['numpy'].random.randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')
    else:
        with patch('services.market_sentiment_service.np.random.uniform') as mock_uniform, \
             patch('services.market_sentiment_service.np.random.randint') as mock_randint:
            mock_uniform.side_effect = lambda low, high: low
            mock_randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')

    assert result['signal'] == 'STRONGLY_BEARISH'
    assert result['overall_sentiment'] <= 0.35

def test_get_social_sentiment_neutral(service):
    if _mocked_numpy:
        with patch.dict(sys.modules, {'numpy': sys.modules['numpy']}):
            sys.modules['numpy'].random.uniform.side_effect = lambda low, high: 0.0 if low < 0 else (low + high) / 2
            sys.modules['numpy'].random.randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')
    else:
        with patch('services.market_sentiment_service.np.random.uniform') as mock_uniform, \
             patch('services.market_sentiment_service.np.random.randint') as mock_randint:
            mock_uniform.side_effect = lambda low, high: 0.0 if low < 0 else (low + high) / 2
            mock_randint.return_value = 1000
            result = service.get_social_sentiment('AAPL')

    assert result['signal'] == 'NEUTRAL'
    assert 0.45 < result['overall_sentiment'] <= 0.55

def test_get_social_sentiment_exception_fallback(service):
    if _mocked_numpy:
        with patch.dict(sys.modules, {'numpy': sys.modules['numpy']}):
            sys.modules['numpy'].random.uniform.side_effect = Exception("API failure")
            result = service.get_social_sentiment('AAPL')
            # Reset side effect
            sys.modules['numpy'].random.uniform.side_effect = None
    else:
        with patch('services.market_sentiment_service.np.random.uniform') as mock_uniform:
            mock_uniform.side_effect = Exception("API failure")
            result = service.get_social_sentiment('AAPL')

    assert result['signal'] == 'NEUTRAL'
    assert result['overall_sentiment'] == 0.5
    assert result['symbol'] == 'AAPL'
