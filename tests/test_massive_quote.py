import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_massive_quote_missing_symbol(client):
    """Test /massive-quote missing symbol query parameter"""
    response = client.get('/massive-quote')
    assert response.status_code == 400
    assert response.json == {'status': 'error', 'message': 'symbol query parameter is required'}

@patch.dict(os.environ, clear=True)
def test_massive_quote_missing_api_key(client):
    """Test /massive-quote missing API key environment variable"""
    # ensure these are not in environ
    if 'MASSIVE_API_KEY' in os.environ:
        del os.environ['MASSIVE_API_KEY']
    if 'POLYGON_API_KEY' in os.environ:
        del os.environ['POLYGON_API_KEY']
    if 'POLYGON_KEY' in os.environ:
        del os.environ['POLYGON_KEY']

    response = client.get('/massive-quote?symbol=AAPL')
    assert response.status_code == 400
    assert response.json == {'status': 'error', 'message': 'MASSIVE/POLYGON API key not configured'}

@patch.dict(os.environ, {'MASSIVE_API_KEY': 'test_key', 'MASSIVE_BASE_URL': 'http://test'})
@patch('services.market_data_service_massive.MassiveMarketDataService')
def test_massive_quote_success(mock_massive_service, client):
    """Test /massive-quote successful response"""
    # Setup mock
    instance = mock_massive_service.return_value
    instance.fetch_quote.return_value = {'price': 150.0}

    response = client.get('/massive-quote?symbol=AAPL')

    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['symbol'] == 'AAPL'
    assert response.json['data'] == {'price': 150.0}
    assert 'timestamp' in response.json

@patch.dict(os.environ, {'MASSIVE_API_KEY': 'test_key', 'MASSIVE_BASE_URL': 'http://test'})
@patch('services.market_data_service_massive.MassiveMarketDataService')
def test_massive_quote_service_error(mock_massive_service, client):
    """Test /massive-quote handles service exceptions"""
    # Setup mock
    instance = mock_massive_service.return_value
    instance.fetch_quote.side_effect = Exception("Service unavailable")

    response = client.get('/massive-quote?symbol=AAPL')

    assert response.status_code == 500
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Service unavailable'
    assert response.json['symbol'] == 'AAPL'
    assert 'timestamp' in response.json
