import os
import sys
import pytest
from unittest.mock import patch, Mock
from datetime import datetime
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.market_data_service_massive import MassiveMarketDataService


def test_fetch_quote_polygon_403_fallback_alpha_vantage():
    msvc = MassiveMarketDataService(api_key='dummy_key', base_url='https://api.polygon.io')

    mock_resp = Mock()
    mock_resp.ok = False
    mock_resp.status_code = 403
    # use a non-entitlement 403 message so fallback providers are attempted
    mock_resp.text = '403 Forbidden: quota exceeded'

    with patch('requests.request', return_value=mock_resp):
        with patch.object(MassiveMarketDataService, '_try_alpha_vantage', return_value=101.0):
            res = msvc.fetch_quote('AAPL')
            assert res.get('price') == 101.0
            assert res.get('source') == 'alpha_vantage'


def test_fetch_quote_timeout_returns_cached():
    msvc = MassiveMarketDataService(api_key='dummy_key', base_url='https://api.polygon.io')
    msvc._last_prices['AAPL'] = {'symbol': 'AAPL', 'price': 42.5, 'source': 'cache', 'timestamp': datetime.now().isoformat()}

    with patch('requests.request', side_effect=requests.exceptions.Timeout()):
        with patch.object(MassiveMarketDataService, '_try_alpha_vantage', return_value=None):
            with patch.object(MassiveMarketDataService, '_try_yfinance', return_value=None):
                res = msvc.fetch_quote('AAPL')
                assert res.get('price') == 42.5
                assert res.get('source') == 'cache'
