import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Setup sys.path to include backend
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'backend'))

# Mock numpy and other dependencies using patch.dict to avoid test suite pollution
# BUT do it globally here so unittest decorators can access the module
try:
    import numpy
except ImportError:
    sys.modules['numpy'] = MagicMock()
try:
    import requests
except ImportError:
    sys.modules['requests'] = MagicMock()

try:
    from services.market_sentiment_service import MarketSentimentService
except ImportError:
    print("Import failed in test setup")
    raise

class TestMarketSentimentService(unittest.TestCase):
    def setUp(self):
        self.service = MarketSentimentService()
        self.service.logger = MagicMock()

    @patch('services.market_sentiment_service.datetime')
    @patch('services.market_sentiment_service.np.mean')
    @patch('services.market_sentiment_service.np.random.uniform')
    def test_analyze_options_flow_bullish(self, mock_uniform, mock_mean, mock_datetime):
        mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12:00:00'
        mock_uniform.return_value = 0.8
        mock_mean.return_value = 0.85

        result = self.service.analyze_options_flow("AAPL")

        self.assertEqual(result['symbol'], "AAPL")
        self.assertEqual(result['flow_score'], 0.85)
        self.assertEqual(result['signal'], "BULLISH_INSTITUTIONAL_FLOW")
        self.assertEqual(result['timestamp'], '2023-01-01T12:00:00')
        self.assertIn('unusual_volume', result['indicators'])

    @patch('services.market_sentiment_service.datetime')
    @patch('services.market_sentiment_service.np.mean')
    @patch('services.market_sentiment_service.np.random.uniform')
    def test_analyze_options_flow_bearish(self, mock_uniform, mock_mean, mock_datetime):
        mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12:00:00'
        mock_uniform.return_value = 0.2
        mock_mean.return_value = 0.15

        result = self.service.analyze_options_flow("AAPL")

        self.assertEqual(result['flow_score'], 0.15)
        self.assertEqual(result['signal'], "BEARISH_INSTITUTIONAL_FLOW")

    @patch('services.market_sentiment_service.datetime')
    @patch('services.market_sentiment_service.np.mean')
    @patch('services.market_sentiment_service.np.random.uniform')
    def test_analyze_options_flow_neutral(self, mock_uniform, mock_mean, mock_datetime):
        mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12:00:00'
        mock_uniform.return_value = 0.5
        mock_mean.return_value = 0.50

        result = self.service.analyze_options_flow("AAPL")

        self.assertEqual(result['flow_score'], 0.50)
        self.assertEqual(result['signal'], "NEUTRAL_FLOW")

    @patch('services.market_sentiment_service.datetime')
    @patch('services.market_sentiment_service.np.random.uniform')
    def test_analyze_options_flow_exception(self, mock_uniform, mock_datetime):
        mock_datetime.now.return_value.isoformat.return_value = '2023-01-01T12:00:00'
        mock_uniform.side_effect = Exception("Mocked exception")

        result = self.service.analyze_options_flow("AAPL")

        self.assertEqual(result['symbol'], "AAPL")
        self.assertEqual(result['flow_score'], 0.5)
        self.assertEqual(result['signal'], "NEUTRAL_FLOW")
        self.assertEqual(result['timestamp'], '2023-01-01T12:00:00')
        self.service.logger.error.assert_called_once()

    @classmethod
    def tearDownClass(cls):
        # Clean up mocks to prevent test suite pollution
        if 'numpy' in sys.modules and isinstance(sys.modules['numpy'], MagicMock):
            del sys.modules['numpy']
        if 'requests' in sys.modules and isinstance(sys.modules['requests'], MagicMock):
            del sys.modules['requests']

if __name__ == '__main__':
    unittest.main()
