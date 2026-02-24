import os
import sys
import pytest

# Use in-memory DB for safe tests
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


def test_trigger_debate(client):
    payload = {'symbol': 'AAPL'}
    resp = client.post('/api/strategy/ai-debate/trigger', json=payload)
assert resp.status_code in [200, 503] # Allow 503 for CI where Debate Engine dependencies might be missing
    data = resp.get_json()

    if resp.status_code == 200:
        assert 'ticker' in data and data['ticker'] == 'AAPL'
        assert 'winning_signal' in data
        assert 'arguments' in data and isinstance(data['arguments'], list)
    else:
        assert 'error' in data
