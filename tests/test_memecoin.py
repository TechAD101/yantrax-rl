import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from db import init_db


def setup_module(module):
    init_db()


def test_scan_and_top():
    import main
    client = main.app.test_client()

    # Scan
    resp = client.post('/api/memecoin/scan', json={'symbols': ['TEST1', 'TEST2', 'TEST3']})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'results' in data
    assert len(data['results']) == 3

    # Top
    top = client.get('/api/memecoin/top?limit=2')
    assert top.status_code == 200
    mems = top.get_json()['memecoins']
    assert len(mems) <= 2


def test_simulate_trade():
    import main
    client = main.app.test_client()

    # Simulate without symbol
    bad = client.post('/api/memecoin/simulate', json={'usd': 50})
    assert bad.status_code == 400

    # Simulate with symbol
    ok = client.post('/api/memecoin/simulate', json={'symbol': 'TEST1', 'usd': 100})
    assert ok.status_code == 200
    res = ok.get_json()['result']
    assert res['symbol'] == 'TEST1'
    assert 'quantity' in res
