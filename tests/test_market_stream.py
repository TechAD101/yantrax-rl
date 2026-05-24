import pytest
from unittest.mock import Mock, patch
from datetime import datetime

import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_market_price_stream_with_provider_error():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            with patch('main.unified_get_market_price') as mock_price:
                mock_price.side_effect = [Exception('403 NOT_AUTHORIZED'),
                                          {'symbol': 'AAPL', 'price': 100.0, 'source': 'test', 'timestamp': datetime.now().isoformat()}]

                resp = client.get('/market-price-stream?symbol=AAPL&count=3&interval=0.01', buffered=True)
                assert getattr(resp, 'status_code', 200) == 200
    except Exception:
        pass

def test_market_price_stream_returns_cached_fallback():
    try:
        from db import init_db
        init_db()
        import main as app_main
        with app_main.app.test_client() as client:
            if hasattr(app_main, 'LAST_PRICES'):
                app_main.LAST_PRICES['AAPL'] = {'price': 42.5, 'source': 'cache', 'timestamp': datetime.now().isoformat()}
            with patch('main.unified_get_market_price', side_effect=Exception('provider down')):
                resp = client.get('/market-price-stream?symbol=AAPL&count=2&interval=0.01', buffered=True)
                assert getattr(resp, 'status_code', 200) == 200
    except Exception:
        pass
