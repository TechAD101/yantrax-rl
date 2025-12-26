import sys
import os
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from ai_firm.ceo import AutonomousCEO
    from ai_firm.agent_manager import AgentManager
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def verify_institutional_audit():
    print("🔱 Initializing Institutional Verification...")
    
    # ceo.py creates its own AgentManager by default
    ceo = AutonomousCEO()
    
    # 1. Test CEO Status
    print("\n[1/3] Verifying CEO Institutional Metrics...")
    status = ceo.get_ceo_status()
    
    metrics = status.get('institutional_metrics', {})
    pain = metrics.get('pain_level')
    mood = metrics.get('market_mood')
    checks = metrics.get('last_fundamental_check', {})
    
    print(f"  - Pain Level: {pain}% (Expected: int 0-100)")
    print(f"  - Market Mood: {mood} (Expected: str)")
    print(f"  - Fundamental Checks: {len(checks)} items found")
    
    assert isinstance(pain, int), "Pain level should be an integer"
    assert mood in ["euphoria", "greed", "neutral", "fear", "despair"], f"Invalid mood: {mood}"
    assert len(checks) == 15, f"Expected 15 fundamental checks, got {len(checks)}"
    print("  ✅ CEO Metrics Verified")

    # 2. Test Dynamic Mood
    print("\n[2/3] Simulating High Success for Euphoria...")
    # Mocking a high confidence decision
    from ai_firm.ceo import CEODecision
    ceo.decision_history.append(CEODecision(
        id="test",
        timestamp=datetime.now(),
        decision_type="BUY",
        context={"ticker": "AAPL"},
        reasoning="Testing euphoria",
        confidence=0.95,
        expected_impact="High",
        agent_overrides=[],
        memory_references=[]
    ))
    new_mood = ceo._determine_market_mood()
    print(f"  - Mood post-success: {new_mood}")
    assert new_mood == "euphoria", "Mood should be euphoria for confidence > 0.85"
    
    print("\n[2.1/3] Simulating High Pain for Low Confidence...")
    ceo.decision_history.append(CEODecision(
        id="test_fail",
        timestamp=datetime.now(),
        decision_type="HOLD",
        context={"ticker": "AAPL"},
        reasoning="Testing pain",
        confidence=0.1,
        expected_impact="Low",
        agent_overrides=[],
        memory_references=[]
    ))
    new_pain = ceo._calculate_pain_level()
    print(f"  - Pain Level post-fail: {new_pain}%")
    assert new_pain > pain, "Pain should increase after low confidence decision"
    print("  ✅ Dynamic Logic Verified")

    # 3. Test Fundamental Checklist Content
    print("\n[3/3] Auditing Checklist Items...")
    required_items = [
        "Revenue Growth", "EPS Increasing", "Debt-to-Equity < 1", 
        "ROE > 15%", "Management Quality Audit", "Economic Moat Verified"
    ]
    for item in required_items:
        assert item in checks, f"Missing required check: {item}"
    print(f"  ✅ All {len(required_items)} core items present in checklist")

    print("\n🏆 Institutional Audit Verification: PASSED")

if __name__ == "__main__":
    verify_institutional_audit()
