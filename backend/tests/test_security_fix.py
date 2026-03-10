import os
import unittest
from unittest.mock import patch, MagicMock
import importlib
import sys

# Mock dependencies before importing auth_service
sys.modules['db'] = MagicMock()
sys.modules['models'] = MagicMock()

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        # Clear auth_service from sys.modules to force re-import with different env vars
        if 'auth_service' in sys.modules:
            del sys.modules['auth_service']

    def tearDown(self):
        if 'auth_service' in sys.modules:
            del sys.modules['auth_service']

    @patch.dict(os.environ, {"FLASK_ENV": "production", "SECRET_KEY": ""})
    def test_secret_key_missing_production(self):
        """Test that missing SECRET_KEY in production raises ValueError"""
        # Ensure SECRET_KEY is not in environ
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        with self.assertRaises(ValueError) as cm:
            import auth_service
        self.assertIn("FATAL: SECRET_KEY environment variable is required in production.", str(cm.exception))

    @patch.dict(os.environ, {"FLASK_ENV": "development", "SECRET_KEY": ""})
    def test_secret_key_missing_development(self):
        """Test that missing SECRET_KEY in development generates a random key"""
        # Ensure SECRET_KEY is not in environ
        if "SECRET_KEY" in os.environ:
            del os.environ["SECRET_KEY"]

        import auth_service
        self.assertTrue(len(auth_service.SECRET_KEY) >= 64) # secrets.token_hex(32) is 64 chars
        self.assertNotEqual(auth_service.SECRET_KEY, 'dev-secret-key-change-in-production')

    @patch.dict(os.environ, {"SECRET_KEY": "provided-secret-key"})
    def test_secret_key_provided(self):
        """Test that provided SECRET_KEY is used"""
        import auth_service
        self.assertEqual(auth_service.SECRET_KEY, "provided-secret-key")

if __name__ == '__main__':
    unittest.main()
