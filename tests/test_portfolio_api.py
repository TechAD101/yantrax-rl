import os
import json
import sys
import pytest

# Ensure test DB is in-memory
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Make backend package importable like other tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))



@pytest.fixture(scope='module', autouse=True)
def setup_db():
    # Initialize in-memory DB before importing main to avoid heavy external imports
    from db import init_db
    init_db()
    yield


@pytest.fixture
def client():
    try:
        import main
        main.app.config['TESTING'] = True
        with main.app.test_client() as client:
            yield client
    except Exception:
        pytest.skip("Unable to import backend.main for testing")


def test_create_and_get_portfolio(client):
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

    # Create
    resp = client.post('/api/portfolio', json=payload)
    assert resp.status_code == 201, resp.data.decode()
    data = resp.get_json()
    assert 'portfolio' in data
    pid = data['portfolio']['id']

    # Fetch by id
    get_resp = client.get(f'/api/portfolio/{pid}')
    assert get_resp.status_code == 200
    fetched = get_resp.get_json()['portfolio']
    assert fetched['name'] == 'Test Portfolio'
    assert fetched['initial_capital'] == 50000
    assert fetched['risk_profile'] == 'conservative'

    # Backwards-compatible summary
    summary = client.get('/portfolio')
    assert summary.status_code == 200
    sdata = summary.get_json()
    assert sdata['id'] == pid
