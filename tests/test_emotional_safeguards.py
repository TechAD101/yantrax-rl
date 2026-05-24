import pytest
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.emotional_safeguards import (
    EmotionalSafeguardsService,
    EmotionalState,
    SafeguardTrigger,
    get_emotional_safeguards
)

@pytest.fixture
def service():
    """Fixture to provide a fresh instance of EmotionalSafeguardsService"""
    return EmotionalSafeguardsService()

def test_initial_state(service):
    """Test the default initial state of the service"""
    status = service.get_status()
    assert status["emotional_state"] == EmotionalState.CALM.value
    assert status["pain_level"] == 0
    assert status["trading_allowed"] is True
    assert status["cooling_off_active"] is False
    assert status["consecutive_losses"] == 0
    assert status["overconfidence_streak"] == 0
    assert status["current_drawdown_pct"] == 0.0

def test_singleton_getter():
    """Test the global singleton getter"""
    instance1 = get_emotional_safeguards()
    instance2 = get_emotional_safeguards()
    assert instance1 is instance2
    assert isinstance(instance1, EmotionalSafeguardsService)

def test_update_state_calm(service):
    """Test updating state without triggering safeguards"""
    context = {
        "portfolio_value": 10000,
        "peak_portfolio_value": 10000,
        "market_volatility": 0.2,
        "agent_confidence": 0.5
    }
    status = service.update_state(context)
    assert status["emotional_state"] == EmotionalState.CALM.value
    assert status["current_drawdown_pct"] == 0.0
    assert status["trading_allowed"] is True

def test_drawdown_triggers_safeguard(service):
    """Test 5% drawdown triggers safeguard and mouna mode"""
    context = {
        "portfolio_value": 9500,
        "peak_portfolio_value": 10000, # 5% drawdown
        "market_volatility": 0.2,
        "agent_confidence": 0.5
    }
    status = service.update_state(context)
    assert status["current_drawdown_pct"] == 5.0
    assert status["emotional_state"] == EmotionalState.MOUNA.value
    assert status["cooling_off_active"] is True
    assert status["trading_allowed"] is False

    events = service.get_event_log()
    assert len(events) == 1
    assert events[0]["trigger"] == SafeguardTrigger.DRAWDOWN_5PCT.value

def test_consecutive_losses_triggers_safeguard(service):
    """Test 3 consecutive losses triggers safeguard"""
    # Set portfolio value first so we don't trigger revenge trade on tiny losses
    context = {"portfolio_value": 10000, "peak_portfolio_value": 10000}
    service.update_state(context)

    # 3 consecutive losses
    service.record_trade_outcome("loss", -10, "AAPL")
    service.record_trade_outcome("loss", -10, "MSFT")
    service.record_trade_outcome("loss", -10, "GOOG")

    context = {
        "portfolio_value": 9900,
        "peak_portfolio_value": 10000,
        "market_volatility": 0.2,
        "agent_confidence": 0.5
    }
    status = service.update_state(context)

    assert status["consecutive_losses"] == 3
    assert status["emotional_state"] == EmotionalState.MOUNA.value
    assert status["cooling_off_active"] is True

    events = service.get_event_log()
    assert any(e["trigger"] == SafeguardTrigger.RAPID_LOSSES.value for e in events)

def test_revenge_trade_detection(service):
    """Test revenge trade safeguard on large loss"""
    context = {
        "portfolio_value": 10000,
        "peak_portfolio_value": 10000,
    }
    service.update_state(context) # set current portfolio value

    # 6% loss on a single trade
    service.record_trade_outcome("loss", -600, "TSLA")

    events = service.get_event_log()
    assert len(events) == 1
    assert events[0]["trigger"] == SafeguardTrigger.REVENGE_TRADE.value

    status = service.get_status()
    assert status["emotional_state"] == EmotionalState.MOUNA.value
    assert status["trading_allowed"] is False

def test_overconfidence_safeguard(service):
    """Test overconfidence streak triggers safeguard"""
    context = {
        "portfolio_value": 10000,
        "peak_portfolio_value": 10000,
        "market_volatility": 0.2,
        "agent_confidence": 0.95
    }

    # 3 consecutive high confidence updates
    service.update_state(context)
    service.update_state(context)
    status = service.update_state(context)

    assert status["overconfidence_streak"] == 3
    assert status["emotional_state"] == EmotionalState.MOUNA.value
    assert status["trading_allowed"] is False

    events = service.get_event_log()
    assert any(e["trigger"] == SafeguardTrigger.OVERCONFIDENCE.value for e in events)

