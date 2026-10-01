"""Mouna Mode governance tests (mission §14).

Mouna must be a deterministic, auditable, enforceable trading-suppression
state: RiskGovernor vetoes while Mouna is active, the canonical pipeline
fails closed to HOLD without execution, and the emotional-state endpoint
exposes the real state to the frontend.
"""
import json
import os
import sys
import unittest

os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app  # noqa: E402


class MounaGovernanceTest(unittest.TestCase):

    def setUp(self):
        from backend.services.emotional_safeguards import get_emotional_safeguards
        self.safeguards = get_emotional_safeguards()
        self._reset()
        app.config['TESTING'] = True

    def tearDown(self):
        self._reset()

    def _reset(self):
        from backend.services.emotional_safeguards import EmotionalState
        self.safeguards._state = EmotionalState.CALM
        self.safeguards._cooling_off_until = None

    def test_mouna_blocks_trading(self):
        self.assertTrue(self.safeguards.is_trading_allowed()['allowed'])
        self.safeguards.manual_override(reason='governance test')
        status = self.safeguards.is_trading_allowed()
        self.assertFalse(status['allowed'])
        self.assertEqual(status['emotional_state'], 'mouna')

    def test_risk_governor_vetoes_mouna(self):
        import asyncio
        from backend.risk.risk_governor import RiskGovernor, GovernanceState
        from backend.core.decision_context import DecisionContext, TradingAction

        self.safeguards.manual_override(reason='governance test')
        ctx = DecisionContext(symbol='AAPL')
        ctx.market_snapshot = None
        result = RiskGovernor().evaluate_preliminary(ctx)
        self.assertIn(result.overall, [GovernanceState.VETO, GovernanceState.BLOCK])

    def test_pipeline_fails_closed_under_mouna(self):
        import asyncio
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        from backend.db import reset_engine, get_engine
        from backend.models import Base
        reset_engine()
        Base.metadata.create_all(get_engine())
        from tests.test_full_pipeline import TestMarketData, TestSentimentService
        from backend.core.decision_pipeline import DecisionPipeline
        from backend.core.decision_context import TradingAction
        from backend.models import Order

        self.safeguards.manual_override(reason='mouna pipeline test')
        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))

        self.assertEqual(ctx.final_action, TradingAction.HOLD)
        self.assertIsNone(ctx.order_id, 'Mouna must prevent execution')
        self.assertIn(ctx.risk_governance.value, ('veto', 'block', 'VETO', 'BLOCK'))
        risk_prov = json.dumps(ctx.provenance.get('risk', {}))
        self.assertIn('mouna', risk_prov.lower())
        self.assertEqual(ctx.final_position_size, 0.0)

    def test_emotional_state_endpoint(self):
        client = app.test_client()
        resp = client.get('/api/emotional-state')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('emotional_state', data)
        self.assertIn('governance_mode', data)
        self.assertIn('trading_allowed', data)

        self.safeguards.manual_override(reason='endpoint test')
        resp = client.get('/api/emotional-state')
        data = resp.get_json()
        self.assertEqual(data['governance_mode'], 'MOUNA')
        self.assertFalse(data['trading_allowed'])


if __name__ == '__main__':
    unittest.main()
