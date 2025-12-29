"""
Verification Script: Explicit AI Personas with Voting Power

Tests the newly implemented PersonaAgent architecture:
- Warren and Cathie as formal voting personas
- PersonaRegistry integration
- Explicit vote() and analyze() methods
- Context-aware voting weight adjustment
"""

import sys
import os

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

from ai_agents.persona_registry import get_persona_registry
from ai_agents.base_persona import VoteType

def test_persona_registry():
    """Test PersonaRegistry initialization and persona discovery"""
    print("=" * 60)
    print("TEST 1: PersonaRegistry Initialization")
    print("=" * 60)
    
    registry = get_persona_registry()
    personas = registry.get_all_personas()
    
    print("✓ PersonaRegistry initialized")
    print(f"✓ Registered personas: {len(personas)}")
    
    for persona in personas:
        print(f"  - {persona.name} ({persona.archetype.value}) | weight={persona.voting_weight}")
    
    assert len(personas) == 2, "Expected 2 personas (Warren, Cathie)"
    print("\n✅ PASS: PersonaRegistry has 2 personas\n")

def test_warren_analysis():
    """Test Warren's analyze() method"""
    print("=" * 60)
    print("TEST 2: Warren Analysis")
    print("=" * 60)
    
    registry = get_persona_registry()
    warren = registry.get_persona('warren')
    
    context = {
        'symbol': 'AAPL',
        'fundamentals': {
            'pe_ratio': 22.5,
            'return_on_equity': 0.18,
            'profit_margin': 0.25,
            'debt_to_equity': 0.4,
            'dividend_yield': 0.025,
            'revenue_growth': 0.08
        },
        'market_trend': 'neutral'
    }
    
    analysis = warren.analyze(context)
    
    print(f"✓ Warren analyzed {analysis.symbol}")
    print(f"  Recommendation: {analysis.recommendation}")
    print(f"  Confidence: {analysis.confidence}")
    print(f"  Reasoning: {analysis.reasoning[:80]}...")
    print(f"  Scores: {analysis.scores}")
    
    assert analysis.persona_name == 'Warren'
    assert analysis.recommendation in ['STRONG_BUY', 'BUY', 'HOLD', 'AVOID']
    print("\n✅ PASS: Warren analysis completed\n")

def test_cathie_analysis():
    """Test Cathie's analyze() method"""
    print("=" * 60)
    print("TEST 3: Cathie Analysis")
    print("=" * 60)
    
    registry = get_persona_registry()
    cathie = registry.get_persona('cathie')
    
    context = {
        'symbol': 'NVDA',
        'fundamentals': {
            'revenue_growth': 0.35,
            'rd_spending': 0.20,
            'market_cap': 500000000000
        },
        'sector_data': {
            'sector': 'artificial_intelligence',
            'disruption_score': 0.85
        },
        'market_trend': 'bullish'
    }
    
    analysis = cathie.analyze(context)
    
    print(f"✓ Cathie analyzed {analysis.symbol}")
    print(f"  Recommendation: {analysis.recommendation}")
    print(f"  Confidence: {analysis.confidence}")
    print(f"  Reasoning: {analysis.reasoning[:80]}...")
    print(f"  Scores: {analysis.scores}")
    
    assert analysis.persona_name == 'Cathie'
    assert analysis.recommendation in ['STRONG_BUY', 'BUY', 'RESEARCH', 'HOLD', 'SELL']
    print("\n✅ PASS: Cathie analysis completed\n")

def test_voting_mechanism():
    """Test explicit voting mechanism"""
    print("=" * 60)
    print("TEST 4: Voting Mechanism")
    print("=" * 60)
    
    registry = get_persona_registry()
    
    proposal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'entry_price': 150.00,
        'target_price': 180.00
    }
    
    market_context = {
        'fundamentals': {
            'pe_ratio': 22.5,
            'return_on_equity': 0.18
        },
        'market_trend': 'neutral',
        'volatility': 0.5
    }
    
    vote_result = registry.conduct_vote(proposal, market_context)
    
    print(f"✓ Vote conducted for {proposal['symbol']}")
    print(f"  Consensus: {vote_result['consensus']}")
    print(f"  Consensus Strength: {vote_result['consensus_strength']}")
    print(f"  Vote Distribution: {vote_result['vote_distribution']}")
    print(f"  Total Voting Power: {vote_result['total_voting_power']}")
    
    print("\n  Individual Votes:")
    for vote in vote_result['votes']:
        print(f"    {vote['persona_name']}: {vote['vote']} (conf={vote['confidence']}, weight={vote['weight']})")
    
    assert len(vote_result['votes']) == 2
    assert vote_result['consensus'] in [v.value for v in VoteType]
    print("\n✅ PASS: Voting mechanism working\n")

def test_context_aware_weighting():
    """Test context-aware voting weight adjustment"""
    print("=" * 60)
    print("TEST 5: Context-Aware Weight Adjustment")
    print("=" * 60)
    
    registry = get_persona_registry()
    warren = registry.get_persona('warren')
    cathie = registry.get_persona('cathie')
    
    # Bear market (Warren should get boosted)
    bear_context = {'market_trend': 'bearish', 'volatility': 0.8}
    warren_bear_weight = warren.get_vote_weight(bear_context)
    
    # Bull market (Cathie should get boosted)
    bull_context = {'market_trend': 'bullish', 'innovation_sentiment': 0.8}
    cathie_bull_weight = cathie.get_vote_weight(bull_context)
    
    print(f"✓ Warren base weight: {warren.voting_weight}")
    print(f"  Warren in bear market: {warren_bear_weight} (expected boost)")
    print(f"✓ Cathie base weight: {cathie.voting_weight}")
    print(f"  Cathie in bull market: {cathie_bull_weight} (expected boost)")
    
    assert warren_bear_weight > warren.voting_weight, "Warren should get boosted in bear markets"
    assert cathie_bull_weight > cathie.voting_weight, "Cathie should get boosted in bull markets"
    print("\n✅ PASS: Context-aware weighting works\n")

def test_performance_summaries():
    """Test that personas track performance metrics"""
    print("=" * 60)
    print("TEST 6: Performance Tracking")
    print("=" * 60)
    
    registry = get_persona_registry()
    summaries = registry.get_all_summaries()
    
    print(f"✓ Retrieved {len(summaries)} persona summaries")
    for summary in summaries:
        print(f"\n  {summary['name']} ({summary['archetype']}):")
        print(f"    Voting weight: {summary['voting_weight']}")
        print(f"    Total votes: {summary['performance']['total_votes']}")
        print(f"    Total analyses: {summary['performance']['total_analyses']}")
        print(f"    Avg confidence: {summary['performance']['avg_confidence']}")
    
    print("\n✅ PASS: Performance summaries available\n")

if __name__ == '__main__':
    try:
        print("\n" + "=" * 60)
        print("  EXPLICIT AI PERSONAS VERIFICATION")
        print("  Testing PersonaAgent Architecture")
        print("=" * 60 + "\n")
        
        test_persona_registry()
        test_warren_analysis()
        test_cathie_analysis()
        test_voting_mechanism()
        test_context_aware_weighting()
        test_performance_summaries()
        
        print("=" * 60)
        print("  ✅ ALL TESTS PASSED!")
        print("  Explicit AI Personas with voting power verified.")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
