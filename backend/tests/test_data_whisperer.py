import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before import
sys.modules['services.market_data_service'] = MagicMock()
sys.modules['services.circuit_breaker'] = MagicMock()
sys.modules['services.metrics_service'] = MagicMock()

from ai_agents.data_whisperer import analyze_data, _analyze_trend, _detect_market_phase

class TestDataWhisperer(unittest.TestCase):

    def test_analyze_trend_strong_bullish(self):
        # price > ma_50 * 1.05
        result = _analyze_trend(106, 100)
        self.assertEqual(result, "strong_bullish")

    def test_analyze_trend_bullish(self):
        # price > ma_50 and <= ma_50 * 1.05
        result = _analyze_trend(101, 100)
        self.assertEqual(result, "bullish")

    def test_analyze_trend_sideways(self):
        # price <= ma_50 and > ma_50 * 0.95
        result = _analyze_trend(100, 100)
        self.assertEqual(result, "sideways")
        result = _analyze_trend(96, 100)
        self.assertEqual(result, "sideways")

    def test_analyze_trend_bearish(self):
        # price <= ma_50 * 0.95 and > ma_50 * 0.90
        result = _analyze_trend(94, 100)
        self.assertEqual(result, "bearish")

    def test_analyze_trend_strong_bearish(self):
        # price <= ma_50 * 0.90
        result = _analyze_trend(89, 100)
        self.assertEqual(result, "strong_bearish")

    def test_detect_market_phase_bull(self):
        # price > ma_50 * 1.02
        result = _detect_market_phase(103, 100)
        self.assertEqual(result, "bull_market")

    def test_detect_market_phase_bear(self):
        # price < ma_50 * 0.98
        result = _detect_market_phase(97, 100)
        self.assertEqual(result, "bear_market")

    def test_detect_market_phase_range(self):
        # price between 0.98 and 1.02 of ma_50
        result = _detect_market_phase(100, 100)
        self.assertEqual(result, "range_bound")

    @patch('ai_agents.data_whisperer.get_latest_price')
    def test_analyze_data_structure(self, mock_get_latest_price):
        mock_get_latest_price.return_value = 150.0

        # We need to ensure random values don't mess up our assertions too much,
        # but for structure check it's fine.
        result = analyze_data("AAPL")

        self.assertIsInstance(result, dict)
        self.assertEqual(result['symbol'], "AAPL")
        self.assertEqual(result['price'], 150.0)
        self.assertIn('trend', result)
        self.assertIn('market_conditions', result)
        self.assertIn('technical_indicators', result)
        self.assertIn('moving_average_50', result['technical_indicators'])

        # Verify that trend matches the logic based on generated MA
        price = result['price']
        ma_50 = result['technical_indicators']['moving_average_50']
        trend = result['trend']

        # Re-verify logic
        expected_trend = _analyze_trend(price, ma_50)
        self.assertEqual(trend, expected_trend)

if __name__ == '__main__':
    unittest.main()
