import asyncio
import sys
import os
os.environ['SECRET_KEY'] = 'test-secret-key-for-ci'

# Add project root and backend to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

from backend.ai_firm.debate_engine import DebateEngine
from backend.ai_firm.personas import Warren, Cathie, Quant, DegenAuditor

# Mock Agent Manager
class MockAgentManager:
    pass

async def test_debate():
    print("🧠 Starting Debate Engine Verification...")
    
    engine = DebateEngine(MockAgentManager())
    
    # Scene 1: An overvalued tech stock (High P/E, High Momentum)
    context_tech_bubble = {
        'fundamentals': {'pe_ratio': 150, 'return_on_equity': 0.05},
        'technicals': {'momentum_score': 85, 'trend': 'bullish', 'rsi': 80},
        'liquidity': 5000000,
        'is_verified': True
    }
    
    print("\n--- DEBATE 1: HYPED TECH STOCK ---")
    result = await engine.conduct_debate("HYPE_TECH", context_tech_bubble)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")

    # Scene 2: A solid value stock
    context_value_stock = {
        'fundamentals': {'pe_ratio': 12, 'return_on_equity': 0.18},
        'technicals': {'momentum_score': 40, 'trend': 'sideways', 'rsi': 45},
        'liquidity': 10000000,
        'is_verified': True
    }
    
    print("\n--- DEBATE 2: BORING VALUE STOCK ---")
    result = await engine.conduct_debate("OLD_CORP", context_value_stock)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")
        
    # Scene 3: A rug pull
    context_rug = {
        'fundamentals': {},
        'technicals': {},
        'liquidity': 500,
        'is_verified': False
    }
    
    print("\n--- DEBATE 3: UNVERIFIED COIN ---")
    result = await engine.conduct_debate("SCAM_COIN", context_rug)
    
    print(f"Winner: {result['winning_signal']}")
    print(f"Consensus: {result['consensus_score']}")
    for arg in result['arguments']:
        print(f"  🗣️ {arg['agent']}: {arg['signal']} ({arg['confidence']}) - {arg['reasoning'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_debate())
