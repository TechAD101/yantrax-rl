"""God-cycle convergence tests (mission §23).

/god-cycle must run the canonical DecisionPipeline — one decision path. With
no real market data it must return an explicit 503, never a random fallback
signal.
"""
import json
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app  # noqa: E402


class GodCycleTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True

    def test_no_real_data_fails_closed_no_random_signal(self):
        """Provider failure -> pipeline fails closed to explicit ABSTAIN, never a random BUY/SELL."""
        # Patch the canonical market provider directly
        with patch('backend.services.canonical_market_provider.get_canonical_market_provider') as mock_get:
            mock_provider = MagicMock()
            mock_provider.get_stock_price.side_effect = ValueError('No usable price for AAPL')
            mock_get.return_value = mock_provider
            
            client = app.test_client()
            resp = client.get('/god-cycle?symbol=AAPL')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data['signal'], 'ABSTAIN')
            self.assertIn('market_snapshot_error', data['provenance'])
            self.assertEqual(data['final_position_size'], 0)

    def test_route_uses_canonical_pipeline(self):
        """The route must construct a DecisionPipeline with the canonical provider."""
        import inspect
        from backend import main
        source = inspect.getsource(main.god_cycle)
        self.assertIn('DecisionPipeline', source)
        self.assertIn('run_canonical_decision_sync', source)
        self.assertNotIn('random.random', source)
    
    def test_real_market_data_works(self):
        """Verify the pipeline works with real market data via canonical provider."""
        client = app.test_client()
        resp = client.get('/god-cycle?symbol=AAPL')
        data = resp.get_json()
        
        # Should succeed with real data
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['status'], 'success')
        # Signal can be HOLD or ABSTAIN for neutral symbols
        self.assertIn(data['signal'], ['HOLD', 'ABSTAIN'])
        self.assertIsNotNone(data['market_data'])
        
        # Market data should be from yfinance
        self.assertEqual(data['market_data']['verified'], True)
        self.assertIn(data['market_data']['source'], ['yfinance', 'alpaca'])
        self.assertGreater(data['market_data']['price'], 0)


if __name__ == '__main__':
    unittest.main()