import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.market_sentiment_service import MarketSentimentService, get_sentiment_service

def test_get_sentiment_service_singleton():
    service1 = get_sentiment_service()
    service2 = get_sentiment_service()
    assert service1 is service2
    assert isinstance(service1, MarketSentimentService)

def test_calculate_fear_greed_index_success():
    service = MarketSentimentService()

    with patch.object(service, '_calculate_market_momentum', return_value=0.5), \
         patch.object(service, '_calculate_market_breadth', return_value=0.5), \
         patch.object(service, '_calculate_put_call_ratio', return_value=0.5), \
         patch.object(service, '_calculate_volatility_sentiment', return_value=0.5), \
         patch.object(service, '_calculate_safe_haven_demand', return_value=0.5), \
         patch.object(service, '_calculate_junk_bond_demand', return_value=0.5):

        result = service.calculate_fear_greed_index("AAPL")

        assert result['symbol'] == "AAPL"
        assert result['fear_greed_index'] == 0.5
        assert result['sentiment'] == "NEUTRAL"
        assert result['recommendation'] == "HOLD"
        assert 'timestamp' in result

def test_calculate_fear_greed_index_extreme_fear():
    service = MarketSentimentService()

    with patch.object(service, '_calculate_market_momentum', return_value=0.1), \
         patch.object(service, '_calculate_market_breadth', return_value=0.1), \
         patch.object(service, '_calculate_put_call_ratio', return_value=0.1), \
         patch.object(service, '_calculate_volatility_sentiment', return_value=0.1), \
         patch.object(service, '_calculate_safe_haven_demand', return_value=0.1), \
         patch.object(service, '_calculate_junk_bond_demand', return_value=0.1):

        result = service.calculate_fear_greed_index("AAPL")

        assert result['fear_greed_index'] == 0.1
        assert result['sentiment'] == "EXTREME_FEAR"
        assert result['recommendation'] == "STRONG_BUY"

def test_calculate_fear_greed_index_exception():
    service = MarketSentimentService()

    with patch.object(service, '_calculate_market_momentum', side_effect=Exception("Test Error")):
        result = service.calculate_fear_greed_index("AAPL")

        assert result['fear_greed_index'] == 0.5
        assert result['sentiment'] == "NEUTRAL"
        assert result['recommendation'] == "HOLD"

@patch('numpy.mean')
def test_analyze_options_flow_bullish(mock_mean):
    service = MarketSentimentService()
    mock_mean.return_value = 0.8

    with patch('numpy.random.uniform', return_value=0.8):
        result = service.analyze_options_flow("TSLA")

        assert result['symbol'] == "TSLA"
        assert result['flow_score'] == 0.8
        assert result['signal'] == "BULLISH_INSTITUTIONAL_FLOW"

@patch('numpy.mean')
def test_analyze_options_flow_bearish(mock_mean):
    service = MarketSentimentService()
    mock_mean.return_value = 0.2

    with patch('numpy.random.uniform', return_value=0.2):
        result = service.analyze_options_flow("TSLA")

        assert result['flow_score'] == 0.2
        assert result['signal'] == "BEARISH_INSTITUTIONAL_FLOW"

def test_analyze_options_flow_exception():
    service = MarketSentimentService()

    with patch('numpy.random.uniform', side_effect=Exception("Flow error")):
        result = service.analyze_options_flow("TSLA")

        assert result['symbol'] == "TSLA"
        assert result['flow_score'] == 0.5
        assert result['signal'] == "NEUTRAL_FLOW"

def test_get_social_sentiment():
    service = MarketSentimentService()

    # Mock to ensure fixed calculation
    with patch('numpy.random.uniform', return_value=0.8), \
         patch('numpy.random.randint', return_value=100):

        result = service.get_social_sentiment("BTC")

        assert result['symbol'] == "BTC"
        assert result['overall_sentiment'] == 0.9
        assert result['signal'] == "STRONGLY_BULLISH"

def test_get_social_sentiment_exception():
    service = MarketSentimentService()

    with patch('numpy.random.uniform', side_effect=Exception("Social error")):
        result = service.get_social_sentiment("BTC")

        assert result['symbol'] == "BTC"
        assert result['overall_sentiment'] == 0.5
        assert result['signal'] == "NEUTRAL"

def test_get_comprehensive_sentiment():
    service = MarketSentimentService()

    mock_fear_greed = {'fear_greed_index': 0.8, 'sentiment': 'GREED'}
    mock_options = {'flow_score': 0.8, 'signal': 'BULLISH'}
    mock_social = {'overall_sentiment': 0.8, 'signal': 'BULLISH'}

    with patch.object(service, 'calculate_fear_greed_index', return_value=mock_fear_greed), \
         patch('numpy.mean', return_value=0.8), \
         patch.object(service, 'analyze_options_flow', return_value=mock_options), \
         patch.object(service, 'get_social_sentiment', return_value=mock_social):

        result = service.get_comprehensive_sentiment("ETH")

        assert result['symbol'] == "ETH"
        assert result['composite_sentiment'] == 0.8
        assert result['recommendation'] == "STRONG_BUY"
        assert result['confidence'] == 0.85
        assert result['analysis_level'] == "INSTITUTIONAL_GRADE"

def test_get_comprehensive_sentiment_exception():
    service = MarketSentimentService()

    with patch.object(service, 'calculate_fear_greed_index', side_effect=Exception("Comprehensive error")):
        result = service.get_comprehensive_sentiment("ETH")

        assert result['symbol'] == "ETH"
        assert result['composite_sentiment'] == 0.5
        assert result['recommendation'] == "HOLD"
        assert result['confidence'] == 0.5
        assert 'error' in result
