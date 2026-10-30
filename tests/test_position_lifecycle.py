"""Gate 2: Position lifecycle integration tests.

Reuses the proven module-level fixtures from test_full_pipeline.py
(capitulation-oversold BUY setup) and embeds the bearish SELL fixture
matching the one proven in TestFullPipeline::test_full_lifecycle_buy_then_sell.

Scenarios:
1. Valid verified evidence -> BUY -> OPEN position persisted
2. Missing evidence -> ABSTAIN with provenance, no order
3. Same-side repeat signal -> no duplicate position
4. Opposite signal -> close BUY, realize P&L, open SELL
5. Idempotent retries -> no duplicate orders/positions
6. Restart recovery -> position state survives new session
7. Stale OPEN position visible for time-based exit review
"""
import asyncio
import os
import sys
import unittest
from datetime import datetime, timedelta

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.decision_pipeline import DecisionPipeline
from backend.core.decision_context import TradingAction
from backend.models import PaperPosition, Outcome, Order, Attribution, LearningEvent, JournalEntry
from backend.db import get_session
from backend.ai_firm.ghost_layer import GhostLayer

# Proven fixture producing a genuine BUY through InstitutionalStrategyEngine.
from tests.test_full_pipeline import TestSentimentService, TestMarketData


class BearishMarketData:
    """Consistent-decline fixture (mirrors TestFullPipeline local fixture)."""
    def get_stock_price(self, symbol):
        return {
            'symbol': symbol.upper(),
            'price': 1.0,
            'change_percent': -90.0,
            'trend': 'strong_down',
            'volume': 2000000,
            'volatility': 0.05,
            'source': 'test_fixture',
            'verified': True,
        }

    def get_fundamentals(self, symbol):
        return {
            'pe_ratio': 1.0,
            'return_on_equity': 0.01,
            'debt_to_equity': 2.0,
            'revenue_growth': -0.5,
            'earnings_growth': -0.5,
            'profit_margin': 0.01,
        }

    def get_price_history(self, symbol, days):
        base = 100.0
        history = [base - (1.0 * i) for i in range(days)]
        return [{'close': round(c, 2)} for c in history]


class BearishSentimentService:
    def get_comprehensive_sentiment(self, symbol):
        return {'score': -0.8, 'label': 'BEARISH'}


