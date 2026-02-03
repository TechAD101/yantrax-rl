"""Base Agent Module

Provides the foundational BaseAgent class and AgentArchetype enum for the
YantraX AI Firm's 20+ agent ecosystem.
"""

from enum import Enum
from typing import Dict, Any, Optional
from dataclasses import dataclass


class AgentArchetype(Enum):
    """Agent personality archetypes"""
    VALUE = "value"
    GROWTH = "growth"
    QUANTATATIVE = "quantitative"
    SYSTEMATIC = "systematic"
    SPECULATIVE = "speculative"


@dataclass
class BaseAgent:
    """Base agent class for placeholder agents in the registry"""
    name: str
    archetype: AgentArchetype
    confidence: float = 0.75
    
    def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder analysis method"""
        return {
            'agent': self.name,
            'signal': 'HOLD',
            'confidence': self.confidence,
            'reasoning': f'{self.name} ({self.archetype.value}) placeholder analysis'
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize agent to dictionary"""
        return {
            'name': self.name,
            'archetype': self.archetype.value,
            'confidence': self.confidence
        }
