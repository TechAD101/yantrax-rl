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


def test_publish_and_list_strategy(client):
    payload = {
        'name': 'Internal Momentum v0.1',
        'description': 'Momentum strategy for MVP testing',
        'archetype': 'quant',
        'params': {'window': 21},
        'metrics': {'win_rate': 0.62, 'sharpe': 1.25}
    }

    resp = client.post('/api/strategy/publish', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['strategy']['name'] == payload['name']

    list_resp = client.get('/api/strategy/list')
    assert list_resp.status_code == 200
    listed = list_resp.get_json()['strategies']
    assert any(s['name'] == payload['name'] for s in listed)

    sid = data['strategy']['id']
    get_resp = client.get(f'/api/strategy/{sid}')
    assert get_resp.status_code == 200
    assert get_resp.get_json()['strategy']['id'] == sid


def test_list_pagination_and_filters(client):
    # Seed multiple strategies
    strategies = [
        {'name': 'Alpha', 'description': 'Alpha strat', 'archetype': 'quant', 'metrics': {'win_rate': 0.7, 'sharpe': 1.3}},
        {'name': 'Beta', 'description': 'Beta strat', 'archetype': 'degen', 'metrics': {'win_rate': 0.55, 'sharpe': 0.6}},
        {'name': 'Gamma', 'description': 'Gamma strat', 'archetype': 'quant', 'metrics': {'win_rate': 0.8, 'sharpe': 1.8}},
        {'name': 'Delta', 'description': 'Delta strat', 'archetype': 'warren', 'metrics': {'win_rate': 0.65, 'sharpe': 0.9}},
    ]

    for s in strategies:
        payload = {**s}
        client.post('/api/strategy/publish', json=payload)

    # Test pagination (per_page=2)
    resp1 = client.get('/api/strategy/list?page=1&per_page=2')
    assert resp1.status_code == 200
    data1 = resp1.get_json()
    assert data1['page'] == 1
    assert data1['per_page'] == 2
    assert data1['total'] >= 4
    assert len(data1['strategies']) == 2

    # Test archetype filter
    qresp = client.get('/api/strategy/list?archetype=quant')
    assert qresp.status_code == 200
    qdata = qresp.get_json()
    assert all(s['archetype'] == 'quant' for s in qdata['strategies'])

    # Test min_sharpe filter
    hresp = client.get('/api/strategy/list?min_sharpe=1.5')
    assert hresp.status_code == 200
    hdata = hresp.get_json()
    assert all((s.get('metrics', {}).get('sharpe', 0) >= 1.5) for s in hdata['strategies'])


def test_total_pages_calculation(client):
    # Seed additional strategies to ensure multiple pages
    for i in range(7):
        client.post('/api/strategy/publish', json={'name': f'P{i}', 'archetype': 'quant', 'metrics': {'sharpe': 0.5 + i*0.1}})

    resp = client.get('/api/strategy/list?page=1&per_page=3')
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['per_page'] == 3
    assert data['total'] >= 7
    assert data['total_pages'] == (data['total'] + 3 - 1) // 3


def test_sorting_and_top_endpoint(client):
    # Ensure sorting by sharpe returns highest-sharpe first
    resp = client.get('/api/strategy/list?sort_by=sharpe&order=desc')
    assert resp.status_code == 200
    data = resp.get_json()
    strategies = data['strategies']
    if len(strategies) >= 2:
        assert strategies[0].get('metrics', {}).get('sharpe', 0) >= strategies[1].get('metrics', {}).get('sharpe', 0)

    # Test top endpoint
    top_resp = client.get('/api/strategy/top?limit=2&metric=sharpe')
    assert top_resp.status_code == 200
    top = top_resp.get_json()['strategies']
    assert len(top) <= 2
    # The top strategies should be sorted by sharpe desc
    if len(top) >= 2:
        assert top[0].get('metrics', {}).get('sharpe', 0) >= top[1].get('metrics', {}).get('sharpe', 0)