def test_volatility_spike_safeguard(service):
    """Test high volatility triggers safeguard"""
    context = {
        "portfolio_value": 10000,
        "peak_portfolio_value": 10000,
        "market_volatility": 0.9, # High volatility > 0.8
        "agent_confidence": 0.5
    }
    status = service.update_state(context)

    assert status["emotional_state"] == EmotionalState.MOUNA.value
    events = service.get_event_log()
    assert any(e["trigger"] == SafeguardTrigger.VOLATILITY_SPIKE.value for e in events)

def test_manual_override(service):
    """Test manual override puts system in mouna mode"""
    status = service.manual_override("Testing override")

    assert status["emotional_state"] == EmotionalState.MOUNA.value
    assert status["trading_allowed"] is False

    events = service.get_event_log()
    assert len(events) == 1
    assert events[0]["trigger"] == SafeguardTrigger.MANUAL_OVERRIDE.value
    assert events[0]["context"]["reason"] == "Testing override"

def test_is_trading_allowed_cooling_off(service):
    """Test is_trading_allowed checks during cooling off"""
    service.manual_override()

    allowed_check = service.is_trading_allowed()
    assert allowed_check["allowed"] is False
    assert "MOUNA_MODE" in allowed_check["reason"]
    assert allowed_check["cooling_off_remaining_seconds"] > 0

def test_cooling_off_expiration(service):
    """Test trading is allowed after cooling off period expires"""
    # Trigger a short 15-minute overconfidence safeguard manually for testing expiration
    # We will manipulate the _cooling_off_until directly to simulate time passing
    service._trigger_safeguard(SafeguardTrigger.OVERCONFIDENCE, {})

    assert service.is_trading_allowed()["allowed"] is False

    # Fast forward time
    service._cooling_off_until = datetime.now() - timedelta(minutes=1)

    # We also need to update state to clear MOUNA since the check relies on MOUNA mode
    # If state is still MOUNA, it blocks trading even if cooling period is over.
    # update_state will re-evaluate emotional state based on context
    context = {
        "portfolio_value": 10000,
        "peak_portfolio_value": 10000,
        "market_volatility": 0.2,
        "agent_confidence": 0.5
    }
    service.update_state(context)

    allowed_check = service.is_trading_allowed()
    assert allowed_check["allowed"] is True
    assert allowed_check["cooling_off_remaining_seconds"] == 0

def test_emotional_state_classification(service):
    """Test classification logic directly"""
    # 20% drawdown -> Panicked
    state = service._classify_emotional_state(0.20, 0, 0.2, 0.5)
    assert state == EmotionalState.PANICKED

    # 5 consecutive losses -> Panicked
    state = service._classify_emotional_state(0.0, 5, 0.2, 0.5)
    assert state == EmotionalState.PANICKED

    # 10% drawdown -> Fearful
    state = service._classify_emotional_state(0.10, 0, 0.2, 0.5)
    assert state == EmotionalState.FEARFUL

    # 5% drawdown -> Anxious
    state = service._classify_emotional_state(0.05, 0, 0.2, 0.5)
    assert state == EmotionalState.ANXIOUS

    # Euphoric
    state = service._classify_emotional_state(0.01, 0, 0.2, 0.95)
    assert state == EmotionalState.EUPHORIC

    # Greedy
    state = service._classify_emotional_state(0.0, 0, 0.2, 0.8)
    assert state == EmotionalState.GREEDY

    # Calm
    state = service._classify_emotional_state(0.0, 0, 0.2, 0.5)
    assert state == EmotionalState.CALM

def test_record_win_resets_losses(service):
    """Test a winning trade resets consecutive losses"""
    service.record_trade_outcome("loss", -10, "AAPL")
    assert service._consecutive_losses == 1

    service.record_trade_outcome("win", 10, "AAPL")
    assert service._consecutive_losses == 0

def test_pain_level_calculation(service):
    """Test pain level calculations"""
    # base = drawdown * 300, loss_bonus = consecutive * 8

    # 10% DD -> 30 pain
    assert service._calculate_pain_level(0.10) == 30

    # 10% DD + 2 losses -> 30 + 16 = 46 pain
    service._consecutive_losses = 2
    assert service._calculate_pain_level(0.10) == 46

    # Cap at 100
    service._consecutive_losses = 10
    assert service._calculate_pain_level(0.50) == 100
