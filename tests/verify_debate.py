import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.ai_firm.debate_engine import DebateEngine
from backend.ai_firm.personas import Warren, Cathie, Quant, DegenAuditor

# Mock Agent Manager (not strictly needed since we iterate personas now, but good for stability)
class MockAgentManager:
    pass

def test_debate():
    print("🧠 Starting Debate Engine Verification...")
    
    engine = DebateEngine(MockAgentManager())
    
    # Scene 1: An overvalued tech stock (High P/E, High Momentum)
    # Warren should hate it, Cathie should love it.
    context_tech_bubble = {
        'fundamentals': {'pe_ratio': 150, 'return_on_equity': 0.05},
        'technicals': {'momentum_score': 85, 'trend': 'bullish', 'rsi': 80},
        'liquidity': 5000000,
        'is_verified': True
    }
    
    print("\n--- DEBATE 1: HYPED TECH STOCK ---")
    result = engine.conduct_debate("HYPE_TECH", context_tech_bubble)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")

    # Scene 2: A solid value stock (Low P/E, Good ROE)
    # Warren should love it, Cathie might find it boring (HOLD).
    context_value_stock = {
        'fundamentals': {'pe_ratio': 12, 'return_on_equity': 0.18},
        'technicals': {'momentum_score': 40, 'trend': 'sideways', 'rsi': 45},
        'liquidity': 10000000,
        'is_verified': True
    }
    
    print("\n--- DEBATE 2: BORING VALUE STOCK ---")
    result = engine.conduct_debate("OLD_CORP", context_value_stock)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")
        
    # Scene 3: A rug pull (Unverified)
    # DegenAuditor should kill it.
    context_rug = {
        'fundamentals': {},
        'technicals': {},
        'liquidity': 500,
        'is_verified': False
    }
    
    print("\n--- DEBATE 3: UNVERIFIED COIN ---")
    result = engine.conduct_debate("SCAM_COIN", context_rug)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")

if __name__ == "__main__":
    test_debate()
