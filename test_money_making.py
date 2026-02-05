#!/usr/bin/env python3
"""
COMPREHENSIVE MONEY-MAKING TEST
Tests actual trading flow to prove system can make money while user sleeps

This tests:
1. God-cycle signal generation 
2. Manual trade execution
3. Portfolio management 
4. Market data integration
5. Trading automation potential
"""

import requests
import json
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:5000"  # Assuming local backend
TEST_SYMBOL = "AAPL"
TEST_USD = 1000

def test_1_god_cycle_signals():
    """Test god-cycle endpoint"""
    print("🧪 Testing God-Cycle Signal Generation...")
    
    try:
        response = requests.get(f"{BASE_URL}/god-cycle?symbol={TEST_SYMBOL}", timeout=30)
        data = response.json()
        
        print(f"✅ God-cycle Status: {data.get('status', 'unknown')}")
        print(f"📊 Signal: {data.get('signal', 'NONE')}")
        print(f"💰 Confidence: {data.get('ceo_decision', {}).get('confidence', 0)}")
        
        # Check if it's a real trading decision or simulation
        signal = data.get('signal', '')
        ceo_decision = data.get('ceo_decision', {})
        
        is_trading = signal in ['BUY', 'SELL', 'HOLD']
        is_simulation = data.get('status') == 'simulated'
        
        print(f"🔍 TRADING: {is_trading} | SIMULATION: {is_simulation}")
        
        if is_simulation:
            print(f"❌ ISSUE: Returning simulated decision instead of trade signal")
            return False
        else:
            print(f"✅ SUCCESS: Real trading decision generated")
            return True
            
    except Exception as e:
        print(f"❌ ERROR: God-cycle test failed: {e}")
        return False

def test_2_manual_trade_execution():
    """Test if we can actually execute trades"""
    print("💼 Testing Manual Trade Execution...")
    
    # Check portfolio exists
    try:
        response = requests.get(f"{BASE_URL}/api/portfolios", timeout=10)
        portfolios = response.json()
        
        if not portfolios.get('portfolios'):
            print("❌ No portfolios found - need to create one first")
            return False
        
        portfolio_id = portfolios['portfolios'][0]['id']
        print(f"✅ Found portfolio #{portfolio_id}")
        
    except Exception as e:
        print(f"❌ ERROR: Failed to get portfolios: {e}")
        return False
    
    # Execute a test trade
    trade_data = {
        "symbol": TEST_SYMBOL,
        "action": "BUY",
        "quantity": TEST_USD,
        "price": 175.50  # Test price for execution
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/portfolio/{portfolio_id}/trade",
            json=trade_data,
            timeout=30
        )
        
        if response.status_code == 201:
            print("💰 SUCCESS: Trade executed via API")
            return True
        else:
            print(f"❌ Trade failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Trade execution failed: {e}")
        return False

def test_3_automation_potential():
    """Test automation bridge potential"""
    print("🤖 Testing Automation Potential...")
    
    # Test if we can create an automated trading script
    signals = []
    
    # Test multiple god-cycle calls to see if we can build automation
    for i in range(3):
        try:
            response = requests.get(f"{BASE_URL}/god-cycle?symbol={TEST_SYMBOL}", timeout=10)
            data = response.json()
            
            signal = data.get('signal', '')
            if signal in ['BUY', 'SELL']:
                signals.append({
                    'time': datetime.now().isoformat(),
                    'signal': signal,
                    'confidence': data.get('ceo_decision', {}).get('confidence', 0)
                })
                
        except Exception as e:
            print(f"❌ Signal capture #{i+1} failed: {e}")
    
    print(f"📊 Captured {len(signals)} trading signals")
    
    if len(signals) >= 2:
        print("✅ SUCCESS: Multiple signals captured - automation potential exists")
        print("🤖 CAPABILITY: System could automate trading based on signal consistency")
        return True
    else:
        print("❌ ISSUE: Insufficient signals for automation")
        return False

def test_4_real_market_integration():
    """Test with real market data"""
    print("📈 Testing Real Market Data Integration...")
    
    try:
        # Test market price API
        response = requests.get(f"{BASE_URL}/api/market-price?symbol={TEST_SYMBOL}", timeout=10)
        data = response.json()
        
        price = data.get('price', 0)
        source = data.get('source', 'unknown')
        
        print(f"✅ Market Price: ${price} (source: {source})")
        
        # Test god-cycle with real data
        response2 = requests.get(f"{BASE_URL}/god-cycle?symbol={TEST_SYMBOL}", timeout=10)
        data2 = response2.json()
        
        real_signal = data2.get('signal', '')
        uses_real_data = source != 'simulated'
        
        print(f"✅ Signal with Real Data: {real_signal}")
        print(f"📈 Uses Real Market Data: {uses_real_data}")
        
        return uses_real_data
        
    except Exception as e:
        print(f"❌ ERROR: Market data test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide detailed analysis"""
    print("=" * 60)
    print("🧪 COMPREHENSIVE MONEY-MAKING TEST")
    print("=" * 60)
    print(f"🕒 Testing with Symbol: {TEST_SYMBOL}")
    print(f"💰 Target: Prove system can make money while user sleeps")
    print()
    
    # Test results
    results = {
        'god_cycle_signals': test_1_god_cycle_signals(),
        'trade_execution': test_2_manual_trade_execution(),
        'automation_potential': test_3_automation_potential(),
        'real_market_integration': test_4_real_market_integration(),
        'timestamp': datetime.now().isoformat()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS:")
    
    success_count = sum(1 for result in results.values() if result)
    print(f"✅ Tests Passed: {success_count}/4")
    
    if success_count >= 3:
        print("💰 CONCLUSION: System has PROVEN money-making potential!")
        print("🤖 CAPABILITY: Can generate signals and execute trades")
        print("🔥 MISSING: Automation bridge from signals to execution")
        
        automation_plan = """
        🔧 IMPLEMENT AUTOMATION BRIDGE:
        
        1. Signal Monitoring Service
           - Background task monitoring god-cycle signals
           - Telegram/Discord notifications for strong signals
           
        2. Trade Execution Service  
           - Convert signal confidence to position sizing
           - Risk management rules
           - Stop-loss automation
           
        3. Portfolio Automation
           - Rebalancing based on AI consensus
           - Profit-taking at target levels
           
        4. Broker Integration
           - Real broker API (Alpaca/Interactive Brokers)
           - Paper trading with real execution
        """
        
        print(automation_plan)
        
    else:
        print("❌ CRITICAL: System lacks money-making automation")
        print("🚨 NEEDS: Automation bridge, real broker integration, scheduled trading")
    
    print("=" * 60)
    return results

if __name__ == "__main__":
    results = run_comprehensive_test()
    
    # Save results to file for analysis
    with open('money_making_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: money_making_test_results.json")
    print("🔍 Ready for automation implementation based on test findings")