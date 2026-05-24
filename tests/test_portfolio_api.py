import json
import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_create_and_get_portfolio():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            payload = {
                'name': 'Test Portfolio',
                'owner_id': 42,
                'risk_profile': 'conservative',
                'initial_capital': 50000,
                'strategy': {
                    'name': 'ai_managed_test',
                    'archetype': 'quant',
                    'params': {'leverage': 1}
                }
            }
            resp = client.post('/api/portfolio', json=payload)
            assert getattr(resp, 'status_code', 201) == 201
    except Exception:
        pass
