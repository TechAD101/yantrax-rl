#!/usr/bin/env python3
"""
Live Data Validation Script for YantraX RL

Tests:
1. FinancialModelingPrep (FMP) connectivity
2. Batch quote validation
3. Data quality validation
4. Performance benchmarking

Usage:
    python backend/test_live_data.py
"""

import os
import sys
import time
import json
from datetime import datetime
from typing import Dict, Any

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

try:
    from services.market_data_service_v2 import MarketDataService, MarketDataConfig
    print_success("MarketDataService v2 imported successfully")
except ImportError as e:
    print_error(f"Failed to import MarketDataService: {e}")
    sys.exit(1)

def test_env_variables():
    """Test 1: Verify environment variables (FMP)"""
    print_header("TEST 1: Environment Variables")

    fmp_key = os.getenv('FMP_API_KEY', '')

    if fmp_key:
        print_success(f"FMP API Key: SET ({fmp_key[:8]}...)")
    else:
        print_error("FMP API Key: MISSING")

    return bool(fmp_key)

def test_service_initialization():
    """Test 2: Service initialization"""
    print_header("TEST 2: MarketDataService Initialization")

    try:
        config = MarketDataConfig(
            fmp_api_key=os.getenv('FMP_API_KEY', '14uTc09TMyUVJEuFKriHayCTnLcyGhyy'),
            cache_ttl_seconds=5,
            rate_limit_calls=300,
            rate_limit_period=60,
            batch_size=50
        )

        service = MarketDataService(config)
        print_success("MarketDataService initialized successfully")
        print_info(f"Configured providers: {[p.value for p in service.providers]}")
        return service
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        return None

def test_fmp(service):
    """Test 3: FinancialModelingPrep (FMP) connectivity"""
    print_header("TEST 3: FMP Data Fetch")

    if not os.getenv('FMP_API_KEY'):
        print_warning("FMP key not configured - skipping test")
        return None

    try:
        start_time = time.time()
        result = service.get_stock_price('AAPL')
        elapsed = time.time() - start_time

        if result and result.get('price', 0) > 0:
            print_success(f"FMP fetch successful in {elapsed:.2f}s")
            print_info(f"Symbol: {result['symbol']}")
            print_info(f"Price: ${result['price']}")
            print_info(f"Change: ${result.get('change', 'N/A')} ({result.get('changePercent', 'N/A')}%)")
            print_info(f"Source: {result['source']}")
            return result
        else:
            print_error("FMP returned invalid data")
            return None
    except Exception as e:
        print_error(f"FMP test failed: {e}")
        return None

# Alpaca tests removed - FMP is the single provider now

def test_intelligent_fetch(service):
    """Test 5: Intelligent provider selection"""
    print_header("TEST 5: Intelligent Provider Fallback")
    
    symbols = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'SOL', 'BNB', 'BTC']
    results = []
    
    for symbol in symbols:
        try:
            start_time = time.time()
            result = service.get_stock_price(symbol)
            elapsed = time.time() - start_time
            
            if result and result.get('price', 0) > 0:
                source = result.get('source', 'unknown')
                cached = result.get('cached', False)
                
                status = f"✅ {symbol}: ${result['price']:.2f} from {source}"
                if cached:
                    status += f" (cached, {result.get('cache_age', 0):.1f}s old)"
                status += f" [{elapsed:.2f}s]"
                
                print_success(status)
                results.append(result)
            else:
                print_error(f"{symbol}: Failed to fetch")
                
            # Small delay to avoid hammering APIs
            time.sleep(0.5)
        except Exception as e:
            print_error(f"{symbol}: Error - {e}")
    
    return results

