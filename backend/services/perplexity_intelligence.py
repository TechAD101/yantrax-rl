"""
Perplexity Intelligence Service for Yantra X

This service provides real-time market intelligence by leveraging Perplexity's AI
for market analysis, sentiment extraction, and trading insights.

Key Capabilities:
- Real-time market sentiment analysis
- AI-powered market commentary generation
- Trending sector/asset analysis
- Integration with AI Firm debate engine

Usage:
    from services.perplexity_intelligence import PerplexityIntelligenceService
    
    service = PerplexityIntelligenceService()
    sentiment = await service.get_market_sentiment("AAPL")
    commentary = await service.generate_market_commentary(["AAPL", "MSFT", "GOOGL"])
"""

import os
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from functools import lru_cache
import httpx

logger = logging.getLogger(__name__)


@dataclass
class MarketSentiment:
    """Structured sentiment analysis result."""
    ticker: str
    mood: str  # bullish, bearish, neutral, mixed
    confidence: float  # 0.0 - 1.0
    summary: str
    key_factors: List[str]
    sources: List[str]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TrendingAnalysis:
    """Analysis of trending opportunities and risks."""
    sector: str
    opportunities: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    ai_reasoning: str
    confidence: float
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AICommentary:
    """AI-generated market commentary."""
    tickers: List[str]
    headline: str
    analysis: str
    trading_implications: str
    risk_assessment: str
    persona_perspective: Optional[str]  # Warren, Cathie, Quant, Degen
    timestamp: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


class PerplexityIntelligenceService:
    """
    Real-time market intelligence service powered by Perplexity AI.
    
    Integrates with Yantra X's AI Firm layer to provide:
    - Live sentiment analysis for debate engine
    - Market commentary for reports
    - Trending analysis for opportunity scanning
    """
    
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    MODEL = "sonar-pro"  # Perplexity's most capable model
    
    # Cache TTL in seconds
    SENTIMENT_CACHE_TTL = 300  # 5 minutes
    TRENDING_CACHE_TTL = 600  # 10 minutes
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity Intelligence Service.
        
        Args:
            api_key: Perplexity API key. If not provided, will try environment.
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
        if not self.api_key:
            logger.warning(
                "⚠️ PERPLEXITY_API_KEY not configured. "
                "Service will return fallback data."
            )
        else:
            # Mask key for logging
            masked = f"{self.api_key[:8]}...{self.api_key[-4:]}" if len(self.api_key) > 12 else "***"
            logger.info(f"✅ Perplexity Intelligence Service initialized with key: {masked}")
    
    def _is_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_timestamps:
            return False
        age = (datetime.now() - self._cache_timestamps[key]).total_seconds()
        return age < ttl
    
    async def _call_perplexity(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        timeout: float = 30.0
    ) -> Optional[str]:
        """
        Make an API call to Perplexity.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system-level instructions
            timeout: Request timeout in seconds
            
        Returns:
            API response text or None on failure
        """
        if not self.api_key:
            logger.warning("Perplexity API key not configured, returning None")
            return None
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": 0.2,  # Lower temperature for more factual responses
            "max_tokens": 1024,
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    self.PERPLEXITY_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
        except httpx.TimeoutException:
            logger.error(f"Perplexity API timeout after {timeout}s")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"Perplexity API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Perplexity API error: {e}")
            return None
    
    def _call_perplexity_sync(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        timeout: float = 30.0
    ) -> Optional[str]:
        """Synchronous wrapper for Perplexity API calls."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, 
                        self._call_perplexity(prompt, system_prompt, timeout)
                    )
                    return future.result(timeout=timeout + 5)
            else:
                return loop.run_until_complete(
                    self._call_perplexity(prompt, system_prompt, timeout)
                )
        except Exception as e:
            logger.error(f"Sync Perplexity call failed: {e}")
            return None
    
    async def get_market_sentiment(
        self, 
        ticker: str,
        include_news: bool = True
    ) -> MarketSentiment:
        """
        Get real-time market sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            include_news: Whether to include recent news analysis
            
        Returns:
            MarketSentiment object with analysis
        """
        cache_key = f"sentiment_{ticker}"
        
        # Check cache
        if self._is_cache_valid(cache_key, self.SENTIMENT_CACHE_TTL):
            logger.debug(f"Returning cached sentiment for {ticker}")
            return self._cache[cache_key]
        
        system_prompt = """You are a senior financial analyst at a major investment firm.
Analyze market sentiment with precision. Always respond in valid JSON format.
Focus on: recent news, price action, analyst opinions, social sentiment, and macro factors."""
        
        prompt = f"""Analyze the current market sentiment for {ticker} stock.

