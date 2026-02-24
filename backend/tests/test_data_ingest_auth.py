import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock Flask and dependencies BEFORE importing routes
mock_flask = MagicMock()
sys.modules['flask'] = mock_flask

# CRITICAL: Make Blueprint.route a pass-through decorator
def route_side_effect(rule, **options):
    def decorator(f):
        return f
    return decorator

mock_blueprint_instance = MagicMock()
mock_blueprint_instance.route.side_effect = route_side_effect
mock_flask.Blueprint.return_value = mock_blueprint_instance

sys.modules['flask_cors'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['models'] = MagicMock()
sys.modules['db'] = MagicMock()

# Mock numpy
mock_np = MagicMock()
mock_np.median.return_value = 100.0
mock_np.mean.return_value = 0.5
sys.modules['numpy'] = mock_np

# Mock Config if necessary, but we can patch it
try:
    from routes.data_ingest import ingest_data
    from config import Config
except ImportError:
    try:
        from backend.routes.data_ingest import ingest_data
        from backend.config import Config
    except ImportError as e:
        print(f"ImportError: {e}")
        sys.exit(1)

class TestDataIngestAuth(unittest.TestCase):

    def setUp(self):
        # Reset mocks
        mock_flask.jsonify.reset_mock()
        # Reset request mock attributes
        mock_flask.request.headers = {}
        mock_flask.request.json = {}
        mock_flask.request.remote_addr = '127.0.0.1'

    def test_config_missing(self):
        print("Testing Config Missing (Default)...")
        # Ensure Config.DATA_INGEST_API_KEY is None (as per updated config.py)
        with patch.object(Config, 'DATA_INGEST_API_KEY', None):
            response = ingest_data()

            # Expect (jsonify(...), 503)
            self.assertIsInstance(response, tuple)
            self.assertEqual(response[1], 503)
            mock_flask.jsonify.assert_called_with({'error': 'configuration_error', 'message': 'Service misconfigured'})
        print("PASS")

    def test_missing_api_key_header(self):
        print("Testing Missing API Key Header...")
        mock_flask.request.headers = {}

        # Patch Config to have a known key so we get past the config check
        with patch.object(Config, 'DATA_INGEST_API_KEY', 'secret-key'):
            response = ingest_data()

            # Expect (jsonify(...), 401)
            self.assertIsInstance(response, tuple)
            self.assertEqual(response[1], 401)
            mock_flask.jsonify.assert_called_with({'error': 'unauthorized', 'message': 'Invalid or missing API key'})
        print("PASS")

    def test_invalid_api_key(self):
        print("Testing Invalid API Key...")
        mock_flask.request.headers = {'X-API-Key': 'wrong-key'}

        # Patch Config to have a known key
        with patch.object(Config, 'DATA_INGEST_API_KEY', 'secret-key'):
            response = ingest_data()

            self.assertIsInstance(response, tuple)
            self.assertEqual(response[1], 401)
            mock_flask.jsonify.assert_called_with({'error': 'unauthorized', 'message': 'Invalid or missing API key'})
        print("PASS")

    def test_valid_api_key(self):
        print("Testing Valid API Key...")
        mock_flask.request.headers = {'X-API-Key': 'secret-key'}
        mock_flask.request.json = {
            "instrument": "TEST",
            "metric": "price",
            "sources": {"fmp": 100},
            "timestamp": "2023-01-01T00:00:00Z"
        }

        with patch.object(Config, 'DATA_INGEST_API_KEY', 'secret-key'):
            response = ingest_data()

            self.assertIsInstance(response, tuple)
            self.assertEqual(response[1], 201)
        print("PASS")

if __name__ == '__main__':
    unittest.main()
