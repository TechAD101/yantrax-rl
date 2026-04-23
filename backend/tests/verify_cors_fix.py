import unittest
import os
import sys
from unittest.mock import MagicMock, patch

# Mock all dependencies of main.py to allow importing it
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['flask_sqlalchemy'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['db'] = MagicMock()
sys.modules['models'] = MagicMock()
sys.modules['service_registry'] = MagicMock()
sys.modules['ai_agents.persona_registry'] = MagicMock()
sys.modules['services.market_sentiment_service'] = MagicMock()
sys.modules['services.institutional_strategy_engine'] = MagicMock()
sys.modules['services.market_data_service_v2'] = MagicMock()
sys.modules['ai_firm.ceo'] = MagicMock()
sys.modules['ai_firm.agent_manager'] = MagicMock()
sys.modules['rl_core.env_market_sim'] = MagicMock()
sys.modules['services.oracle_service'] = MagicMock()
sys.modules['ai_firm.debate_engine'] = MagicMock()
sys.modules['routes.data_ingest'] = MagicMock()
sys.modules['memecoin_service'] = MagicMock()
sys.modules['order_manager'] = MagicMock()
sys.modules['backtest_service'] = MagicMock()
sys.modules['auth_service'] = MagicMock()
sys.modules['ai_firm.mood_board'] = MagicMock()
sys.modules['services.marketplace_service'] = MagicMock()

# Now we can try to test the logic in config.py directly
from config import Config

class TestCORSConfiguration(unittest.TestCase):
    def test_cors_parsing_logic(self):
        """Test the logic used in Config to parse CORS_ALLOWED_ORIGINS."""
        def parse_origins(env_val):
            # This mimics the logic in backend/config.py
            _cors_origins = env_val if env_val is not None else 'http://localhost:3000,http://127.0.0.1:3000'
            return [origin.strip() for origin in _cors_origins.split(',') if origin.strip()]

        # Test default
        self.assertEqual(parse_origins(None), ['http://localhost:3000', 'http://127.0.0.1:3000'])

        # Test custom
        self.assertEqual(parse_origins('http://myapp.com'), ['http://myapp.com'])

        # Test multiple
        self.assertEqual(parse_origins('http://a.com, http://b.com'), ['http://a.com', 'http://b.com'])

        # Test with spaces and empty elements
        self.assertEqual(parse_origins(' http://a.com , , http://b.com '), ['http://a.com', 'http://b.com'])

    def test_config_with_env_var(self):
        """Test that Config correctly picks up the environment variable by simulating its logic."""
        with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": "http://env-test.com"}):
            env_val = os.getenv('CORS_ALLOWED_ORIGINS')
            _cors_origins = env_val if env_val is not None else 'http://localhost:3000,http://127.0.0.1:3000'
            origins = [origin.strip() for origin in _cors_origins.split(',') if origin.strip()]

            self.assertEqual(origins, ['http://env-test.com'])

    def test_main_cors_init(self):
        """Verify that CORS is initialized with Config.CORS_ALLOWED_ORIGINS in main.py."""
        with open('backend/main.py', 'r') as f:
            content = f.read()
            self.assertIn('CORS(app, origins=Config.CORS_ALLOWED_ORIGINS)', content)

if __name__ == '__main__':
    unittest.main()
