<<<<<<< HEAD
# services/market_data_service.py
import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
=======
import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.timeframe import TimeFrame
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563

def get_latest_price(symbol="AAPL"):
    try:
        API_KEY = os.getenv("ALPACA_API_KEY")
        API_SECRET = os.getenv("ALPACA_SECRET_KEY")
<<<<<<< HEAD
        if not API_KEY or not API_SECRET:
            print("[Market Data] Alpaca API KEY/SECRET missing.")
            return None

        client = StockHistoricalDataClient(API_KEY, API_SECRET)

        # request last 5 mins bars
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Minute,
            start=datetime.now() - timedelta(minutes=5),
            end=datetime.now()
        )
        bars = client.get_stock_bars(request_params)

        df = bars.df
        if not df.empty:
            price = df['close'].iloc[-1]
            return float(price)
        else:
            print(f"[Market Data] No data returned for {symbol}.")
=======

        client = StockHistoricalDataClient(API_KEY, API_SECRET)

        # Fetch minute bars for the symbol
        bars = client.get_stock_bars(symbol, TimeFrame.Minute)

        # Extract the latest 'close' price from the DataFrame
        if not bars.df.empty:
            price = bars.df['close'].iloc[-1]
            return float(price)
        else:
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
            return None

    except Exception as e:
        print(f"[Market Data] Alpaca error: {e}")
        return None
<<<<<<< HEAD


def get_market_data(symbol="AAPL"):
    """Wrapper to return structured market data"""
    price = get_latest_price(symbol)
    if price is None:
        return None

    return {
        "symbol": symbol,
        "market_data": {
            "price": price,
            "sentiment": "neutral",   # placeholder for ML sentiment later
            "volatility": 0.02        # placeholder for volatility calculation
        }
    }
=======
>>>>>>> a77fc5118146028486e59aa4c855b92fa20c9563
