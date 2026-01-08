"""
YantraX Visual Mood Board Module ("The Gamification Layer")

Generates the "Weather Map" of the market for the frontend.
Aggregates:
1. Market VIX & Trend (from MarketDataService)
2. CEO Emotion & Pain Level (from AutonomousCEO)
3. AI Trivia (Randomized financial wisdom)
"""

import random
from typing import Dict, Any

class MoodBoardManager:
    def __init__(self, ceo_instance, market_data_service):
        self.ceo = ceo_instance
        self.market_data = market_data_service
        self.trivia_db = [
            "Did you know? BTC tends to spike after S&P 500 drops 2%+",
            "Fun Fact: The VIX is known as the 'Fear Gauge'. Above 30 = Panic.",
            "History: The 2008 crash was predicted by yield curve inversion 18 months prior.",
            "Strategy: 'Time in the market beats timing the market' - Warren Buffett",
            "Psyche: Fear spreads faster than greed, but greed lasts longer.",
            "Data: 80% of day traders lose money in the first year. Stick to the AI.",
        ]

    def get_dashboard_state(self) -> Dict[str, Any]:
        """Returns the full gamified state for the frontend"""
        
        # 1. Get Core Data
        ceo_status = self.ceo.get_ceo_status()
        pain_level = ceo_status.get('institutional_metrics', {}).get('pain_level', 0)
        market_mood = ceo_status.get('institutional_metrics', {}).get('market_mood', 'neutral')
        
        # 2. Gamify "Weather"
        weather_map = {
            "euphoria": {"weather": "Sunny", "icon": "☀️", "color": "green-500", "animation": "pulse-fast"},
            "greed": {"weather": "Clear Skies", "icon": "🌤️", "color": "emerald-400", "animation": "pulse-slow"},
            "neutral": {"weather": "Cloudy", "icon": "☁️", "color": "gray-400", "animation": "none"},
            "fear": {"weather": "Rainy", "icon": "🌧️", "color": "orange-500", "animation": "bounce"},
            "despair": {"weather": "Thunderstorm", "icon": "⚡", "color": "red-600", "animation": "shake"},
        }
        
        current_weather = weather_map.get(market_mood, weather_map['neutral'])
        
        # 3. Generate "HeatMap" Mock (Until we have live sector data)
        # In future, this comes from market_data.get_sector_performance()
        heatmap = [
            {"sector": "Tech", "change": random.uniform(-2, 3), "status": "surging" if random.random() > 0.5 else "cooling"},
            {"sector": "Crypto", "change": random.uniform(-5, 8), "status": "volatile"},
            {"sector": "Energy", "change": random.uniform(-1, 2), "status": "silent"},
        ]

        return {
            "emotion_dial": {
                "current_mood": market_mood.upper(),
                "pain_meter": pain_level, # 0-100
                "visuals": current_weather
            },
            "market_weather": current_weather['weather'],
            "trivia_ticker": random.choice(self.trivia_db),
            "heatmap": heatmap,
            "philosophy_quote": self.ceo.philosophy.get_guidance({'drawdown': pain_level/100}) # Dynamic quote from Soul Layer
        }
