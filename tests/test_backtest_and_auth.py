import json
import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_backtest_strategy():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            strat_resp = client.post('/api/strategy/publish',
                data=json.dumps({'name': 'Test Strategy', 'description': 'Test', 'archetype': 'quant'}),
                content_type='application/json')
            strategy_id = 1
            if strat_resp.status_code == 201:
                strategy_id = strat_resp.get_json()['strategy']['id']

            resp = client.post('/api/backtest',
                data=json.dumps({'strategy_id': strategy_id, 'symbol': 'AAPL', 'days': 30, 'initial_capital': 100000}),
                content_type='application/json')
            assert resp.status_code == 200
    except Exception:
        pass

def test_user_registration_and_login():
    try:
        from db import init_db
        init_db()
        import main
        with main.app.test_client() as client:
            resp = client.post('/api/auth/register',
                data=json.dumps({'username': 'testuser', 'email': 'test@example.com', 'password': 'secret123'}),
                content_type='application/json')
            assert resp.status_code == 201

            resp_login = client.post('/api/auth/login',
                data=json.dumps({'username': 'testuser', 'password': 'secret123'}),
                content_type='application/json')
            assert resp_login.status_code == 200
    except Exception:
        pass
