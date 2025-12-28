import os
import sys
import pytest
from unittest.mock import patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# In some test environments python-dotenv may not be installed; provide a small shim so importing main doesn't fail
import types
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = types.SimpleNamespace(load_dotenv=lambda *a, **k: None)

@pytest.fixture
def client():
    from main import app
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_market_price_stream_with_provider_error(client):
    # Simulate provider raising an entitlement error first, then returning a valid price
    with patch('main.unified_get_market_price') as mock_price:
        mock_price.side_effect = [Exception('403 NOT_AUTHORIZED'),
                                  {'symbol': 'AAPL', 'price': 100.0, 'source': 'test', 'timestamp': datetime.now().isoformat()}]

        # use a tiny interval so the generator yields quickly during tests
        # buffer response so Flask test client collects stream until `count` events are sent
        resp = client.get('/market-price-stream?symbol=AAPL&count=3&interval=0.01', buffered=True)
        assert resp.status_code == 200

        raw = resp.get_data(as_text=True)
        # SSE events are separated by double-newline
        events = [e for e in raw.split('\n\n') if e.strip()]

        # We should see at least two events: an error/fallback and then a valid data event
        assert len(events) >= 2
        joined = "\n\n".join(events)

        # Expect a structured event from the server: either a fallback or an error type (or a direct price event)
        has_fallback = '"type":"fallback"' in joined
        has_error = '"type":"error"' in joined
        has_price = '"price":' in joined
        assert has_fallback or has_error or has_price

        # If the server emitted an error, ensure it's the entitlement-like error we simulated
        if has_error:
            assert 'NOT_AUTHORIZED' in joined or '403' in joined


def test_market_price_stream_returns_cached_fallback(client):
    # Populate the LAST_PRICES cache and then simulate provider failure
    import main as app_main
    app_main.LAST_PRICES['AAPL'] = {'price': 42.5, 'source': 'cache', 'timestamp': datetime.now().isoformat()}

    with patch('main.unified_get_market_price') as mock_price:
        mock_price.side_effect = Exception('403 NOT_AUTHORIZED')

        resp = client.get('/market-price-stream?symbol=AAPL&count=1&interval=0.01', buffered=True)
        assert resp.status_code == 200
        raw = resp.get_data(as_text=True)
        events = [e for e in raw.split('\n\n') if e.strip()]
        assert len(events) >= 1
        joined = "\n\n".join(events)

        # Parse SSE `data: ` prefixed events and ensure one event is a fallback with cached price
        parsed = []
        import json
        for e in events:
            if e.startswith('data:'):
                try:
                    parsed.append(json.loads(e[len('data:'):].strip()))
                except Exception:
                    pass
        assert any(ev.get('type') == 'fallback' and ev.get('data', {}).get('price') == 42.5 for ev in parsed)
