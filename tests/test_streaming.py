import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import app


def test_market_price_stream_count_three():
    with app.test_client() as client:
        resp = client.get('/market-price-stream?symbol=AAPL&count=3', buffered=True)
        assert resp.status_code == 200
        data = resp.get_data(as_text=True)
        # SSE events are separated by double newlines
        events = [e for e in data.split('\n\n') if e.strip()]
        assert len(events) == 3
        for ev in events:
            assert ev.startswith('data: ')
            payload = json.loads(ev[len('data: '):])
            assert payload['symbol'] == 'AAPL'
            assert 'data' in payload
            # data can be error payload or success
            assert 'timestamp' in payload
