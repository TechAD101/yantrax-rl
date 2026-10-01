# services/market_data_service.py
import os
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

def _get_alpaca_bars(symbol: str, minutes: int = 60):
    """Fetch recent Alpaca minute bars used consistently for price and derived metrics."""
    API_KEY = os.getenv("ALPACA_API_KEY")
    API_SECRET = os.getenv("ALPACA_SECRET_KEY")
    if not API_KEY or not API_SECRET:
        raise RuntimeError("Alpaca API key/secret missing")

    client = StockHistoricalDataClient(API_KEY, API_SECRET)
    end = datetime.now()
    start = end - timedelta(minutes=minutes)
    request_params = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Minute,
        start=start,
        end=end,
    )
    bars = client.get_stock_bars(request_params)
    df = bars.df
    if df.empty:
        raise RuntimeError(f"No Alpaca bars returned for {symbol}")
    return df

def get_latest_price(symbol="AAPL"):
    try:
        df = _get_alpaca_bars(symbol, minutes=5)
        return float(df["close"].iloc[-1])
    except Exception as e:
        print(f"[Market Data] Alpaca error: {e}")
        return None

def get_market_data(symbol="AAPL"):
    """Return price and metrics derived only from Alpaca market bars."""
    try:
        df = _get_alpaca_bars(symbol, minutes=60)
        closes = df["close"].astype(float)
        price = float(closes.iloc[-1])

        returns = closes.pct_change().dropna()
        volatility = float(returns.std()) if len(returns) >= 2 else 0.0

        volume = float(df["volume"].iloc[-1]) if "volume" in df.columns else 0.0
        change_percent = 0.0
        if len(closes) >= 2 and closes.iloc[0] > 0:
            change_percent = float((closes.iloc[-1] / closes.iloc[0] - 1.0) * 100.0)

        return {
            "symbol": symbol.upper(),
            "market_data": {
                "price": price,
                "change_percent": change_percent,
                "volume": volume,
                "volatility": volatility,
                "source": "alpaca",
                "verified": True,
            },
        }
    except Exception as e:
        print(f"[Market Data] Alpaca error: {e}")
        return None
