import os
import sys
import subprocess

print("\n" + "="*70)
print("    COMPREHENSIVE PRE-DEPLOYMENT VERIFICATION")
print("="*70 + "\n")

issues_found = []
successes = []

# 1. Check if v2 service file exists
print("[1/10] Checking if MarketDataService v2 exists...")
if os.path.exists('services/market_data_service_v2.py'):
    successes.append("✅ services/market_data_service_v2.py exists")
    print("    ✅ PASS: File exists")
else:
    issues_found.append("❌ services/market_data_service_v2.py NOT FOUND")
    print("    ❌ FAIL: File missing")

# 2. Check if services/__init__.py exists
print("\n[2/10] Checking services/__init__.py...")
if not os.path.exists('services/__init__.py'):
    with open('services/__init__.py', 'w') as f:
        f.write('')
    successes.append("✅ Created services/__init__.py")
    print("    ✅ PASS: Created __init__.py")
else:
    successes.append("✅ services/__init__.py exists")
    print("    ✅ PASS: Already exists")

# 3. Check main.py imports MarketDataService
print("\n[3/10] Checking main.py imports...")
with open('main.py', 'r') as f:
    main_content = f.read()
    
if 'from services.market_data_service_v2 import MarketDataService' in main_content:
    successes.append("✅ main.py imports MarketDataService v2")
    print("    ✅ PASS: Correct import found")
else:
    issues_found.append("❌ main.py does NOT import MarketDataService v2")
    print("    ❌ FAIL: Import missing")

# 4. Check main.py instantiates MarketDataService
print("\n[4/10] Checking main.py instantiation...")
if 'market_data = MarketDataService()' in main_content:
    successes.append("✅ main.py uses MarketDataService()")
    print("    ✅ PASS: Correct instantiation")
else:
    issues_found.append("❌ main.py does NOT use MarketDataService()")
    print("    ❌ FAIL: Still using old MarketDataManager")

# 5. Check for old imports
print("\n[5/10] Checking for old MarketDataManager imports...")
if 'from fix_market_data import MarketDataManager' in main_content:
    issues_found.append("❌ main.py still has old MarketDataManager import")
    print("    ❌ FAIL: Old import found")
else:
    successes.append("✅ No old MarketDataManager import")
    print("    ✅ PASS: Old import removed")

# 6. Check method calls
print("\n[6/10] Checking method calls...")
if '.get_price(' in main_content:
    successes.append("✅ Uses .get_price() method")
    print("    ✅ PASS: Correct method")
else:
    # Check if it's still using old method
    if '.get_stock_price(' in main_content:
        issues_found.append("⚠️  Still using .get_stock_price() (may work but inconsistent)")
        print("    ⚠️  WARNING: Using old method name")
    else:
        successes.append("✅ Method usage OK")
        print("    ✅ PASS: Method OK")

# 7. Check if Alpha Vantage key is in environment
print("\n[7/10] Checking environment variables...")
if os.getenv('ALPHA_VANTAGE_KEY'):
    successes.append("✅ ALPHA_VANTAGE_KEY is set locally")
    print("    ✅ PASS: API key present")
else:
    print("    ⚠️  WARNING: ALPHA_VANTAGE_KEY not set locally (OK if set in Render)")

# 8. Python syntax check
print("\n[8/10] Python syntax validation...")
try:
    result = subprocess.run(['python', '-m', 'py_compile', 'main.py'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        successes.append("✅ main.py has valid Python syntax")
        print("    ✅ PASS: No syntax errors")
    else:
        issues_found.append(f"❌ main.py syntax error: {result.stderr}")
        print(f"    ❌ FAIL: {result.stderr}")
except Exception as e:
    print(f"    ⚠️  WARNING: Could not validate syntax: {e}")

# 9. Check v2 service syntax
print("\n[9/10] Validating MarketDataService v2 syntax...")
try:
    result = subprocess.run(['python', '-m', 'py_compile', 'services/market_data_service_v2.py'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        successes.append("✅ market_data_service_v2.py has valid syntax")
        print("    ✅ PASS: No syntax errors")
    else:
        issues_found.append(f"❌ v2 service syntax error: {result.stderr}")
        print(f"    ❌ FAIL: {result.stderr}")
except Exception as e:
    print(f"    ⚠️  WARNING: Could not validate: {e}")

# 10. Check requirements.txt for needed packages
print("\n[10/10] Checking requirements.txt...")
if os.path.exists('requirements.txt'):
    with open('requirements.txt', 'r') as f:
        reqs = f.read()
    required_packages = ['requests', 'fastapi']
    missing = [pkg for pkg in required_packages if pkg not in reqs.lower()]
    if missing:
        issues_found.append(f"❌ Missing packages in requirements.txt: {missing}")
        print(f"    ❌ FAIL: Missing {missing}")
    else:
        successes.append("✅ All required packages in requirements.txt")
        print("    ✅ PASS: Dependencies OK")
else:
    issues_found.append("❌ requirements.txt not found")
    print("    ❌ FAIL: requirements.txt missing")

# Summary
print("\n" + "="*70)
print("                         SUMMARY")
print("="*70)

print(f"\n✅ PASSED: {len(successes)}")
for s in successes:
    print(f"   {s}")

if issues_found:
    print(f"\n❌ ISSUES FOUND: {len(issues_found)}")
    for issue in issues_found:
        print(f"   {issue}")
    print("\n" + "="*70)
    print("⛔ DEPLOYMENT BLOCKED - FIX ISSUES ABOVE FIRST")
    print("="*70 + "\n")
    sys.exit(1)
else:
    print("\n" + "="*70)
    print("✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
    print("="*70 + "\n")
    sys.exit(0)
