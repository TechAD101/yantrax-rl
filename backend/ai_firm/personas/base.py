from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BasePersona(ABC):
    """
    Abstract base class for all AI Personas.
    Each persona has a distinct philosophy, risk tolerance, and analytical focus.
    """
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.confidence_threshold = 0.6  # Default confidence needed to vote
        self.vote_weight = 1.0           # Default voting weight
        # Late import to avoid circular dependency
        from services.knowledge_base_service import get_knowledge_base
        self.kb = get_knowledge_base()

    @abstractmethod
    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the market data from this persona's unique perspective.
        Returns a dictionary containing:
        - signal: 'BUY', 'SELL', 'HOLD'
        - confidence: float (0.0 to 1.0)
        - reasoning: str
        - concerns: List[str]
        """
        pass

    @abstractmethod
    def get_philosophy_quote(self) -> str:
        """Returns a quote that embodies the persona's current state of mind."""
        pass
