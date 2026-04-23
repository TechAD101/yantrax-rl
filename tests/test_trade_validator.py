import sys
import os
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock external dependencies only in restricted environments
try:
    import sqlalchemy
except ImportError:
    for mod in ["sqlalchemy", "sqlalchemy.orm", "sqlalchemy.ext.declarative", "flask", "numpy",
                "alpaca", "alpaca.data", "alpaca.data.historical", "alpaca.data.requests",
                "alpaca.data.timeframe", "chromadb", "chromadb.config", "redis", "pydantic",
                "google", "google.generativeai", "openai", "anthropic"]:
        m = MagicMock()
        m.__path__ = []
        sys.modules[mod] = m

from services.trade_validator import TradeValidator, get_trade_validator

@pytest.fixture
def validator():
    return TradeValidator()

def test_trade_validator_init(validator):
    assert validator.MACRO_ALIGNMENT_MIN == 50
    assert validator.LIQUIDITY_ALIGNMENT_MIN == 40
    assert validator.CONFIDENCE_BAND_MIN == 60
    assert validator.RISK_REWARD_MIN == 1.5
    assert validator.BLACK_SWAN_VIX_MAX == 40
    assert validator.POSITION_SIZE_MAX == 0.10
    assert validator.EXECUTION_RISK_MAX == 0.02

def test_check_macro_alignment_bullish_buy(validator):
    proposal = {'action': 'BUY'}
    context = {'market_trend': 'bullish', 'market_mood': 'calm'}

    result = validator._check_macro_alignment(proposal, context)

    assert result['passed'] is True
    assert result['score'] == 80  # 75 + 5 for calm
    assert result['name'] == 'macro_alignment'

def test_check_macro_alignment_counter_trend(validator):
    proposal = {'action': 'BUY'}
    context = {'market_trend': 'bearish', 'market_mood': 'panic'}

    result = validator._check_macro_alignment(proposal, context)

    assert result['passed'] is False
    assert result['score'] == 35  # Counter trend is 35, panic doesn't adjust action=BUY
    assert 'Macro score' in result['reason']

def test_check_liquidity_alignment_high_volume(validator):
    proposal = {}
    context = {'volume': 1500000, 'bid_ask_spread': 0.01}

    result = validator._check_liquidity_alignment(proposal, context)

    assert result['passed'] is True
    assert result['score'] == 80

def test_check_liquidity_alignment_wide_spread(validator):
    proposal = {}
    context = {'volume': 1500000, 'bid_ask_spread': 0.05}

    result = validator._check_liquidity_alignment(proposal, context)

    assert result['passed'] is True  # 80 - 20 = 60 >= 40
    assert result['score'] == 60

def test_check_liquidity_alignment_low_volume_wide_spread(validator):
    proposal = {}
    context = {'volume': 5000, 'bid_ask_spread': 0.05}

    result = validator._check_liquidity_alignment(proposal, context)

    assert result['passed'] is False  # 20 - 20 = 0 < 40
    assert result['score'] == 0

@patch('services.trade_validator.get_knowledge_base')
def test_check_confidence_band_pass(mock_get_kb, validator):
    mock_kb = MagicMock()
    mock_kb.query_wisdom.return_value = [{'text': 'Buy low sell high'}]
    mock_get_kb.return_value = mock_kb

    proposal = {'symbol': 'AAPL'}
    context = {
        'persona_votes': [
            {'weight': 1.0, 'confidence': 0.8},
            {'weight': 2.0, 'confidence': 0.7}
        ]
    }

    result = validator._check_confidence_band(proposal, context)

    assert result['passed'] is True
    # Weighted avg: (0.8*1 + 0.7*2) / 3 * 100 = 2.2 / 3 * 100 = 73.33...
    assert round(result['confidence']) == 73

