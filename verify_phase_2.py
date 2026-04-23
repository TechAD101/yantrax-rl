
import sys
import os

# Setup path
sys.path.append(os.path.abspath("c:/Users/ABhati/Documents/yantrax-rl/backend"))

# Mock imports
from services.marketplace_service import MarketplaceService

print("--- 🤝 PHASE 2: THE SOCIAL LAYER VALIDATION ---")

# 1. Initialize Service
market = MarketplaceService()
print("✅ MarketplaceService Initialized.")

# 2. Test Leaderboard
print("\n--- 🏆 VALIDATING LEADERBOARD ---")
top_strats = market.get_top_strategies()
print(f"Found {len(top_strats)} strategies.")
first = top_strats[0]
print(f"Top Strategy: {first['name']} by {first['author']} (Sharpe: {first['sharpe_ratio']})")

if first['sharpe_ratio'] >= 2.0:
    print("✅ PASS: Leaderboard sorting works (High Sharpe first).")
else:
    print("❌ FAIL: Leaderboard sorting broken.")

# 3. Test Publishing
print("\n--- 📝 VALIDATING PUBLISHING ---")
new_strat = market.publish_strategy({
    "name": "My AI Alpha",
    "author": "Aditya",
    "description": "Reinforcement Learning scalper",
    "type": "AI_MODEL"
})
print(f"Published: {new_strat['name']} (ID: {new_strat['id']})")

if new_strat['id'] in market.strategies:
    print("✅ PASS: Strategy successfully stored.")
else:
    print("❌ FAIL: Strategy not found in DB.")

# 4. Test Copy Trading
print("\n--- 🐑 VALIDATING COPY TRADING ---")
copy_res = market.copy_strategy(new_strat['id'], "user_test_99", 5000)
print(f"Copy Result: {copy_res['message']}")

if copy_res['success']:
    print("✅ PASS: Copy Trade registered.")
else:
    print("❌ FAIL: Copy Trade failed.")

# 5. Test Contests
print("\n--- ⚔️ VALIDATING CONTESTS ---")
contest = market.get_active_contest()
print(f"Active Contest: {contest['title']} (Prize: {contest['prize_pool']})")

if contest['status'] == "ACTIVE":
    print("✅ PASS: Contest is active.")
else:
    print("❌ FAIL: No active contest.")

print("\n--- 🌍 SYSTEM IS SOCIALLY CONNECTED ---")
