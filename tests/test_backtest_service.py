import sys
import os
import datetime
from unittest.mock import MagicMock, patch

# Mock dependencies before importing backtest_service
import sys
sys.modules['db'] = MagicMock()
sys.modules['models'] = MagicMock()
sys.modules['services.knowledge_base_service'] = MagicMock()
sys.modules['services'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backtest_service import generate_price_history
from hypothesis import given, strategies as st

@given(
    symbol=st.text(min_size=1, max_size=10),
    days=st.integers(min_value=1, max_value=365)
)
def test_generate_price_history_properties(symbol, days):
    prices = generate_price_history(symbol, days)

    assert len(prices) == days

    # Dates should be strictly increasing
    previous_date = None
    for p in prices:
        assert 'date' in p
        assert 'open' in p
        assert 'close' in p
        assert 'high' in p
        assert 'low' in p
        assert 'volume' in p

        # Test financial price rules
        assert p['low'] <= p['open']
        assert p['low'] <= p['close']
        assert p['low'] <= p['high']
        assert p['high'] >= p['open']
        assert p['high'] >= p['close']

        # Volume should be positive
        assert p['volume'] > 0

        # Prices should be positive
        assert p['open'] > 0
        assert p['close'] > 0
        assert p['high'] > 0
        assert p['low'] > 0

        # Verify chronological order
        current_date = datetime.datetime.fromisoformat(p['date'])
        if previous_date is not None:
            assert current_date > previous_date

        previous_date = current_date

def test_generate_price_history_default_days():
    prices = generate_price_history("AAPL")
    assert len(prices) == 30
