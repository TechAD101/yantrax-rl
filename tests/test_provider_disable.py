import os
import sys
import pytest
from unittest.mock import Mock, patch
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.market_data_service_massive import MassiveMarketDataService


def test_polygon_disabled_after_consecutive_403s():
    msvc = MassiveMarketDataService(api_key='dummy', base_url='https://api.polygon.io')
    # make sure thresholds are small for tests
    msvc._failure_threshold = 2
    msvc._disable_duration = 1  # 1 second

    mock_resp = Mock()
    mock_resp.ok = False
    mock_resp.status_code = 403
    # use a non-entitlement message so the standard disable-by-threshold path is used
    mock_resp.text = '403 Temporary quota exceeded'

    with patch('requests.request', return_value=mock_resp):
        # force fallbacks to fail so polygon failures accumulate
        with patch.object(MassiveMarketDataService, '_try_alpha_vantage', return_value=None):
            with patch.object(MassiveMarketDataService, '_try_yfinance', return_value=None):
                # first failure -> record (no fallback)
                res1 = msvc.fetch_quote('AAPL')
                assert res1.get('price') is None
                # second failure -> should disable provider (still no fallback)
                res2 = msvc.fetch_quote('AAPL')
                assert res2.get('price') is None

    # provider should now be disabled
    assert msvc._is_provider_disabled('polygon') is True

    # wait for disable to expire
    time.sleep(1.1)
    assert msvc._is_provider_disabled('polygon') is False


def test_yfinance_disabled_on_429():
    msvc = MassiveMarketDataService(api_key='dummy', base_url='https://api.polygon.io')
    msvc._failure_threshold = 1
    msvc._disable_duration = 1

    # simulate a 429 style error raised within yfinance wrapper
    # simulate yfinance raising a 429-style exception via _try_yfinance
    with patch.object(MassiveMarketDataService, '_try_yfinance', side_effect=Exception('429 Too Many Requests')):
        with pytest.raises(Exception):
            msvc._try_yfinance('AAPL')
        # record of failure should be added by the wrapper caller; emulate that by recording manually
        msvc._record_provider_failure('yfinance', None, '429 Too Many Requests')
        msvc._maybe_disable_provider('yfinance')

    # after the recorded failure threshold, yfinance should be disabled
    assert msvc._is_provider_disabled('yfinance') is True
    time.sleep(1.1)
    assert msvc._is_provider_disabled('yfinance') is False
