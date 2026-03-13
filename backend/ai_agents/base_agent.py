"""Base Agent Module

Provides the foundational BaseAgent class and AgentArchetype enum for the
YantraX AI Firm's 20+ agent ecosystem.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


from .base_persona import PersonaAgent, PersonaArchetype, PersonaVote, PersonaAnalysis, VoteType

class BaseAgent(PersonaAgent):
    """Base agent class for placeholder agents in the registry"""
    def __init__(self, name: str, archetype: PersonaArchetype, voting_weight: float = 1.0):
        super().__init__(
            name=name,
            archetype=archetype,
            voting_weight=voting_weight,
            mandate=f"Support institutional growth through {archetype.value} analysis."
        )
        self.confidence = 0.75
    
    def analyze(self, context: Dict[str, Any]) -> PersonaAnalysis:
        """Placeholder analysis method"""
        return PersonaAnalysis(
            symbol=context.get('symbol', 'UNKNOWN'),
            persona_name=self.name,
            archetype=self.archetype,
            recommendation='HOLD',
            confidence=self.confidence,
            reasoning=f'{self.name} ({self.archetype.value}) placeholder analysis',
            scores={'general': 0.5},
            risk_assessment={'risk': 'low'},
            time_horizon="Medium-term"
        )
    
    def vote(self, proposal: Dict[str, Any], market_context: Dict[str, Any]) -> PersonaVote:
        """Cast a neutral vote by default"""
        return PersonaVote(
            persona_name=self.name,
            archetype=self.archetype,
            vote=VoteType.HOLD,
            confidence=self.confidence,
            reasoning=f"{self.name} neutral stance on proposal.",
            weight=self.voting_weight
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent to dictionary"""
        return self.get_performance_summary()
