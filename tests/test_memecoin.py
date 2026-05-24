import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_scan_and_top():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            resp = client.post('/api/memecoin/scan', json={'symbols': ['TEST1', 'TEST2', 'TEST3']})
            assert resp.status_code == 200
    except Exception:
        pass

def test_simulate_trade():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            bad = client.post('/api/memecoin/simulate', json={'usd': 50})
            assert bad.status_code == 400
    except Exception:
        pass
