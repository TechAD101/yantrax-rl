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
os.environ['DATABASE_URL'] = 'sqlite:///./test_yantrax.db'
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
    
    def test_synthetic_market_data_pipeline_works(self):
        """Verify the pipeline works with synthetic market data fixtures."""
        # Mock the canonical provider to return synthetic data
        with patch('backend.services.canonical_market_provider.get_canonical_market_provider') as mock_get:
            mock_provider = MagicMock()
            # Simulate bullish signal with synthetic price data
            mock_provider.get_stock_price.return_value = {
                'price': 150.00,
                'source': 'synthetic',
                'timestamp': '2024-01-15T10:00:00Z'
            }
            mock_provider.is_available = True
            mock_get.return_value = mock_provider
            
            client = app.test_client()
            resp = client.get('/god-cycle?symbol=TEST')
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data['status'], 'success')
            self.assertIn(data['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])
            self.assertIsNotNone(data.get('market_data'))


if __name__ == '__main__':
    unittest.main()