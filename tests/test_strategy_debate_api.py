import pytest
import json

@pytest.fixture
def client():
    import main
    main.app.config['TESTING'] = True
    with main.app.test_client() as client:
        yield client

def test_trigger_debate(client):
    payload = {'symbol': 'AAPL'}

    resp = client.post('/api/strategy/ai-debate/trigger', json=payload)

    # In CI environment, external services (Perplexity, ChromaDB) might not be initialized
    # leading to 503. This is acceptable for this test.
    assert resp.status_code in [200, 503]

    if resp.status_code == 200:
        data = resp.get_json()
        assert isinstance(data, dict)
