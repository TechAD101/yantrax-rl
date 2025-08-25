<<<<<<< HEAD
# ai_agents/data_whisperer.py
=======
import random
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
from services.market_data_service import get_latest_price

def analyze_data(symbol="AAPL"):
    price = get_latest_price(symbol)
    if price is None:
<<<<<<< HEAD
        # fallback: return fake/random market data for RL simulation
        return {
            "price": 21000,
            "volatility": 0.02,
            "sentiment": "neutral"
        }
    return {
        "price": price,
        "volatility": 0.02,  # can enhance later with real volatility
        "sentiment": "neutral"
=======
        price = round(random.uniform(10000, 60000), 2)
    market_data = {
        "price": price,
        "volume": random.randint(100, 10000),
        "trend": random.choice(["bullish", "bearish", "sideways"])
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
    }
