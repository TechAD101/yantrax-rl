"""Learning-loop tests (mission §18, §37 learning tests)."""

import asyncio
import os
import sys
import unittest

os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.db import reset_engine, get_engine  # noqa: E402
from backend.models import Base, PaperPosition, Outcome, Attribution, LearningEvent  # noqa: E402
reset_engine()
Base.metadata.create_all(get_engine())


class TestLearningLoop(unittest.TestCase):

    def setUp(self):
        # Fresh in-memory DB per test
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        # Reset the learning coordinator's applied event ids to avoid interference between tests
        from backend.services.learning_coordinator import _coordinator
        if _coordinator is not None:
            _coordinator._applied_event_ids.clear()

    def test_agent_manager_bounded_confidence_update(self):
        from backend.ai_firm.agent_manager import AgentManager
        am = AgentManager()
        name = next(iter(am.enhanced_agents))
        am.enhanced_agents[name]['confidence'] = 0.5

        self.assertTrue(am.apply_confidence_update(name, 0.52))
        self.assertEqual(am.enhanced_agents[name]['confidence'], 0.52)
        # Bounded: extreme updates clamp
        am.apply_confidence_update(name, 5.0)
        self.assertEqual(am.enhanced_agents[name]['confidence'], 0.99)
        am.apply_confidence_update(name, -1.0)
        self.assertEqual(am.enhanced_agents[name]['confidence'], 0.1)
        # Unknown agent ignored
        self.assertFalse(am.apply_confidence_update('nonexistent_agent', 0.5))

    def _get_bearish_market_data(self):
        class BearishMarketData:
            def get_stock_price(self, symbol):
                print(f"BEARISH MARKET DATA: get_stock_price called for {symbol}")
                return {
                    'symbol': symbol.upper(),
                    'price': 1.0,  # Extremely low price to induce SELL
                    'change_percent': -99.0,  # From 100 to 1 is a 99% decline
                    'trend': 'bearish',
                    'volume': 2000000,
                    'volatility': 0.05,
                    'source': 'test_fixture',
                    'verified': True,
                }

            def get_fundamentals(self, symbol):
                # Poor fundamentals to reinforce SELL
                return {
                    'pe_ratio': 1.0,
                    'return_on_equity': 0.01,
                    'debt_to_equity': 2.0,
                    'revenue_growth': -0.5,
                    'earnings_growth': -0.5,
                    'profit_margin': 0.01,
                }

            def get_price_history(self, symbol, days):
                # Create a price history that consistently declines from 100 to 1.0 over the given days
                # We want the last price in the history to match the current price (1.0)
                start = 100.0
                end = 1.0
                if days == 1:
                    step = 0
                else:
                    step = (start - end) / (days - 1)
                history = []
                for i in range(days):
                    price = start - step * i
                    history.append(round(price, 2))
                return [{'close': close} for close in history]
        return BearishMarketData()

    def _get_bearish_sentiment_service(self):
        class BearishSentimentService:
            def get_comprehensive_sentiment(self, symbol):
                return {
                    'symbol': symbol,
                    'composite_sentiment': -0.8,
                    'recommendation': 'SELL',
                    'confidence': 0.9,
                    'components': {
                        'fear_greed': {
                            'fear_greed_index': 0.2,  # Very fearful (adjusted to avoid LIQUIDITY_CRUNCH)
                        },
                        'options_flow': {
                            'flow_score': 0.1,  # Weak options flow
                        },
                        'social_sentiment': {
                            'overall_sentiment': 0.1,  # Bearish social sentiment
                        },
                    },
                }
        return BearishSentimentService()

    def test_full_trade_updates_measured_state(self):
        """A complete paper trade must measurably update agent and strategy state."""
        from tests.test_full_pipeline import TestMarketData, TestSentimentService
        from backend.core.decision_pipeline import DecisionPipeline
        from backend.core.decision_context import TradingAction
        from backend.services.learning_coordinator import get_learning_coordinator
        from backend.db import get_session

        # First decision: open position (BUY signal) with normal market data
        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        ctx1 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertEqual(ctx1.final_action, TradingAction.BUY)
        self.assertIsNone(ctx1.outcome_id)  # No outcome until position is closed
        self.assertIsNotNone(ctx1.position_id)  # Position opened

        # Capture the strategy engine state before the second decision
        engine_before = pipeline.strategy_engine.min_confidence_threshold

        # Clear trade validator history to allow reversal (close BUY, open SELL)
        from backend.services.trade_validator import get_trade_validator
        validator = get_trade_validator()
        validator.trade_history.clear()

        # Second decision: opposite signal (SELL) with bearish market data and sentiment
        # Use mock strategy engine to inject SELL signal for the bearish fixture
        from tests.mock_strategy_engine import MockStrategyEngineForBearishFixture
        pipeline2 = DecisionPipeline(
            market_data=self._get_bearish_market_data(),
            sentiment_service=self._get_bearish_sentiment_service(),
            strategy_engine=MockStrategyEngineForBearishFixture(),
        )
        ctx2 = asyncio.run(pipeline2.execute_decision('AAPL'))
        # Now we expect the position from ctx1 to be closed and a new position (SELL) opened? 
        # Actually, our logic: 
        #   - In the second decision, we first check for an open position (we find the one from ctx1).
        #   - Because the signal is SELL and the existing position is BUY (opposite), we close the existing position.
        #   - Then we proceed to create a new position for the SELL signal.
        # So we end up with: 
        #   - The original position (BUY) closed (with outcome, attribution, learning events).
        #   - A new position (SELL) opened (no outcome yet).
        self.assertEqual(ctx2.final_action, TradingAction.SELL)
        self.assertIsNotNone(ctx2.outcome_id)  # Outcome from the closed BUY position
        self.assertIsNotNone(ctx2.position_id)  # Position ID of the new SELL position

        # Check database
        session = get_session()
        try:
            # We should have two PaperPositions: one closed (BUY) and one open (SELL)
            positions = session.query(PaperPosition).all()
            self.assertEqual(len(positions), 2)
            closed_count = sum(1 for p in positions if p.status == 'CLOSED')
            open_count = sum(1 for p in positions if p.status == 'OPEN')
            self.assertEqual(closed_count, 1)
            self.assertEqual(open_count, 1)
            closed_pos = [p for p in positions if p.status == 'CLOSED'][0]
            open_pos = [p for p in positions if p.status == 'OPEN'][0]
            self.assertEqual(closed_pos.side, 'BUY')
            self.assertEqual(open_pos.side, 'SELL')
            # Check that the closed position has an outcome
            outcomes = session.query(Outcome).all()
            self.assertEqual(len(outcomes), 1)
            outcome = outcomes[0]
            self.assertEqual(outcome.symbol, 'AAPL')
            self.assertEqual(outcome.action, 'BUY')  # The action of the closed position
            self.assertIsNotNone(outcome.pnl)
            # Check attributions and learning events from the closed outcome
            attributions = session.query(Attribution).all()
            self.assertGreater(len(attributions), 0)
            learning_events = session.query(LearningEvent).all()
            self.assertGreater(len(learning_events), 0)
        finally:
            session.close()

        # 1. Learning events persisted (from the closed outcome)
        session = get_session()
        try:
            events = session.query(LearningEvent).filter_by(outcome_id=ctx2.outcome_id).all()
            self.assertGreater(len(events), 0)
        finally:
            session.close()

        # 2. Coordinator applied them to live components
        applied = ctx2.provenance.get('position_closed', {}).get('details', {}).get('details', {}).get('learning_applied', {})
        self.assertGreater(applied.get('events_applied', 0), 0)
        self.assertTrue(ctx2.learning_event_ids)

        # 3. Measured agent history exists
        stats = pipeline.learning_coordinator.get_agent_stats()
        self.assertGreater(len(stats), 0)
        any_agent = next(iter(stats))
        self.assertGreaterEqual(stats[any_agent]['decisions'], 1)  # at least one decision that produced a learning event (the second decision)
        self.assertIn('accuracy', stats[any_agent])

        # 4. AgentManager confidence demonstrably moved from realized outcome
        am = pipeline.agent_manager
        moved = [name for name, a in am.enhanced_agents.items()
                 if name in applied.get('agent_confidence_updates', {})]
        self.assertGreater(len(moved), 0)

        # 5. Strategy engine measured state updated
        self.assertGreaterEqual(pipeline.strategy_engine.measured_outcomes, 1)
        self.assertNotEqual(pipeline.strategy_engine.min_confidence_threshold, engine_before)

        # 6. Experience retrievable for future decisions (DB-backed)
        experience = pipeline.learning_coordinator.get_relevant_experience('AAPL', limit=5)
        self.assertGreater(len(experience), 0)
        self.assertIn('event_type', experience[0])

    def test_experience_provenance_recorded(self):
        from tests.test_full_pipeline import TestMarketData, TestSentimentService
        from backend.core.decision_pipeline import DecisionPipeline
        from backend.services.learning_coordinator import get_learning_coordinator
        from backend.db import get_session

        coordinator = get_learning_coordinator()
        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        # First decision: open position (BUY) -> no outcome, no learning events
        asyncio.run(pipeline.execute_decision('AAPL'))
        # Clear trade validator history to allow reversal (close BUY, open SELL)
        from backend.services.trade_validator import get_trade_validator
        validator = get_trade_validator()
        validator.trade_history.clear()
        # Second decision: opposite signal (SELL) -> close the position, produce outcome, attribution, learning events
        # Use mock strategy engine to inject SELL signal for the bearish fixture
        from tests.mock_strategy_engine import MockStrategyEngineForBearishFixture
        pipeline2 = DecisionPipeline(
            market_data=self._get_bearish_market_data(),
            sentiment_service=self._get_bearish_sentiment_service(),
            strategy_engine=MockStrategyEngineForBearishFixture(),
        )
        ctx2 = asyncio.run(pipeline2.execute_decision('AAPL'))
        # Now the learning events from the closed position have been applied by the coordinator.
        # Third decision: should see the learned experience in the provenance.
        ctx3 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertIn('learned_experience', ctx3.provenance)
        self.assertGreater(ctx3.provenance['learned_experience']['details']['events_recalled'], 0)


if __name__ == '__main__':
    unittest.main()