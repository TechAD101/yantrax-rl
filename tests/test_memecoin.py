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

def test_get_top_memecoins_direct():
    from memecoin_service import get_top_memecoins
    from db import get_session
    from models import Memecoin

    session = get_session()
    # Insert test data
    coins_data = [
        ('COIN_A', 10.5),
        ('COIN_B', 50.2),
        ('COIN_C', 5.1),
        ('COIN_D', 10000.0),  # very high to ensure it's at the top
        ('COIN_E', 25.5)
    ]

    for symbol, score in coins_data:
        m = session.query(Memecoin).filter_by(symbol=symbol).first()
        if not m:
            session.add(Memecoin(symbol=symbol, score=score))
        else:
            m.score = score
    session.commit()

    try:
        # Test default limit
        results_default = get_top_memecoins()
        assert len(results_default) <= 10
        assert len(results_default) >= 5 # since we inserted 5

        # Assert sorting
        scores = [r['score'] for r in results_default]
        assert scores == sorted(scores, reverse=True)
        assert results_default[0]['symbol'] == 'COIN_D'

        # Test specific limit
        results_limit = get_top_memecoins(limit=3)
        assert len(results_limit) == 3
        assert results_limit[0]['symbol'] == 'COIN_D'
        assert results_limit[0]['score'] >= results_limit[1]['score']
        assert results_limit[1]['score'] >= results_limit[2]['score']
    finally:
        # cleanup
        for symbol, _ in coins_data:
            session.query(Memecoin).filter_by(symbol=symbol).delete()
        session.commit()
        session.close()
