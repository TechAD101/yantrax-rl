"""Base Persona Agent Architecture

Implements the foundational class for all AI personas with explicit voting power,
debate integration, and formal agent identity aligned with project history vision.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import json


class PersonaArchetype(Enum):
    """Core persona archetypes from project history"""
    VALUE = "warren"  # Conservative, fundamentals-focused
    GROWTH = "cathie"  # Innovation, disruptive tech
    SYSTEMATIC = "quant"  # Pure algorithmic, no emotion
    RISK_AUDITOR = "degen_auditor"  # Monitors and mitigates excessive risk


class VoteType(Enum):
    """Vote types for debate engine"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    ABSTAIN = "ABSTAIN"


@dataclass
class PersonaVote:
    """Structured vote from a persona"""
    persona_name: str
    archetype: PersonaArchetype
    vote: VoteType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    weight: float  # Voting weight based on role/experience
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'persona_name': self.persona_name,
            'archetype': self.archetype.value,
            'vote': self.vote.value,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'weight': self.weight,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PersonaAnalysis:
    """Comprehensive analysis result from a persona"""
    symbol: str
    persona_name: str
    archetype: PersonaArchetype
    recommendation: str
    confidence: float
    reasoning: str
    scores: Dict[str, float]  # Component scores (fundamental, growth, etc.)
    risk_assessment: Dict[str, Any]
    time_horizon: str
    position_sizing: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'persona_name':  self.persona_name,
            'archetype': self.archetype.value,
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'scores': self.scores,
            'risk_assessment': self.risk_assessment,
            'time_horizon': self.time_horizon,
            'position_sizing': self.position_sizing,
            'timestamp': self.timestamp.isoformat()
        }


class PersonaAgent(ABC):
    """
    Base class for all AI trading personas.
    
    Aligned with project history requirements:
    - Explicit voting power in debate engine
    - Named identity with distinct mandate
    - Independent learning capability
    - Integration with memory systems
    """
    
    def __init__(self, 
                 name: str, 
                 archetype: PersonaArchetype,
                 voting_weight: float = 1.0,
                 preferred_strategies: Optional[List[str]] = None):
        """
        Initialize persona agent
        
        Args:
            name: Human-readable name (e.g., "Warren", "Cathie")
            archetype: Persona archetype enum
            voting_weight: Weight in debate engine (0.5-2.0, default 1.0)
            preferred_strategies: List of strategy types this persona prefers
        """
        self.name = name
        self.archetype = archetype
        self.voting_weight = voting_weight
        self.preferred_strategies = preferred_strategies or []
        self.vote_history: List[PersonaVote] = []
        self.analysis_history: List[PersonaAnalysis] = []
        self.performance_metrics = {
            'total_votes': 0,
            'total_analyses': 0,
            'avg_confidence': 0.0
        }
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        """
        Perform persona-specific analysis
        
        Args:
            context: Market context with symbol, fundamentals, technicals, etc.
        
        Returns:
            PersonaAnalysis with recommendation, reasoning, scores
        """
        pass
    
    @abstractmethod
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        """
        Cast a vote on a trade proposal
        
        Args:
            proposal: Trade proposal dict with symbol, action, entry, exit, etc.
            market_context: Current market conditions
        
        Returns:
            PersonaVote with vote type, confidence, reasoning, weight
        """
        pass
    
    def get_vote_weight(self, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate effective voting weight (can be context-dependent)
        
        Args:
            context: Optional context for dynamic weighting
        
        Returns:
            Effective vote weight
        """
        # Base weight
        weight = self.voting_weight
        
        # Context-based adjustments (e.g., Warren gets higher weight in bear markets)
        if context:
            # Subclasses can override for specific logic
            weight = self._adjust_weight_for_context(context, weight)
        
        return weight
    
    def _adjust_weight_for_context(self, context: Dict[str, Any], base_weight: float) -> float:
        """
        Hook for subclasses to adjust weight based on market context
        Override in subclasses for persona-specific logic
        """
        return base_weight
    
    def record_vote(self, vote: PersonaVote):
        """Record vote in history"""
        self.vote_history.append(vote)
        self.performance_metrics['total_votes'] += 1
        self._update_metrics()
    
    def record_analysis(self, analysis: PersonaAnalysis):
        """Record analysis in history"""
        self.analysis_history.append(analysis)
        self.performance_metrics['total_analyses'] += 1
        self._update_metrics()
    
    def _update_metrics(self):
        """Update performance metrics"""
        if self.vote_history:
            self.performance_metrics['avg_confidence'] = sum(
                v.confidence for v in self.vote_history
            ) / len(self.vote_history)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        recent_votes = [v for v in self.vote_history 
                       if (datetime.now() - v.timestamp).days <= 30]
        
        return {
            'persona_name': self.name,
            'archetype': self.archetype.value,
            'total_votes': self.performance_metrics['total_votes'],
            'total_analyses': self.performance_metrics['total_analyses'],
            'avg_confidence': round(self.performance_metrics['avg_confidence'], 3),
            'recent_votes_30d': len(recent_votes),
            'voting_weight': self.voting_weight,
            'preferred_strategies': self.preferred_strategies
        }
    
    def get_recent_reasoning(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent vote reasoning for transparency"""
        recent = sorted(self.vote_history, key=lambda v: v.timestamp, reverse=True)[:limit]
        return [
            {
                'vote': v.vote.value,
                'confidence': v.confidence,
                'reasoning': v.reasoning,
                'timestamp': v.timestamp.isoformat()
            }
            for v in recent
        ]
    
    def __repr__(self) -> str:
        return f"<PersonaAgent: {self.name} ({self.archetype.value}) weight={self.voting_weight}>"
