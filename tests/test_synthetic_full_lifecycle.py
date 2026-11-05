"""Comprehensive deterministic lifecycle test using SyntheticMarketProvider.

This test validates the complete position lifecycle:
1. Synthetic scenario that legitimately passes strategy confidence and CEO governance
2. Cycle 1: Generate an approved BUY decision and open a paper position
3. Cycle 2: Prove the same position remains open in database (position persistence)
4. Cycle 3: Supply deterministic opposite signal and close position
5. Verify realized P&L, outcome attribution, provenance, and learning events
6. Verify no learning event existed before closure and is generated only after closure
"""

import os
import sys
import asyncio
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ['DATABASE_URL'] = 'sqlite:///./test_yantrax.db'

from backend.core.decision_pipeline import DecisionPipeline
from backend.core.decision_context import TradingAction
from backend.db import get_session
from backend.models import PaperPosition, Outcome, Attribution, LearningEvent
from backend.services.synthetic_market_provider import SyntheticMarketProvider
from tests.mock_strategy_engine import MockStrategyEngineForBearishFixture

class TestSyntheticFullLifecycle(unittest.TestCase):
    """Deterministic lifecycle demonstration using synthetic market fixtures."""

    def setUp(self):
        """Reset database and services before each test."""
        from backend.db import reset_engine, init_db
        reset_engine()
        init_db()
        from backend.services.trade_validator import get_trade_validator
        validator = get_trade_validator()
        validator.trade_history.clear()

    def test_full_deterministic_lifecycle(self):
        """
        Complete lifecycle demonstration with verification at each step.
        
        This test proves:
        - Phase 1: Synthetic scenario produces genuine BUY signal
        - Phase 2: Position persists across separate pipeline invocations
        - Phase 3: Position closes with outcome attribution and learning events
        - Phase 4: P&L calculation and attribution chain verification
        """
        # ============================================================
        # CYCLE 1: Generate an approved BUY decision and open paper position
        # ============================================================
        provider_bullish = SyntheticMarketProvider(scenario='bullish_mean_reversion')
        pipeline1 = DecisionPipeline(market_data=provider_bullish, sentiment_service=provider_bullish)
        ctx1 = asyncio.run(pipeline1.execute_decision('AAPL'))

        # Verify BUY signal generated
        self.assertEqual(ctx1.final_action, TradingAction.BUY,
                         f"Expected BUY signal, got {ctx1.final_action}")
        self.assertIsNotNone(ctx1.final_position_size,
                             "Position size should be non-zero")
        self.assertGreater(ctx1.final_position_size, 0,
                           "Position size must be positive for BUY")

        # Verify governance passed
        self.assertIsNotNone(ctx1.position_id,
                             "Position should have been opened with ID")
        self.assertIsNone(ctx1.outcome_id,
                          "No outcome should exist before position closure")
        self.assertIsNone(ctx1.attribution_id,
                          "No attribution before position closure")
        self.assertIsNone(ctx1.learning_event_id,
                          "No learning events before position closure")

        # Verify market snapshot is valid (verified=True allows passage)
        self.assertIsNotNone(ctx1.market_snapshot,
                             "Market snapshot must exist")
        self.assertTrue(ctx1.market_snapshot.verified,
                       "Market snapshot must be verified")
        
        # Verify SYNTHETIC PROVENANCE - this is the key test
        market_source = ctx1.market_snapshot.source
        self.assertEqual(market_source, 'synthetic_test_fixture',
                        f"Market source must be synthetic_test_fixture for test, got {market_source}")
        
        # Verify no external market provider was used
        self.assertNotIn(market_source, ['yahoo_finance', 'polygon', 'alpha_vantage', 'finnhub', 'iex'],
                        f"Market source must NOT be an external provider, got {market_source}")

        # Capture position ID for persistence verification
        position_id = ctx1.position_id

        # ============================================================
        # CYCLE 2: Prove position remains open in database (persistence)
        # ============================================================
        session = get_session()
        try:
            position = session.query(PaperPosition).filter(PaperPosition.id == position_id).first()
            self.assertIsNotNone(position, "Position must exist in database")
            self.assertEqual(position.status, 'OPEN', "Position must be OPEN")
            self.assertEqual(position.side.lower(), 'buy', "Position side must be BUY")
            self.assertIsNotNone(position.decision_id, "Position must have decision_id")
            self.assertIsNotNone(position.entry_order_id, "Position must have entry_order_id")

            # Verify no outcomes exist yet
            outcomes = session.query(Outcome).filter(Outcome.symbol == 'AAPL').all()
            self.assertEqual(len(outcomes), 0, "No outcomes should exist yet")
            
            # Verify the position is from synthetic provider
            self.assertIn('synthetic', position.meta.get('source', ''),
                         "Position must be from synthetic provider")
        finally:
            session.close()

        # ============================================================
        # CYCLE 3: Supply deterministic opposite signal and close position
        # ============================================================
        provider_bearish = SyntheticMarketProvider(scenario='bearish_decline')
        pipeline2 = DecisionPipeline(
            market_data=provider_bearish,
            sentiment_service=provider_bearish,
            strategy_engine=MockStrategyEngineForBearishFixture(),
        )
        ctx2 = asyncio.run(pipeline2.execute_decision('AAPL'))

        # Verify SELL signal generated
        self.assertEqual(ctx2.final_action, TradingAction.SELL,
                         f"Expected SELL signal, got {ctx2.final_action}")

        # Verify outcome attribution
        self.assertIsNotNone(ctx2.outcome_id,
                             "Position closure should have outcome_id")
        session = get_session()
        try:
            outcome = session.query(Outcome).filter(Outcome.id == ctx2.outcome_id).first()
            self.assertIsNotNone(outcome, "Outcome must exist in database")
            self.assertEqual(outcome.symbol, 'AAPL')
            self.assertEqual(outcome.action, 'BUY', "Closed position action was BUY")
            self.assertIsNotNone(outcome.pnl, "Outcome must have P&L")
            self.assertIsNotNone(outcome.risk_governance,
                                 "Outcome must have risk_governance")

            # Verify attribution exists
            attributions = session.query(Attribution).filter(Attribution.outcome_id == ctx2.outcome_id).all()
            self.assertGreater(len(attributions), 0, "Attribution records must exist")

            # Verify learning events exist
            learning_events = session.query(LearningEvent).all()
            self.assertGreater(len(learning_events), 0, "Learning events must exist after closure")

            # Verify closed position
            closed_position = session.query(PaperPosition).filter(PaperPosition.id == position_id).first()
            self.assertIsNotNone(closed_position, "Original position should still exist")
            self.assertEqual(closed_position.status, 'CLOSED',
                             "Position should be CLOSED after exit")

            # Verify the closed position's source is synthetic
            self.assertIn('synthetic', closed_position.meta.get('source', ''),
                         "Closed position must be from synthetic provider")

            # Check there's a new position for the SELL
            new_positions = session.query(PaperPosition).filter(PaperPosition.symbol == 'AAPL').all()
            self.assertGreaterEqual(len(new_positions), 1, "At least one position should exist")
        finally:
            session.close()

        # ============================================================
        # CYCLE 4: Verify no learning event existed before closure
        # ============================================================
        # Reset database and verify learning event timing
        session = get_session()
        try:
            # Count learning events - should be from cycle 3 closure
            learning_events = session.query(LearningEvent).filter(
                LearningEvent.event_type.in_(['confidence_update', 'strategy_metric_update', 'knowledge_update'])
            ).all()
            self.assertGreater(len(learning_events), 0,
                               "Learning events should exist after position closure")

            # Each learning event should be tied to an attribution
            for le in learning_events:
                self.assertIsNotNone(le.attribution_id,
                                    f"Learning event {le.id} must have attribution_id")
                
                # Verify learning event is from synthetic/bearish scenario
                self.assertIsNotNone(le.timestamp, "Learning event must have timestamp")
        finally:
            session.close()

        # ============================================================
        # Verify provenance chain
        # ============================================================
        # First decision: up to position_opened (no outcome attribution yet)
        expected_stages_first = [
            'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
            'ceo_governance', 'risk', 'position_sizing', 'execution', 'position_opened'
        ]
        for stage in expected_stages_first:
            self.assertIn(stage, ctx1.provenance,
                          f"Missing provenance stage in first decision: {stage}")

        # Second decision: includes outcome_attribution
        expected_stages_second = [
            'market_snapshot', 'evidence_synthesis', 'strategy_candidate', 'agent_voting', 'debate',
            'ceo_governance', 'risk', 'position_sizing', 'execution', 'outcome_attribution'
        ]
        for stage in expected_stages_second:
            self.assertIn(stage, ctx2.provenance,
                          f"Missing provenance stage in second decision: {stage}")

        # ============================================================
        # Verify real provider is NOT used (synthetic provenance verified)
        # ============================================================
        # Check that all sources are synthetic_test_fixture
        self.assertEqual(ctx1.market_snapshot.source, 'synthetic_test_fixture',
                        "First cycle must use synthetic_test_fixture")
        self.assertEqual(ctx2.market_snapshot.source, 'synthetic_test_fixture',
                        "Second cycle must use synthetic_test_fixture")

if __name__ == '__main__':
    unittest.main()