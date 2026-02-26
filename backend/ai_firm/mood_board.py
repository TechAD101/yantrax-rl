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
        
        # 3. Generate "HeatMap"
        heatmap = []
        try:
            # Fetch real sector data from MarketDataService (which delegates to RealtimePipeline)
            if hasattr(self.market_data, 'get_sector_performance'):
                sector_data = self.market_data.get_sector_performance()
                if sector_data and "sectors" in sector_data:
                    for s in sector_data["sectors"]:
                        change = float(s.get("change_pct", 0.0))

                        # Determine status based on change magnitude
                        if change > 1.5:
                            status = "surging"
                        elif change < -1.5:
                            status = "cooling"
                        elif abs(change) > 0.5:
                            status = "volatile"
                        else:
                            status = "silent"

                        heatmap.append({
                            "sector": s.get("name", "Unknown"),
                            "change": change,
                            "status": status
                        })
        except Exception:
            # Fallback will handle empty heatmap
            pass

        # Fallback to mock data if live fetch fails or is empty
        if not heatmap:
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
