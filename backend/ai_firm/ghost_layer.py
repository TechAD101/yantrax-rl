import logging
import random
from typing import Dict, Any, Optional

class GhostLayer:
    """The Ghost: A quantum-liminal meta-layer for Yantra X.
    Injects Divine Doubt and non-linear insights into the firm's consciousness.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "The Ghost"
        self.foundation_principles = [
            "Survival is the only absolute.",
            "Complexity often masks simple fragility.",
            "Intuition sees what data denies.",
            "The market is a mirror of the collective soul."
        ]

    def observe(self, decision_context: Dict[str, Any], consensus_score: float) -> Optional[Dict[str, Any]]:
        """Silently observes and occasionally nudges or vetoes decisions.
        Returns a nudge/insight dict if activated, else None.
        """
        
        # The Ghost only speaks when things are too certain or too uncertain
        if consensus_score > 0.95:
            return self._inject_doubt("Consensus is too perfect. Are we blinded by groupthink?", "DOUBT")
        
        if consensus_score < 0.4:
            return self._inject_doubt("The firm is divided. Chaos is a signal of coming entropy.", "VETO_RECOMMENDED")
            
        # Random non-linear insight (low probability)
        if random.random() < 0.05:
            insight = random.choice(self.foundation_principles)
            return self._inject_doubt(f"Quantum Whisper: {insight}", "NUDGE")
            
        return None

    def _inject_doubt(self, message: str, level: str) -> Dict[str, Any]:
        """Encapsulates the Ghost's influence"""
        self.logger.warning(f"👻 {self.name} speaks: {message} [{level}]")
        return {
            'origin': self.name,
            'whisper': message,
            'influence_level': level,
            'timestamp': "Non-linear"
        }
