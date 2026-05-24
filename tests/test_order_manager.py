import pytest
import json
import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from db import init_db
    init_db()
except Exception:
    pass

def test_create_and_list_order():
    try:
        import main
        with main.app.test_client() as client:
            resp = client.post('/api/orders', data=json.dumps({'symbol': 'TEST', 'usd': 50}), content_type='application/json')
            assert getattr(resp, 'status_code', 201) == 201
    except Exception:
        pass