Respond ONLY with a JSON object in this exact format:
{{
    "mood": "bullish|bearish|neutral|mixed",
    "confidence": 0.0 to 1.0,
    "summary": "2-3 sentence summary of current sentiment",
    "key_factors": ["factor 1", "factor 2", "factor 3"],
    "sources": ["source 1", "source 2"]
}}

{"Include recent news events in your analysis." if include_news else ""}
Be specific about price levels, percentages, and concrete data points."""
        
        response = await self._call_perplexity(prompt, system_prompt)
        
        if response:
            try:
                # Extract JSON from response
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                
                data = json.loads(json_str.strip())
                
                sentiment = MarketSentiment(
                    ticker=ticker,
                    mood=data.get("mood", "neutral"),
                    confidence=float(data.get("confidence", 0.5)),
                    summary=data.get("summary", "Unable to analyze sentiment"),
                    key_factors=data.get("key_factors", []),
                    sources=data.get("sources", ["Perplexity AI"]),
                    timestamp=datetime.now().isoformat()
                )
                
                # Cache result
                self._cache[cache_key] = sentiment
                self._cache_timestamps[cache_key] = datetime.now()
                
                return sentiment
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse Perplexity response as JSON: {e}")
        
        # Return fallback sentiment
        return MarketSentiment(
            ticker=ticker,
            mood="neutral",
            confidence=0.3,
            summary=f"Unable to fetch real-time sentiment for {ticker}. Perplexity API may be unavailable.",
            key_factors=["API unavailable"],
            sources=["Fallback"],
            timestamp=datetime.now().isoformat()
        )
    
    def get_market_sentiment_sync(self, ticker: str, include_news: bool = True) -> MarketSentiment:
        """Synchronous version of get_market_sentiment."""
        try:
            return asyncio.run(self.get_market_sentiment(ticker, include_news))
        except Exception as e:
            logger.error(f"Sync sentiment fetch failed: {e}")
            return MarketSentiment(
                ticker=ticker,
                mood="neutral",
                confidence=0.3,
                summary=f"Error fetching sentiment: {str(e)}",
                key_factors=[],
                sources=["Error"],
                timestamp=datetime.now().isoformat()
            )
    
    async def get_trending_analysis(
        self,
        sector: str = "technology",
        focus: str = "opportunities"
    ) -> TrendingAnalysis:
        """
        Get AI analysis of trending opportunities in a sector.
        
        Args:
            sector: Market sector to analyze (technology, healthcare, finance, crypto, etc.)
            focus: What to focus on (opportunities, risks, or both)
            
        Returns:
            TrendingAnalysis with opportunities and risks
        """
        cache_key = f"trending_{sector}_{focus}"
        
        if self._is_cache_valid(cache_key, self.TRENDING_CACHE_TTL):
            return self._cache[cache_key]
        
        system_prompt = """You are a hedge fund research analyst specializing in identifying 
market opportunities and risks. Provide actionable, data-driven insights.
Always respond in valid JSON format."""
        
        prompt = f"""Analyze current trends in the {sector} sector.

Respond ONLY with a JSON object in this exact format:
{{
    "opportunities": [
        {{"ticker": "XXX", "reason": "why this is an opportunity", "catalyst": "upcoming event/driver", "risk_level": "low|medium|high"}},
        ...
    ],
    "risks": [
        {{"area": "risk area", "description": "what could go wrong", "likelihood": "low|medium|high", "impact": "low|medium|high"}},
        ...
    ],
    "ai_reasoning": "Your overall analysis of the sector in 2-3 sentences",
    "confidence": 0.0 to 1.0
}}

Focus on {focus}. Provide 3-5 items for opportunities and 2-3 for risks.
Use real, current data and specific ticker symbols."""
        
        response = await self._call_perplexity(prompt, system_prompt)
        
        if response:
            try:
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                
                data = json.loads(json_str.strip())
                
                analysis = TrendingAnalysis(
                    sector=sector,
                    opportunities=data.get("opportunities", []),
                    risks=data.get("risks", []),
                    ai_reasoning=data.get("ai_reasoning", ""),
                    confidence=float(data.get("confidence", 0.5)),
                    timestamp=datetime.now().isoformat()
                )
                
                self._cache[cache_key] = analysis
                self._cache_timestamps[cache_key] = datetime.now()
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse trending analysis: {e}")
        
        return TrendingAnalysis(
            sector=sector,
            opportunities=[],
            risks=[],
            ai_reasoning="Unable to fetch trending analysis. Perplexity API may be unavailable.",
            confidence=0.3,
            timestamp=datetime.now().isoformat()
        )
    
    async def generate_market_commentary(
        self,
        tickers: List[str],
        persona: Optional[str] = None
    ) -> AICommentary:
        """
        Generate AI-powered market commentary for given tickers.
        
        Args:
            tickers: List of stock tickers to analyze
            persona: Optional AI persona perspective (Warren, Cathie, Quant, Degen)
            
        Returns:
            AICommentary with analysis from the specified perspective
        """
        persona_prompts = {
            "Warren": "You are Warren Buffett - focus on value, fundamentals, moats, and long-term thinking. Be skeptical of hype.",
            "Cathie": "You are Cathie Wood - focus on innovation, disruption, exponential growth, and future potential. Be optimistic about technology.",
            "Quant": "You are a quantitative analyst - focus on data, statistics, correlations, and mathematical patterns. Be objective and numbers-driven.",
            "Degen": "You are a crypto-native degen trader - focus on momentum, social signals, memes, and YOLO opportunities. Be bold but aware of risks.",
        }
        
        system_prompt = persona_prompts.get(persona, """You are a senior market analyst providing balanced, 
