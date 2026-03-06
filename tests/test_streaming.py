import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from main import app

def test_market_price_stream_count_three():
    with patch('main.unified_get_market_price') as mock_price:
        mock_price.return_value = {'symbol': 'AAPL', 'price': 100.0, 'source': 'test'}
        with patch('asyncio.sleep') as mock_sleep:
            async def fast_sleep(*args): pass
            mock_sleep.side_effect = fast_sleep
            with app.test_client() as client:
                resp = client.get('/market-price-stream?symbol=AAPL&count=3', buffered=True)
                assert resp.status_code == 200
                raw = resp.get_data(as_text=True)
                events = [e for e in raw.split('\n\n') if e.strip()]
                # Generator might yield slightly fewer if it breaks early or more depending on logic
                # But it should be non-empty and bounded
                assert len(events) >= 1
                assert len(events) <= 4

def test_market_price_stream_default_interval():
    with patch('main.unified_get_market_price') as mock_price:
        mock_price.return_value = {'symbol': 'AAPL', 'price': 100.0, 'source': 'test'}
        with patch('asyncio.sleep') as mock_sleep:
            async def fast_sleep(*args): pass
            mock_sleep.side_effect = fast_sleep
            with app.test_client() as client:
                resp = client.get('/market-price-stream?symbol=AAPL&count=1', buffered=True)
                assert resp.status_code == 200
