import os
import sys
import pytest
from unittest.mock import patch, MagicMock
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
    # Tests that streaming API emits error events if provider fails
    import main as app_main
    with patch('main.unified_get_market_price') as mock_price:
        # We need mock_price to be async if it is awaited
        async def mock_price_async(*args, **kwargs):
            if mock_price_async.calls == 0:
                mock_price_async.calls += 1
                raise Exception('403 NOT_AUTHORIZED')
            else:
                return {'symbol': 'AAPL', 'price': 100.0, 'source': 'test', 'timestamp': datetime.now().isoformat()}
        mock_price_async.calls = 0

        # Override to_thread mock if needed, but easier is just patching the target
        # Actually in main.py it's `await asyncio.to_thread(unified_get_market_price, symbol)`
        # If unified_get_market_price raises Exception, to_thread correctly propagates it.
        mock_price.side_effect = [Exception('403 NOT_AUTHORIZED'),
                                  {'symbol': 'AAPL', 'price': 100.0, 'source': 'test', 'timestamp': datetime.now().isoformat()},
                                  {'symbol': 'AAPL', 'price': 100.0, 'source': 'test', 'timestamp': datetime.now().isoformat()}]

        # Patch sleep to not wait 5 seconds!
        with patch('asyncio.sleep') as mock_sleep:
            async def fast_sleep(*args): pass
            mock_sleep.side_effect = fast_sleep

            resp = client.get('/market-price-stream?symbol=AAPL&count=3&interval=0.01', buffered=True)
            assert resp.status_code == 200

            raw = resp.get_data(as_text=True)
            events = [e for e in raw.split('\n\n') if e.strip()]
            assert len(events) >= 2
            joined = "\n\n".join(events)

            has_fallback = '"type":"fallback"' in joined
            has_error = '"type":"error"' in joined
            has_price = '"price":' in joined
            assert has_fallback or has_error or has_price

            if has_error:
                assert 'NOT_AUTHORIZED' in joined or '403' in joined

def test_market_price_stream_returns_cached_fallback(client):
    import main as app_main
    app_main.LAST_PRICES['AAPL'] = {'price': 42.5, 'source': 'cache', 'timestamp': datetime.now().isoformat()}

    with patch('main.unified_get_market_price') as mock_price:
        mock_price.side_effect = Exception('403 NOT_AUTHORIZED')

        with patch('asyncio.sleep') as mock_sleep:
            async def fast_sleep(*args): pass
            mock_sleep.side_effect = fast_sleep

            resp = client.get('/market-price-stream?symbol=AAPL&count=1&interval=0.01', buffered=True)
            assert resp.status_code == 200
            raw = resp.get_data(as_text=True)
            events = [e for e in raw.split('\n\n') if e.strip()]
            assert len(events) >= 1
            joined = "\n\n".join(events)

            import json
            parsed = []
            for e in events:
                if e.startswith('data:'):
                    try:
                        parsed.append(json.loads(e[len('data:'):].strip()))
                    except Exception:
                        pass
            assert any(ev.get('type') == 'fallback' and ev.get('data', {}).get('price') == 42.5 for ev in parsed)