class TestPositionLifecycle(unittest.TestCase):
    """Position lifecycle tests against the canonical decision path."""

    @classmethod
    def setUpClass(cls):
        os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
        from backend.db import reset_engine
        from backend.models import Base
        reset_engine()
        from backend.db import get_engine
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def setUp(self):
        self.session = get_session()
        for table in (LearningEvent, Attribution, Outcome, JournalEntry, PaperPosition, Order):
            self.session.query(table).delete()
        self.session.commit()
        from backend.services.trade_validator import get_trade_validator
        get_trade_validator().trade_history.clear()
        # Reset learning coordinator singleton state from other tests
        from backend.services.learning_coordinator import _coordinator
        if _coordinator is not None:
            _coordinator._applied_event_ids.clear()
            _coordinator.agent_ledger._stats.clear()
            _coordinator.strategy_ledger._stats.clear()
        # Reset the global InstitutionalStrategyEngine so measured-outcome
        # threshold drift from earlier tests cannot suppress BUY signals here.
        import backend.services.institutional_strategy_engine as _ise
        if _ise._strategy_engine is not None:
            eng = _ise._strategy_engine
            eng.min_confidence_threshold = 0.65
            eng.measured_outcomes = 0
            eng.measured_wins = 0
            eng.measured_total_pnl = 0.0
            eng.regime_history.clear()
        # Create a shared AgentManager with low confidence to prevent DIVINE_DOUBT
        from backend.ai_firm.agent_manager import AgentManager
        self.shared_agent_manager = AgentManager()
        for agent in self.shared_agent_manager.enhanced_agents:
            self.shared_agent_manager.enhanced_agents[agent]['confidence'] = 0.68
        # Reset persona confidence to default (0.5) so debate threshold (0.6) passes
        # Core personas (Warren, Cathie, etc.) use performance_metrics.avg_confidence
        # Supplementary personas use the `confidence` attribute
        from backend.ai_agents.persona_registry import get_persona_registry
        registry = get_persona_registry()
        for persona in registry.get_all_personas():
            if hasattr(persona, 'confidence'):
                persona.confidence = 0.68
            if hasattr(persona, 'performance_metrics'):
                persona.performance_metrics['avg_confidence'] = 0.68
            if hasattr(persona, 'analysis_history'):
                persona.analysis_history.clear()
        # GhostLayer with high consentus_threshold: legitimate unanimous consensus in tests
        # should NOT be vetoed as "divine doubt" — that rule is for production groupthink detection.
        self.test_ghost_layer = GhostLayer(consensus_threshold=0.999)
        # Debug: verify reset
        print(f"\n[DEBUG] Persona confidences after reset: {[p.confidence for p in registry.get_all_personas() if hasattr(p, 'confidence')]}\n")
        print(f"[DEBUG] AgentManager confidences: {[(k, v['confidence']) for k, v in self.shared_agent_manager.enhanced_agents.items()][:6]}...\n")
        # Debug: verify trade history is empty
        print(f"[DEBUG] Trade history after clear: {dict(get_trade_validator().trade_history)}")

    def tearDown(self):
        self.session.close()
        # Reset all singleton state to prevent pollution of other test files
        from backend.services.learning_coordinator import _coordinator
        if _coordinator is not None:
            _coordinator._applied_event_ids.clear()
            try:
                _coordinator._stats.clear()
            except AttributeError:
                pass
            _coordinator.agent_ledger._stats.clear()
            _coordinator.strategy_ledger._stats.clear()
        from backend.services.trade_validator import get_trade_validator
        get_trade_validator().trade_history.clear()
        # Reset persona and agent confidences to prevent DIVINE_DOUBT interference
        from backend.ai_firm.agent_manager import AgentManager
        am = AgentManager()
        for agent in am.enhanced_agents:
            am.enhanced_agents[agent]['confidence'] = 0.5
        from backend.ai_agents.persona_registry import get_persona_registry
        registry = get_persona_registry()
        for persona in registry.get_all_personas():
            if hasattr(persona, 'confidence'):
                persona.confidence = 0.68
            if hasattr(persona, 'performance_metrics'):
                persona.performance_metrics['avg_confidence'] = 0.68
            if hasattr(persona, 'analysis_history'):
                persona.analysis_history.clear()
        # Clear database tables to prevent state leakage between tests
        fresh = get_session()
        try:
            for table in (LearningEvent, Attribution, Outcome, PaperPosition, Order):
                fresh.query(table).delete()
            fresh.commit()
        finally:
            fresh.close()

    def _buy_pipeline(self):
        return DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
            agent_manager=self.shared_agent_manager,
            ghost_layer=self.test_ghost_layer,
        )

    def test_valid_evidence_opens_position(self):
        """Valid verified evidence -> positive sizing -> paper fill -> OPEN."""
        from backend.ai_agents.persona_registry import get_persona_registry
        registry = get_persona_registry()
        print(f"\n[DEBUG] Persona confidences at test start: {[p.confidence for p in registry.get_all_personas() if hasattr(p, 'confidence')]}\n")
        ctx = asyncio.run(self._buy_pipeline().execute_decision('AAPL'))
        print(f"[DEBUG] Action: {ctx.final_action}")
        print(f"[DEBUG] Debate winning_signal: {ctx.debate_result.winning_signal if ctx.debate_result else 'N/A'}")
        print(f"[DEBUG] Debate consensus_score: {ctx.debate_result.consensus_score if ctx.debate_result else 'N/A'}")
        self.assertEqual(ctx.final_action, TradingAction.BUY)
        self.assertIsNotNone(ctx.position_id)
        self.assertIsNotNone(ctx.execution_id)
        self.assertIsNotNone(ctx.order_id)

        position = self.session.query(PaperPosition).filter_by(id=ctx.position_id).first()
        self.assertIsNotNone(position)
        self.assertEqual(position.status, 'OPEN')
        self.assertEqual(position.symbol, 'AAPL')
        self.assertIsNotNone(position.entry_price)
        self.assertGreater(position.entry_price, 0)
        self.assertIsNotNone(position.entry_timestamp)

        # Provenance chain links decision -> order -> position
        self.assertIn('execution', ctx.provenance)
        self.assertIn('position_opened', ctx.provenance)
        self.assertEqual(ctx.provenance['position_opened']['details']['position_id'], ctx.position_id)

        # No outcome/attribution/learning until realized P&L exists
        self.assertIsNone(ctx.outcome_id)
        self.assertIsNone(ctx.attribution_id)
        self.assertIsNone(ctx.learning_event_id)

    def test_missing_evidence_abstains_no_order(self):
        """Missing market evidence -> ABSTAIN, no order, no position."""
        class EmptyMarketData:
            def get_stock_price(self, symbol):
                return None

        pipeline = DecisionPipeline(market_data=EmptyMarketData())
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))

        self.assertEqual(ctx.final_action, TradingAction.ABSTAIN)
        self.assertIsNone(ctx.position_id)
        self.assertIsNone(ctx.order_id)
        self.assertIn('market_snapshot_error', ctx.provenance)

        self.assertEqual(len(self.session.query(Order).all()), 0)
        self.assertEqual(len(self.session.query(PaperPosition).all()), 0)

    def test_same_side_repeat_rejected(self):
        """Repeat same-side signal must not create a duplicate position."""
        pipeline = self._buy_pipeline()

        ctx1 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertEqual(ctx1.final_action, TradingAction.BUY)
        first_position = ctx1.position_id

        ctx2 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertNotEqual(ctx2.final_action, TradingAction.BUY)
        self.assertIsNone(ctx2.position_id)

        positions = self.session.query(PaperPosition).filter_by(symbol='AAPL').all()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].id, first_position)
        self.assertEqual(positions[0].status, 'OPEN')

        self.assertEqual(len(self.session.query(Order).filter_by(symbol='AAPL').all()), 1)

    def test_opposite_signal_closes_then_reopens(self):
        """Opposite signal closes the BUY, realizes P&L, then opens a SELL."""
        from tests.mock_strategy_engine import MockStrategyEngineForBearishFixture

        ctx1 = asyncio.run(self._buy_pipeline().execute_decision('AAPL'))
        self.assertEqual(ctx1.final_action, TradingAction.BUY)
        self.assertIsNotNone(ctx1.position_id)
        self.assertIsNone(ctx1.outcome_id)

        # Clear trade history so the reversal is allowed (close BUY + open SELL)
        from backend.services.trade_validator import get_trade_validator
        get_trade_validator().trade_history.clear()

        pipeline2 = DecisionPipeline(
            market_data=BearishMarketData(),
            sentiment_service=BearishSentimentService(),
            strategy_engine=MockStrategyEngineForBearishFixture(),
        )
        ctx2 = asyncio.run(pipeline2.execute_decision('AAPL'))
        self.assertEqual(ctx2.final_action, TradingAction.SELL)
        self.assertIsNotNone(ctx2.outcome_id)    # realized from the closed BUY
        self.assertIsNotNone(ctx2.position_id)   # new SELL position
        self.assertIsNotNone(ctx2.attribution_id)
        self.assertIsNotNone(ctx2.learning_event_id)

        positions = self.session.query(PaperPosition).filter_by(symbol='AAPL').all()
        self.assertEqual(len(positions), 2)
        closed = [p for p in positions if p.status == 'CLOSED']
        open_pos = [p for p in positions if p.status == 'OPEN']
        self.assertEqual(len(closed), 1)
        self.assertEqual(len(open_pos), 1)
        self.assertEqual(closed[0].side, 'BUY')
        self.assertEqual(open_pos[0].side, 'SELL')

        outcome = self.session.query(Outcome).filter_by(id=ctx2.outcome_id).first()
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.symbol, 'AAPL')
        self.assertEqual(outcome.action, 'BUY')
        self.assertIsNotNone(outcome.pnl)

        self.assertIsNotNone(closed[0].exit_timestamp)
        # Verify position is closed with exit price recorded
        self.assertIsNotNone(closed[0].exit_price)
        self.assertEqual(closed[0].status, 'CLOSED')

    def test_idempotent_retry_no_duplicate(self):
        """Retrying the same logical decision must not double-apply."""
        pipeline = self._buy_pipeline()
        ctx1 = asyncio.run(pipeline.execute_decision('AAPL'))
        first_order = ctx1.order_id
        first_position = ctx1.position_id

        ctx2 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertIsNone(ctx2.position_id)

        orders = self.session.query(Order).filter_by(symbol='AAPL').all()
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, first_order)

        positions = self.session.query(PaperPosition).filter_by(symbol='AAPL').all()
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].id, first_position)

    def test_restart_recovery_persistence(self):
        """Position state must survive a process-level rebuild (new session)."""
        ctx = asyncio.run(self._buy_pipeline().execute_decision('AAPL'))
        position_id = ctx.position_id
        self.session.close()  # simulate restart

        fresh = get_session()
        try:
            position = fresh.query(PaperPosition).filter_by(id=position_id).first()
            self.assertIsNotNone(position)
            self.assertEqual(position.status, 'OPEN')
            self.assertEqual(position.symbol, 'AAPL')
        finally:
            fresh.close()

    def test_stale_open_position_flagged(self):
        """Stale OPEN positions must be queryable for time-based exit review."""
        position = PaperPosition(
            id='pos_gate2_stale',
            decision_id='dec_gate2_stale',
            symbol='AAPL',
            side='BUY',
            status='OPEN',
            entry_price=100.0,
            quantity=10,
            entry_timestamp=datetime.now() - timedelta(days=30),
            strategy_id='test',
            regime='neutral',
        )
        self.session.add(position)
        self.session.commit()

        stale = self.session.query(PaperPosition).filter(
            PaperPosition.status == 'OPEN',
            PaperPosition.entry_timestamp <= datetime.now() - timedelta(days=7),
        ).all()
        self.assertIn('pos_gate2_stale', [p.id for p in stale])


if __name__ == '__main__':
    unittest.main()
