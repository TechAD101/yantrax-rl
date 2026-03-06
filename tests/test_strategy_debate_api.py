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

    # Mock DEBATE_ENGINE to prevent 503 in test environments
    mock_debate_engine = MagicMock()
    mock_debate_engine.conduct_debate = AsyncMock(return_value={
        'ticker': 'AAPL',
        'winning_signal': 'buy',
        'arguments': [{'persona': 'quant', 'argument': 'Numbers go up'}]
    })

    # Inject into main module
    main.DEBATE_ENGINE = mock_debate_engine

    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

    # Cleanup (optional, but good practice)
    if hasattr(main, 'DEBATE_ENGINE'):
        del main.DEBATE_ENGINE

def test_trigger_debate(client):
    payload = {'symbol': 'AAPL'}
    resp = client.post('/api/strategy/ai-debate/trigger', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'ticker' in data and data['ticker'] == 'AAPL'
    assert 'winning_signal' in data
    assert 'arguments' in data and isinstance(data['arguments'], list)
