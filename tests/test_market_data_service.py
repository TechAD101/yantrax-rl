import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Mock alpaca before importing the service to avoid ModuleNotFoundError
mock_alpaca = MagicMock()
sys.modules["alpaca"] = mock_alpaca
sys.modules["alpaca.data"] = MagicMock()
sys.modules["alpaca.data.historical"] = MagicMock()
sys.modules["alpaca.data.requests"] = MagicMock()
sys.modules["alpaca.data.timeframe"] = MagicMock()

import pytest
from services.market_data_service import get_market_data

def test_get_market_data_success():
    """Test get_market_data returns structured data when price is available"""
    symbol = "AAPL"
    mock_price = 175.50
    with patch("services.market_data_service.get_latest_price", return_value=mock_price) as mock_get_price:
        result = get_market_data(symbol)

        mock_get_price.assert_called_once_with(symbol)
        assert result is not None
        assert result["symbol"] == symbol
        assert result["market_data"]["price"] == mock_price
        assert result["market_data"]["sentiment"] == "neutral"
        assert result["market_data"]["volatility"] == 0.02

def test_get_market_data_failure():
    """Test get_market_data returns None when price is not available"""
    symbol = "UNKNOWN"
    with patch("services.market_data_service.get_latest_price", return_value=None) as mock_get_price:
        result = get_market_data(symbol)

        mock_get_price.assert_called_once_with(symbol)
        assert result is None

def test_get_market_data_default_symbol():
    """Test get_market_data works with default symbol"""
    mock_price = 180.0
    with patch("services.market_data_service.get_latest_price", return_value=mock_price) as mock_get_price:
        result = get_market_data()

        mock_get_price.assert_called_once_with("AAPL")
        assert result["symbol"] == "AAPL"
        assert result["market_data"]["price"] == mock_price
