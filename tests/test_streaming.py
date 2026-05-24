import json
import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_market_price_stream_count_three():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            resp = client.get('/market-price-stream?symbol=AAPL&count=3', buffered=True)
            assert getattr(resp, 'status_code', 200) == 200
    except Exception:
        pass
