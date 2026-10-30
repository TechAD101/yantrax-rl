import logging
import random
from typing import Dict, Any, Optional
from datetime import datetime

class GhostLayer:
    """The Ghost: A quantum-liminal meta-layer for Yantra X.
    Injects Divine Doubt and non-linear insights into the firm's consciousness.
    Named 'Akasha Node' or 'The 9th Chamber' in internal lore.
    """

    def __init__(self, consensus_threshold: float = 0.98):
        self.logger = logging.getLogger(__name__)
        self.name = "The Ghost"
        self.lore_name = "Akasha Node"
        self.dimension = "9th Chamber"
        self.foundation_principles = [
            "Survival is the only absolute.",
            "Complexity often masks simple fragility.",
            "Intuition sees what data denies.",
            "The market is a mirror of the collective soul.",
            "From Chaos, Order. From Emotion, Intelligence. From Strategy, Immortality.",
            "God mode is not a state of power, but a state of perfect observation.",
            "Beta is for the many; Alpha is for the silent.",
            "The 9th Chamber hears the whispers before the roar."
        ]
        self.veto_history = []
        self.consensus_threshold = consensus_threshold

    def observe(self, decision_context: Dict[str, Any], consensus_score: float, avg_confidence: float = 0.5) -> Optional[Dict[str, Any]]:
        """Silently observes and occasionally nudges or vetoes decisions.
        Returns a nudge/insight dict if activated, else None.
        """
        # High consensus + low confidence = uniform uncertainty (not euphoria)
        # High consensus + high confidence = potential groupthink
        if consensus_score > self.consensus_threshold and avg_confidence > 0.7:
            # Consensus too high AND high confidence: Dangerous groupthink/euphoria
            return self._inject_influence("Consensus/Euphoria is too perfect. The Akasha Node senses a trap in the crowd's certainty.", "DIVINE_DOUBT")

        if consensus_score < 0.35:
            # Extreme division: Chaos
            veto = self._inject_influence("The firm is fractured beyond reason. Veto active: Transitioning to defensive soul-searching.", "VETO")
            self.veto_history.append({'timestamp': datetime.now().isoformat(), 'reason': veto['whisper']})
            return veto

        # Volatility Stress Check
        volatility = decision_context.get('market_volatility', 0)
        if volatility > 0.65:
            return self._inject_influence("Extreme volatility detected. The 9th Chamber advises stillness until the echo fades.", "CAUTION_NUDGE")

        # Random non-linear insight (low probability)
        if random.random() < 0.03:
            insight = random.choice(self.foundation_principles)
            return self._inject_influence(f"Quantum Whisper: {insight}", "WISDOM_DROP")

        return None

    def _inject_influence(self, message: str, level: str) -> Dict[str, Any]:
        """Encapsulates the Ghost's influence with vision-aligned metadata"""
        self.logger.warning(f"👻 {self.name} [{self.lore_name}] speaks: {message} [{level}]")
        return {
            'origin': self.name,
            'lore_ref': self.lore_name,
            'dimension': self.dimension,
            'whisper': message,
            'influence_level': level,
            'timestamp': datetime.now().isoformat(),
            'quantum_signature': "".join(random.choices("01αβγδε", k=8))
        }

    def get_ghost_logs(self):
        """Returns the silent history of the Ghost Layer"""
        return {
            'lore_name': self.lore_name,
            'dimension': self.dimension,
            'veto_count': len(self.veto_history),
            'principles': self.foundation_principles
        }
