import json
import os
import sys
import pytest

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db import init_db


@pytest.fixture(scope='module', autouse=True)
def setup_db():
    init_db()
    yield


@pytest.fixture
def client():
    import main
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client


def test_backtest_strategy(client):    
    # First create a strategy
    strat_resp = client.post('/api/strategy/publish', 
        data=json.dumps({'name': 'Test Strategy', 'description': 'Test', 'archetype': 'quant'}),
        content_type='application/json')
    
    if strat_resp.status_code == 201:
        strategy_id = strat_resp.get_json()['strategy']['id']
    else:
        strategy_id = 1  # fallback
    
    # Run backtest
    resp = client.post('/api/backtest',
        data=json.dumps({'strategy_id': strategy_id, 'symbol': 'AAPL', 'days': 30, 'initial_capital': 100000}),
        content_type='application/json')
    
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'backtest' in data
    assert data['backtest']['symbol'] == 'AAPL'
    assert 'total_return' in data['backtest']


def test_user_registration_and_login(client):

    
    # Register
    resp = client.post('/api/auth/register',
        data=json.dumps({'username': 'testuser', 'email': 'test@example.com', 'password': 'secret123'}),
        content_type='application/json')
    
    assert resp.status_code == 201
    user_data = resp.get_json()
    assert 'user' in user_data
    assert user_data['user']['username'] == 'testuser'
    
    # Login
    resp2 = client.post('/api/auth/login',
        data=json.dumps({'username': 'testuser', 'password': 'secret123'}),
        content_type='application/json')
    
    assert resp2.status_code == 200
    assert resp2.get_json()['user']['username'] == 'testuser'
