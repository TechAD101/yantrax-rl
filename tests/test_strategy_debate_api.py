import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock

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

    # Mock DEBATE_ENGINE if not present or even if present to avoid external calls
    mock_engine = MagicMock()
    mock_engine.conduct_debate = AsyncMock(return_value={
        'ticker': 'AAPL',
        'winning_signal': 'BUY',
        'confidence': 0.85,
        'arguments': [
            {'agent': 'Warren', 'signal': 'HOLD', 'reasoning': 'Value is okay'},
            {'agent': 'Cathie', 'signal': 'BUY', 'reasoning': 'Innovation!'}
        ]
    })

    # Inject into main module
    main.DEBATE_ENGINE = mock_engine

    with main.app.test_client() as client:
        yield client


def test_trigger_debate(client):
    payload = {'symbol': 'AAPL'}
    resp = client.post('/api/strategy/ai-debate/trigger', json=payload)

    # If endpoint returns 503, it means DEBATE_ENGINE is not found or falsely evaluates to False.
    # We injected a mock, so it should be found.
    assert resp.status_code == 200, f"Response: {resp.data.decode()}"

    data = resp.get_json()
    assert 'ticker' in data and data['ticker'] == 'AAPL'
    assert 'winning_signal' in data
    assert 'arguments' in data and isinstance(data['arguments'], list)
