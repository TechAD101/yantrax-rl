import json
import sys
import os
import pytest

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_and_list_order(client):
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
