import sys
import os
import pytest

# Add backend directory to sys.path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.backtesting_engine import _sma_crossover_signals, _rsi_signals, _momentum_signals

class TestBacktestingSignals:
    """Tests for signal generation logic in backtesting engine."""
    pass

class TestSMACrossoverSignals:
    """Tests for _sma_crossover_signals."""

    def test_golden_cross(self):
        """Test BUY signal when fast MA crosses above slow MA."""
        # Setup: Fast MA (3-day) crosses Slow MA (5-day)
        # Day 0-4: Fast < Slow (Bearish)
        # Day 5: Fast > Slow (Bullish - Golden Cross)
        prices = [10, 9, 8, 7, 6, 15, 16, 17]
        # Calculation:
        # slow=5, fast=3
        # i=5 (index 5, value 15):
        # Fast MA (indices 3,4,5 -> 7,6,15): avg=9.33
        # Slow MA (indices 1,2,3,4,5 -> 9,8,7,6,15): avg=9.0
        # Prev Fast (indices 2,3,4 -> 8,7,6): avg=7.0
        # Prev Slow (indices 0,1,2,3,4 -> 10,9,8,7,6): avg=8.0
        # Condition: PrevFast <= PrevSlow (7<=8) AND Fast > Slow (9.33>9) -> BUY

        signals = _sma_crossover_signals(prices, fast=3, slow=5)
        assert signals[5] == "BUY"
        assert signals[4] == "HOLD"  # Before crossover

    def test_death_cross(self):
        """Test SELL signal when fast MA crosses below slow MA."""
        # Setup: Fast MA (3-day) crosses Slow MA (5-day)
        # Day 0-4: Fast > Slow (Bullish)
        # Day 5: Fast < Slow (Bearish - Death Cross)
        prices = [10, 11, 12, 13, 14, 5, 4, 3]
        # Calculation:
        # slow=5, fast=3
        # i=5 (index 5, value 5):
        # Fast MA (indices 3,4,5 -> 13,14,5): avg=10.66
        # Slow MA (indices 1,2,3,4,5 -> 11,12,13,14,5): avg=11.0
        # Prev Fast (indices 2,3,4 -> 12,13,14): avg=13.0
        # Prev Slow (indices 0,1,2,3,4 -> 10,11,12,13,14): avg=12.0
        # Condition: PrevFast >= PrevSlow (13>=12) AND Fast < Slow (10.66<11) -> SELL

        signals = _sma_crossover_signals(prices, fast=3, slow=5)
        assert signals[5] == "SELL"
        assert signals[4] == "HOLD"

    def test_no_signal_hold(self):
        """Test HOLD when no crossover occurs."""
        prices = [10, 10, 10, 10, 10, 10, 10]
        signals = _sma_crossover_signals(prices, fast=3, slow=5)
        assert all(s == "HOLD" for s in signals)

    def test_insufficient_data(self):
        """Test behavior with insufficient data points."""
        prices = [10, 11, 12]
        # slow=5, len=3. Loop range(5, 3) is empty.
        signals = _sma_crossover_signals(prices, fast=3, slow=5)
        assert signals == ["HOLD"] * 3
        assert len(signals) == 3

    def test_exact_crossover_boundary(self):
        """Test exact boundary conditions where MAs are equal."""
        # Case 1: Prev Fast == Prev Slow, Fast > Slow -> BUY
        # Case 2: Prev Fast == Prev Slow, Fast < Slow -> SELL
        # This is tricky to construct exactly with floats, but let's try simple integers
        # Fast=2, Slow=4
        # Day 0-3:
        # i=3:
        # Prev Fast (1,2):
        # Prev Slow (0,1,2):
        pass

class TestRSISignals:
    """Tests for _rsi_signals."""

    def test_overbought_sell(self):
        """Test SELL signal when RSI > 70."""
        # Setup: Construct a price series with strong gains to push RSI high
        prices = [10.0] * 15
        for i in range(15):
            prices.append(10.0 + i)  # Constant growth
        # RSI Period=14. i=29.
        # Gains: 14 ones. Losses: 0.
        # Avg Gain = 1, Avg Loss = ~0
        # RS -> large
        # RSI -> ~100 > 70 -> SELL

        signals = _rsi_signals(prices, period=14, oversold=30, overbought=70)
        assert signals[-1] == "SELL"

    def test_oversold_buy(self):
        """Test BUY signal when RSI < 30."""
        # Setup: Construct a price series with strong losses to push RSI low
        prices = [100.0] * 15
        for i in range(15):
            prices.append(100.0 - i)  # Constant decline
        # RSI Period=14. i=29.
        # Gains: 0. Losses: 14 ones.
        # Avg Gain = 0, Avg Loss = 1
        # RS = 0
        # RSI = 0 < 30 -> BUY

        signals = _rsi_signals(prices, period=14, oversold=30, overbought=70)
        assert signals[-1] == "BUY"

    def test_neutral_hold(self):
        """Test HOLD when RSI is between oversold and overbought."""
        # Setup: Oscillating prices to keep RSI around 50
        prices = [10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 11]
        # Period 14.
        # Gains: 7 ones. Losses: 7 ones.
        # Avg Gain = 0.5, Avg Loss = 0.5
        # RS = 1
        # RSI = 50 -> HOLD

        signals = _rsi_signals(prices, period=14, oversold=30, overbought=70)
        assert signals[-1] == "HOLD"

    def test_insufficient_data(self):
        """Test with insufficient data points."""
        prices = [10, 11, 12]
        signals = _rsi_signals(prices, period=14)
        assert signals == ["HOLD"] * 3
        assert len(signals) == 3

class TestMomentumSignals:
    """Tests for _momentum_signals."""

    def test_positive_momentum_buy(self):
        """Test BUY signal when price increases > 5%."""
        # Setup:
        # Price at i-lookback (i-20) = 100
        # Price at i = 106 (> 100 * 1.05) -> BUY
        prices = [100.0] * 20
        prices.append(106.0)
        # Lookback=20. i=20.
        # pct_change = (106 - 100) / 100 = 0.06 > 0.05 -> BUY

        signals = _momentum_signals(prices, lookback=20)
        assert signals[-1] == "BUY"

    def test_negative_momentum_sell(self):
        """Test SELL signal when price decreases < -5%."""
        # Setup:
        # Price at i-lookback (i-20) = 100
        # Price at i = 94 (< 100 * 0.95) -> SELL
        prices = [100.0] * 20
        prices.append(94.0)
        # Lookback=20. i=20.
        # pct_change = (94 - 100) / 100 = -0.06 < -0.05 -> SELL

        signals = _momentum_signals(prices, lookback=20)
        assert signals[-1] == "SELL"

    def test_neutral_hold(self):
        """Test HOLD when momentum is weak."""
        # Setup:
        # Price at i-lookback (i-20) = 100
        # Price at i = 104 (within 5%) -> HOLD
        prices = [100.0] * 20
        prices.append(104.0)

        signals = _momentum_signals(prices, lookback=20)
        assert signals[-1] == "HOLD"

        # Price at i = 96 (within 5%) -> HOLD
        prices[-1] = 96.0
        signals = _momentum_signals(prices, lookback=20)
        assert signals[-1] == "HOLD"

    def test_insufficient_data(self):
        """Test with insufficient data points."""
        prices = [100.0] * 19
        signals = _momentum_signals(prices, lookback=20)
        assert signals == ["HOLD"] * 19
        assert len(signals) == 19