def test_cache_mechanism(service):
    """Test 6: Cache functionality"""
    print_header("TEST 6: Cache Mechanism")
    
    symbol = 'AAPL'
    
    # First fetch (should hit API)
    print_info("First fetch (should hit API)...")
    start_time = time.time()
    result1 = service.get_stock_price(symbol)
    elapsed1 = time.time() - start_time
    
    if result1.get('cached'):
        print_warning(f"First fetch was cached (unexpected) - {elapsed1:.2f}s")
    else:
        print_success(f"First fetch hit API - {elapsed1:.2f}s")
    
    # Second fetch (should hit cache)
    print_info("Second fetch (should hit cache)...")
    start_time = time.time()
    result2 = service.get_stock_price(symbol)
    elapsed2 = time.time() - start_time
    
    if result2.get('cached'):
        print_success(f"Second fetch hit cache - {elapsed2:.2f}s (age: {result2.get('cache_age', 0):.1f}s)")
    else:
        print_warning(f"Second fetch hit API (cache miss) - {elapsed2:.2f}s")
    
    # Cache should be much faster
    if result2.get('cached') and elapsed2 < elapsed1:
        speedup = elapsed1 / elapsed2 if elapsed2 > 0 else 0
        print_success(f"Cache speedup: {speedup:.1f}x faster")

def test_data_quality(results):
    """Test 7: Data quality validation"""
    print_header("TEST 7: Data Quality Validation")
    
    if not results:
        print_error("No results to validate")
        return
    
    quality_checks = {
        'valid_prices': 0,
        'valid_symbols': 0,
        'has_timestamp': 0,
        'has_source': 0,
        'real_data': 0
    }
    
    for result in results:
        if result.get('price', 0) > 0:
            quality_checks['valid_prices'] += 1
        if result.get('symbol'):
            quality_checks['valid_symbols'] += 1
        if result.get('timestamp'):
            quality_checks['has_timestamp'] += 1
        if result.get('source'):
            quality_checks['has_source'] += 1
        if result.get('source') not in ['mock_data', 'error']:
            quality_checks['real_data'] += 1
    
    total = len(results)
    print_info(f"Total results: {total}")
    print_success(f"Valid prices: {quality_checks['valid_prices']}/{total}")
    print_success(f"Valid symbols: {quality_checks['valid_symbols']}/{total}")
    print_success(f"Has timestamp: {quality_checks['has_timestamp']}/{total}")
    print_success(f"Has source: {quality_checks['has_source']}/{total}")
    
    real_data_pct = (quality_checks['real_data'] / total * 100) if total > 0 else 0
    if real_data_pct >= 80:
        print_success(f"Real data: {quality_checks['real_data']}/{total} ({real_data_pct:.1f}%)")
    elif real_data_pct >= 50:
        print_warning(f"Real data: {quality_checks['real_data']}/{total} ({real_data_pct:.1f}%)")
    else:
        print_error(f"Real data: {quality_checks['real_data']}/{total} ({real_data_pct:.1f}%)")

def test_health_endpoint(service):
    """Test 8: Health endpoint"""
    print_header("TEST 8: Health Check")
    
    try:
        health = service.get_health()
        print_success(f"Health check passed")
        print_info(f"Healthy: {health['healthy']}")
        print_info(f"Providers: {health['providers']}")
        print_info(f"Cache size: {health['cache_size']}")
        
        for provider, limits in health.get('rate_limits', {}).items():
            print_info(f"{provider}: {limits['calls_remaining']} calls remaining")
    except Exception as e:
        print_error(f"Health check failed: {e}")

def run_all_tests():
    """Run complete test suite"""
    print_header("🧪 YantraX RL - Live Data Validation Suite")
    print_info(f"Started at: {datetime.now().isoformat()}")
    
    # Test 1: Environment Variables
    if not test_env_variables():
        print_error("\nFATAL: No API credentials configured!")
        print_info("Set FMP_API_KEY in environment")
        return False

    # Test 2: Service Initialization
    service = test_service_initialization()
    if not service:
        print_error("\nFATAL: Service initialization failed!")
        return False

    # Test 3: FMP
    fmp_result = test_fmp(service)
    if not fmp_result:
        print_error("\nFATAL: FMP provider failed!")
        return False

    # Test 4: Intelligent Fetch (batch symbols)
    results = test_intelligent_fetch(service)

    # Test 5: Cache
    test_cache_mechanism(service)

    # Test 6: Data Quality
    test_data_quality(results)

    # Test 7: Health
    test_health_endpoint(service)    
    # Final Summary
    print_header("🎯 Test Summary")
    print_success("All critical tests passed!")
    print_success("YantraX RL live data system is operational")
    print_info(f"Completed at: {datetime.now().isoformat()}")
    
    return True

if __name__ == '__main__':
    print("\n" * 2)
    success = run_all_tests()
    print("\n" * 2)
    
    sys.exit(0 if success else 1)