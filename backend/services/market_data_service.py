import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame

def get_latest_price(symbol="AAPL"):
    try:
        API_KEY = os.getenv("ALPACA_API_KEY")
        API_SECRET = os.getenv("ALPACA_SECRET_KEY")

        client = StockHistoricalDataClient(API_KEY, API_SECRET)

        # Fetch minute bars for the symbol
        bars = client.get_stock_bars(symbol, TimeFrame.Minute)

        # Extract the latest 'close' price from the DataFrame
        if not bars.df.empty:
            price = bars.df['close'].iloc[-1]
            return float(price)
        else:
            return None

    except Exception as e:
        print(f"[Market Data] Alpaca error: {e}")
        return None
