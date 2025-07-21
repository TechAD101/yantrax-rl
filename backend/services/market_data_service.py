import os
from alpaca.data.historical import StockHistoricalDataClient

API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_SECRET_KEY")

def get_latest_price(symbol="AAPL"):
    try:
        client = StockHistoricalDataClient(API_KEY, API_SECRET)
        bars = client.get_stock_bars(symbol, "minute", limit=1)
        if not bars.df.empty:
            price = float(bars.df['close'].iloc[-1])
            return price
        else:
            return None
    except Exception as e:
        print(f"[Market Data] Alpaca error: {e}")
        return None
