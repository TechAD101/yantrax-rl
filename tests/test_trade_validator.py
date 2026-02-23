import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Mock chromadb before any other imports
mock_chroma = MagicMock()
sys.modules['chromadb'] = mock_chroma
sys.modules['chromadb.config'] = MagicMock()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.trade_validator import TradeValidator

@pytest.fixture
def validator():
    # Mock Knowledge Base
    mock_kb = MagicMock()
    mock_kb.query_wisdom.return_value = [{'text': 'Stay data-driven.'}]

    with patch('services.trade_validator.get_knowledge_base', return_value=mock_kb):
        return TradeValidator()

def test_initialization(validator):
    assert validator.MACRO_ALIGNMENT_MIN == 50
    assert validator.LIQUIDITY_ALIGNMENT_MIN == 40
    assert validator.CONFIDENCE_BAND_MIN == 60
    assert validator.RISK_REWARD_MIN == 1.5
    assert validator.BLACK_SWAN_VIX_MAX == 40
    assert validator.POSITION_SIZE_MAX == 0.10
    assert validator.EXECUTION_RISK_MAX == 0.02

def test_check_macro_alignment(validator):
    # Case 1: Bullish + BUY = 75 (Pass)
    res = validator._check_macro_alignment({'action': 'BUY'}, {'market_trend': 'bullish'})
    assert res['passed'] is True
    assert res['score'] == 75

    # Case 2: Bearish + SELL = 75 (Pass)
    res = validator._check_macro_alignment({'action': 'SELL'}, {'market_trend': 'bearish'})
    assert res['passed'] is True
    assert res['score'] == 75

    # Case 3: Neutral = 55 (Pass)
    res = validator._check_macro_alignment({'action': 'BUY'}, {'market_trend': 'neutral'})
    assert res['passed'] is True
    assert res['score'] == 55

    # Case 4: Counter-trend = 35 (Fail)
    res = validator._check_macro_alignment({'action': 'SELL'}, {'market_trend': 'bullish'})
    assert res['passed'] is False
    assert res['score'] == 35

    # Case 5: Euphoric + BUY = 75 - 10 = 65 (Pass)
    res = validator._check_macro_alignment({'action': 'BUY'}, {'market_trend': 'bullish', 'market_mood': 'euphoric'})
    assert res['passed'] is True
    assert res['score'] == 65

    # Case 6: Panic + SELL = 75 - 10 = 65 (Pass)
    res = validator._check_macro_alignment({'action': 'SELL'}, {'market_trend': 'bearish', 'market_mood': 'panic'})
    assert res['passed'] is True
    assert res['score'] == 65

    # Case 7: Calm mood = score + 5
    res = validator._check_macro_alignment({'action': 'BUY'}, {'market_trend': 'neutral', 'market_mood': 'calm'})
    assert res['passed'] is True
    assert res['score'] == 60

def test_check_liquidity_alignment(validator):
    # Case 1: Volume > 1M = 80 (Pass)
    res = validator._check_liquidity_alignment({}, {'volume': 1500000})
    assert res['passed'] is True
    assert res['score'] == 80

    # Case 2: Volume > 100K = 60 (Pass)
    res = validator._check_liquidity_alignment({}, {'volume': 500000})
    assert res['passed'] is True
    assert res['score'] == 60

    # Case 3: Volume > 10K = 40 (Pass)
    res = validator._check_liquidity_alignment({}, {'volume': 50000})
    assert res['passed'] is True
    assert res['score'] == 40

    # Case 4: Volume <= 10K = 20 (Fail)
    res = validator._check_liquidity_alignment({}, {'volume': 5000})
    assert res['passed'] is False
    assert res['score'] == 20

    # Case 5: Penalty for wide spread (>2%)
    res = validator._check_liquidity_alignment({}, {'volume': 1500000, 'bid_ask_spread': 0.03})
    assert res['passed'] is True
    assert res['score'] == 60 # 80 - 20

def test_check_confidence_band(validator):
    # Case 1: Persona votes average 70% (Pass)
    context = {
        'persona_votes': [
            {'confidence': 0.8, 'weight': 1.0},
            {'confidence': 0.6, 'weight': 1.0}
        ]
    }
    res = validator._check_confidence_band({'symbol': 'AAPL'}, context)
    assert res['passed'] is True
    assert res['confidence'] == 70.0

    # Case 2: Persona votes average 50% (Fail)
    context = {
        'persona_votes': [
            {'confidence': 0.4, 'weight': 1.0},
            {'confidence': 0.6, 'weight': 1.0}
        ]
    }
    res = validator._check_confidence_band({'symbol': 'AAPL'}, context)
    assert res['passed'] is False
    assert res['confidence'] == 50.0

    # Case 3: Weighted average
    context = {
        'persona_votes': [
            {'confidence': 0.9, 'weight': 2.0},
            {'confidence': 0.3, 'weight': 1.0}
        ]
    }
    # (0.9*2 + 0.3*1) / 3 = (1.8 + 0.3) / 3 = 0.7 -> 70%
    res = validator._check_confidence_band({'symbol': 'AAPL'}, context)
    assert res['passed'] is True
    assert res['confidence'] == 70.0

    # Case 4: No votes -> default 50% (Fail)
    res = validator._check_confidence_band({'symbol': 'AAPL'}, {})
    assert res['passed'] is False
    assert res['confidence'] == 50.0

