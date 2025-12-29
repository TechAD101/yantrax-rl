import os
import sys
import pytest
from unittest.mock import Mock, patch
import requests
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.market_data_service_massive import MassiveMarketDataService


def test_polygon_entitlement_triggers_long_disable():
    msvc = MassiveMarketDataService(api_key='dummy', base_url='https://api.polygon.io')
    msvc._entitlement_disable_seconds = 5

    mock_resp = Mock()
    mock_resp.ok = False
    mock_resp.status_code = 403
    # full JSON body as seen in logs
    mock_resp.text = '{"status":"NOT_AUTHORIZED","request_id":"abc","message":"You are not entitled to this data. Please upgrade your plan"}'

    with patch('requests.request', return_value=mock_resp):
        res = msvc.fetch_quote('AAPL')
        assert res.get('price') is None
        assert res.get('error', {}).get('entitlement_required') is True

    assert msvc._is_provider_disabled('polygon') is True
    # wait for disable to expire
    time.sleep(5.1)
    assert msvc._is_provider_disabled('polygon') is False


def test_yfinance_429_and_json_errors_backoff():
    msvc = MassiveMarketDataService(api_key='dummy', base_url='https://api.polygon.io')
    msvc._failure_threshold = 1
    msvc._disable_duration = 2

    # Simulate JSON parsing error by patching _try_yfinance to raise
    with patch.object(MassiveMarketDataService, '_try_yfinance', side_effect=Exception('Expecting value: line 1 column 1 (char 0)')):
        res = None
        try:
            res = msvc._try_yfinance('AAPL')
        except Exception:
            # _try_yfinance should raise the exception in this patched scenario; ensure we record failure
            msvc._record_provider_failure('yfinance', None, 'Expecting value')
        assert msvc._provider_status.get('yfinance', {}).get('consecutive_failures', 0) >= 1

    # Simulate 429 by patching _try_yfinance to raise 429-style exception
    with patch.object(MassiveMarketDataService, '_try_yfinance', side_effect=Exception('429 Too Many Requests')):
        try:
            msvc._try_yfinance('AAPL')
        except Exception:
            msvc._record_provider_failure('yfinance', None, '429 Too Many Requests')
            msvc._maybe_disable_provider('yfinance')
        assert msvc._is_provider_disabled('yfinance') is True
        time.sleep(2.1)
        assert msvc._is_provider_disabled('yfinance') is False