@patch('services.trade_validator.get_knowledge_base')
def test_check_confidence_band_fail(mock_get_kb, validator):
    mock_kb = MagicMock()
    mock_kb.query_wisdom.return_value = [{'text': 'Market is risky'}]
    mock_get_kb.return_value = mock_kb

    proposal = {'symbol': 'AAPL'}
    context = {
        'persona_votes': [
            {'weight': 1.0, 'confidence': 0.4},
            {'weight': 1.0, 'confidence': 0.5}
        ]
    }

    result = validator._check_confidence_band(proposal, context)

    assert result['passed'] is False
    assert result['confidence'] == 45.0  # (0.4+0.5)/2 * 100

def test_check_risk_reward_pass(validator):
    proposal = {
        'entry_price': 100,
        'target_price': 130,  # +30
        'stop_loss': 90       # -10
    }
    # RR = 30 / 10 = 3.0 >= 1.5

    result = validator._check_risk_reward(proposal)
    assert result['passed'] is True
    assert result['rr_ratio'] == 3.0

def test_check_risk_reward_fail(validator):
    proposal = {
        'entry_price': 100,
        'target_price': 110,  # +10
        'stop_loss': 90       # -10
    }
    # RR = 10 / 10 = 1.0 < 1.5

    result = validator._check_risk_reward(proposal)
    assert result['passed'] is False
    assert result['rr_ratio'] == 1.0

def test_check_risk_reward_missing_fields(validator):
    proposal = {
        'entry_price': 100
    }

    result = validator._check_risk_reward(proposal)
    assert result['passed'] is True  # Passes by default when missing fields

def test_check_no_reversals_pass(validator):
    validator.trade_history = {
        'AAPL': [
            {'action': 'BUY'},
            {'action': 'BUY'}
        ]
    }
    proposal = {'symbol': 'AAPL', 'action': 'BUY'}

    result = validator._check_no_reversals(proposal)
    assert result['passed'] is True

def test_check_no_reversals_fail(validator):
    validator.trade_history = {
        'AAPL': [
            {'action': 'BUY'},
            {'action': 'SELL'},
            {'action': 'BUY'}
        ]
    }
    # Reversals detected, trying to reverse again
    proposal = {'symbol': 'AAPL', 'action': 'SELL'}

    result = validator._check_no_reversals(proposal)
    assert result['passed'] is False
    assert result['reversals'] > 0

def test_check_no_black_swan_pass(validator):
    context = {'vix': 20, 'volatility': 0.5}
    result = validator._check_no_black_swan(context)
    assert result['passed'] is True

def test_check_no_black_swan_vix_fail(validator):
    context = {'vix': 50, 'volatility': 0.5}  # > 40
    result = validator._check_no_black_swan(context)
    assert result['passed'] is False

def test_check_no_black_swan_volatility_fail(validator):
    context = {'vix': 20, 'volatility': 0.9}  # > 0.8
    result = validator._check_no_black_swan(context)
    assert result['passed'] is False

def test_check_position_size_pass(validator):
    proposal = {
        'shares': 50,
        'entry_price': 100,  # 5000 value
        'portfolio_value': 100000
    }
    # 5% <= 10%
    result = validator._check_position_size(proposal)
    assert result['passed'] is True

def test_check_position_size_fail(validator):
    proposal = {
        'shares': 150,
        'entry_price': 100,  # 15000 value
        'portfolio_value': 100000
    }
    # 15% > 10%
    result = validator._check_position_size(proposal)
    assert result['passed'] is False

def test_check_execution_risk_pass(validator):
    proposal = {}
    context = {
        'bid_ask_spread': 0.001,
        'volatility': 0.1
    }
    # Risk = 0.001 + 0.01 = 0.011 < 0.02
    result = validator._check_execution_risk(proposal, context)
    assert result['passed'] is True

def test_check_execution_risk_fail(validator):
    proposal = {}
    context = {
        'bid_ask_spread': 0.01,
        'volatility': 0.2
    }
    # Risk = 0.01 + 0.02 = 0.03 > 0.02
    result = validator._check_execution_risk(proposal, context)
    assert result['passed'] is False

