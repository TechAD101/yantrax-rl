import sys
import time
import unittest.mock
from unittest.mock import MagicMock
import logging
import os

# Configure logging
logging.basicConfig(level=logging.ERROR)

# Add backend to path
sys.path.append(os.path.abspath('backend'))

# Mock pandas
mock_pd = MagicMock()
sys.modules['pandas'] = mock_pd

# Mock yfinance
mock_yfinance = MagicMock()
sys.modules['yfinance'] = mock_yfinance

from services.market_data_service_waterfall import WaterfallMarketDataService

def benchmark():
    service = WaterfallMarketDataService()
    symbols = [f"SYM{i}" for i in range(10)]

    # 1. Benchmark Sequential (get_price)
    mock_ticker = MagicMock()
    class MockFastInfo:
        @property
        def last_price(self):
            time.sleep(0.1) # Simulate 100ms latency
            return 150.0
    mock_ticker.fast_info = MockFastInfo()
    mock_yfinance.Ticker.return_value = mock_ticker

    print(f"Benchmarking get_price for {len(symbols)} symbols sequentially...")
    start_time = time.time()
    for symbol in symbols:
        service.get_price(symbol)
    end_time = time.time()
    duration = end_time - start_time
    print(f"Sequential Duration: {duration:.4f} seconds")

    # 2. Benchmark Bulk (get_prices)
    def side_effect_download(tickers, period, interval, progress, group_by):
        time.sleep(0.1) # Simulate 100ms total latency for bulk

        # Create a mock DataFrame structure
        mock_data = MagicMock()
        mock_data.__contains__.side_effect = lambda key: key in tickers

        def get_symbol_data(symbol):
            mock_symbol_df = MagicMock()
            mock_symbol_df.empty = False
            mock_symbol_df.columns = ['Close']
            mock_series = MagicMock()
            mock_series.iloc.__getitem__.return_value = 150.0
            mock_symbol_df.__getitem__.return_value = mock_series
            return mock_symbol_df

        mock_data.__getitem__.side_effect = get_symbol_data
        return mock_data

    mock_yfinance.download.side_effect = side_effect_download

    service.cache['price'] = {}

    print(f"\nBenchmarking get_prices for {len(symbols)} symbols in bulk...")
    start_time = time.time()
    results_bulk = service.get_prices(symbols)

    # Verify correctness
    assert len(results_bulk) == len(symbols), f"Expected {len(symbols)} results, got {len(results_bulk)}"
    for symbol in symbols:
        assert symbol in results_bulk, f"Missing symbol {symbol}"
        # Accessing nested dict
        # _success returns {'symbol': symbol, 'price': price, 'source': source, ...}
        assert results_bulk[symbol]['price'] == 150.0, f"Incorrect price for {symbol}: {results_bulk[symbol]['price']}"
        assert results_bulk[symbol]['symbol'] == symbol, f"Incorrect symbol: {results_bulk[symbol]['symbol']}"

    end_time = time.time()
    duration_bulk = end_time - start_time
    print(f"Bulk Duration: {duration_bulk:.4f} seconds")

    if duration_bulk > 0:
        print(f"Speedup: {duration / duration_bulk:.2f}x")

    print("\n✅ Verification Passed!")

if __name__ == "__main__":
    benchmark()
