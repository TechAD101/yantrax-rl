import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time

# Add backend to path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from services.market_data_service_waterfall import WaterfallMarketDataService

class TestWaterfallService(unittest.TestCase):
    def setUp(self):
        self.patcher_env = patch.dict(os.environ, {
            'FMP_API_KEY': 'test_fmp_key',
            'ALPACA_API_KEY': 'test_alpaca_key',
            'ALPACA_SECRET_KEY': 'test_alpaca_secret',
            'ALPHAVANTAGE_API_KEY': 'test_av_key',
            'FMP_DAILY_LIMIT': '1000'
        })
        self.patcher_env.start()

        self.service = WaterfallMarketDataService()

        # Clear cache for isolation
        self.service.cache['price'] = {}
        self.service.cache['fundamentals'] = {}
        self.service.audit_log = []

    def tearDown(self):
        self.patcher_env.stop()

    def test_init_providers(self):
        self.assertTrue(self.service.providers['fmp']['enabled'])
        self.assertTrue(self.service.providers['alpaca']['enabled'])
        self.assertTrue(self.service.providers['alpha_vantage']['enabled'])
        self.assertTrue(self.service.providers['yfinance']['enabled'])

    def test_get_price_yfinance_success(self):
        mock_yf = MagicMock()
        mock_ticker = MagicMock()
        mock_ticker.fast_info.last_price = 150.0
        mock_yf.Ticker.return_value = mock_ticker

        with patch.dict(sys.modules, {'yfinance': mock_yf}):
            result = self.service.get_price('AAPL')
            self.assertEqual(result['price'], 150.0)
            self.assertEqual(result['source'], 'yfinance')

    def test_get_price_fmp_fallback(self):
        mock_yf = MagicMock()
        mock_yf.Ticker.side_effect = Exception("YFinance Error")
        mock_requests = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{'price': 155.0}]
        mock_requests.get.return_value = mock_resp

        with patch.dict(sys.modules, {'yfinance': mock_yf, 'requests': mock_requests}):
            result = self.service.get_price('AAPL')
            self.assertEqual(result['price'], 155.0)
            self.assertEqual(result['source'], 'fmp')

    def test_get_price_alpaca_fallback(self):
        mock_yf = MagicMock()
        mock_yf.Ticker.side_effect = Exception("YF Error")

        mock_requests = MagicMock()
        def side_effect(url, **kwargs):
            if 'financialmodelingprep' in url:
                raise Exception("FMP Error")
            if 'alpaca' in url:
                r = MagicMock()
                r.status_code = 200
                r.json.return_value = {'quote': {'ap': 160.0}}
                return r
            return MagicMock()
        mock_requests.get.side_effect = side_effect

        with patch.dict(sys.modules, {'yfinance': mock_yf, 'requests': mock_requests}):
            result = self.service.get_price('AAPL')
            self.assertEqual(result['price'], 160.0)
            self.assertEqual(result['source'], 'alpaca')

    def test_get_price_all_fail(self):
        mock_yf = MagicMock()
        mock_yf.Ticker.side_effect = Exception("YFinance Error")
        mock_requests = MagicMock()
        mock_requests.get.side_effect = Exception("API Error")

        with patch.dict(sys.modules, {'yfinance': mock_yf, 'requests': mock_requests}):
            result = self.service.get_price('AAPL')
            self.assertEqual(result['source'], 'error')
            self.assertEqual(result['price'], 0.0)

    def test_caching(self):
        mock_yf = MagicMock()
        mock_ticker = MagicMock()
        mock_ticker.fast_info.last_price = 150.0
        mock_yf.Ticker.return_value = mock_ticker

        with patch.dict(sys.modules, {'yfinance': mock_yf}):
            result1 = self.service.get_price('AAPL')
            self.assertEqual(result1['price'], 150.0)

        mock_yf_2 = MagicMock()
        mock_yf_2.Ticker.side_effect = Exception("Fail")
        with patch.dict(sys.modules, {'yfinance': mock_yf_2}):
            result2 = self.service.get_price('AAPL')
            self.assertEqual(result2['price'], 150.0)
            self.assertIn('(cached)', result2['source'])

    def test_get_fundamentals_yfinance(self):
        mock_yf = MagicMock()
        mock_ticker = MagicMock()
        mock_ticker.info = {'trailingPE': 20.5}
        mock_yf.Ticker.return_value = mock_ticker

        with patch.dict(sys.modules, {'yfinance': mock_yf}):
            result = self.service.get_fundamentals('AAPL')
            self.assertEqual(result['pe_ratio'], 20.5)
            self.assertEqual(result['source'], 'yfinance')

    def test_get_fundamentals_fmp_fallback(self):
        mock_yf = MagicMock()
        mock_yf.Ticker.side_effect = Exception("YF Error")
        mock_requests = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [{'peRatioTTM': 22.0}]
        mock_requests.get.return_value = mock_resp

        with patch.dict(sys.modules, {'yfinance': mock_yf, 'requests': mock_requests}):
            result = self.service.get_fundamentals('AAPL')
            self.assertEqual(result['pe_ratio'], 22.0)
            self.assertEqual(result['source'], 'fmp')

    def test_get_fundamentals_mock_fallback(self):
        mock_yf = MagicMock()
        mock_yf.Ticker.side_effect = Exception("YF Error")
        mock_requests = MagicMock()
        mock_requests.get.side_effect = Exception("FMP Error")

        with patch.dict(sys.modules, {'yfinance': mock_yf, 'requests': mock_requests}):
            result = self.service.get_fundamentals('AAPL')
            self.assertEqual(result['source'], 'mock')
            self.assertEqual(result['pe_ratio'], 15.0)

    def test_get_price_verified_consensus(self):
        with patch.object(self.service, '_fetch_price_yfinance', return_value=150.0),              patch.object(self.service, '_fetch_price_fmp', return_value=150.1),              patch.object(self.service, '_fetch_price_alpha_vantage', return_value=150.05):

            result = self.service.get_price_verified('AAPL')
            self.assertEqual(result['price'], 150.05)
            self.assertEqual(result['verification']['status'], 'verified')

    def test_get_price_verified_variance(self):
        with patch.object(self.service, '_fetch_price_yfinance', return_value=150.0),              patch.object(self.service, '_fetch_price_fmp', return_value=160.0),              patch.object(self.service, '_fetch_price_alpha_vantage', return_value=140.0):

            result = self.service.get_price_verified('AAPL')
            self.assertEqual(result['price'], 150.0)
            self.assertEqual(result['verification']['status'], 'variance_flag')

    def test_get_price_verified_failure(self):
        with patch.object(self.service, '_fetch_price_yfinance', side_effect=Exception("Error")),              patch.object(self.service, '_fetch_price_fmp', return_value=None),              patch.object(self.service, '_fetch_price_alpha_vantage', return_value=None):

            result = self.service.get_price_verified('AAPL')
            self.assertIsNone(result['price'])
            self.assertEqual(result['verification']['status'], 'failed')

    def test_audit_logs_and_stats(self):
        with patch.object(self.service, '_fetch_price_yfinance', return_value=150.0),              patch.object(self.service, '_fetch_price_fmp', return_value=150.1),              patch.object(self.service, '_fetch_price_alpha_vantage', return_value=150.0):

            self.service.get_price_verified('AAPL')
            stats = self.service.get_verification_stats()
            self.assertEqual(stats['total_verifications'], 1)
            self.assertEqual(stats['successful_verifications'], 1)
            logs = self.service.get_recent_audit_logs()
            self.assertEqual(len(logs), 1)

if __name__ == '__main__':
    unittest.main()
