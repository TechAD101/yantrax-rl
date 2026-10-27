import os
os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'

import json
from main import app


def test_create_and_list_order():
    client = app.test_client()

    # create order with explicit price (fail-closed: no synthetic fallback)
    resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50, 'price': 150.0}), content_type='application/json')
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'order' in data
    order = data['order']
    assert order['symbol'] == 'TEST'
    assert order['usd'] == 50
    assert order['price'] == 150.0

    # list orders
    resp2 = client.get('/api/orders')
    assert resp2.status_code == 200
    data2 = resp2.get_json()
    assert 'orders' in data2
    assert any(o['symbol'] == 'TEST' for o in data2['orders'])


def test_create_order_missing_price_fails_closed():
    """Fail-closed: missing price without simulation_mode must return 400."""
    client = app.test_client()
    resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50}), content_type='application/json')
    assert resp.status_code == 400
    assert 'price' in resp.get_json().get('error', '').lower()


def test_create_order_zero_price_fails_closed():
    """Fail-closed: zero price must be rejected."""
    client = app.test_client()
    resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50, 'price': 0}), content_type='application/json')
    assert resp.status_code == 400
    assert 'price' in resp.get_json().get('error', '').lower()


def test_create_order_negative_price_fails_closed():
    """Fail-closed: negative price must be rejected."""
    client = app.test_client()
    resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50, 'price': -5.0}), content_type='application/json')
    assert resp.status_code == 400
    assert 'price' in resp.get_json().get('error', '').lower()
