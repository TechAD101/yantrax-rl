import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies to avoid ImportErrors in the restricted environment
mock_modules = [
    'numpy',
    'flask',
    'flask_cors',
    'sqlalchemy',
    'sqlalchemy.orm',
    'dotenv',
    'ai_agents.persona_registry',
    'db',
    'models',
    'services.market_sentiment_service',
    'services.institutional_strategy_engine',
    'ai_firm.ceo',
    'ai_firm.agent_manager',
    'rl_core.env_market_sim',
    'services.oracle_service',
    'ai_firm.debate_engine',
    'routes.data_ingest',
    'ai_firm.report_generation',
    'services.market_data_service_massive',
    'ai_firm.mood_board',
    'services.marketplace_service',
    'memecoin_service',
    'order_manager',
    'backtest_service',
    'auth_service',
    'requests'
]

for mod_name in mock_modules:
    sys.modules[mod_name] = MagicMock()

# Specifically mock Config to return something useful if needed
mock_config = MagicMock()
mock_config.get_market_config.return_value = {}
sys.modules['config'] = MagicMock(Config=mock_config)

# Mock service_registry
mock_registry = MagicMock()
sys.modules['service_registry'] = MagicMock(registry=mock_registry)

# Import the service module to mock the class inside it
import services.market_data_service_v2 as market_data_service_v2

class TestMainFallback(unittest.TestCase):
    def test_dummy_market_provider_fallback(self):
        # We want to trigger the except block in main.py for MarketDataService initialization

        # Patch the class inside the module we just imported
        with patch.object(market_data_service_v2, 'MarketDataService') as mock_mds:
            # Force initialization to fail
            mock_mds.side_effect = Exception("Initialization failed")

            # Now import main.
            if 'main' in sys.modules:
                del sys.modules['main']

            import main

            # Verify market_provider is an instance of DummyMarketProvider
            provider = main.market_provider

            # Check its methods
            self.assertEqual(provider.get_recent_audit_logs(10), [])
            self.assertEqual(provider.get_price("AAPL"), {'price': 0, 'error': 'Market data unavailable'})
            self.assertEqual(provider.get_fundamentals("AAPL"), {})
            self.assertEqual(provider.get_verification_stats(), {})
            self.assertEqual(provider.get_price_verified("AAPL"), {'verified': False, 'price': 0})

            print("✅ DummyMarketProvider fallback verified successfully")

if __name__ == '__main__':
    unittest.main()
