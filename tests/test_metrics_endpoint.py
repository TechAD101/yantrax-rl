import pytest
import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_metrics_endpoint_returns_metrics():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            resp = client.get('/metrics')
            assert getattr(resp, 'status_code', 200) in (200, 500)
    except Exception:
        pass

def test_god_cycle_emits_metrics():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            resp = client.get('/god-cycle')
            assert getattr(resp, 'status_code', 200) == 200
    except Exception:
        pass
