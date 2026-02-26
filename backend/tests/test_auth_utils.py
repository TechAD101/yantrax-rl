import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock flask module completely first
flask_mock = MagicMock()
sys.modules['flask'] = flask_mock

# Mock Config - Use "test_secret" to align with conftest.py if it runs
config_mock = MagicMock()
config_mock.Config.ADMIN_API_KEY = "test_secret"
sys.modules['config'] = config_mock

# Now import utils.security
import utils.security
from utils.security import require_api_key

class TestRequireApiKey(unittest.TestCase):
    def setUp(self):
        self.mock_request = utils.security.request
        self.mock_request.reset_mock()
        self.mock_request.path = "/test"
        utils.security.jsonify = lambda x: x

    def test_valid_key_header(self):
        # Align with conftest.py's "test_secret"
        self.mock_request.headers.get.return_value = "test_secret"
        self.mock_request.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        result = target()
        self.assertEqual(result, "ok")

    def test_valid_key_query(self):
        self.mock_request.headers.get.return_value = None
        self.mock_request.args.get.return_value = "test_secret"

        @require_api_key
        def target():
            return "ok"

        result = target()
        self.assertEqual(result, "ok")

    def test_invalid_key(self):
        self.mock_request.headers.get.return_value = "wrong"
        self.mock_request.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        result = target()
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[1], 401)
        self.assertEqual(result[0]['error'], 'Unauthorized')

    def test_missing_key(self):
        self.mock_request.headers.get.return_value = None
        self.mock_request.args.get.return_value = None

        @require_api_key
        def target():
            return "ok"

        result = target()
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[1], 401)

    def test_config_missing(self):
        # This test is tricky because conftest.py enforces a value.
        # We need to explicitly patch the Config object that utils.security uses.

        # utils.security imports Config.
        # We can patch config.Config.ADMIN_API_KEY

        from config import Config
        with patch.object(Config, 'ADMIN_API_KEY', None):
            with patch('os.getenv', return_value=None):
                @require_api_key
                def target():
                    return "ok"

                result = target()
                self.assertEqual(result[1], 500)
                self.assertIn('Server configuration error', result[0]['error'])

if __name__ == '__main__':
    unittest.main()