@patch('services.trade_validator.get_knowledge_base')
def test_validate_trade_all_pass(mock_get_kb, validator):
    mock_kb = MagicMock()
    mock_kb.query_wisdom.return_value = [{'text': 'Good trade'}]
    mock_get_kb.return_value = mock_kb

    proposal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'shares': 50,
        'entry_price': 100,
        'target_price': 130,
        'stop_loss': 90,
        'portfolio_value': 100000
    }
    context = {
        'market_trend': 'bullish',
        'market_mood': 'calm',
        'volume': 1500000,
        'bid_ask_spread': 0.001,
        'persona_votes': [{'weight': 1.0, 'confidence': 0.8}],
        'vix': 20,
        'volatility': 0.1
    }

    # We should also mock _log_validation to prevent test noise, but we actually want to test it
    result = validator.validate_trade(proposal, context)

    assert result['allowed'] is True
    assert result['checks_passed'] == 8
    assert len(result['failures']) == 0
    assert result['validation_id'] is not None

    # Check that it was added to history
    history = validator.get_validation_history()
    assert len(history) == 1
    assert history[0]['allowed'] is True

    # Check that trade was recorded
    assert 'AAPL' in validator.trade_history
    assert validator.trade_history['AAPL'][0]['action'] == 'BUY'

@patch('services.trade_validator.get_knowledge_base')
def test_validate_trade_one_fail_blocks_all(mock_get_kb, validator):
    mock_kb = MagicMock()
    mock_kb.query_wisdom.return_value = [{'text': 'Bad trade'}]
    mock_get_kb.return_value = mock_kb

    proposal = {
        'symbol': 'AAPL',
        'action': 'BUY',
        'shares': 50,
        'entry_price': 100,
        'target_price': 130,
        'stop_loss': 90,
        'portfolio_value': 100000
    }
    context = {
        'market_trend': 'bullish',
        'market_mood': 'calm',
        'volume': 1500000,
        'bid_ask_spread': 0.001,
        'persona_votes': [{'weight': 1.0, 'confidence': 0.8}],
        'vix': 50,  # This will fail the black swan check
        'volatility': 0.1
    }

    result = validator.validate_trade(proposal, context)

    assert result['allowed'] is False
    assert result['checks_passed'] == 7
    assert len(result['failures']) == 1
    assert 'no_black_swan' in result['failures']

def test_get_trade_validator_singleton():
    v1 = get_trade_validator()
    v2 = get_trade_validator()
    assert v1 is v2

def test_validation_history_limit(validator):
    """Test that history respects the 100 item limit"""
    proposal = {'symbol': 'TEST'}
    # Force 105 validations
    for i in range(105):
        validator._log_validation(proposal, {
            'allowed': True,
            'checks_passed': 8,
            'failures': [],
            'timestamp': '2023-01-01'
        })

    assert len(validator.validation_history) == 100

def test_get_validation_stats(validator):
    proposal = {'symbol': 'TEST'}
    # Add 3 approved, 1 blocked
    for _ in range(3):
        validator._log_validation(proposal, {
            'allowed': True, 'checks_passed': 8, 'failures': [], 'timestamp': '2023-01-01'
        })
    validator._log_validation(proposal, {
        'allowed': False, 'checks_passed': 7, 'failures': ['risk'], 'timestamp': '2023-01-01'
    })

    stats = validator.get_validation_stats()
    assert stats['total_validations'] == 4
    assert stats['approved'] == 3
    assert stats['blocked'] == 1
    assert stats['approval_rate'] == 0.75

def test_empty_validation_stats(validator):
    stats = validator.get_validation_stats()
    assert stats['total_validations'] == 0
    assert stats['approved'] == 0
    assert stats['blocked'] == 0
    assert stats['approval_rate'] == 0.0

def test_trade_history_limit(validator):
    """Test that trade history keeps only last 5 per symbol"""
    proposal = {'symbol': 'TEST', 'action': 'BUY'}
    # Record 7 trades
    for _ in range(7):
        validator._record_trade(proposal)

    assert len(validator.trade_history['TEST']) == 5

def test_record_trade_no_symbol(validator):
    """Test that empty symbol doesn't cause errors"""
    proposal = {'action': 'BUY'}
    validator._record_trade(proposal)
    assert len(validator.trade_history) == 0
