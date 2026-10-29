"""Persistent CEO Memory System backed by CEODecisionRecord table.

Provides durable storage and retrieval of CEO decisions, reasoning, and performance
memories across process restarts.
"""
import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PersistedDecisionMemory:
    """A CEO decision loaded from persistent storage."""
    id: str
    timestamp: datetime
    decision_type: str
    symbol: Optional[str]
    decision_hash: Optional[str]
    reasoning: str
    confidence: float
    outcome_id: Optional[str]
    position_id: Optional[str]
    memory_tags: List[str]
    metadata_json: Optional[Dict[str, Any]]


class PersistentCEOMemorySystem:
    """CEO memory system backed by database — survives process restarts."""

    def __init__(self, session_factory=None):
        self._session_factory = session_factory
        self._in_memory_cache: List[Dict] = []
        self._cache_loaded = False

    def _get_session(self):
        if self._session_factory:
            return self._session_factory()
        # Fallback for standalone usage
        from backend.db import get_session
        return get_session()

    def _ensure_cache_loaded(self):
        """Lazy-load cache from database on first access."""
        if self._cache_loaded:
            return
        try:
            session = self._get_session()
            try:
                from backend.models import CEODecisionRecord
                records = session.query(CEODecisionRecord).order_by(
                    CEODecisionRecord.timestamp.desc()
                ).limit(200).all()
                self._in_memory_cache = [r.to_dict() for r in records]
                logger.info(f"Loaded {len(self._in_memory_cache)} CEO decisions from persistent storage")
            finally:
                session.close()
        except Exception as e:
            logger.warning(f"Could not load CEO memory from DB: {e}")
            self._in_memory_cache = []
        self._cache_loaded = True

    def store_decision_memory(self, decision, session=None) -> bool:
        """Store a CEO decision to persistent storage.

        Args:
            decision: CEODecision object with id, timestamp, decision_type, context,
                     reasoning, confidence, etc.
            session: Optional existing DB session (for transactional writes)

        Returns:
            True if stored successfully, False otherwise
        """
        own_session = False
        if session is None:
            session = self._get_session()
            own_session = True

        try:
            from backend.models import CEODecisionRecord

            # Extract tags from context
            tags = self._extract_tags(decision.context)

            # Create decision hash for dedup
            context_hash = self._hash_context(decision.context)[:16]

            record = CEODecisionRecord(
                id=decision.id,
                timestamp=decision.timestamp,
                decision_type=decision.decision_type,
                symbol=decision.context.get('ticker') or decision.context.get('symbol'),
                decision_hash=context_hash,
                reasoning=decision.reasoning,
                confidence=decision.confidence,
                outcome_id=decision.context.get('outcome_id'),
                position_id=decision.context.get('position_id'),
                memory_tags=tags,
                metadata_json={
                    'strategy_action': decision.context.get('strategy_action'),
                    'agent_overrides': decision.agent_overrides,
                    'memory_references': decision.memory_references,
                    'expected_impact': decision.expected_impact,
                }
            )

            session.merge(record)
            if own_session:
                session.commit()

            # Update cache
            self._in_memory_cache.insert(0, record.to_dict())
            if len(self._in_memory_cache) > 200:
                self._in_memory_cache = self._in_memory_cache[:200]

            logger.debug(f"Persisted CEO decision {decision.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to persist CEO decision {decision.id}: {e}")
            if own_session:
                session.rollback()
            return False
        finally:
            if own_session:
                session.close()

    def store_performance_memory(self, performance: Dict[str, Any], session=None) -> bool:
        """Store performance evaluation as a memory record."""
        # Performance memories stored as special decision_type='performance'
        # Reuse the same table with a synthetic ID
        own_session = False
        if session is None:
            session = self._get_session()
            own_session = True

        try:
            from backend.models import CEODecisionRecord

            perf_id = f"perf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(performance)) & 0xFFFF:04x}"

            record = CEODecisionRecord(
                id=perf_id,
                timestamp=datetime.utcnow(),
                decision_type='performance',
                symbol=None,
                decision_hash='',
                reasoning=json.dumps(performance, default=str),
                confidence=performance.get('overall_score', 0.0),
                outcome_id=None,
                position_id=None,
                memory_tags=['performance', 'evaluation'],
                metadata_json=performance
            )

            session.merge(record)
            if own_session:
                session.commit()

            self._in_memory_cache.insert(0, record.to_dict())
            if len(self._in_memory_cache) > 200:
                self._in_memory_cache = self._in_memory_cache[:200]

            return True

        except Exception as e:
            logger.error(f"Failed to persist performance memory: {e}")
            if own_session:
                session.rollback()
            return False
        finally:
            if own_session:
                session.close()

    def recall_relevant_memories(self, context: Dict, limit: int = 5) -> List[Dict]:
        """Recall memories relevant to current context from persistent storage."""
        self._ensure_cache_loaded()

        context_tags = self._extract_tags(context)
        relevant = []

        for memory in self._in_memory_cache:
            # Only consider decision-type memories (skip performance)
            if memory.get('decision_type') == 'performance':
                continue

            relevance = self._calculate_relevance(memory, context_tags)
            if relevance > 0.3:
                m = memory.copy()
                m['relevance'] = relevance
                relevant.append(m)

        # Sort by relevance then recency
        relevant.sort(key=lambda m: (m['relevance'], m.get('timestamp', '')), reverse=True)
        return relevant[:limit]

    def get_decisions_for_symbol(self, symbol: str, limit: int = 20) -> List[Dict]:
        """Get all decisions for a specific symbol."""
        self._ensure_cache_loaded()
        return [m for m in self._in_memory_cache if m.get('symbol') == symbol][:limit]

    def get_decision_by_outcome_id(self, outcome_id: str) -> Optional[Dict]:
        """Find decision linked to a specific outcome."""
        self._ensure_cache_loaded()
        for m in self._in_memory_cache:
            if m.get('outcome_id') == outcome_id:
                return m
        return None

    def get_decision_by_position_id(self, position_id: str) -> Optional[Dict]:
        """Find decision linked to a specific position."""
        self._ensure_cache_loaded()
        for m in self._in_memory_cache:
            if m.get('position_id') == position_id:
                return m
        return None

    def get_recent_decisions(self, limit: int = 10) -> List[Dict]:
        """Get most recent decisions."""
        self._ensure_cache_loaded()
        return [m for m in self._in_memory_cache if m.get('decision_type') != 'performance'][:limit]

    def _hash_context(self, context: Dict) -> str:
        """Create hash of context for similarity matching."""
        context_str = json.dumps(context, sort_keys=True, default=str)
        return hashlib.md5(context_str.encode()).hexdigest()

    def _extract_tags(self, context: Dict) -> List[str]:
        """Extract relevant tags from context."""
        tags = []

        if 'market_trend' in context:
            tags.append(f"trend_{context['market_trend']}")

        volatility = context.get('volatility', 0)
        if volatility > 0.3:
            tags.append('high_volatility')
        elif volatility < 0.1:
            tags.append('low_volatility')

        if 'type' in context:
            tags.append(context['type'])

        # Strategy-related tags
        candidate = context.get('candidate_strategy', {})
        if candidate.get('action'):
            tags.append(f"action_{candidate['action'].lower()}")

        return tags

    def _calculate_relevance(self, memory: Dict, context_tags: List[str]) -> float:
        """Calculate relevance score between memory and context."""
        memory_tags = memory.get('memory_tags', [])

        # Tag overlap score
        common_tags = set(memory_tags) & set(context_tags)
        tag_score = len(common_tags) / max(len(memory_tags), len(context_tags), 1)

        # Recency score
        timestamp_str = memory.get('timestamp', '')
        try:
            if isinstance(timestamp_str, str):
                ts = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                ts = timestamp_str
            days_old = (datetime.utcnow() - ts).days
            recency_score = max(0, 1 - (days_old / 365))
        except Exception:
            recency_score = 0.5

        return (tag_score * 0.7) + (recency_score * 0.3)


# Global instance for backward compatibility
_persistent_memory = None


def get_persistent_ceo_memory(session_factory=None) -> PersistentCEOMemorySystem:
    """Get or create the global persistent CEO memory instance."""
    global _persistent_memory
    if _persistent_memory is None:
        _persistent_memory = PersistentCEOMemorySystem(session_factory)
    elif session_factory and _persistent_memory._session_factory is None:
        _persistent_memory._session_factory = session_factory
    return _persistent_memory