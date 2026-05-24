import sys
import os
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# We cannot reliably guess when to conditionally mock using `try...except ImportError`
# in an environment where numpy might exist but `services.market_sentiment_service.np` behaves strangely
# when patched.
#
# A much safer and universal pattern for mocking missing dependencies in these
# restricted environments that prevents both `ModuleNotFoundError` locally AND
# `AssertionError` (MagicMock evaluation) remotely is to ALWAYS patch using `sys.modules`.
#
# However, we must provide a minimal viable mock of `numpy.random` that actually works
# if the backend code attempts to invoke it.

import unittest.mock

mock_np = MagicMock()
# Provide explicit, usable MagicMocks that can be patched over
mock_np.random = MagicMock()
mock_np.random.uniform = MagicMock()
mock_np.random.randint = MagicMock()

mocks = {
    'numpy': mock_np,
    'requests': MagicMock()
}

# Apply the sys.modules patch globally for this test file context
with unittest.mock.patch.dict(sys.modules, mocks):
    from services.market_sentiment_service import MarketSentimentService

@pytest.fixture
def service():
    # Because MarketSentimentService might be instantiating things at runtime that need numpy,
    # we ensure the fixture also runs inside the patch context.
    with unittest.mock.patch.dict(sys.modules, mocks):
        return MarketSentimentService()

def test_get_social_sentiment_strongly_bullish(service):
    with unittest.mock.patch.dict(sys.modules, mocks):
        # Directly set the behavior of our mock_np object
        mock_np.random.uniform.side_effect = lambda low, high: high
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')

        assert result['signal'] == 'STRONGLY_BULLISH'
        assert result['overall_sentiment'] > 0.65
        assert result['symbol'] == 'AAPL'
        assert 'timestamp' in result
        assert 'sources' in result

        # Reset side effect for isolation
        mock_np.random.uniform.side_effect = None

def test_get_social_sentiment_strongly_bearish(service):
    with unittest.mock.patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = lambda low, high: low
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')

        assert result['signal'] == 'STRONGLY_BEARISH'
        assert result['overall_sentiment'] <= 0.35

        mock_np.random.uniform.side_effect = None

def test_get_social_sentiment_neutral(service):
    with unittest.mock.patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = lambda low, high: 0.0 if low < 0 else (low + high) / 2
        mock_np.random.randint.return_value = 1000

        result = service.get_social_sentiment('AAPL')

        assert result['signal'] == 'NEUTRAL'
        assert 0.45 < result['overall_sentiment'] <= 0.55

        mock_np.random.uniform.side_effect = None

def test_get_social_sentiment_exception_fallback(service):
    with unittest.mock.patch.dict(sys.modules, mocks):
        mock_np.random.uniform.side_effect = Exception("API failure")

        result = service.get_social_sentiment('AAPL')

        assert result['signal'] == 'NEUTRAL'
        assert result['overall_sentiment'] == 0.5
        assert result['symbol'] == 'AAPL'

        mock_np.random.uniform.side_effect = None
