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


def test_calculate_fear_greed_index_returns_real_data_or_provenance():
    """Fear & Greed index now uses real yfinance data where available."""
    service = MarketSentimentService()
    result = service.calculate_fear_greed_index("AAPL")

    assert result['symbol'] == "AAPL"
    # Score should be 0-1
    assert 0.0 <= result['fear_greed_index'] <= 1.0
    assert result['sentiment'] in ["EXTREME_FEAR", "FEAR", "NEUTRAL", "GREED", "EXTREME_GREED"]
    assert result['recommendation'] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    assert 'timestamp' in result
    # Provenance should indicate data source
    assert 'provenance' in result


def test_calculate_fear_greed_index_falls_back_on_exception():
    """When all data sources fail, should fall back to neutral with provenance."""
    service = MarketSentimentService()

    # Mock yfinance to raise
    with patch('services.market_sentiment_service._HAS_YFINANCE', False):
        result = service.calculate_fear_greed_index("AAPL")
        assert result['fear_greed_index'] == 0.5
        assert result['sentiment'] == "NEUTRAL"
        assert result['provenance'] == 'real_data_where_available'


def test_analyze_options_flow_returns_neutral_with_provenance():
    """Options flow has no public source, should return neutral with provenance."""
    service = MarketSentimentService()
    result = service.analyze_options_flow("TSLA")

    assert result['symbol'] == "TSLA"
    assert result['flow_score'] == 0.5
    assert result['signal'] == "NEUTRAL_FLOW"
    assert result.get('provenance') == 'unavailable'


def test_get_social_sentiment_returns_neutral_with_provenance():
    """Social sentiment has no public source, should return neutral with provenance."""
    service = MarketSentimentService()
    result = service.get_social_sentiment("BTC")

    assert result['symbol'] == "BTC"
    assert result['overall_sentiment'] == 0.5
    assert result['signal'] == "NEUTRAL"
    assert result.get('provenance') == 'unavailable'


def test_get_comprehensive_sentiment():
    service = MarketSentimentService()

    mock_fear_greed = {'fear_greed_index': 0.8, 'sentiment': 'GREED', 'provenance': 'real'}
    mock_options = {'flow_score': 0.5, 'signal': 'NEUTRAL_FLOW', 'provenance': 'unavailable'}
    mock_social = {'overall_sentiment': 0.5, 'signal': 'NEUTRAL', 'provenance': 'unavailable'}

    with patch.object(service, 'calculate_fear_greed_index', return_value=mock_fear_greed), \
         patch.object(service, 'analyze_options_flow', return_value=mock_options), \
         patch.object(service, 'get_social_sentiment', return_value=mock_social):

        result = service.get_comprehensive_sentiment("ETH")

        assert result['symbol'] == "ETH"
        # Composite = mean of [0.8, 0.5, 0.5] = 0.6
        assert result['composite_sentiment'] == 0.6
        # 0.6 is not > 0.6, so falls to HOLD
        assert result['recommendation'] == "HOLD"
        assert result['analysis_level'] == "INSTITUTIONAL_GRADE"
        assert result.get('provenance') == 'real'


def test_get_comprehensive_sentiment_exception():
    service = MarketSentimentService()

    with patch.object(service, 'calculate_fear_greed_index', side_effect=Exception("Comprehensive error")):
        result = service.get_comprehensive_sentiment("ETH")

        assert result['symbol'] == "ETH"
        assert result['composite_sentiment'] == 0.5
        assert result['recommendation'] == "HOLD"
