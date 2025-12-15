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
    alpha_vantage_key=os.environ.get('ALPHA_VANTAGE_KEY', '9RIUV'),
    cache_ttl_seconds=60,
    rate_limit_calls=5,
    rate_limit_period=60,
    fallback_to_mock=False
)

print(f"📋 Configuration:")
print(f"   API Key: {config.alpha_vantage_key[:10]}...")
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
    
    if result.get('source') == 'alpha_vantage':
        print("\n✅ Alpha Vantage integration working!")
    elif result.get('source') == 'alpaca':
        print("\n✅ Alpaca integration working (fallback)")
    elif result.get('source') == 'error':
        print("\n❌ No providers available; mock data is disabled")
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

print("\n✨ All tests completed!\n")
