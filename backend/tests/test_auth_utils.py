import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock flask
flask_mock = MagicMock()
request_mock = MagicMock()
flask_mock.request = request_mock
flask_mock.jsonify = MagicMock(side_effect=lambda x: x) # Return dict for easy inspection
sys.modules['flask'] = flask_mock

# Mock Config
config_mock = MagicMock()
config_mock.Config.ADMIN_API_KEY = "secret"
sys.modules['config'] = config_mock

from utils.security import require_api_key

class TestRequireApiKey(unittest.TestCase):
    def test_valid_key_header(self):
        request_mock.headers.get.return_value = "secret"
        request_mock.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        self.assertEqual(target(), "ok")

    def test_valid_key_query(self):
        request_mock.headers.get.return_value = None
        request_mock.args.get.return_value = "secret"

        @require_api_key
        def target():
            return "ok"

        self.assertEqual(target(), "ok")

    def test_invalid_key(self):
        request_mock.headers.get.return_value = "wrong"
        request_mock.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        result = target()
        # Should return tuple (json, 401)
        self.assertEqual(result[1], 401)
        self.assertEqual(result[0]['error'], 'Unauthorized')

    def test_missing_key(self):
        request_mock.headers.get.return_value = None
        request_mock.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        result = target()
        self.assertEqual(result[1], 401)

    def test_config_missing(self):
        # Temporarily mock Config.ADMIN_API_KEY as None
        with patch('config.Config.ADMIN_API_KEY', None):
            # Also patch os.getenv to return None
            with patch('os.getenv', return_value=None):
                @require_api_key
                def target():
                    return "ok"

                result = target()
                self.assertEqual(result[1], 500)
                self.assertIn('Server configuration error', result[0]['error'])

if __name__ == '__main__':
    unittest.main()
