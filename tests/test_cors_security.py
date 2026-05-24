import os
import sys
import unittest
import importlib

# Adjust sys.path so we can resolve backend
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

class TestCORSSecurity(unittest.TestCase):
    def setUp(self):
        # Save environment
        self.original_env = dict(os.environ)

    def tearDown(self):
        # Restore environment
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_config_cors_origins_default(self):
        # Remove CORS_ORIGINS from environment if it exists
        if 'CORS_ORIGINS' in os.environ:
            del os.environ['CORS_ORIGINS']

        import backend.config
        importlib.reload(backend.config)

        self.assertEqual(backend.config.Config.CORS_ORIGINS, ['*'])

    def test_config_cors_origins_custom(self):
        # Set custom CORS_ORIGINS
        os.environ['CORS_ORIGINS'] = 'http://localhost:3000, https://myapp.com '

        import backend.config
        importlib.reload(backend.config)

        self.assertEqual(backend.config.Config.CORS_ORIGINS, ['http://localhost:3000', 'https://myapp.com'])

if __name__ == '__main__':
    unittest.main()
