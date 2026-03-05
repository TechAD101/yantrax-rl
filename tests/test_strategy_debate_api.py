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


from unittest.mock import AsyncMock

@pytest.fixture
def client():
    import main
    main.app.config['TESTING'] = True

    # Mock the debate engine to prevent 503
    main.DEBATE_ENGINE = AsyncMock()
    main.DEBATE_ENGINE.conduct_debate.return_value = {
        'ticker': 'AAPL',
        'winning_signal': 'BUY',
        'arguments': ['Argument 1', 'Argument 2']
    }

    with main.app.test_client() as client:
        yield client


def test_trigger_debate(client):
    payload = {'symbol': 'AAPL'}
    resp = client.post('/api/strategy/ai-debate/trigger', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'ticker' in data and data['ticker'] == 'AAPL'
    assert 'winning_signal' in data
    assert 'arguments' in data and isinstance(data['arguments'], list)
