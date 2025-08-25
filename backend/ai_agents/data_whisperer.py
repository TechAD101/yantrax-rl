# ai_agents/data_whisperer.py
from services.market_data_service import get_latest_price

def analyze_data(symbol="AAPL"):
    price = get_latest_price(symbol)
    if price is None:
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
    }
