import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

# Adjust path to import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestPerplexityIntelligenceService(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls):
        # Create a mock for httpx
        cls.mock_httpx = MagicMock()
        cls.mock_httpx.AsyncClient = MagicMock()

        # Define custom exceptions on the mock
        class MockHTTPStatusError(Exception):
            def __init__(self, message, response=None, request=None):
                super().__init__(message)
                self.response = response
                self.request = request

        class MockTimeoutException(Exception):
            pass

        cls.mock_httpx.HTTPStatusError = MockHTTPStatusError
        cls.mock_httpx.TimeoutException = MockTimeoutException

        # Patch sys.modules to include mocked httpx
        cls.httpx_patcher = patch.dict(sys.modules, {'httpx': cls.mock_httpx})
        cls.httpx_patcher.start()

        # Now import the service module
        # We import it here so it uses the mocked httpx
        import backend.services.perplexity_intelligence as service_module
        cls.service_module = service_module
        cls.PerplexityIntelligenceService = service_module.PerplexityIntelligenceService
        cls.MarketSentiment = service_module.MarketSentiment
        cls.TrendingAnalysis = service_module.TrendingAnalysis
        cls.AICommentary = service_module.AICommentary

    @classmethod
    def tearDownClass(cls):
        cls.httpx_patcher.stop()
        # Clean up imports to avoid side effects
        if 'backend.services.perplexity_intelligence' in sys.modules:
            del sys.modules['backend.services.perplexity_intelligence']

    def setUp(self):
        self.api_key = "pplx-test-key"
        self.service = self.PerplexityIntelligenceService(api_key=self.api_key)

    def test_init(self):
        self.assertEqual(self.service.api_key, self.api_key)
        self.assertEqual(self.service._cache, {})

    def test_init_from_env(self):
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-env-key"}):
            service = self.PerplexityIntelligenceService()
            self.assertEqual(service.api_key, "pplx-env-key")

    async def test_call_perplexity_success(self):
        # We need to patch AsyncClient on the mock we injected
        # Since we have reference to it via self.mock_httpx or sys.modules['httpx']

        mock_client = AsyncMock()
        self.mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_client.post.return_value = mock_response

        response = await self.service._call_perplexity("Test prompt")
        self.assertEqual(response, "Test response")

        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        self.assertEqual(kwargs["json"]["messages"][0]["content"], "Test prompt")

    async def test_call_perplexity_error(self):
        mock_client = AsyncMock()
        self.mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

        # Test generic exception
        mock_client.post.side_effect = Exception("Connection error")
        response = await self.service._call_perplexity("Test prompt")
        self.assertIsNone(response)

    async def test_get_comprehensive_market_data_success(self):
        expected_data = {
            "market_sentiment": "bullish",
            "risk_factors": ["Inflation"],
            "trends": ["AI boom"],
            "confidence": 0.8
        }

        with patch.object(self.service, "_call_perplexity", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(expected_data)

            result = await self.service.get_comprehensive_market_data(["AAPL"])

            self.assertIn("comprehensive_data", result)
            self.assertEqual(result["comprehensive_data"]["market_sentiment"], "bullish")
            self.assertEqual(result["confidence"], 0.8)

            # Verify caching
            cache_key = "comprehensive_AAPL_True"
            self.assertIn(cache_key, self.service._cache)

    async def test_get_market_sentiment_success(self):
        mock_comp_data = {
            "comprehensive_data": {
                "market_sentiment": "bearish",
                "risk_factors": ["Rate hike"],
                "confidence": 0.9
            }
        }

        with patch.object(self.service, "get_comprehensive_market_data", new_callable=AsyncMock) as mock_get_comp:
            mock_get_comp.return_value = mock_comp_data

            sentiment = await self.service.get_market_sentiment("TSLA")

            self.assertIsInstance(sentiment, self.MarketSentiment)
            self.assertEqual(sentiment.ticker, "TSLA")
            self.assertEqual(sentiment.mood, "bearish")
            self.assertEqual(sentiment.confidence, 0.9)

            # Check cache
            self.assertIn("sentiment_TSLA", self.service._cache)

    async def test_get_market_sentiment_fallback(self):
        with patch.object(self.service, "get_comprehensive_market_data", side_effect=Exception("API Error")):
            sentiment = await self.service.get_market_sentiment("GOOGL")

            self.assertEqual(sentiment.ticker, "GOOGL")
            self.assertEqual(sentiment.mood, "neutral") # Fallback
            self.assertEqual(sentiment.sources, ["Fallback"])

    async def test_get_trending_analysis_success(self):
        mock_response = {
            "opportunities": [{"ticker": "NVDA", "reason": "AI"}],
            "risks": [],
            "ai_reasoning": "AI is booming",
            "confidence": 0.85
        }

        with patch.object(self.service, "_call_perplexity", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(mock_response)

            analysis = await self.service.get_trending_analysis("technology")

            self.assertIsInstance(analysis, self.TrendingAnalysis)
            self.assertEqual(analysis.sector, "technology")
            self.assertEqual(analysis.confidence, 0.85)

    async def test_get_trending_analysis_invalid_json(self):
        with patch.object(self.service, "_call_perplexity", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Invalid JSON"

            analysis = await self.service.get_trending_analysis("crypto")

            # Fallback
            self.assertEqual(analysis.opportunities, [])
            self.assertEqual(analysis.confidence, 0.3)

    async def test_generate_market_commentary_success(self):
        mock_response = {
            "headline": "Tech Rally",
            "analysis": "Tech stocks are up.",
            "trading_implications": "Buy dip",
            "risk_assessment": "High vol"
        }

        with patch.object(self.service, "_call_perplexity", new_callable=AsyncMock) as mock_call:
            mock_call.return_value = json.dumps(mock_response)

            commentary = await self.service.generate_market_commentary(["MSFT", "AAPL"])

            self.assertIsInstance(commentary, self.AICommentary)
            self.assertEqual(commentary.headline, "Tech Rally")
            self.assertEqual(commentary.tickers, ["MSFT", "AAPL"])

    async def test_search_financial_news_success(self):
        mock_client = AsyncMock()
        self.mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"title": "News 1", "url": "https://bloomberg.com/news1", "snippet": "Snippet 1", "date": "2023-01-01"}
            ]
        }
        mock_client.post.return_value = mock_response

        result = await self.service.search_financial_news("market news")

        self.assertEqual(result["count"], 1)
        self.assertEqual(result["results"][0]["title"], "News 1")
        self.assertEqual(result["results"][0]["source"], "bloomberg.com")

    async def test_search_financial_news_error(self):
        mock_client = AsyncMock()
        self.mock_httpx.AsyncClient.return_value.__aenter__.return_value = mock_client

        mock_response = MagicMock()
        mock_response.status_code = 404

        # Create the custom error
        error = self.mock_httpx.HTTPStatusError("404 Not Found", response=mock_response)

        mock_client.post.side_effect = error

        result = await self.service.search_financial_news("bad query")

        self.assertIn("error", result)
        self.assertEqual(result["results"], [])

if __name__ == '__main__':
    unittest.main()
