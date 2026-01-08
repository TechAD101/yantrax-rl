from .base import BasePersona
from typing import Dict, Any

class MacroMonk(BasePersona):
    def __init__(self):
        super().__init__("MacroMonk", "Geopolitical Strategist")
        self.vote_weight = 1.8 
        self.focus = "Global Conflict, Oil, Gold, VIX, Black Swan Events"

    def analyze(self, market_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        MacroMonk meditates on chaos. He looks for war, famine, and fear.
        """
        vix = market_data.get('vix', 15.0)
        oil_price = market_data.get('oil', 75.0)
        news_sentiment = market_data.get('news_sentiment', 0.0) # -1 to 1
        
        signal = 'HOLD'
        confidence = 0.5
        reasoning = "World is relatively peaceful. Om."
        concerns = []

        # 1. Fear Gauge (VIX)
        if vix > 30:
            signal = 'SELL'
            confidence = 0.9
            reasoning = f"VIX at {vix}. Fear is spiking. Cash is king. Om."
            concerns.append("EXTREME_VOLATILITY")
        
        # 2. War Signals (Oil Spike + Negative Sentiment)
        elif oil_price > 90 and news_sentiment < -0.5:
             signal = 'HEDGE' # Special signal for buying Puts/Gold
             confidence = 0.85
             reasoning = "Oil spiking + Negative Sentiment. Conflict risk high. Buy Gold/Puts."
             concerns.append("GEOPOLITICAL_CONFLICT")

        # 3. Euphoria (Low VIX)
        elif vix < 12:
             signal = 'BUY'
             confidence = 0.6
             reasoning = "VIX unusually low. Complacency detected. Good time to accumulate quietly."

        return {
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            'concerns': concerns
        }

    def get_philosophy_quote(self) -> str:
        return "Chaos is a ladder for the prepared, but a grave for the greedy."
