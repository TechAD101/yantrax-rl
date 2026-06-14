import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock missing things before importing main
import sys
sys.modules['alpaca'] = MagicMock()
sys.modules['alpaca.data'] = MagicMock()
sys.modules['alpaca.data.historical'] = MagicMock()
sys.modules['alpaca.data.requests'] = MagicMock()
sys.modules['alpaca.data.timeframe'] = MagicMock()

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_test_fmp_missing_credentials(client):
    with patch('os.getenv', return_value=None):
        resp = client.get('/test-fmp')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'error'
        assert data['message'] == 'FMP credentials not configured'

def test_test_fmp_success_v3(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.status_code = 200
            mock_resp.json.return_value = [{'symbol': 'AAPL', 'price': 150.0}]
            mock_get.return_value = mock_resp

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == 'success'
            assert data['response'] == [{'symbol': 'AAPL', 'price': 150.0}]

            # Verify only first url called
            mock_get.assert_called_once()
            args, kwargs = mock_get.call_args
            assert args[0] == 'https://financialmodelingprep.com/api/v3/quote/AAPL'

def test_test_fmp_fallback_v4(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            # First request fails with 403 legacy
            mock_resp1 = MagicMock()
            mock_resp1.ok = False
            mock_resp1.status_code = 403
            mock_resp1.text = 'Legacy Endpoint error'

            # Second request (v4) succeeds
            mock_resp2 = MagicMock()
            mock_resp2.ok = True
            mock_resp2.status_code = 200
            mock_resp2.json.return_value = [{'symbol': 'AAPL', 'price': 151.0}]

            mock_get.side_effect = [mock_resp1, mock_resp2]

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == 'success'
            assert data['response'] == [{'symbol': 'AAPL', 'price': 151.0}]

            assert mock_get.call_count == 2
            assert mock_get.call_args_list[0][0][0] == 'https://financialmodelingprep.com/api/v3/quote/AAPL'
            assert mock_get.call_args_list[1][0][0] == 'https://financialmodelingprep.com/api/v4/quote/AAPL'

def test_test_fmp_fallback_quote_short(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            # First request fails (not 403 legacy)
            mock_resp1 = MagicMock()
            mock_resp1.ok = False
            mock_resp1.status_code = 500
            mock_resp1.text = 'Internal error'

            # Second request (quote-short) succeeds
            mock_resp2 = MagicMock()
            mock_resp2.ok = True
            mock_resp2.status_code = 200
            mock_resp2.json.return_value = [{'symbol': 'AAPL', 'price': 152.0}]

            mock_get.side_effect = [mock_resp1, mock_resp2]

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == 'success'
            assert data['response'] == [{'symbol': 'AAPL', 'price': 152.0}]

            assert mock_get.call_count == 2
            assert mock_get.call_args_list[0][0][0] == 'https://financialmodelingprep.com/api/v3/quote/AAPL'
            assert mock_get.call_args_list[1][0][0] == 'https://financialmodelingprep.com/api/v3/quote-short/AAPL'

def test_test_fmp_fallback_real_time(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            mock_resp_fail = MagicMock()
            mock_resp_fail.ok = False
            mock_resp_fail.status_code = 500
            mock_resp_fail.text = 'Fail'

            mock_resp_success = MagicMock()
            mock_resp_success.ok = True
            mock_resp_success.status_code = 200
            mock_resp_success.json.return_value = [{'symbol': 'AAPL', 'price': 153.0}]

            mock_get.side_effect = [mock_resp_fail, mock_resp_fail, mock_resp_success]

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data['status'] == 'success'
            assert data['response'] == [{'symbol': 'AAPL', 'price': 153.0}]

            assert mock_get.call_count == 3
            assert mock_get.call_args_list[2][0][0] == 'https://financialmodelingprep.com/api/v3/stock/real-time-price/AAPL'

def test_test_fmp_all_fail(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            mock_resp_fail = MagicMock()
            mock_resp_fail.ok = False
            mock_resp_fail.status_code = 404
            mock_resp_fail.text = 'Not Found'
            mock_resp_fail.json.side_effect = ValueError("Invalid JSON") # Test fallback parsing

            mock_get.return_value = mock_resp_fail

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 404
            data = resp.get_json()
            assert data['status'] == 'error'
            assert data['response_status'] == 404
            assert data['response'] == {'error': 'invalid_response', 'text': 'Not Found'}

def test_test_fmp_exception(client):
    with patch('os.getenv', return_value='fake_key'):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Connection Refused")

            resp = client.get('/test-fmp?symbol=AAPL')
            assert resp.status_code == 500
            data = resp.get_json()
            assert data['status'] == 'error'
            assert data['message'] == 'Connection Refused'
