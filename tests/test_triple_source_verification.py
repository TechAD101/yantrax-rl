import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List, Optional
from datetime import datetime
import concurrent.futures

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock dependencies before importing
mock_requests = MagicMock()
mock_yfinance = MagicMock()
sys.modules['requests'] = mock_requests
sys.modules['yfinance'] = mock_yfinance

import services.triple_source_verification_methods as v_methods

class MockWaterfallService:
    def __init__(self):
        self.audit_log = []
        self.verification_stats = {
            'total_verifications': 0,
            'successful_verifications': 0,
            'variance_flags': 0,
            'partial_verifications': 0,
            'failed_verifications': 0
        }
        self.providers = {
            'fmp': {
                'enabled': True,
                'key': 'test_fmp_key',
                'limiter': MagicMock()
            },
            'alpha_vantage': {
                'enabled': True,
                'key': 'test_av_key',
                'limiter': MagicMock()
            }
        }

    # Bind the methods
    get_price_verified = v_methods.get_price_verified
    _compute_variance = v_methods._compute_variance
    _create_audit_entry = v_methods._create_audit_entry
    get_recent_audit_logs = v_methods.get_recent_audit_logs
    get_verification_stats = v_methods.get_verification_stats
    _fetch_price_yfinance = v_methods._fetch_price_yfinance
    _fetch_price_fmp = v_methods._fetch_price_fmp
    _fetch_price_alpha_vantage = v_methods._fetch_price_alpha_vantage

@pytest.fixture
def service():
    return MockWaterfallService()

@pytest.fixture(autouse=True)
def reset_mocks():
    mock_requests.reset_mock()
    mock_requests.get.side_effect = None
    mock_requests.get.return_value = MagicMock()

    mock_yfinance.reset_mock()
    mock_yfinance.Ticker.side_effect = None
    mock_yfinance.Ticker.return_value = MagicMock()

def test_compute_variance(service):
    # Single value
    assert service._compute_variance([100.0]) == 0.0

    # Two values, median is 110.0 (index 1 of [100.0, 110.0])
    # Deviations: |100-110|/110 = 0.090909; |110-110|/110 = 0.
    assert service._compute_variance([100.0, 110.0]) == pytest.approx(10/110)

    # Three values: [100, 105, 110], median is 105.
    assert service._compute_variance([100.0, 105.0, 110.0]) == pytest.approx(5/105)

def test_fetch_price_yfinance_success(service):
    mock_ticker = MagicMock()
    mock_yfinance.Ticker.return_value = mock_ticker
    mock_history = MagicMock()
    mock_history.empty = False
    mock_history.__getitem__.return_value.iloc.__getitem__.return_value = 150.0
    mock_ticker.history.return_value = mock_history

    price = service._fetch_price_yfinance("AAPL")
    assert price == 150.0

def test_fetch_price_yfinance_failure(service):
    mock_yfinance.Ticker.side_effect = Exception("YF Error")
    price = service._fetch_price_yfinance("AAPL")
    assert price is None

def test_fetch_price_fmp_success(service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{'price': 151.0}]
    mock_requests.get.return_value = mock_response

    price = service._fetch_price_fmp("AAPL")
    assert price == 151.0
    service.providers['fmp']['limiter'].increment.assert_called()

def test_fetch_price_fmp_failure(service):
    mock_requests.get.side_effect = Exception("FMP Error")
    price = service._fetch_price_fmp("AAPL")
    assert price is None

def test_fetch_price_alpha_vantage_success(service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'Global Quote': {'05. price': '152.0'}}
    mock_requests.get.return_value = mock_response

    price = service._fetch_price_alpha_vantage("AAPL")
    assert price == 152.0
    service.providers['alpha_vantage']['limiter'].increment.assert_called()

def test_fetch_price_alpha_vantage_failure(service):
    mock_requests.get.side_effect = Exception("AV Error")
    price = service._fetch_price_alpha_vantage("AAPL")
    assert price is None

def test_get_price_verified_all_success_low_variance(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=100.0), \
         patch.object(service, '_fetch_price_fmp', return_value=100.1), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=99.9):

        result = service.get_price_verified("AAPL")

        assert result['symbol'] == 'AAPL'
        assert result['price'] == 100.0
        assert result['verification']['status'] == 'verified'
        assert result['verification']['confidence'] == 0.95

def test_get_price_verified_high_variance(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=100.0), \
         patch.object(service, '_fetch_price_fmp', return_value=90.0), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=110.0):

        result = service.get_price_verified("AAPL")

        assert result['price'] == 100.0
        assert result['verification']['status'] == 'variance_flag'
        assert result['verification']['confidence'] == 0.80

def test_get_price_verified_partial(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=100.0), \
         patch.object(service, '_fetch_price_fmp', return_value=100.1), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=None):

        result = service.get_price_verified("AAPL")

        assert result['price'] == 100.1
        assert result['verification']['status'] == 'partial'
        assert result['verification']['confidence'] == 0.75

def test_get_price_verified_unverified(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=100.0), \
         patch.object(service, '_fetch_price_fmp', return_value=None), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=None):

        result = service.get_price_verified("AAPL")

        assert result['price'] == 100.0
        assert result['verification']['status'] == 'unverified'
        assert result['verification']['confidence'] == 0.50

def test_get_price_verified_failed(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=None), \
         patch.object(service, '_fetch_price_fmp', return_value=None), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=None):

        result = service.get_price_verified("AAPL")

        assert result['price'] is None
        assert result['verification']['status'] == 'failed'
        assert 'error' in result

def test_audit_logs_and_stats(service):
    with patch.object(service, '_fetch_price_yfinance', return_value=100.0), \
         patch.object(service, '_fetch_price_fmp', return_value=100.0), \
         patch.object(service, '_fetch_price_alpha_vantage', return_value=100.0):

        service.get_price_verified("AAPL")
        service.get_price_verified("MSFT")

    logs = service.get_recent_audit_logs(limit=5)
    assert len(logs) == 2

    stats = service.get_verification_stats()
    assert stats['total_verifications'] == 2
    assert stats['successful_verifications'] == 2
    assert stats['success_rate'] == 1.0
