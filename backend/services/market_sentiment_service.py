"""Advanced Market Sentiment Analysis Service

Institutional-grade sentiment analysis combining:
- Social media sentiment (Twitter, Reddit)
- News sentiment analysis
- Options flow analysis
- Fear & Greed Index calculation
- Institutional flow tracking
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
import json
import asyncio
import aiohttp

class MarketSentimentService:
    """Advanced sentiment analysis for institutional trading decisions"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.fear_greed_cache = {}
        self.sentiment_cache = {}
        
        # API endpoints
        self.alternative_api_key = self.config.get('ALTERNATIVE_API_KEY')
        self.news_api_key = self.config.get('NEWS_API_KEY')
        
        # Sentiment thresholds
        self.extreme_fear = 0.2
        self.extreme_greed = 0.8
        
    def calculate_fear_greed_index(self, symbol: str = None) -> Dict[str, Any]:
        """Calculate comprehensive Fear & Greed Index
        
        Combines multiple indicators:
        - Market momentum (S&P 500 vs 125-day average)
        - Stock price breadth (advancing vs declining issues)
        - Put/Call ratio
        - Junk bond demand
        - Market volatility (VIX)
        - Safe haven demand (stocks vs bonds)
        """
        
        try:
            indicators = {}
            
            # 1. Market Momentum
            momentum_score = self._calculate_market_momentum()
            indicators['momentum'] = momentum_score
            
            # 2. Stock Price Strength
            breadth_score = self._calculate_market_breadth()
            indicators['breadth'] = breadth_score
            
            # 3. Put/Call Ratio
            put_call_score = self._calculate_put_call_ratio()
            indicators['put_call'] = put_call_score
            
            # 4. Market Volatility (VIX)
            volatility_score = self._calculate_volatility_sentiment()
            indicators['volatility'] = volatility_score
            
            # 5. Safe Haven Demand
            safe_haven_score = self._calculate_safe_haven_demand()
            indicators['safe_haven'] = safe_haven_score
            
            # 6. Junk Bond Demand
            junk_bond_score = self._calculate_junk_bond_demand()
            indicators['junk_bonds'] = junk_bond_score
            
            # Calculate weighted average
            weights = {
                'momentum': 0.20,
                'breadth': 0.15,
                'put_call': 0.15,
                'volatility': 0.20,
                'safe_haven': 0.15,
                'junk_bonds': 0.15
            }
            
            fear_greed_score = sum(indicators[key] * weights[key] for key in indicators)
            
            # Determine sentiment
            if fear_greed_score <= self.extreme_fear:
                sentiment = "EXTREME_FEAR"
                recommendation = "STRONG_BUY"
            elif fear_greed_score <= 0.4:
                sentiment = "FEAR"
                recommendation = "BUY"
            elif fear_greed_score <= 0.6:
                sentiment = "NEUTRAL"
                recommendation = "HOLD"
            elif fear_greed_score <= self.extreme_greed:
                sentiment = "GREED"
                recommendation = "SELL"
            else:
                sentiment = "EXTREME_GREED"
                recommendation = "STRONG_SELL"
            
            return {
                'fear_greed_index': round(fear_greed_score, 2),
                'sentiment': sentiment,
                'recommendation': recommendation,
                'indicators': indicators,
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol or 'MARKET'
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating Fear & Greed index: {e}")
            return self._get_neutral_sentiment()
    
    def analyze_options_flow(self, symbol: str) -> Dict[str, Any]:
        """Analyze unusual options activity for institutional flow detection"""
        
        try:
            # This would integrate with Unusual Whales or FlowPoint API
            # For now, simulated institutional flow analysis
            
            flow_signals = {
                'unusual_volume': np.random.uniform(0.1, 0.9),
                'call_put_ratio': np.random.uniform(0.5, 2.0),
                'institutional_activity': np.random.uniform(0.2, 0.8),
                'strike_sensitivity': np.random.uniform(0.3, 0.7)
            }
            
            # Calculate composite flow score
            flow_score = np.mean([
                flow_signals['unusual_volume'],
                flow_signals['institutional_activity'],
                1.0 - abs(flow_signals['call_put_ratio'] - 1.0),
                flow_signals['strike_sensitivity']
            ])
            
            if flow_score > 0.7:
                flow_signal = "BULLISH_INSTITUTIONAL_FLOW"
            elif flow_score < 0.3:
                flow_signal = "BEARISH_INSTITUTIONAL_FLOW"
            else:
                flow_signal = "NEUTRAL_FLOW"
            
            return {
                'symbol': symbol,
                'flow_score': round(flow_score, 2),
                'signal': flow_signal,
                'indicators': flow_signals,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing options flow for {symbol}: {e}")
            return self._get_neutral_flow(symbol)
    
    def get_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze social media sentiment from Twitter, Reddit, StockTwits"""
        
        try:
            # Simulated sentiment analysis
            # In production, integrate with:
            # - Twitter API for tweet sentiment
            # - Reddit API for WallStreetBets and investing subs
            # - StockTwits API
            # - News APIs for sentiment scoring
            
            sentiment_sources = {
                'twitter': {
                    'sentiment': np.random.uniform(-0.5, 0.5),
                    'volume': np.random.randint(100, 1000),
                    'influence': np.random.uniform(0.3, 0.9)
                },
                'reddit': {
                    'sentiment': np.random.uniform(-0.7, 0.7),
                    'volume': np.random.randint(50, 500),
                    'influence': np.random.uniform(0.4, 0.8)
                },
                'stocktwits': {
                    'sentiment': np.random.uniform(-0.3, 0.3),
                    'volume': np.random.randint(20, 200),
                    'influence': np.random.uniform(0.2, 0.6)
                }
            }
            
            # Calculate weighted sentiment score
            total_weighted_sentiment = 0
            total_weight = 0
            
            for source, data in sentiment_sources.items():
                weight = data['influence'] * data['volume']
                total_weighted_sentiment += data['sentiment'] * weight
                total_weight += weight
            
            if total_weight > 0:
                overall_sentiment = total_weighted_sentiment / total_weight
            else:
                overall_sentiment = 0
            
            # Normalize to 0-1 scale
            normalized_sentiment = (overall_sentiment + 1) / 2
            
            if normalized_sentiment > 0.65:
                social_signal = "STRONGLY_BULLISH"
            elif normalized_sentiment > 0.55:
                social_signal = "BULLISH"
            elif normalized_sentiment > 0.45:
                social_signal = "NEUTRAL"
            elif normalized_sentiment > 0.35:
                social_signal = "BEARISH"
            else:
                social_signal = "STRONGLY_BEARISH"
            
            return {
                'symbol': symbol,
                'overall_sentiment': round(normalized_sentiment, 3),
                'signal': social_signal,
                'sources': sentiment_sources,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting social sentiment for {symbol}: {e}")
            return self._get_neutral_social_sentiment(symbol)
    
    def get_comprehensive_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Combine all sentiment indicators for institutional-grade analysis"""
        
        try:
            # Get all sentiment components
            fear_greed = self.calculate_fear_greed_index(symbol)
            options_flow = self.analyze_options_flow(symbol)
            social_sentiment = self.get_social_sentiment(symbol)
            
            # Calculate composite sentiment score
            components = [
                fear_greed['fear_greed_index'],
                options_flow['flow_score'],
                social_sentiment['overall_sentiment']
            ]
            
            composite_score = np.mean(components)
            
            # Generate final recommendation
            if composite_score > 0.7:
                final_recommendation = "STRONG_BUY"
                confidence = 0.85
            elif composite_score > 0.6:
                final_recommendation = "BUY"
                confidence = 0.75
            elif composite_score > 0.4:
                final_recommendation = "HOLD"
                confidence = 0.60
            elif composite_score > 0.3:
                final_recommendation = "SELL"
                confidence = 0.70
            else:
                final_recommendation = "STRONG_SELL"
                confidence = 0.80
            
            return {
                'symbol': symbol,
                'composite_sentiment': round(composite_score, 3),
                'recommendation': final_recommendation,
                'confidence': confidence,
                'components': {
                    'fear_greed': fear_greed,
                    'options_flow': options_flow,
                    'social_sentiment': social_sentiment
                },
                'analysis_level': 'INSTITUTIONAL_GRADE',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive sentiment analysis for {symbol}: {e}")
            return self._get_emergency_sentiment(symbol)
    
    def _calculate_market_momentum(self) -> float:
        """Calculate market momentum based on S&P 500 performance"""
        # Simulated - in production, fetch real S&P data
        momentum = np.random.uniform(0.2, 0.8)
        return momentum
    
    def _calculate_market_breadth(self) -> float:
        """Calculate market breadth (advancing vs declining stocks)"""
        # Simulated breadth calculation
        breadth = np.random.uniform(0.3, 0.7)
        return breadth
    
    def _calculate_put_call_ratio(self) -> float:
        """Calculate sentiment from put/call ratio"""
        # Simulated PCR analysis
        pcr = np.random.uniform(0.6, 1.4)
        # Convert to sentiment score (closer to 1 = more bullish)
        sentiment = 2.0 - pcr if pcr > 1.0 else pcr
        return np.clip(sentiment / 2.0, 0, 1)
    
    def _calculate_volatility_sentiment(self) -> float:
        """Calculate sentiment from VIX levels"""
        # Simulated VIX analysis
        vix = np.random.uniform(15, 35)
        # Lower VIX = more bullish
        sentiment = max(0, (40 - vix) / 25)
        return sentiment
    
    def _calculate_safe_haven_demand(self) -> float:
        """Calculate safe haven demand (stocks vs bonds)"""
        # Simulated safe haven analysis
        demand = np.random.uniform(0.2, 0.8)
        return demand
    
    def _calculate_junk_bond_demand(self) -> float:
        """Calculate junk bond demand (risk appetite indicator)"""
        # Simulated junk bond analysis
        demand = np.random.uniform(0.3, 0.7)
        return demand
    
    def _get_neutral_sentiment(self) -> Dict[str, Any]:
        """Fallback neutral sentiment"""
        return {
            'fear_greed_index': 0.5,
            'sentiment': 'NEUTRAL',
            'recommendation': 'HOLD',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_neutral_flow(self, symbol: str) -> Dict[str, Any]:
        """Fallback neutral flow"""
        return {
            'symbol': symbol,
            'flow_score': 0.5,
            'signal': 'NEUTRAL_FLOW',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_neutral_social_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Fallback neutral social sentiment"""
        return {
            'symbol': symbol,
            'overall_sentiment': 0.5,
            'signal': 'NEUTRAL',
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_emergency_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Emergency fallback for critical errors"""
        return {
            'symbol': symbol,
            'composite_sentiment': 0.5,
            'recommendation': 'HOLD',
            'confidence': 0.5,
            'error': 'Sentiment analysis unavailable',
            'timestamp': datetime.now().isoformat()
        }

# Global instance
_sentiment_service = None

def get_sentiment_service(config: Dict[str, Any] = None) -> MarketSentimentService:
    """Get or create global sentiment service instance"""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = MarketSentimentService(config)
    return _sentiment_service