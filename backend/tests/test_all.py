import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath('backend'))

# Mock required dependencies to allow import
sys.modules['flask'] = MagicMock()
sys.modules['flask_cors'] = MagicMock()
sys.modules['flask_sqlalchemy'] = MagicMock()
sys.modules['psycopg2'] = MagicMock()
sys.modules['redis'] = MagicMock()
sys.modules['sqlalchemy'] = MagicMock()
sys.modules['sqlalchemy.orm'] = MagicMock()
sys.modules['sqlalchemy.ext.declarative'] = MagicMock()
sys.modules['chromadb'] = MagicMock()
sys.modules['langchain'] = MagicMock()
sys.modules['openai'] = MagicMock()
sys.modules['tiktoken'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['scipy'] = MagicMock()
sys.modules['sklearn'] = MagicMock()
sys.modules['yfinance'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['google'] = MagicMock()

import main

class TestCache(unittest.TestCase):
    def test_cache_functionality(self):
        # Using a mock massive fetch quote method to track calls
        mock_fetch = MagicMock(return_value={"price": 100})

        with patch.object(main, 'MARKET_SERVICE_READY', False), patch('os.getenv') as mock_getenv:
            # force Massive
            def getenv_side_effect(key, default=None):
                if key == 'MASSIVE_API_KEY': return 'fake_key'
                return default
            mock_getenv.side_effect = getenv_side_effect

            with patch('services.market_data_service_massive.MassiveMarketDataService.fetch_quote', mock_fetch):
                # Call multiple times
                main.unified_get_market_price('AAPL')
                main.unified_get_market_price('AAPL')
                main.unified_get_market_price('AAPL')

                # Should only be called once because of cache
                mock_fetch.assert_called_once_with('AAPL')

if __name__ == '__main__':
    unittest.main()
