"""Crisis-scenario harness (mission §25).

Deterministic scenario matrix traced through the full canonical pipeline:
Market -> Evidence -> Strategy -> Agents -> Debate -> Ghost -> CEO -> Risk
-> Execution decision. Architecture validation, not theatrics: every scenario
asserts an explicit, deterministic outcome and a complete provenance chain.
"""
import asyncio
import copy
import json
import os
import sys
import unittest

os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.db import reset_engine, get_engine  # noqa: E402
from backend.models import Base  # noqa: E402
reset_engine()
Base.metadata.create_all(get_engine())

from tests.test_full_pipeline import TestMarketData, TestSentimentService  # noqa: E402
from backend.core.decision_pipeline import DecisionPipeline  # noqa: E402
from backend.core.decision_context import TradingAction  # noqa: E402
from backend.services.emotional_safeguards import (  # noqa: E402
    get_emotional_safeguards, EmotionalState,
)

REQUIRED_STAGES = [
    'market_snapshot', 'strategy_candidate',
    'agent_voting', 'debate', 'ceo_governance',
]

# Evidence synthesis either succeeds (evidence_synthesis) or fails closed
# explicitly (evidence_synthesis_error).
EVIDENCE_STAGES = ['evidence_synthesis', 'evidence_synthesis_error']


def scenario_provider(base: TestMarketData, overrides: dict):
    """Deterministic provider fixture with explicit scenario overrides."""
    class ScenarioProvider(TestMarketData):
        def get_stock_price(self, symbol):
            quote = base.get_stock_price(symbol)
            quote.update(copy.deepcopy(overrides))
            quote['source'] = 'scenario_fixture'
            quote['verified'] = True
            return quote
    return ScenarioProvider()


class CrisisScenarioTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.safeguards = get_emotional_safeguards()

    def tearDown(self):
        self.safeguards._state = EmotionalState.CALM
        self.safeguards._cooling_off_until = None

    def _run(self, provider=None):
        pipeline = DecisionPipeline(
            market_data=provider or TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))
        return ctx

    def _assert_traceable(self, ctx, full=True):
        """Every scenario must carry a complete provenance chain up to its stop point."""
        self.assertIn('market_snapshot', ctx.provenance)
        self.assertTrue(any(s in ctx.provenance for s in EVIDENCE_STAGES),
                        'evidence synthesis must be traceable (success or explicit fail-closed)')
        if full:
            for stage in REQUIRED_STAGES:
                self.assertIn(stage, ctx.provenance, f'missing provenance stage: {stage}')
            self.assertIsNotNone(ctx.evidence)
            self.assertIsNotNone(ctx.candidate_strategy)
        self.assertIsNotNone(ctx.decision_id)

    # ── Market scenarios ────────────────────────────────────────────
    def test_normal_market_base_scenario(self):
        ctx = self._run()
        self._assert_traceable(ctx)
        self.assertIn(ctx.final_action, [TradingAction.BUY, TradingAction.HOLD])

    def test_high_volatility_blocks_direction(self):
        ctx = self._run(scenario_provider(TestMarketData(), {
            'volatility': 0.65, 'trend': 'bearish', 'change_percent': -5.0,
        }))
        self._assert_traceable(ctx)
        # Extreme volatility must never produce a confidently sized BUY
        if ctx.final_action == TradingAction.BUY:
            self.assertLess(ctx.final_confidence, 0.5)

    def test_liquidity_crunch_fails_closed(self):
        # Provider returns no history at all -> strategy cannot run -> explicit failure
        class NoHistory(TestMarketData):
            def get_price_history(self, symbol, days):
                return []
        ctx = self._run(NoHistory())
        self._assert_traceable(ctx, full=False)
        self.assertNotEqual(ctx.final_action, TradingAction.BUY)

    def test_data_failure_fails_closed(self):
        class DeadProvider(TestMarketData):
            def get_stock_price(self, symbol):
                raise RuntimeError('provider outage')
        ctx = self._run(DeadProvider())
        self.assertNotEqual(ctx.final_action, TradingAction.BUY)
        prov = json.dumps(ctx.provenance)
        self.assertIn('market_snapshot_error', prov)

    # ── Governance scenarios ────────────────────────────────────────
    def test_mouna_trigger_blocks_execution(self):
        self.safeguards.manual_override(reason='crisis drill')
        ctx = self._run()
        self._assert_traceable(ctx)
        self.assertIsNone(ctx.order_id)
        self.assertEqual(ctx.final_position_size, 0.0)

    def test_missing_market_provider_abstains(self):
        pipeline = DecisionPipeline(market_data=None, sentiment_service=TestSentimentService())
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertEqual(ctx.final_action, TradingAction.ABSTAIN)
        self.assertIn('market_snapshot_error', ctx.provenance)

    # ── Execution scenarios ─────────────────────────────────────────
    def test_execution_failure_is_visible_not_silent(self):
        from backend.core.decision_pipeline import create_order
        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        # Force executor failure
        import backend.core.decision_pipeline as dp
        orig = dp.create_order
        def failing_order(symbol, usd):
            raise RuntimeError('execution venue unavailable')
        dp.create_order = failing_order
        try:
            ctx = asyncio.run(pipeline.execute_decision('AAPL'))
        finally:
            dp.create_order = orig
        if ctx.final_action == TradingAction.BUY:
            self.assertIn('execution_error', ctx.provenance)
            self.assertIsNone(ctx.order_id)
            self.assertIsNone(ctx.outcome_id)


if __name__ == '__main__':
    unittest.main()