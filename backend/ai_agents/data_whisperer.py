import random
from services.market_data_service import get_latest_price

def analyze_data(symbol="AAPL"):
    price = get_latest_price(symbol)
    if price is None:
        price = round(random.uniform(10000, 60000), 2)
    market_data = {
        "price": price,
        "volume": random.randint(100, 10000),
        "trend": random.choice(["bullish", "bearish", "sideways"])
    }
    print(f"[Data Whisperer] Market data: {market_data}")
    return market_data
