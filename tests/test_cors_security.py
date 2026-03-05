import os
import sys
from unittest.mock import MagicMock, patch

# Mock all the heavy dependencies that are not installed in this environment
mock_modules = [
    'numpy', 'sqlalchemy', 'sqlalchemy.orm', 'flask', 'flask_cors',
    'dotenv', 'service_registry', 'ai_agents.persona_registry',
    'db', 'models', 'services.market_sentiment_service',
    'services.institutional_strategy_engine', 'services.market_data_service_v2',
    'ai_firm.ceo', 'ai_firm.agent_manager', 'rl_core.env_market_sim',
    'ai_firm.debate_engine', 'routes.data_ingest', 'ai_firm.report_generation',
    'memecoin_service', 'order_manager', 'backtest_service', 'auth_service',
    'ai_firm.mood_board', 'services.marketplace_service'
]

for module_name in mock_modules:
    sys.modules[module_name] = MagicMock()

# Setup some specific mocks needed for the app to initialize
mock_flask = sys.modules['flask']
mock_app = MagicMock()
mock_flask.Flask.return_value = mock_app
mock_flask.jsonify = lambda x: x
mock_flask.request = MagicMock()
mock_flask.Response = MagicMock

mock_cors = sys.modules['flask_cors']
mock_cors.CORS = MagicMock()

# Now we can safely import Config and main
# We need to add backend to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_cors_configuration():
    """Test that CORS is configured with the expected origins from Config."""
    from config import Config

    # We need to re-import main or use a patch to see the call
    with patch('flask_cors.CORS') as mocked_cors_call:
        # Since main is already imported in some environments,
        # but here we are running from a fresh process or before importing main
        import main

        # Check if CORS was called with Config.CORS_ALLOWED_ORIGINS
        # Note: main.py calls CORS(app, origins=Config.CORS_ALLOWED_ORIGINS)

        # In main.py:
        # app = Flask(__name__)
        # CORS(app, origins=Config.CORS_ALLOWED_ORIGINS)

        mocked_cors_call.assert_called()
        args, kwargs = mocked_cors_call.call_args
        assert kwargs['origins'] == Config.CORS_ALLOWED_ORIGINS
        print(f"Verified CORS called with: {kwargs['origins']}")

def test_config_defaults():
    """Test that Config has sensible CORS defaults."""
    from config import Config
    assert 'http://localhost:3000' in Config.CORS_ALLOWED_ORIGINS
    assert 'http://127.0.0.1:3000' in Config.CORS_ALLOWED_ORIGINS

if __name__ == "__main__":
    # Simple manual execution if pytest is problematic
    try:
        test_config_defaults()
        print("test_config_defaults PASSED")
        test_cors_configuration()
        print("test_cors_configuration PASSED")
    except Exception as e:
        print(f"Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
