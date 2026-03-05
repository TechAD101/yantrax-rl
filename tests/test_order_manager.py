import json
import pytest
from main import app
from db import get_session, init_db
from models import Portfolio

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_create_and_list_order(client):
    # Ensure default portfolio exists
    session = get_session()
    try:
        if not session.query(Portfolio).filter_by(name="Default Paper Portfolio").first():
            p = Portfolio(name="Default Paper Portfolio", owner_id=1, initial_capital=100000.0)
            session.add(p)
            session.commit()
    finally:
        session.close()

    # create order
    resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50}), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'order' in data
    order = data['order']
    assert order['symbol'] == 'TEST'
    assert order['usd'] == 50

    # list orders
    resp2 = client.get('/api/orders')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert 'orders' in data2
    assert any(o['symbol'] == 'TEST' for o in data2['orders'])
