
import sys
import os
import logging

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

logging.basicConfig(level=logging.INFO)

from services.market_data_service_waterfall import WaterfallMarketDataService

def test_waterfall():
    print("🌊 Initializing Waterfall Service...")
    service = WaterfallMarketDataService()
    
    symbol = "AAPL"
    
    print(f"\n1. Testing Price Fetch for {symbol}...")
    try:
        price_data = service.get_price(symbol)
        print(f"✅ Price Result: {price_data}")
    except Exception as e:
        print(f"❌ Price Fetch Failed: {e}")

    print(f"\n2. Testing Fundamentals Fetch for {symbol}...")
    try:
        fund_data = service.get_fundamentals(symbol)
        print(f"✅ Fundamentals Result: {fund_data}")
    except Exception as e:
        print(f"❌ Fundamentals Fetch Failed: {e}")

if __name__ == "__main__":
    test_waterfall()
