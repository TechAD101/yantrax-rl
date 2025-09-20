#!/usr/bin/env python3
"""
YantraX AI Firm Startup Diagnostics
Runs comprehensive checks to ensure all AI firm components can initialize properly
"""

import sys
import os
import traceback
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

print("ℹ️ YantraX AI Firm Startup Diagnostics")
print(f"📁 Working Directory: {os.getcwd()}")
print(f"🐍 Python Path: {sys.path[:3]}...")
print()

# Test core dependencies
print("🔍 Testing Core Dependencies:")
try:
    import flask
    import numpy as np
    import yfinance
    print("✅ Flask, NumPy, yfinance - OK")
except ImportError as e:
    print(f"❌ Core dependencies failed: {e}")
    sys.exit(1)

# Test AI firm components
print("
🤖 Testing AI Firm Components:")

# Test AI Firm imports
try:
    from ai_firm.ceo import AutonomousCEO, CEOPersonality
    print("✅ CEO module - OK")
except ImportError as e:
    print(f"⚠️ CEO module failed: {e}")
    traceback.print_exc()

try:
    from ai_firm.agent_manager import AgentManager
    print("✅ Agent Manager - OK")
except ImportError as e:
    print(f"⚠️ Agent Manager failed: {e}")
    traceback.print_exc()

# Test personas
try:
    from ai_agents.personas.warren import WarrenAgent
    print("✅ Warren persona - OK")
except ImportError as e:
    print(f"⚠️ Warren persona failed: {e}")
    traceback.print_exc()

try:
    from ai_agents.personas.cathie import CathieAgent
    print("✅ Cathie persona - OK")
except ImportError as e:
    print(f"⚠️ Cathie persona failed: {e}")
    traceback.print_exc()

# Test AI firm initialization
print("
🚀 Testing AI Firm Initialization:")
try:
    ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
    warren = WarrenAgent()
    cathie = CathieAgent()
    agent_manager = AgentManager()
    
    print("✅ AI Firm initialization - SUCCESS")
    print(f"  • CEO personality: {ceo.personality.value}")
    print(f"  • Warren agent: {warren.name}")
    print(f"  • Cathie agent: {cathie.name}")
    print(f"  • Total agents: {len(agent_manager.agents)}")
    
    # Test a sample decision
    sample_context = {'type': 'startup_test', 'market_trend': 'neutral'}
    test_decision = ceo.make_strategic_decision(sample_context)
    print(f"  • CEO test decision confidence: {test_decision.confidence:.2f}")
    
except Exception as e:
    print(f"❌ AI Firm initialization failed: {e}")
    traceback.print_exc()

print("
✨ Startup diagnostics complete!")
print("If all components show ✅ OK, the AI firm should be fully operational.")
