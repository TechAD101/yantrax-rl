import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Make sure backend is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ai_agents.persona_registry import PersonaRegistry, get_persona_registry
from ai_agents.base_persona import PersonaArchetype, VoteType, PersonaVote

def test_registry_initialization():
    registry = PersonaRegistry()
    personas = registry.get_all_personas()
    assert len(personas) >= 6

def test_get_persona():
    registry = PersonaRegistry()
    agent = registry.get_persona("TradeExecutor")
    assert agent is not None
    assert agent.name == "TradeExecutor"

def test_get_personas_by_archetype():
    registry = PersonaRegistry()
    agents = registry.get_personas_by_archetype(PersonaArchetype.SYSTEMATIC)
    assert len(agents) >= 1
    for agent in agents:
        assert agent.archetype == PersonaArchetype.SYSTEMATIC

def test_get_persona_summary():
    registry = PersonaRegistry()
    summary = registry.get_persona_summary("TradeExecutor")
    assert summary is not None
    assert summary['name'] == "tradeexecutor"
    assert summary['archetype'] == PersonaArchetype.SYSTEMATIC.value

    # Test non-existent persona
    assert registry.get_persona_summary("NonExistent") is None

def test_get_all_summaries():
    registry = PersonaRegistry()
    summaries = registry.get_all_summaries()
    assert len(summaries) >= 6
    names = [s['name'] for s in summaries]
    assert "tradeexecutor" in names

def test_conduct_vote():
    registry = PersonaRegistry()

    proposal = {"symbol": "BTC", "action": "BUY"}
    market_context = {"market_trend": "bullish"}

    mock_agent1 = MagicMock()
    mock_agent1.name = "Mock1"
    mock_agent1.vote.return_value = PersonaVote(
        persona_name="Mock1",
        archetype=PersonaArchetype.VALUE,
        vote=VoteType.BUY,
        confidence=0.8,
        reasoning="good",
        weight=1.0
    )

    mock_agent2 = MagicMock()
    mock_agent2.name = "Mock2"
    mock_agent2.vote.return_value = PersonaVote(
        persona_name="Mock2",
        archetype=PersonaArchetype.GROWTH,
        vote=VoteType.BUY,
        confidence=0.9,
        reasoning="great",
        weight=1.5
    )

    registry._personas = {
        "mock1": mock_agent1,
        "mock2": mock_agent2
    }

    result = registry.conduct_vote(proposal, market_context)
    assert result['proposal'] == proposal
    assert len(result['votes']) == 2
    assert result['consensus'] == VoteType.BUY.value
    assert result['consensus_strength'] == 1.0
    # Floating point arithmetic precision issue handled with round()
    assert result['total_voting_power'] == round((1.0 * 0.8) + (1.5 * 0.9), 3)

def test_conduct_vote_exception():
    registry = PersonaRegistry()
    mock_agent = MagicMock()
    mock_agent.name = "ErrorAgent"
    mock_agent.vote.side_effect = Exception("Vote failed")
    registry._personas = {"erroragent": mock_agent}

    result = registry.conduct_vote({}, {})
    # Should handle exception and default to HOLD
    assert result['consensus'] == "HOLD"
    assert result['total_voting_power'] == 0

def test_get_persona_registry_singleton():
    import ai_agents.persona_registry as pr
    pr._persona_registry = None

    reg1 = get_persona_registry()
    reg2 = get_persona_registry()

    assert reg1 is reg2
    assert isinstance(reg1, PersonaRegistry)

def test_initialization_fallback():
    with patch('importlib.import_module', side_effect=Exception("Mocked import error")):
        registry = PersonaRegistry()
        assert len(registry._personas) == 6 # The 6 supplementary personas

def test_get_persona_summary_base_agent_fallback():
    registry = PersonaRegistry()
    # Create an agent without 'voting_weight' to trigger the else block
    class DummyAgent:
        name = "Dummy"
        archetype = PersonaArchetype.VALUE
        confidence = 0.5

    dummy = DummyAgent()
    registry._personas["dummy"] = dummy
    summary = registry.get_persona_summary("dummy")

    assert summary['name'] == "dummy"
    assert summary['confidence'] == 0.5
    assert summary['voting_weight'] == 1.0
    assert summary['department'] == 'placeholder'
