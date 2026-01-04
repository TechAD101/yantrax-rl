from .base import BasePersona
from typing import Dict, Any

class DegenAuditor(BasePersona):
    def __init__(self):
        super().__init__("DegenAuditor", "Head of Risk Control")
        self.vote_weight = 2.0  # Veto power implicit in high weight
        self.focus = "Risk Mitigation & Scam Detection"

    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        DegenAuditor likes: High Liquidity, Proven Contracts, Low Slippage.
        DegenAuditor hates: Low Liquidity, Brand new tokens, "Trust me bro" signals.
        """
        liquidity = market_data.get('liquidity', 1000000)
        is_verified = market_data.get('is_verified', True)
        
        signal = 'HOLD'
        confidence = 0.6
        reasoning = "Scanning for rugs..."
        concerns = []

        if not is_verified:
            signal = 'SELL'
            confidence = 1.0
            reasoning = "Asset is unverified. IMMEDIATE REJECT. Capital preservation protocol active."
            concerns.append("UNVERIFIED CONTRACT")
        
        elif liquidity < 50000:
            signal = 'SELL'
            confidence = 0.9
            reasoning = f"Liquidity is dangerously low (${liquidity}). High slippage risk detected."
            concerns.append("Low Liquidity")
        
        else:
            signal = 'HOLD' # DegenAuditor rarely buys, mostly approves/rejects
            confidence = 0.5
            reasoning = "Liquidity parameters acceptable. No obvious scams detected."

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'concerns': concerns
        }

    def get_philosophy_quote(self) -> str:
        return "I assume everything is a rug pull until proven otherwise."
