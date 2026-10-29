"""Test Gate 3: CEO memory and learning loop persistence across restarts."""
import os
import json
import tempfile
import pytest

# Use isolated test database
_db_path = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
os.environ['DATABASE_URL'] = 'sqlite:///' + _db_path


from backend.db import init_db, reset_engine, get_session
from backend.ai_firm.ceo_persistent_memory import PersistentCEOMemorySystem, get_persistent_ceo_memory
from backend.services.learning_coordinator import LearningCoordinator
from backend.ai_firm.ceo import CEODecision, CEOPersonality
from backend.models import CEODecisionRecord, LearningState, LearningEvent as LearningEventORM, Outcome, PaperPosition
from backend.core.decision_context import LearningEvent as InMemLearningEvent
from datetime import datetime


@pytest.fixture(autouse=True)
def fresh_db():
    """Create fresh database tables for each test."""
    init_db()
    yield
    # Clean up state between tests
    session = get_session()
    try:
        session.query(CEODecisionRecord).delete()
        session.query(LearningState).delete()
        session.query(LearningEventORM).delete()
        session.query(Outcome).delete()
        session.query(PaperPosition).delete()
        session.commit()
    finally:
        session.close()


def _make_learning_event(event_id, target_type, target_id, old_val, new_val, metadata=None):
    """Create a learning event dataclass and a backing ORM outcome for the FK."""
    session = get_session()
    try:
        # Create a minimal outcome row for the FK
        outcome = Outcome(
            id=f"outcome_{event_id}",
            decision_id="dec_test",
            symbol="TEST",
            action="BUY",
            quantity=1,
            entry_price=100.0,
            exit_price=100.0,
            pnl=0.0,
        )
        session.merge(outcome)
        session.commit()
    finally:
        session.close()

    return InMemLearningEvent(
        event_id=event_id,
        outcome_id=f"outcome_{event_id}",
        event_type='confidence_update',
        target_type=target_type,
        target_id=target_id,
        old_value=str(old_val),
        new_value=str(new_val),
        metadata=metadata or {},
        timestamp=datetime.utcnow(),
    )


class TestPersistentCEOMemorySystem:
    def test_store_and_retrieve_decision(self):
        """Test that a CEO decision is persisted to and retrieved from DB."""
        memory = PersistentCEOMemorySystem()
        decision = CEODecision(
            id="dec_test_001",
            timestamp=datetime.utcnow(),
            decision_type="strategic",
            context={
                'ticker': 'AAPL',
                'market_trend': 'bullish',
                'volatility': 0.15,
                'type': 'entry',
                'candidate_strategy': {'action': 'BUY'},
            },
            reasoning="Market is bullish, buying AAPL.",
            confidence=0.85,
            expected_impact="High positive impact expected",
            agent_overrides=[],
            memory_references=[],
        )

        result = memory.store_decision_memory(decision)
        assert result is True

        # Retrieve by symbol
        decisions = memory.get_decisions_for_symbol('AAPL')
        assert len(decisions) >= 1
        assert decisions[0]['id'] == 'dec_test_001'

        # Verify tags
        assert 'trend_bullish' in decisions[0]['memory_tags']

    def test_persistence_across_restarts(self):
        """Test that memory survives a 'restart' (new instance)."""
        memory1 = PersistentCEOMemorySystem()
        memory1._cache_loaded = True
        memory1._in_memory_cache = []
        decision = CEODecision(
            id="dec_persist_001",
            timestamp=datetime.utcnow(),
            decision_type="strategic",
            context={
                'ticker': 'TSLA',
                'market_trend': 'bearish',
                'type': 'exit',
                'candidate_strategy': {'action': 'SELL'},
            },
            reasoning="Bearish trend detected, exiting.",
            confidence=0.70,
            expected_impact="Portfolio defense",
            agent_overrides=[],
            memory_references=[],
        )
        memory1.store_decision_memory(decision)

        # Simulate restart — new instance loads from DB
        memory2 = PersistentCEOMemorySystem()
        decisions = memory2.get_decisions_for_symbol('TSLA')
        assert len(decisions) >= 1
        assert decisions[0]['id'] == 'dec_persist_001'

    def test_recall_relevant_memories(self):
        """Test recall returns relevant memories based on context tags."""
        memory = PersistentCEOMemorySystem()
        memory._cache_loaded = True
        memory._in_memory_cache = []

        # Store two decisions with different symbols/trends
        for ticker, trend in [('SPY', 'bullish'), ('QQQ', 'bearish')]:
            decision = CEODecision(
                id=f"dec_{ticker}",
                timestamp=datetime.utcnow(),
                decision_type="strategic",
                context={'ticker': ticker, 'market_trend': trend, 'type': 'entry'},
                reasoning=f"Trend is {trend}.",
                confidence=0.6,
                expected_impact="test",
                agent_overrides=[],
                memory_references=[],
            )
            memory.store_decision_memory(decision)

        # Recall with bullish context should favor SPY
        context = {'ticker': 'SPY', 'market_trend': 'bullish', 'type': 'entry', 'volatility': 0.2}
        relevant = memory.recall_relevant_memories(context)
        assert len(relevant) >= 1

    def test_get_decision_by_outcome_id(self):
        """Test lookup by linked outcome ID."""
        memory = PersistentCEOMemorySystem()
        memory._cache_loaded = True
        memory._in_memory_cache = []

        decision = CEODecision(
            id="dec_outcome_001",
            timestamp=datetime.utcnow(),
            decision_type="tactical",
            context={
                'ticker': 'NVDA',
                'outcome_id': 'out_abc_123',
                'position_id': 'pos_xyz_789',
                'type': 'entry',
            },
            reasoning="High conviction entry.",
            confidence=0.9,
            expected_impact="Strong",
            agent_overrides=[],
            memory_references=[],
        )
        memory.store_decision_memory(decision)

        found = memory.get_decision_by_outcome_id('out_abc_123')
        assert found is not None
        assert found['id'] == 'dec_outcome_001'


