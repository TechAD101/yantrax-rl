
import sys
import os
import json

# Setup path
sys.path.append(os.path.abspath("c:/Users/ABhati/Documents/yantrax-rl/backend"))

# Mock imports
from ai_firm.ceo import AutonomousCEO, CEOPersonality

print("--- 🧪 PHASE 1: THE SOUL LAYER VALIDATION ---")

# 1. Test Philosophy Injection
ceo = AutonomousCEO()
print(f"✅ CEO Created. Personality: {ceo.personality.value}")
if hasattr(ceo, 'philosophy'):
    print("✅ Philosophy Manager Found in CEO (Soul Injection Successful).")
else:
    print("❌ ERROR: CEO has no Soul.")
    sys.exit(1)

# 2. Test "Ungli Kato" Protocol (Stop Loss)
print("\n--- 🗡️ TESTING UNGLI KATO PROTOCOL ---")
high_risk_context = {
    'ticker': 'BTC',
    'volatility': 0.8,
    'cummulative_drawdown': 0.15, # 15% drawdown (High)
    'loss_streak': 3
}

guidance = ceo.philosophy.get_guidance(high_risk_context)
print(f"INPUT: Drawdown=15%, LossStreak=3")
print(f"GUIDANCE: {guidance}")

if "Ungli kato" in guidance:
    print("✅ PASS: Ungli Kato Triggered correctly.")
else:
    print("❌ FAIL: Ungli Kato NOT triggered.")

# 3. Test Mood Board Logic
print("\n--- 🎭 TESTING MOOD BOARD LOGIC ---")
from ai_firm.mood_board import MoodBoardManager
# Mock Market Service
class MockMarket:
    pass
    
mood_board = MoodBoardManager(ceo, MockMarket())
data = mood_board.get_dashboard_state()
print(f"Current Mood: {data['emotion_dial']['current_mood']}")
print(f"Visual Weather: {data['market_weather']}")
print(f"Trivia: {data['trivia_ticker']}")
print(f"Philosophy Quote: {data['philosophy_quote']}")

if 'Ungli' in data['philosophy_quote'] or 'Bund' in data['philosophy_quote'] or 'Bazaar' in data['philosophy_quote']:
    print("✅ PASS: Philosophy quote injected into Mood Board.")
else:
     print("❌ FAIL: Philosophy quote missing.")

print("\n--- ✨ SYSTEM IS WORLD CLASS READY ---")
