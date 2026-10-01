"""LearningCoordinator — single consumer of LearningEvent records (mission §18).

Closes the feedback path: Outcome -> Attribution -> LearningEvent ->
Coordinator -> {AgentManager confidence, StrategyEngine metrics, measured
history, retrievable experience for future decisions}.

Heuristic confidence adjustments (+/-2% agents, +/-1% strategy) are bounded
and based on realized P&L only — learning events are never generated for open
positions or blocked trades.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentPerformanceLedger:
    """Measured per-agent history — accumulated from realized outcomes."""

    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}

    def record(self, agent_name: str, was_correct: bool, outcome_pnl: float):
        stats = self._stats.setdefault(agent_name, {
            'decisions': 0, 'correct': 0, 'incorrect': 0, 'abstains': 0,
            'total_pnl': 0.0, 'recent': [],
        })
        stats['decisions'] += 1
        if was_correct:
            stats['correct'] += 1
        else:
            stats['incorrect'] += 1
        stats['total_pnl'] = round(stats['total_pnl'] + outcome_pnl, 4)
        stats['recent'] = (stats['recent'][-19:] + [1 if was_correct else 0])
        stats['recent_accuracy'] = round(sum(stats['recent']) / len(stats['recent']), 3)
        stats['accuracy'] = round(stats['correct'] / stats['decisions'], 3) if stats['decisions'] else None

    def record_abstain(self, agent_name: str):
        stats = self._stats.setdefault(agent_name, {
            'decisions': 0, 'correct': 0, 'incorrect': 0, 'abstains': 0,
            'total_pnl': 0.0, 'recent': [],
        })
        stats['abstains'] += 1

    def get(self, agent_name: str) -> Dict[str, Any]:
        return dict(self._stats.get(agent_name, {}))

    def all(self) -> Dict[str, Dict[str, Any]]:
        return {name: dict(s) for name, s in self._stats.items()}


class StrategyPerformanceLedger:
    """Measured per-strategy history from realized outcomes."""

    def __init__(self):
        self._stats: Dict[str, Dict[str, Any]] = {}

    def record(self, strategy_name: str, pnl: float, confidence_delta: float):
        stats = self._stats.setdefault(strategy_name, {
            'outcomes': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0.0,
        })
        stats['outcomes'] += 1
        if pnl > 0:
            stats['wins'] += 1
        elif pnl < 0:
            stats['losses'] += 1
        stats['total_pnl'] = round(stats['total_pnl'] + pnl, 4)
        stats['win_rate'] = round(stats['wins'] / stats['outcomes'], 3)
        stats['confidence_delta_applied'] = round(stats.get('confidence_delta_applied', 0.0) + confidence_delta, 4)

    def get(self, strategy_name: str) -> Dict[str, Any]:
        return dict(self._stats.get(strategy_name, {}))

    def all(self) -> Dict[str, Dict[str, Any]]:
        return {name: dict(s) for name, s in self._stats.items()}


class LearningCoordinator:
    """Applies generated LearningEvents to live components and maintains
    measured performance ledgers. Registered consumers receive each event."""

    def __init__(self):
        self.agent_ledger = AgentPerformanceLedger()
        self.strategy_ledger = StrategyPerformanceLedger()
        self._consumers = []
        self._applied_event_ids = set()

    def register_consumer(self, consumer) -> None:
        """consumer signature: (learning_event) -> None"""
        self._consumers.append(consumer)

    def apply_learning_events(self, learning_events: List[Any]) -> Dict[str, Any]:
        """Apply a batch of generated LearningEvent objects.

        Returns an application summary stored in decision provenance so the
        learning path is auditable end-to-end.
        """
        summary = {
            'events_applied': 0,
            'agent_confidence_updates': {},
            'strategy_metric_updates': {},
            'ledger_agent_updates': 0,
            'ledger_strategy_updates': 0,
        }
        for event in learning_events:
            if event.event_id in self._applied_event_ids:
                continue
            self._applied_event_ids.add(event.event_id)

            try:
                meta = event.metadata or {}
                if event.target_type == 'agent':
                    self.agent_ledger.record(
                        event.target_id,
                        bool(meta.get('was_correct')),
                        float(meta.get('outcome_pnl', 0.0) or 0.0),
                    )
                    summary['ledger_agent_updates'] += 1
                elif event.target_type == 'strategy':
                    pnl = float(meta.get('outcome_pnl', 0.0) or 0.0)
                    self.strategy_ledger.record(event.target_id, pnl, 0.0)
                    summary['ledger_strategy_updates'] += 1

                for consumer in self._consumers:
                    try:
                        consumer(event)
                    except Exception as e:
                        logger.error(f"Learning consumer failed for {event.event_id}: {e}")

                if event.target_type == 'agent':
                    summary['agent_confidence_updates'][event.target_id] = event.new_value
                elif event.target_type == 'strategy':
                    summary['strategy_metric_updates'][event.target_id] = event.new_value
                summary['events_applied'] += 1
            except Exception as e:
                logger.error(f"LearningCoordinator failed on {event.event_id}: {e}")

        return summary

    def get_relevant_experience(self, symbol: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve recent realized-outcome learning for future decisions.

        Reads persisted LearningEvent rows (DB-backed), newest first, for any
        symbol; used to inject institutional experience into agent voting.
        """
        try:
            from backend.db import get_session
            from backend.models import LearningEvent as LearningEventORM
            session = get_session()
            try:
                rows = (
                    session.query(LearningEventORM)
                    .order_by(LearningEventORM.timestamp.desc())
                    .limit(limit * 3)
                    .all()
                )
            finally:
                session.close()
            experience = []
            for row in rows:
                meta = row.event_metadata or {}
                experience.append({
                    'event_type': row.event_type,
                    'target_type': row.target_type,
                    'target_id': row.target_id,
                    'new_value': row.new_value,
                    'outcome_pnl': meta.get('outcome_pnl'),
                    'regime': meta.get('regime'),
                    'was_correct': meta.get('was_correct'),
                })
                if len(experience) >= limit:
                    break
            return experience
        except Exception as e:
            logger.error(f"Experience retrieval failed: {e}")
            return []

    def get_agent_stats(self) -> Dict[str, Any]:
        return self.agent_ledger.all()

    def get_strategy_stats(self) -> Dict[str, Any]:
        return self.strategy_ledger.all()


_coordinator: Optional[LearningCoordinator] = None


def get_learning_coordinator() -> LearningCoordinator:
    global _coordinator
    if _coordinator is None:
        _coordinator = LearningCoordinator()
    return _coordinator
