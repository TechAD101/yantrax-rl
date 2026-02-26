import pytest
import sys
import os
import time
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.emotional_safeguards import (
    EmotionalSafeguardsService,
    EmotionalState,
    SafeguardTrigger,
    SafeguardEvent
)

class TestEmotionalSafeguardsService:

    @pytest.fixture
    def safeguards(self):
        """Fixture for a fresh EmotionalSafeguardsService instance."""
        s = EmotionalSafeguardsService()
        return s

    def test_initial_state(self, safeguards):
        """Test the initial state of the service."""
        assert safeguards._state == EmotionalState.CALM
        assert safeguards._pain_level == 0
        assert safeguards._consecutive_losses == 0
        assert safeguards._cooling_off_until is None
        status = safeguards.get_status()
        assert status["emotional_state"] == EmotionalState.CALM.value
        assert status["trading_allowed"] is True

    def test_state_transitions_drawdown(self, safeguards):
        """Test state transitions based on drawdown percentage."""
        # Setup: Initial portfolio value
        safeguards._peak_portfolio_value = 100000.0
        safeguards._current_portfolio_value = 100000.0

        # Case 1: Small drawdown (no change, still CALM)
        context = {
            "portfolio_value": 99000.0,  # 1% drawdown
            "peak_portfolio_value": 100000.0,
            "trade_result": None,
            "agent_confidence": 0.5
        }
        safeguards.update_state(context)
        assert safeguards._state == EmotionalState.CALM

        # Case 2: Anxious state (5% drawdown)
        context["portfolio_value"] = 95000.0  # 5% drawdown
        safeguards.update_state(context)
        # 5% drawdown triggers DRAWDOWN_5PCT safeguard -> MOUNA
        assert safeguards._state == EmotionalState.MOUNA

    def test_safeguard_triggers_cooling_off(self, safeguards):
        """Test that safeguards trigger cooling-off periods correctly."""
        safeguards._peak_portfolio_value = 100000.0
        safeguards._current_portfolio_value = 100000.0

        # Trigger 5% drawdown safeguard
        context = {
            "portfolio_value": 94000.0,  # 6% drawdown
            "peak_portfolio_value": 100000.0,
            "trade_result": None
        }

        # Capture the trigger event
        with patch.object(safeguards, '_trigger_safeguard', wraps=safeguards._trigger_safeguard) as mock_trigger:
            safeguards.update_state(context)
            mock_trigger.assert_called()
            found = False
            for call in mock_trigger.call_args_list:
                if call[0][0] == SafeguardTrigger.DRAWDOWN_5PCT:
                    found = True
                    break
            assert found, "DRAWDOWN_5PCT should have been triggered"

        # Check cooling off status
        status = safeguards.get_status()
        assert status["cooling_off_active"] is True
        assert status["emotional_state"] == EmotionalState.MOUNA.value
        assert safeguards._cooling_off_until is not None

        # Verify duration (approx 30 mins for 5% drawdown)
        remaining = safeguards._cooling_off_remaining()
        assert 29 * 60 < remaining <= 30 * 60

    def test_consecutive_losses_logic(self, safeguards):
        """Test consecutive losses tracking and rapid loss trigger."""
        safeguards._peak_portfolio_value = 100000.0
        safeguards._current_portfolio_value = 100000.0

        # Record 1st loss
        safeguards.update_state({"trade_result": "loss", "portfolio_value": 99900})
        assert safeguards._consecutive_losses == 1

        # Record 2nd loss
        safeguards.update_state({"trade_result": "loss", "portfolio_value": 99800})
        assert safeguards._consecutive_losses == 2

        # Record 3rd loss -> Should trigger RAPID_LOSSES
        context = {
            "portfolio_value": 99700.0,
            "peak_portfolio_value": 100000.0,
            "trade_result": "loss"
        }

        safeguards.update_state(context)
        assert safeguards._consecutive_losses == 3

        # Verify Mouna mode triggered by rapid losses
        assert safeguards._state == EmotionalState.MOUNA
        assert any(e.trigger == SafeguardTrigger.RAPID_LOSSES.value for e in safeguards._events)

    def test_revenge_trade_detection(self, safeguards):
        """Test detection of revenge trading behavior."""
        safeguards._current_portfolio_value = 100000.0

        # Normal loss
        safeguards.record_trade_outcome("loss", -1000.0, "AAPL") # 1% loss
        assert not any(e.trigger == SafeguardTrigger.REVENGE_TRADE.value for e in safeguards._events)

        # Huge loss (>5% of portfolio)
        safeguards.record_trade_outcome("loss", -6000.0, "TSLA") # 6% loss

        # Should have triggered revenge trade safeguard
        assert any(e.trigger == SafeguardTrigger.REVENGE_TRADE.value for e in safeguards._events)
        assert safeguards._state == EmotionalState.MOUNA

    def test_manual_override(self, safeguards):
        """Test manual override functionality."""
        status = safeguards.manual_override("Testing override")

        assert safeguards._state == EmotionalState.MOUNA
        assert status["cooling_off_active"] is True
        assert any(e.trigger == SafeguardTrigger.MANUAL_OVERRIDE.value for e in safeguards._events)

        # Verify duration (approx 6 hours)
        remaining = safeguards._cooling_off_remaining()
        assert 5 * 3600 < remaining <= 6 * 3600

    def test_cooling_off_expiration(self, safeguards):
        """Test that cooling off expires correctly."""
        # Manually set a short cooling off period
        safeguards._cooling_off_until = datetime.now() + timedelta(milliseconds=100)
        safeguards._state = EmotionalState.MOUNA

        # Wait for expiration
        time.sleep(0.2)

        # Run update_state to re-evaluate state
        context = {
            "portfolio_value": 100000.0,
            "peak_portfolio_value": 100000.0,
            "trade_result": None
        }
        safeguards.update_state(context)

        # Should be expired and state reset to CALM (assuming no other triggers)
        assert safeguards._cooling_off_remaining() == 0
        assert safeguards._state == EmotionalState.CALM
        assert safeguards.is_trading_allowed()["allowed"] is True

    def test_is_trading_allowed_logic(self, safeguards):
        """Test the specific logic in is_trading_allowed."""
        # 1. Normal state
        assert safeguards.is_trading_allowed()["allowed"] is True

        # 2. Cooling off active
        safeguards._cooling_off_until = datetime.now() + timedelta(minutes=10)
        status = safeguards.is_trading_allowed()
        assert status["allowed"] is False
        assert "COOLING_OFF" in status["reason"]

        # 3. Panicked state
        safeguards._cooling_off_until = None # Clear cooling off
        safeguards._state = EmotionalState.PANICKED
        status = safeguards.is_trading_allowed()
        assert status["allowed"] is False
        assert "PANIC_LOCK" in status["reason"]

        # 4. MOUNA state check
        safeguards._state = EmotionalState.MOUNA
        status = safeguards.is_trading_allowed()
        assert status["allowed"] is False
        assert "MOUNA_MODE" in status["reason"]

    def test_overconfidence_trigger(self, safeguards):
        """Test overconfidence safeguard."""
        safeguards._peak_portfolio_value = 100000.0
        safeguards._current_portfolio_value = 100000.0

        context = {
            "portfolio_value": 100000.0,
            "peak_portfolio_value": 100000.0,
            "trade_result": "win",
            "agent_confidence": 0.95 # High confidence
        }

        # Need 3 consecutive overconfidence signals
        # 1
        safeguards.update_state(context)
        assert safeguards._overconfidence_streak == 1
        assert safeguards._state != EmotionalState.MOUNA

        # 2
        safeguards.update_state(context)
        assert safeguards._overconfidence_streak == 2
        assert safeguards._state != EmotionalState.MOUNA

        # 3 -> Trigger
        safeguards.update_state(context)

        assert safeguards._state == EmotionalState.MOUNA
        assert any(e.trigger == SafeguardTrigger.OVERCONFIDENCE.value for e in safeguards._events)
