"""
YantraX Firm Philosophy Module
"The Code of the Samurai / The Dharma of the Trader"

This module centralizes the "Belief System" of the AI Firm. 
It is not just metadata; these are hard constraints and biases that ALL agents must respect.
"""

from enum import Enum
from typing import Dict, List, Any
import random

class BeliefLayer(Enum):
    SURVIVAL = 1      # "Ungli Kato" (Capital Preservation)
    OPERATING = 2     # "Risk is Rent" (Calculated Aggression)
    METAPHYSICAL = 3  # "Market is Mirror" (Emotional Intelligence)

class PhilosophyManager:
    def __init__(self):
        self.active_principles = self._load_principles()
        self.language_mode = "EN" # Default to English, can switch to HINDI_MIX
    
    def _load_principles(self) -> Dict[str, Any]:
        return {
            "ungli_kato": {
                "name": "Ungli Kato Protocol", 
                "hindi": "Ungli kato warna hath katna padega",
                "meaning": "Cut the finger or lose the hand.",
                "type": "STOP_LOSS",
                "layer": BeliefLayer.SURVIVAL,
                "threshold_penalty": 20.0 # Multiplier for stop-loss urgency
            },
            "bund_bund": {
                "name": "Droplet Doctrine",
                "hindi": "Bund bund se sagar banta hai",
                "meaning": "An ocean is made drop by drop.",
                "type": "PROFIT_TAKING",
                "layer": BeliefLayer.OPERATING,
                "strategy_bias": "COMPOUNDING"
            },
            "ek_din_raja": {
                "name": "Anti-Greed Governor",
                "hindi": "1 din me raja nhi, sirf bikhari bante hai",
                "meaning": "Trying to be a king in one day makes you a beggar.",
                "type": "RISK_CAP",
                "layer": BeliefLayer.OPERATING,
                "max_leverage": 3
            },
            "market_mirror": {
                "name": "Metaphysical Reflection",
                "hindi": "Bazaar man ka darpan hai",
                "meaning": "The market is a mirror of the mind.",
                "type": "EMOTION_HEDGE",
                "layer": BeliefLayer.METAPHYSICAL,
                "action": "READ_MOOD_BEFORE_TRADE"
            }
        }

    def get_guidance(self, context: Dict[str, Any]) -> str:
        """
        Returns philosophical guidance based on context.
        """
        loss_streak = context.get('loss_streak', 0)
        drawdown = context.get('cummulative_drawdown', 0.0)
        volatility = context.get('volatility', 0.0)
        
        # Priority 1: SURVIVAL (Ungli Kato)
        if drawdown > 0.05 or loss_streak >= 2:
            return self._format_message("ungli_kato", "CRITICAL WARNING: Bleeding detected. Activate immediate defense.")

        # Priority 2: ANTI-GREED (Ek Din Raja)
        if context.get('leverage', 1) > 5 or volatility > 0.4:
             return self._format_message("ek_din_raja", "WARNING: Hubris detected. Reduce exposure.")

        # Priority 3: STEADY GROWTH (Bund Bund) - Default state
        return self._format_message("bund_bund", "Steady course. Compounding active.")

    def _format_message(self, principle_key: str, suffix: str) -> str:
        p = self.active_principles[principle_key]
        return f"🔱 [PHILOSOPHY] {p['hindi']} ({p['meaning']}) -> {suffix}"

    def check_compliance(self, decision: Dict[str, Any]) -> bool:
        """
        Validates if a decision respeces the core philosophy.
        """
        # Example: Reject high leverage if "Ek Din Raja" rule is active
        risk = decision.get('risk_score', 0)
        if risk > 8 and decision.get('type') == 'ALL_IN':
            return False # Vetoed by philosophy
        return True
