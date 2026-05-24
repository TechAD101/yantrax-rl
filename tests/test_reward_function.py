import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from rl_core.reward_function import calculate_reward

@pytest.mark.parametrize("position, expected_reward", [
    ("long", 0.1),
    ("short", -0.1),
    ("none", -0.1),
])
def test_calculate_reward_hold(position, expected_reward):
    state = {"price": 100, "mood": "neutral", "position": position}
    assert calculate_reward("hold", state) == expected_reward

@pytest.mark.parametrize("mood, expected_reward", [
    ("bullish", 1.0),
    ("panic", 2.0),
    ("euphoric", -0.7),  # -0.2 - 0.5
    ("bearish", -0.2),
    ("neutral", -0.2),
])
def test_calculate_reward_buy(mood, expected_reward):
    state = {"price": 100, "mood": mood, "position": "none"}
    assert calculate_reward("buy", state) == expected_reward

@pytest.mark.parametrize("mood, expected_reward", [
    ("bearish", 1.0),
    ("euphoric", 2.0),
    ("panic", -0.7),  # -0.2 - 0.5
    ("bullish", -0.2),
    ("neutral", -0.2),
])
def test_calculate_reward_sell(mood, expected_reward):
    state = {"price": 100, "mood": mood, "position": "long"}
    assert calculate_reward("sell", state) == expected_reward

def test_calculate_reward_curiosity_bonus():
    # Base buy bullish reward is 1.0
    # With curiosity > 3, it should be 1.2
    state_no_bonus = {"price": 100, "mood": "bullish", "position": "none", "curiosity": 3}
    state_with_bonus = {"price": 100, "mood": "bullish", "position": "none", "curiosity": 3.1}

    assert calculate_reward("buy", state_no_bonus) == 1.0
    assert calculate_reward("buy", state_with_bonus) == 1.2

def test_calculate_reward_rounding():
    # Force a situation that might need rounding if not handled
    # (though current logic uses fixed increments, it's good to test)
    # If we had reward = 0.1 + 0.2 = 0.30000000000000004 without rounding
    state = {"price": 100, "mood": "neutral", "position": "long", "curiosity": 3.1}
    # hold (0.1) + curiosity (0.2) = 0.3
    assert calculate_reward("hold", state) == 0.3

def test_calculate_reward_default_curiosity():
    state = {"price": 100, "mood": "bullish", "position": "none"}
    # curiosity defaults to 0, no bonus
    assert calculate_reward("buy", state) == 1.0