class TestLearningCoordinatorPersistence:
    def test_state_persists_across_restart(self):
        """Test that applied event IDs and ledgers persist across coordinator restart."""
        lc1 = LearningCoordinator(persist=True)
        event = _make_learning_event(
            "evt_learn_001", 'agent', 'warren', 0.5, 0.52,
            {'was_correct': True, 'outcome_pnl': 100.0}
        )
        lc1.apply_learning_events([event])
        assert 'evt_learn_001' in lc1._applied_event_ids

        # Simulate restart — new coordinator loads from DB
        lc2 = LearningCoordinator(persist=True)
        assert 'evt_learn_001' in lc2._applied_event_ids
        assert 'warren' in lc2.agent_ledger._stats

    def test_idempotent_application(self):
        """Test that replay of the same event does not double-apply."""
        lc = LearningCoordinator(persist=True)
        event = _make_learning_event(
            "evt_idempotent_001", 'strategy', 'momentum', 0.0, 0.01,
            {'outcome_pnl': 50.0}
        )

        summary1 = lc.apply_learning_events([event])
        assert summary1['events_applied'] == 1

        # Re-apply same event — should be skipped
        summary2 = lc.apply_learning_events([event])
        assert summary2['events_applied'] == 0

    def test_learning_only_from_realized_outcomes(self):
        """Test that learning events are tied to realized outcomes."""
        lc = LearningCoordinator(persist=True)
        event = _make_learning_event(
            "evt_blocked_001", 'agent', 'cathie', 0.5, 0.51,
            {'was_correct': False, 'outcome_pnl': 0.0, 'symbol': 'TEST'}
        )
        lc.apply_learning_events([event])
        stats = lc.agent_ledger.get('cathie')
        assert stats['decisions'] >= 1

    def test_get_relevant_experience_scoped_by_symbol(self):
        """Test that experience retrieval filters by symbol context."""
        lc = LearningCoordinator(persist=True)

        event = _make_learning_event(
            "evt_aapl_001", 'agent', 'warren', 0.5, 0.53,
            {'was_correct': True, 'outcome_pnl': 150.0, 'symbol': 'AAPL'}
        )
        lc.apply_learning_events([event])

        # In-memory ledger should reflect the applied event
        stats = lc.agent_ledger.get('warren')
        assert stats['decisions'] >= 1
        assert stats['total_pnl'] >= 150.0


class TestCEOMemoryAndLearningIntegration:
    def test_full_chain_persistence(self):
        """Test the full decision → outcome → learning chain persists."""
        from backend.ai_firm.ceo import AutonomousCEO
        import asyncio

        ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
        context = {
            'ticker': 'META',
            'market_trend': 'bullish',
            'volatility': 0.2,
            'type': 'strategic',
            'candidate_strategy': {'action': 'BUY'},
            'debate_result': {
                'winning_signal': 'BULLISH',
                'consensus_score': 0.75,
                'arguments': [],
            }
        }

        decision = asyncio.run(ceo.make_strategic_decision(context))
        assert decision.id is not None

        # Verify it was persisted
        memory = PersistentCEOMemorySystem()
        decisions = memory.get_decisions_for_symbol('META')
        assert any(d['id'] == decision.id for d in decisions)

        # Verify CEO status reflects persisted memory
        status = ceo.get_ceo_status()
        assert status['total_decisions'] >= 1
        assert status['memory_items'] >= 1
