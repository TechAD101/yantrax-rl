import sys
import unittest
from unittest.mock import MagicMock, patch

class TestMarketSentimentService(unittest.TestCase):
    def setUp(self):
        # Create a dictionary to patch sys.modules cleanly
        self.mock_modules = {
            'numpy': MagicMock(),
            'requests': MagicMock(),
        }
        # Start the patcher
        self.module_patcher = patch.dict(sys.modules, self.mock_modules)
        self.module_patcher.start()

        # Dynamically import the service AFTER patching
        import backend.services.market_sentiment_service as mss
        self.mss = mss

        # Save the original state of the global variable
        self.original_sentiment_service = getattr(self.mss, '_sentiment_service', None)
        # Reset the global variable for the test
        self.mss._sentiment_service = None

    def tearDown(self):
        # Restore the original state of the global variable
        if hasattr(self, 'mss'):
            self.mss._sentiment_service = self.original_sentiment_service

        # Stop the patcher so other tests are not affected
        self.module_patcher.stop()

    def test_get_sentiment_service_singleton(self):
        # First call should instantiate a new service
        instance1 = self.mss.get_sentiment_service({'test': 'config'})
        self.assertIsInstance(instance1, self.mss.MarketSentimentService)

        # Second call should return the exact same instance
        instance2 = self.mss.get_sentiment_service()
        self.assertIs(instance1, instance2, "get_sentiment_service should return a singleton instance")

if __name__ == '__main__':
    unittest.main()
