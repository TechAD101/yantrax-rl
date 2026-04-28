import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Setup sys.path to include backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock ALL dependencies that main.py might import
mocks = {
    'numpy': MagicMock(),
    'flask': MagicMock(),
    'flask_cors': MagicMock(),
    'sqlalchemy': MagicMock(),
    'sqlalchemy.orm': MagicMock(),
    'sqlalchemy.ext.declarative': MagicMock(),
    'chromadb': MagicMock(),
    'openai': MagicMock(),
    'google.generativeai': MagicMock(),
    'yfinance': MagicMock(),
    'alpaca.data.historical': MagicMock(),
    'alpaca.data.requests': MagicMock(),
    'alpaca.data.timeframe': MagicMock(),
    'alpaca.data.live': MagicMock(),
    'alpaca.trading.client': MagicMock(),
    'alpaca.trading.requests': MagicMock(),
    'dotenv': MagicMock(),
    'config': MagicMock(),
    'service_registry': MagicMock(),
    'ai_agents.persona_registry': MagicMock(),
    'db': MagicMock(),
    'models': MagicMock(),
    'services.market_sentiment_service': MagicMock(),
    'services.institutional_strategy_engine': MagicMock(),
    'services.market_data_service_v2': MagicMock(),
    'ai_firm.ceo': MagicMock(),
    'ai_firm.agent_manager': MagicMock(),
    'rl_core.env_market_sim': MagicMock(),
    'services.oracle_service': MagicMock(),
    'ai_firm.debate_engine': MagicMock(),
    'routes.data_ingest': MagicMock(),
    'memecoin_service': MagicMock(),
    'order_manager': MagicMock(),
    'backtest_service': MagicMock(),
    'auth_service': MagicMock(),
    'ai_firm.report_generation': MagicMock(),
    'ai_firm.mood_board': MagicMock(),
    'services.marketplace_service': MagicMock(),
}

for name, m in mocks.items():
    sys.modules[name] = m

mocks['flask'].Flask.return_value.route.return_value = lambda f: f

import main

class TestHealthDetailed(unittest.TestCase):
    def test_detailed_health_function(self):
        """Test the detailed_health function directly"""

        def mock_jsonify(data):
            return data

        with patch('main.jsonify', side_effect=mock_jsonify), \
             patch('main.datetime') as mock_datetime:

            mock_datetime.now.return_value.isoformat.return_value = '2025-01-01T00:00:00'

            # Test all services ready
            with patch('main.MARKET_SERVICE_READY', True), \
                 patch('main.AI_FIRM_READY', True), \
                 patch('main.RL_ENV_READY', True), \
                 patch('main.error_counts', {'error': 0}):

                result = main.detailed_health()

                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['services']['market_data'], 'v2')
                self.assertEqual(result['services']['ai_firm'], 'operational')
                self.assertEqual(result['services']['rl_core'], 'operational')
                self.assertTrue(result['ai_firm']['enabled'])
                self.assertEqual(result['ai_firm']['agents'], 24)

            # Test all services fallback
            with patch('main.MARKET_SERVICE_READY', False), \
                 patch('main.AI_FIRM_READY', False), \
                 patch('main.RL_ENV_READY', False), \
                 patch('main.error_counts', {'error': 1}):

                result = main.detailed_health()

                self.assertEqual(result['status'], 'healthy')
                self.assertEqual(result['services']['market_data'], 'fallback')
                self.assertEqual(result['services']['ai_firm'], 'fallback')
                self.assertEqual(result['services']['rl_core'], 'not_loaded')
                self.assertFalse(result['ai_firm']['enabled'])
                self.assertEqual(result['ai_firm']['agents'], 4)
                self.assertEqual(result['performance']['error'], 1)

    def test_detailed_health_exception(self):
        """Test detailed_health handling exceptions"""

        def mock_jsonify(data):
            return data

        with patch('main.jsonify', side_effect=mock_jsonify), \
             patch('main.datetime') as mock_dt:

            # The issue was likely that datetime.now() was called multiple times,
            # and the first call raised an exception, but the except block calls it again.
            # If side_effect is just an Exception, every call raises.
            # Let's use a side_effect list to raise then return something.

            mock_dt.now.side_effect = [Exception("Time is broken"), MagicMock()]
            mock_dt.now.return_value.isoformat.return_value = '2025-01-01T00:00:00'

            result = main.detailed_health()
            self.assertIsInstance(result, tuple)
            data, status_code = result

            self.assertEqual(status_code, 500)
            self.assertEqual(data['status'], 'error')
            self.assertEqual(data['message'], 'Time is broken')

if __name__ == '__main__':
    unittest.main()
