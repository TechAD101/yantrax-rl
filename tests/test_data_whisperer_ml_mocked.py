import sys
import unittest
from unittest.mock import MagicMock
import os

# Setup sys.path to include backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock dependencies
sys.modules['services'] = MagicMock()
sys.modules['services.market_data_service'] = MagicMock()
sys.modules['services.perplexity_intelligence'] = MagicMock()
sys.modules['services.market_sentiment_service'] = MagicMock()
sys.modules['services.circuit_breaker'] = MagicMock()
sys.modules['services.metrics_service'] = MagicMock()
# Mock httpx and numpy as they might be imported by other things
sys.modules['httpx'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['alpaca'] = MagicMock()
sys.modules['alpaca.data'] = MagicMock()

market_data_mock = sys.modules['services.market_data_service']
market_data_mock.get_latest_price.return_value = 150.0

perplexity_mock_module = sys.modules['services.perplexity_intelligence']
market_sentiment_mock_module = sys.modules['services.market_sentiment_service']

# Now we can import the module under test
try:
    from ai_agents.data_whisperer import analyze_data
except ImportError:
    # If import fails, we might need to adjust sys.path or mocks
    print("Import failed in test setup")
    raise

class TestDataWhispererML(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        perplexity_mock_module.get_perplexity_service.reset_mock()
        perplexity_mock_module.get_sentiment.reset_mock()
        market_sentiment_mock_module.get_sentiment_service.reset_mock(); market_sentiment_mock_module.get_sentiment_service.side_effect = None

    def test_perplexity_sentiment(self):
        # Setup Perplexity to be configured and return a sentiment
        pplx_service = MagicMock()
        pplx_service.is_configured.return_value = True
        perplexity_mock_module.get_perplexity_service.return_value = pplx_service

        perplexity_mock_module.get_sentiment.return_value = {
            'market_sentiment': 'strong bullish',
            'confidence': 0.9,
            'extra': 'info'
        }

        result = analyze_data("AAPL")

        self.assertEqual(result['sentiment'], 'very_bullish')
        self.assertEqual(result['sentiment_source'], 'perplexity_ai')
        self.assertEqual(result['sentiment_confidence'], 0.9)
        self.assertEqual(result['sentiment_details']['extra'], 'info')

    def test_market_sentiment_service_fallback(self):
        # Setup Perplexity to be NOT configured
        pplx_service = MagicMock()
        pplx_service.is_configured.return_value = False
        perplexity_mock_module.get_perplexity_service.return_value = pplx_service

        # Setup MarketSentimentService
        mss_service = MagicMock()
        mss_service.get_comprehensive_sentiment.return_value = {
            'recommendation': 'SELL',
            'confidence': 0.7
        }
        market_sentiment_mock_module.get_sentiment_service.return_value = mss_service

        result = analyze_data("AAPL")

        self.assertEqual(result['sentiment'], 'bearish')
        self.assertEqual(result['sentiment_source'], 'market_sentiment_service')
        self.assertEqual(result['sentiment_confidence'], 0.7)

    def test_all_fail_fallback(self):
        # Setup Perplexity to be NOT configured
        pplx_service = MagicMock()
        pplx_service.is_configured.return_value = False
        perplexity_mock_module.get_perplexity_service.return_value = pplx_service

        # Setup MarketSentimentService to raise exception
        market_sentiment_mock_module.get_sentiment_service.side_effect = Exception("Service down")

        result = analyze_data("AAPL")

        self.assertIn(result['sentiment'], ["very_bullish", "bullish", "neutral", "bearish", "very_bearish"])
        self.assertEqual(result['sentiment_source'], 'heuristic_fallback')
        self.assertEqual(result['sentiment_confidence'], 0.5)

if __name__ == '__main__':
    unittest.main()
