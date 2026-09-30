import os
import sys
import unittest
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.decision_pipeline import DecisionPipeline
from backend.core.decision_context import DecisionContext, TradingAction, GovernanceState
from backend.attribution.attribution_engine import AttributionEngine
from backend.models import Outcome, Attribution, LearningEvent, JournalEntry
from backend.db import init_db, get_session
from backend.service_registry import registry


class TestMarketData:
    def get_stock_price(self, symbol):
        return {
            'symbol': symbol.upper(),
            'price': 150.0,
            'change_percent': 0.5,
            'volume': 1000000,
            'volatility': 0.02,
            'source': 'test_fixture',
            'verified': True,
        }

    def get_fundamentals(self, symbol):
        return {}

    def get_price_history(self, symbol, days):
        return [{'close': 150.0} for _ in range(days)]


class TestFullPipeline(unittest.TestCase):
    """Test the full paper-trade lifecycle from market snapshot to learning."""

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        from backend.db import reset_engine, get_engine
        from backend.models import Base
        reset_engine()
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def setUp(self):
        self.pipeline = DecisionPipeline(market_data=TestMarketData())
        self.session = get_session()
        self.session.query(LearningEvent).delete()
        self.session.query(Attribution).delete()
        self.session.query(Outcome).delete()
        self.session.query(JournalEntry).delete()
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_full_lifecycle_buy_trade(self):
        """Test a complete BUY trade through all 13 stages."""
        import asyncio
        ctx = asyncio.run(self.pipeline.execute_decision('AAPL'))

        self.assertIsNotNone(ctx.decision_id)
        self.assertTrue(ctx.decision_id.startswith('dec_'))
        self.assertEqual(ctx.symbol, 'AAPL')
        self.assertIsNotNone(ctx.market_snapshot)
        self.assertEqual(ctx.market_snapshot.symbol, 'AAPL')
        self.assertIsNotNone(ctx.evidence)
        self.assertIsNotNone(ctx.evidence.technical)
        self.assertIsNotNone(ctx.evidence.fundamental)
        self.assertIsNotNone(ctx.evidence.sentiment)
        self.assertIsNotNone(ctx.candidate_strategy)
        self.assertIsNotNone(ctx.candidate_strategy.action)
        self.assertIsNotNone(ctx.voting_result)
        self.assertGreater(len(ctx.voting_result.votes), 0)
        self.assertIsNotNone(ctx.debate_result)
        self.assertIsNotNone(ctx.debate_result.winning_signal)
        self.assertIsNotNone(ctx.ceo_decision)
        self.assertIsNotNone(ctx.ceo_decision.action)
        self.assertIsNotNone(ctx.risk_state)
        self.assertIsNotNone(ctx.risk_governance)
        self.assertIn(ctx.risk_governance, [GovernanceState.APPROVE, GovernanceState.WARNING, GovernanceState.BLOCK])

        if ctx.risk_governance != GovernanceState.BLOCK:
            self.assertGreater(ctx.final_position_size, 0)
            self.assertIsNotNone(ctx.order_id)
            self.assertIsNotNone(ctx.execution_id)
            self.assertIsNotNone(ctx.outcome_id)
            outcome = self.session.query(Outcome).filter_by(id=ctx.outcome_id).first()
            self.assertIsNotNone(outcome)
            self.assertEqual(outcome.decision_id, ctx.decision_id)
            self.assertEqual(outcome.symbol, 'AAPL')
            self.assertIn(outcome.action, [TradingAction.BUY, TradingAction.SELL])
            self.assertIsNotNone(ctx.attribution_id)
            attribution = self.session.query(Attribution).filter_by(id=ctx.attribution_id).first()
            self.assertIsNotNone(attribution)
            self.assertEqual(attribution.outcome_id, ctx.outcome_id)
            self.assertGreater(len(attribution.attributions), 0)
            self.assertAlmostEqual(
                attribution.total_attributed_pnl + attribution.residual_pnl,
                attribution.net_pnl,
                places=2,
                msg="Attribution math should balance",
            )
            self.assertIsNotNone(ctx.learning_event_id)
            learning_event = self.session.query(LearningEvent).filter_by(id=ctx.learning_event_id).first()
            self.assertIsNotNone(learning_event)
            self.assertEqual(learning_event.outcome_id, ctx.outcome_id)
            self.assertIn(learning_event.event_type, ['confidence_update', 'strategy_metric_update', 'memory_store'])

            expected_stages = [
                'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
                'ceo_governance', 'risk', 'position_sizing', 'execution', 'outcome_attribution'
            ]
        else:
            expected_stages = [
                'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
                'ceo_governance', 'risk'
            ]

        for stage in expected_stages:
            self.assertIn(stage, ctx.provenance, f"Missing provenance for stage: {stage}")

        if ctx.risk_governance != GovernanceState.BLOCK:
            self.assertEqual(attribution.outcome.decision_id, ctx.decision_id)
            self.assertEqual(learning_event.outcome.decision_id, ctx.decision_id)

    def test_blocked_trade_provenance(self):
        """Test that a blocked trade preserves provenance without outcome."""
        import asyncio
        asyncio.run(self.pipeline.execute_decision('AAPL'))

        from backend.services.emotional_safeguards import get_emotional_safeguards
        safeguards = get_emotional_safeguards()
        safeguards._state = safeguards._state.__class__.MOUNA
        ctx_blocked = asyncio.run(self.pipeline.execute_decision('AAPL'))

        self.assertEqual(ctx_blocked.risk_governance, GovernanceState.BLOCK,
                         "Trade should be blocked when in MOUNA mode")
        self.assertIsNone(ctx_blocked.outcome_id)
        self.assertIn('risk', ctx_blocked.provenance)
        self.assertNotIn('execution', ctx_blocked.provenance)
        self.assertNotIn('outcome_attribution', ctx_blocked.provenance)
        self.assertIsNotNone(ctx_blocked.decision_id)
        safeguards._state = safeguards._state.__class__.CALM

    def test_attribution_engine_directly(self):
        """Test the attribution engine in isolation."""
        engine = AttributionEngine()
        from backend.attribution.attribution_engine import OutcomeRecord
        from datetime import datetime

        outcome = OutcomeRecord(
            outcome_id='out_test123',
            decision_id='dec_test123',
            order_id='order_test123',
            fill_id='fill_test123',
            symbol='AAPL',
            action='BUY',
            requested_size=10,
            filled_size=10,
            requested_price=150.0,
            filled_price=150.0,
            stop_loss=140.0,
            take_profit=160.0,
            decision_timestamp=datetime.utcnow(),
            order_timestamp=datetime.utcnow(),
            fill_timestamp=datetime.utcnow(),
            close_timestamp=datetime.utcnow(),
            gross_pnl=100.0,
            net_pnl=100.0,
            commission=1.0,
            slippage=0.5,
            spread_cost=0.0,
            market_price_at_decision=150.0,
            market_regime_at_decision='bull_market',
            volatility_at_decision=0.2,
            market_price_at_close=160.0,
            market_regime_at_close='bull_market',
            volatility_at_close=0.2,
            strategy_name='institutional',
            strategy_confidence=0.8,
            agent_votes={'consensus_strength': 0.7, 'technical_confidence': 0.8, 'fundamental_confidence': 0.7, 'sentiment_confidence': 0.6},
            debate_result={'winning_signal': 'BUY', 'consensus_score': 0.75},
            ceo_decision={'final_signal': 'BUY', 'confidence': 0.85, 'override_applied': False, 'reasoning': 'Strong fundamentals'},
            risk_governance='APPROVE',
            position_size_method='kelly'
        )
        attributed_outcome = engine.attribute_outcome(outcome)
        self.assertIsNotNone(attributed_outcome)
        self.assertEqual(attributed_outcome.outcome_id, outcome.outcome_id)
        self.assertEqual(attributed_outcome.net_pnl, 100.0)
        self.assertGreater(len(attributed_outcome.attributions), 0)


if __name__ == '__main__':
    unittest.main()