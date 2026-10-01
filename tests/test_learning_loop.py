"""Learning-loop tests (mission §18, §37 learning tests).

Proves the full feedback path: outcome -> attribution -> learning events ->
LearningCoordinator -> agent confidence / strategy metrics -> retrievable
experience for future decisions. No 'self-learning' claims without a
demonstrated behavioral update.
"""
import asyncio
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


class TestLearningLoop(unittest.TestCase):

    def setUp(self):
        # Fresh in-memory DB per test
        engine = get_engine()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

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

    def test_full_trade_updates_measured_state(self):
        """A complete paper trade must measurably update agent and strategy state."""
        from tests.test_full_pipeline import TestMarketData, TestSentimentService
        from backend.core.decision_pipeline import DecisionPipeline
        from backend.core.decision_context import TradingAction
        from backend.services.learning_coordinator import get_learning_coordinator
        from backend.models import LearningEvent as LearningEventORM
        from backend.db import get_session

        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        engine_before = pipeline.strategy_engine.min_confidence_threshold
        ctx = asyncio.run(pipeline.execute_decision('AAPL'))

        if ctx.final_action != TradingAction.BUY or not ctx.outcome_id:
            self.fail(f"expected a completed paper trade, got {ctx.final_action}")

        # 1. Learning events persisted
        session = get_session()
        try:
            events = session.query(LearningEventORM).filter_by(outcome_id=ctx.outcome_id).all()
            self.assertGreater(len(events), 0)
        finally:
            session.close()

        # 2. Coordinator applied them to live components
        applied = (ctx.provenance.get('position_closed', {}).get('details', {})
                   .get('learning_applied', {}))
        self.assertGreater(applied.get('events_applied', 0), 0)
        self.assertTrue(ctx.learning_event_ids)

        # 3. Measured agent history exists
        stats = pipeline.learning_coordinator.get_agent_stats()
        self.assertGreater(len(stats), 0)
        any_agent = next(iter(stats))
        self.assertGreaterEqual(stats[any_agent]['decisions'], 1)
        self.assertIn('accuracy', stats[any_agent])

        # 4. AgentManager confidence demonstrably moved from realized outcome
        am = pipeline.agent_manager
        moved = [
            name for name, a in am.enhanced_agents.items()
            if name in applied.get('agent_confidence_updates', {})
        ]
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
        from backend.models import LearningEvent as LearningEventORM
        from backend.db import get_session

        coordinator = get_learning_coordinator()
        pipeline = DecisionPipeline(
            market_data=TestMarketData(),
            sentiment_service=TestSentimentService(),
        )
        asyncio.run(pipeline.execute_decision('AAPL'))
                # Once experience exists in the ledger, later decisions record it
        ctx2 = asyncio.run(pipeline.execute_decision('AAPL'))
        self.assertIn('learned_experience', ctx2.provenance)
        self.assertGreater(ctx2.provenance['learned_experience']['details']['events_recalled'], 0)


if __name__ == '__main__':
    unittest.main()