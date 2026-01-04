from .base import BasePersona
from typing import Dict, Any

class Cathie(BasePersona):
    def __init__(self):
        super().__init__("Cathie", "Head of Innovation Strategy")
        self.vote_weight = 1.2
        self.focus = "Disruptive Innovation & Momentum"

    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cathie likes: High Momentum, Volatility (as opportunity), thematic growth.
        Cathie ignores: Short-term valuation metrics.
        """
        technicals = market_data.get('technicals', {})
        momentum = technicals.get('momentum_score', 50) # 0-100
        volatility = technicals.get('volatility_index', 0)
        
        signal = 'HOLD'
        confidence = 0.5
        reasoning = "Analyzing innovation curve."
        concerns = []

        if momentum > 70:
            signal = 'BUY'
            confidence = 0.9
            reasoning = f"Momentum is accelerating (Score: {momentum}). The adoption curve is steepening."
        elif momentum < 30:
            signal = 'BUY' # Buy the dip if conviction is high (simplified)
            confidence = 0.6
            reasoning = "Market is misunderstanding the long-term potential. Aggressive entry point."
            concerns.append("Short-term headwinds are strong.")
        else:
            reasoning = "Innovation signals are mixed."

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'concerns': concerns
        }

    def get_philosophy_quote(self) -> str:
        return "Innovation solves problems and creates exponential value."