def test_check_risk_reward(validator):
    # Case 1: Entry 100, Target 120, Stop 90 -> RR 2.0 (Pass)
    res = validator._check_risk_reward({'entry_price': 100, 'target_price': 120, 'stop_loss': 90})
    assert res['passed'] is True
    assert res['rr_ratio'] == 2.0

    # Case 2: Entry 100, Target 110, Stop 90 -> RR 1.0 (Fail)
    res = validator._check_risk_reward({'entry_price': 100, 'target_price': 110, 'stop_loss': 90})
    assert res['passed'] is False
    assert res['rr_ratio'] == 1.0

    # Case 3: Missing fields -> Pass by default
    res = validator._check_risk_reward({'entry_price': 100})
    assert res['passed'] is True
    assert res['reason'] == 'No target/stop defined (pass by default)'

def test_check_no_reversals(validator):
    # Case 1: No history (Pass)
    res = validator._check_no_reversals({'symbol': 'AAPL', 'action': 'BUY'})
    assert res['passed'] is True

    # Case 2: One trade in history (Pass)
    validator.trade_history['AAPL'] = [{'action': 'BUY'}]
    res = validator._check_no_reversals({'symbol': 'AAPL', 'action': 'SELL'})
    assert res['passed'] is True

    # Case 3: Reversal in history, but current action follows last action (Pass)
    # History: BUY, SELL (1 reversal)
    # Current: SELL
    validator.trade_history['AAPL'] = [{'action': 'BUY'}, {'action': 'SELL'}]
    res = validator._check_no_reversals({'symbol': 'AAPL', 'action': 'SELL'})
    assert res['passed'] is True

    # Case 4: Reversal in history, current action is another reversal (Fail)
    # History: BUY, SELL (1 reversal)
    # Current: BUY
    validator.trade_history['AAPL'] = [{'action': 'BUY'}, {'action': 'SELL'}]
    res = validator._check_no_reversals({'symbol': 'AAPL', 'action': 'BUY'})
    assert res['passed'] is False
    assert 'Reversal detected' in res['reason']

def test_check_no_black_swan(validator):
    # Case 1: Normal conditions (Pass)
    res = validator._check_no_black_swan({'vix': 20, 'volatility': 0.3})
    assert res['passed'] is True

    # Case 2: VIX too high (Fail)
    res = validator._check_no_black_swan({'vix': 41, 'volatility': 0.3})
    assert res['passed'] is False
    assert 'VIX 41 > 40' in res['reason']

    # Case 3: Volatility too high (Fail)
    res = validator._check_no_black_swan({'vix': 20, 'volatility': 0.81})
    assert res['passed'] is False
    assert 'Extreme volatility 81.0%' in res['reason']

def test_check_position_size(validator):
    # Case 1: 5% of portfolio (Pass)
    res = validator._check_position_size({'shares': 100, 'entry_price': 50, 'portfolio_value': 100000})
    assert res['passed'] is True
    assert res['position_pct'] == 0.05

    # Case 2: 25% of portfolio (Fail)
    res = validator._check_position_size({'shares': 500, 'entry_price': 50, 'portfolio_value': 100000})
    assert res['passed'] is False
    assert res['position_pct'] == 0.25

def test_check_execution_risk(validator):
    # Case 1: Low risk (Pass)
    # 0.005 + (0.1 * 0.1) = 0.005 + 0.01 = 0.015 < 0.02
    res = validator._check_execution_risk({}, {'bid_ask_spread': 0.005, 'volatility': 0.1})
    assert res['passed'] is True
    assert res['execution_risk'] == 0.015

    # Case 2: High risk (Fail)
    # 0.015 + (0.2 * 0.1) = 0.015 + 0.02 = 0.035 >= 0.02
    res = validator._check_execution_risk({}, {'bid_ask_spread': 0.015, 'volatility': 0.2})
    assert res['passed'] is False
    assert res['execution_risk'] == 0.035

def test_validate_trade_approved(validator):
    # All checks pass
    proposal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'shares': 100,
        'entry_price': 150,
        'target_price': 180,
        'stop_loss': 140,
        'portfolio_value': 1000000
    }
    context = {
        'market_trend': 'bullish',
        'volume': 2000000,
        'vix': 20,
        'volatility': 0.1,
        'bid_ask_spread': 0.005,
        'persona_votes': [{'confidence': 0.8, 'weight': 1.0}]
    }
    res = validator.validate_trade(proposal, context)
    assert res['allowed'] is True
    assert res['checks_passed'] == 8
    assert len(res['failures']) == 0
    assert 'validation_id' in res

def test_validate_trade_blocked(validator):
    # One check fails (Risk-Reward)
    proposal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'shares': 100,
        'entry_price': 150,
        'target_price': 160, # RR = 10/10 = 1.0 < 1.5
        'stop_loss': 140,
        'portfolio_value': 1000000
    }
    context = {
        'market_trend': 'bullish',
        'volume': 2000000,
        'vix': 20,
        'volatility': 0.1,
        'bid_ask_spread': 0.005,
        'persona_votes': [{'confidence': 0.8, 'weight': 1.0}]
    }
    res = validator.validate_trade(proposal, context)
    assert res['allowed'] is False
    assert res['checks_passed'] == 7
    assert 'risk_reward' in res['failures']

def test_history_management(validator):
    proposal = {'symbol': 'TSLA', 'action': 'BUY'}
    result = {'allowed': True, 'checks_passed': 8, 'failures': [], 'timestamp': 'now'}

    # Test _log_validation
    val_id = validator._log_validation(proposal, result)
    assert val_id.startswith('val_')
    assert len(validator.validation_history) == 1

    # Test _record_trade
    validator._record_trade(proposal)
    assert len(validator.trade_history['TSLA']) == 1
    assert validator.trade_history['TSLA'][0]['action'] == 'BUY'

    # Test get_validation_history
    history = validator.get_validation_history()
    assert len(history) == 1
    assert history[0]['validation_id'] == val_id

    # Test get_validation_stats
    stats = validator.get_validation_stats()
    assert stats['total_validations'] == 1
    assert stats['approved'] == 1
    assert stats['approval_rate'] == 1.0
