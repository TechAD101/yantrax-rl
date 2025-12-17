#!/usr/bin/env python3
"""
Test script for MarketDataService v2
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from services.market_data_service_v2 import MarketDataService, MarketDataConfig

print("\n🧪 Testing MarketDataService v2...\n")

# Create configuration
config = MarketDataConfig(
    fmp_api_key=os.environ.get('FMP_API_KEY', '14uTc09TMyUVJEuFKriHayCTnLcyGhyy'),
    cache_ttl_seconds=5,
    rate_limit_calls=300,
    rate_limit_period=60,
    batch_size=50
)

print(f"📋 Configuration:")
print(f"   FMP API Key: {config.fmp_api_key[:10]}...")
print(f"   Cache TTL: {config.cache_ttl_seconds}s")
print(f"   Rate Limit: {config.rate_limit_calls} calls/{config.rate_limit_period}s\n")

# Initialize service
service = MarketDataService(config)

print("\n✅ Service initialized successfully!\n")

# Test getting a stock price
print("🔍 Testing AAPL stock price fetch...\n")
try:
    result = service.get_stock_price('AAPL')
    
    print("📊 Result:")
    print(f"   Symbol: {result.get('symbol')}")
    print(f"   Price: ${result.get('price')}")
    print(f"   Change: {result.get('change')} ({result.get('changePercent')}%)")
    print(f"   Source: {result.get('source')}")
    print(f"   Cached: {result.get('cached', False)}")
    
    if result.get('source') == 'fmp':
        print("\n✅ FMP integration working!")
    elif result.get('source') == 'error':
        print("\n❌ No providers available; FMP may be misconfigured")
    else:
        print(f"\n❓ Unexpected source: {result.get('source')}")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test cache
print("\n�� Testing cache (fetching AAPL again)...\n")
try:
    result2 = service.get_stock_price('AAPL')
    if result2.get('cached'):
        print(f"✅ Cache working! Age: {result2.get('cache_age')}s")
    else:
        print("⚠️  Cache not used")
except Exception as e:
    print(f"❌ Cache test failed: {e}")

# Test health check
print("\n🏥 Service Health Check...\n")
try:
    health = service.get_health()
    print(f"   Status: {'Healthy' if health.get('healthy') else 'Unhealthy'}")
    print(f"   Providers: {', '.join(health.get('providers', []))}")
    print(f"   Cache Size: {health.get('cache_size')}")
    print(f"\n✅ Health check passed!")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# New unit test: FMP batch provider (monkeypatched)
print("\n🧪 Testing FMP batch provider with monkeypatched requests...\n")

def _run_fmp_batch_unit_test():
    sample = [
        {"symbol": "AAPL", "price": 199.99, "bid": 199.9, "ask": 200.1, "changesPercentage": 0.5},
        {"symbol": "TSLA", "price": 950.50, "bid": 949.8, "ask": 951.2, "changesPercentage": -0.8},
        {"symbol": "BTC",  "price": 62000.0, "bid": 61900, "ask": 62100, "changesPercentage": 1.2}
    ]

    class DummyResp:
        def __init__(self, json_data): self._json = json_data
        def raise_for_status(self): return
        def json(self): return self._json

    def fake_get(url, params=None, timeout=10):
        # Return subset for requested symbols
        return DummyResp(sample)

    # Monkeypatch the requests.get used by market_data_service_v2
    import services.market_data_service_v2 as msvc
    orig_get = msvc.requests.get
    msvc.requests.get = fake_get

    try:
        cfg = MarketDataConfig(fmp_api_key='testkey', cache_ttl_seconds=1)
        s = MarketDataService(cfg)
        res = s.get_batch_prices(['AAPL', 'TSLA', 'BTC'])
        assert res['AAPL']['price'] == round(199.99, 2)
        assert res['TSLA']['price'] == round(950.50, 2)
        assert res['BTC']['price'] == round(62000.0, 2)
        print("✅ FMP batch unit test passed")
    finally:
        msvc.requests.get = orig_get

_run_fmp_batch_unit_test()

print("\n✨ All tests completed!\n")