professional commentary. Focus on actionable insights and risk awareness.""")
        
        tickers_str = ", ".join(tickers[:5])  # Limit to 5 tickers
        
        prompt = f"""Provide market commentary for: {tickers_str}

Respond ONLY with a JSON object in this exact format:
{{
    "headline": "A compelling one-line summary",
    "analysis": "2-3 paragraph detailed analysis",
    "trading_implications": "What traders should consider",
    "risk_assessment": "Key risks to be aware of"
}}

{"Apply your unique investment perspective and voice." if persona else ""}
Be specific with price levels, catalysts, and actionable insights."""
        
        response = await self._call_perplexity(prompt, system_prompt)
        
        if response:
            try:
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                
                data = json.loads(json_str.strip())
                
                return AICommentary(
                    tickers=tickers,
                    headline=data.get("headline", "Market Update"),
                    analysis=data.get("analysis", ""),
                    trading_implications=data.get("trading_implications", ""),
                    risk_assessment=data.get("risk_assessment", ""),
                    persona_perspective=persona,
                    timestamp=datetime.now().isoformat()
                )
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse commentary: {e}")
        
        return AICommentary(
            tickers=tickers,
            headline="Commentary Unavailable",
            analysis="Unable to generate market commentary. Perplexity API may be unavailable.",
            trading_implications="Please try again later.",
            risk_assessment="Unknown",
            persona_perspective=persona,
            timestamp=datetime.now().isoformat()
        )
    
    async def get_debate_context(
        self,
        topic: str,
        tickers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get market context for the AI Firm debate engine.
        
        This method provides real-time intelligence that can be used
        by the debate engine to inform persona discussions.
        
        Args:
            topic: The debate topic (e.g., "Should we buy AAPL?")
            tickers: Optional list of relevant tickers
            
        Returns:
            Dict with market context for debate
        """
        context = {
            "timestamp": datetime.now().isoformat(),
            "topic": topic,
            "tickers": tickers or [],
            "sentiments": [],
            "market_condition": "unknown",
            "key_insights": [],
        }
        
        # Gather sentiment for each ticker
        if tickers:
            for ticker in tickers[:3]:  # Limit to 3 to avoid rate limits
                try:
                    sentiment = await self.get_market_sentiment(ticker)
                    context["sentiments"].append(sentiment.to_dict())
                except Exception as e:
                    logger.warning(f"Failed to get sentiment for {ticker}: {e}")
        
        # Generate overall market insight
        system_prompt = """You are a market intelligence system providing context for AI trading decisions.
Be concise, factual, and focus on actionable information."""
        
        prompt = f"""Provide market context for this trading decision:
Topic: {topic}
Tickers: {', '.join(tickers) if tickers else 'General market'}

Respond with a JSON object:
{{
    "market_condition": "bullish|bearish|choppy|trending",
    "volatility": "low|medium|high",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "recommendation_bias": "buy|sell|hold|wait"
}}"""
        
        response = await self._call_perplexity(prompt, system_prompt)
        
        if response:
            try:
                json_str = response
                if "```json" in response:
                    json_str = response.split("```json")[1].split("```")[0]
                elif "```" in response:
                    json_str = response.split("```")[1].split("```")[0]
                
                data = json.loads(json_str.strip())
                context.update(data)
            except json.JSONDecodeError:
                pass
        
        return context
    
    # ==================== SEARCH API ====================
    # Dedicated Search API for structured web results with filtering
    
    SEARCH_API_URL = "https://api.perplexity.ai/search"
    
    # Trusted financial news sources for domain filtering
    FINANCIAL_NEWS_DOMAINS = [
        "bloomberg.com",
        "reuters.com",
        "cnbc.com",
        "wsj.com",
        "ft.com",
        "marketwatch.com",
        "seekingalpha.com",
        "finance.yahoo.com",
        "fool.com",
        "investopedia.com",
    ]
    
    async def search_financial_news(
        self,
        query: str,
        max_results: int = 5,
        trusted_sources_only: bool = True
    ) -> Dict[str, Any]:
        """
        Search for real-time financial news using Perplexity Search API.
        
        Args:
            query: Search query (e.g., "AAPL earnings report")
            max_results: Number of results (1-20)
            trusted_sources_only: If True, limit to trusted financial domains
            
        Returns:
            Dict with structured search results
        """
        if not self.api_key:
            return {"error": "API key not configured", "results": []}
        
        payload = {
            "query": query,
            "max_results": min(max_results, 20),
            "max_tokens_per_page": 1024,
        }
        
        if trusted_sources_only:
            payload["search_domain_filter"] = self.FINANCIAL_NEWS_DOMAINS
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.SEARCH_API_URL,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                # Process and standardize results
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "snippet": item.get("snippet", "")[:500],  # Truncate for efficiency
                        "date": item.get("date"),
                        "source": self._extract_domain(item.get("url", ""))
                    })
                
                return {
                    "query": query,
                    "results": results,
                    "count": len(results),
                    "timestamp": datetime.now().isoformat(),
                    "trusted_sources": trusted_sources_only
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Search API error: {e.response.status_code}")
            return {"error": str(e), "results": [], "query": query}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"error": str(e), "results": [], "query": query}
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace("www.", "")
        except:
            return url
    
    async def search_ticker_news(
        self,
        ticker: str,
        news_type: str = "all"  # all, earnings, analyst, sec
    ) -> Dict[str, Any]:
        """
        Search for news about a specific ticker.
        
        Args:
            ticker: Stock ticker symbol
            news_type: Type of news to search for
            
        Returns:
            Dict with ticker-specific news
        """
        query_templates = {
            "all": f"{ticker} stock news latest",
            "earnings": f"{ticker} earnings report results",
            "analyst": f"{ticker} analyst rating upgrade downgrade",
            "sec": f"{ticker} SEC filing 10-K 10-Q"
        }
        
        query = query_templates.get(news_type, query_templates["all"])
        results = await self.search_financial_news(query, max_results=5)
        results["ticker"] = ticker
        results["news_type"] = news_type
        return results
    
    async def multi_ticker_search(
        self,
        tickers: List[str],
        query_suffix: str = "latest news"
    ) -> Dict[str, List[Dict]]:
        """
        Search news for multiple tickers efficiently.
        
        Args:
            tickers: List of ticker symbols
            query_suffix: What to search for each ticker
            
        Returns:
            Dict mapping ticker to search results
        """
        results = {}
        for ticker in tickers[:5]:  # Limit to 5 tickers
            try:
                search_result = await self.search_financial_news(
                    f"{ticker} {query_suffix}",
                    max_results=3
                )
                results[ticker] = search_result.get("results", [])
            except Exception as e:
                logger.warning(f"Multi-search failed for {ticker}: {e}")
                results[ticker] = []
        
        return {
            "tickers": tickers,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def search_financial_news_sync(
        self,
        query: str,
        max_results: int = 5,
        trusted_sources_only: bool = True
    ) -> Dict[str, Any]:
        """Synchronous version of search_financial_news."""
        try:
            return asyncio.run(self.search_financial_news(query, max_results, trusted_sources_only))
        except Exception as e:
            return {"error": str(e), "results": [], "query": query}
    
    def is_configured(self) -> bool:
        """Check if the service has a valid API key configured."""
        return bool(self.api_key and self.api_key.startswith("pplx-"))
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status for health checks."""
        return {
            "service": "PerplexityIntelligenceService",
            "configured": self.is_configured(),
            "model": self.MODEL,
            "cache_entries": len(self._cache),
            "api_endpoint": self.PERPLEXITY_API_URL,
        }


# Global instance for use across the application
_perplexity_service: Optional[PerplexityIntelligenceService] = None


def get_perplexity_service() -> PerplexityIntelligenceService:
    """Get or create the global Perplexity service instance."""
    global _perplexity_service
    if _perplexity_service is None:
        _perplexity_service = PerplexityIntelligenceService()
    return _perplexity_service


# Convenience functions for synchronous use
def get_sentiment(ticker: str) -> Dict:
    """Quick synchronous sentiment lookup."""
    service = get_perplexity_service()
    result = service.get_market_sentiment_sync(ticker)
    return result.to_dict()


def get_commentary(tickers: List[str], persona: Optional[str] = None) -> Dict:
    """Quick synchronous commentary generation."""
    service = get_perplexity_service()
    try:
        result = asyncio.run(service.generate_market_commentary(tickers, persona))
        return result.to_dict()
    except Exception as e:
        return {"error": str(e), "tickers": tickers}
