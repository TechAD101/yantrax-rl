from .base import BasePersona
from typing import Dict, Any

class Quant(BasePersona):
    def __init__(self):
        super().__init__("Quant", "Head of Algorithmic Trading")
        self.vote_weight = 1.3
        self.focus = "Statistical Arbitrage & Trends"

    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Quant likes: Trend alignment, RSI neutral-to-oversold (in uptrend), Volatility compression.
        """
        technicals = market_data.get('technicals', {})
        trend = technicals.get('trend', 'neutral')
        rsi = technicals.get('rsi', 50)
        
        signal = 'HOLD'
        confidence = 0.5
        reasoning = "calculating probabilities..."
        concerns = []

        if trend == 'bullish':
            if rsi < 70:
                signal = 'BUY'
                confidence = 0.8
                reasoning = f"Trend is bullish and RSI ({rsi}) allows for entry. Statistical edge present."
            else:
                reasoning = f"Trend is bullish but RSI ({rsi}) is overextended. Awaiting mean reversion."
                concerns.append("Overbought conditions.")
        elif trend == 'bearish':
            signal = 'SELL'
            confidence = 0.75
            reasoning = "Trend is bearish. Probability suggests lower prices."
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'concerns': concerns
        }

    def get_philosophy_quote(self) -> str:
        return "The math doesn't lie. Emotions do."
