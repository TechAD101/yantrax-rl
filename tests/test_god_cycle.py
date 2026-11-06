"""God-cycle convergence tests (mission §23).

/god-cycle must run the canonical DecisionPipeline — one decision path. With
no real market data it must return ABSTAIN (fail-closed), never a random
BUY/SELL signal.

With synthetic=true query param, the synthetic provider is used so the real
pipeline can be exercised without yfinance.
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

    def test_no_real_data_fails_closed_to_abstain(self):
        """Provider failure -> pipeline fails closed to explicit ABSTAIN, never a random BUY/SELL."""
        with patch('backend.services.canonical_market_provider.get_canonical_market_provider') as mock_get:
            mock_provider = MagicMock()
            mock_provider.get_stock_price.side_effect = ValueError('No usable price for AAPL')
            mock_get.return_value = mock_provider

            client = app.test_client()
            resp = client.get('/god-cycle?symbol=AAPL')
            # Pipeline returns 200 with ABSTAIN (fail-closed), not 503
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data['signal'], 'ABSTAIN')
            self.assertIn('market_snapshot_error', data['provenance'])
            self.assertEqual(data['final_position_size'], 0)

    def test_synthetic_path_returns_success(self):
        """With synthetic=true, the real pipeline runs with deterministic data."""
        client = app.test_client()
        resp = client.get('/god-cycle?symbol=AAPL&synthetic=true')
        # Should return 200 with a valid decision from the pipeline
        self.assertEqual(resp.status_code, 200,
            f"Expected 200 with synthetic data, got {resp.status_code}: {resp.get_json()}")
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn(data['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])
        # Synthetic data must be verified
        self.assertTrue(data['market_data']['verified'])
        self.assertEqual(data['market_data']['source'], 'synthetic_test_fixture')

    def test_run_cycle_synthetic(self):
        """POST /run-cycle with synthetic=true also works."""
        client = app.test_client()
        resp = client.post('/run-cycle',
            json={'symbol': 'AAPL', 'synthetic': True})
        self.assertEqual(resp.status_code, 200,
            f"Expected 200, got {resp.status_code}: {resp.get_json()}")
        data = resp.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn(data['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])
        self.assertEqual(data['data_source'], 'synthetic')

    def test_synthetic_provides_verified_price(self):
        """Synthetic provider must provide verified, deterministic prices."""
        client = app.test_client()
        resp = client.get('/god-cycle?symbol=AAPL&synthetic=true')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        # Verify market snapshot has verified price
        self.assertTrue(data['market_data']['verified'],
            "Synthetic data must be marked as verified")
        self.assertIsInstance(data['market_data']['price'], float)
        # Price should be deterministic (not random)
        # bullish_mean_reversion scenario: 60-day decline from 100 to 41, then bounce
        self.assertEqual(data['market_data']['price'], 41.0)

    def test_route_uses_canonical_pipeline(self):
        """The route must construct a DecisionPipeline with the canonical provider."""
        import inspect
        from backend import main
        source = inspect.getsource(main.god_cycle)
        self.assertIn('DecisionPipeline', source)
        self.assertIn('run_canonical_decision_sync', source)
        self.assertNotIn('random.random', source)
        # Verify synthetic param is supported
        self.assertIn('synthetic', source)

    def test_no_random_decision_generation(self):
        """Ensure no random decision logic exists in god_cycle endpoint."""
        import inspect
        from backend import main
        source = inspect.getsource(main.god_cycle)
        # Should not contain any random decision generation
        self.assertNotIn('random.choice', source)
        self.assertNotIn('randint', source)


class IntegrationTest(unittest.TestCase):
    """Integration tests that exercise the actual endpoint + pipeline."""

    def setUp(self):
        app.config['TESTING'] = True

    def test_end_to_end_synthetic_pipeline(self):
        """Full integration: endpoint -> provider -> pipeline -> response."""
        from backend.services.synthetic_market_provider import SyntheticMarketProvider
        from backend.core.decision_pipeline import DecisionPipeline, run_canonical_decision_sync

        # Use the real synthetic provider (not mocked)
        provider = SyntheticMarketProvider()
        pipeline = DecisionPipeline(market_data=provider)

        # Run the actual pipeline
        ctx = run_canonical_decision_sync('AAPL', pipeline=pipeline)

        # Verify we get a proper decision context back
        self.assertIsNotNone(ctx.decision_id)
        self.assertIn(ctx.final_action.value, ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])
        self.assertIsNotNone(ctx.market_snapshot)
        self.assertTrue(ctx.market_snapshot.verified)
        self.assertIsInstance(ctx.market_snapshot.price, float)
        # Price should be deterministic
        self.assertEqual(ctx.market_snapshot.price, 41.0)  # bullish_mean_reversion scenario

        # Verify provenance chain exists
        self.assertIn('market_snapshot', ctx.provenance)
        self.assertIn('final_decision', ctx.provenance)

    def test_endpoint_integration_with_synthetic(self):
        """Test the full request path through Flask app."""
        client = app.test_client()

        # Make request with synthetic=true
        resp = client.get('/god-cycle?symbol=AAPL&synthetic=true')

        # Verify response structure
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        # Required fields must be present
        self.assertIn('status', data)
        self.assertIn('signal', data)
        self.assertIn('decision_id', data)
        self.assertIn('market_data', data)
        self.assertIn('timestamp', data)

        # Signal must be valid
        self.assertIn(data['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])

        # Market data must show synthetic source and verified
        self.assertEqual(data['market_data']['source'], 'synthetic_test_fixture')
        self.assertTrue(data['market_data']['verified'])
        self.assertEqual(data['market_data']['price'], 41.0)  # bullish_mean_reversion scenario

    def test_god_cycle_and_run_cycle_consistency(self):
        """Both endpoints should produce consistent results with synthetic data."""
        client = app.test_client()

        # GET /god-cycle with synthetic
        resp1 = client.get('/god-cycle?symbol=MSFT&synthetic=true')
        data1 = resp1.get_json()

        # POST /run-cycle with synthetic
        resp2 = client.post('/run-cycle', json={'symbol': 'MSFT', 'synthetic': True})
        data2 = resp2.get_json()

        # Both should succeed
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)

        # Both should have valid signals
        self.assertIn(data1['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])
        self.assertIn(data2['signal'], ['BUY', 'SELL', 'HOLD', 'ABSTAIN'])

        # Both should use synthetic source
        self.assertEqual(data1['market_data']['source'], 'synthetic_test_fixture')
        self.assertEqual(data2['data_source'], 'synthetic')


if __name__ == '__main__':
    unittest.main()
