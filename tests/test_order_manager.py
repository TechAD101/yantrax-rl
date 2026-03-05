import json
from main import app


def test_create_and_list_order():
    import main
    from db import get_session
    from models import Portfolio

    client = app.test_client()

    # Ensure Default Paper Portfolio exists
    with app.app_context():
        session = get_session()
        p = session.query(Portfolio).filter_by(name='Default Paper Portfolio').first()
        if not p:
            p = Portfolio(name='Default Paper Portfolio', initial_capital=100000.0, current_value=100000.0)
            session.add(p)
            session.commit()
            session.refresh(p)
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
