from .base import BasePersona
from typing import Dict, Any

class Warren(BasePersona):
    def __init__(self):
        super().__init__("Warren", "Director of Market Intelligence")
        self.vote_weight = 1.5
        self.focus = "Long-term Value & Fundamentals"

    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Warren likes: Low P/E, High ROE, Low Debt, Consistent Earnings.
        Warren hates: Hype, High Volatility, Unproven Tech.
        """
        fundamentals = market_data.get('fundamentals', {})
        pe = fundamentals.get('pe_ratio', 0)
        roe = fundamentals.get('return_on_equity', 0)
        
        signal = 'HOLD'
        confidence = 0.5
        reasoning = "Waiting for a pitch."
        concerns = []

        if pe > 0 and pe < 20 and roe > 0.15:
            signal = 'BUY'
            confidence = 0.85
            reasoning = f"Fundamentals are stellar. P/E of {pe} with ROE of {roe*100:.1f}% indicates a high-quality business at a fair price."
        elif pe > 40:
            signal = 'SELL'
            confidence = 0.7
            reasoning = f"Market is exuberant. P/E of {pe} implies growth that may not materialize."
            concerns.append("Valuation is stretched.")
        else:
            reasoning = f"P/E of {pe} is average. Nothing remarkable to justify capital allocation."

        # Fetch Wisdom for enrichment
        wisdom = self.kb.query_wisdom(topic=f"value investing in {context.get('market_trend', 'neutral')} market", archetype_filter="warren", max_results=1)
        if wisdom:
            reasoning += f" As logic dictates: \"{wisdom[0]['content']}\""
            if wisdom[0].get('relevance_score', 0) > 0.8:
                confidence = min(0.98, confidence + 0.05)


        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'concerns': concerns
        }

    def get_philosophy_quote(self) -> str:
        return "Price is what you pay. Value is what you get."
