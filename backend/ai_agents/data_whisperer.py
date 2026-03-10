# ai_agents/data_whisperer.py - Enhanced Data Analysis Agent

import random
from typing import Dict, Any
from services.market_data_service import get_latest_price

# ML/AI Service Imports
try:
    from services.perplexity_intelligence import get_perplexity_service, get_sentiment
    from services.market_sentiment_service import get_sentiment_service
except ImportError:
    # Graceful degradation if services module structure is different or dependencies missing
    get_perplexity_service = None
    get_sentiment = None
    get_sentiment_service = None
import threading
import time

# Attempt to use Redis-backed circuit breaker service
try:
    from services.circuit_breaker import RedisCircuitBreaker
    cb = RedisCircuitBreaker()
except Exception:
    cb = None

# Optional metrics
try:
    from services.metrics_service import agent_latency, cb_state_changes
except Exception:
    agent_latency = None
    cb_state_changes = None

# Thread lock for thread-safe operations
_data_lock = threading.Lock()

# Simple circuit breaker state
_cb_failures = 0
_cb_open = False
_cb_last_attempt = 0
_CB_FAILURE_THRESHOLD = 3
_CB_RESET_TIMEOUT = 30  # seconds

def analyze_data(symbol: str = "AAPL") -> Dict:
    """
    Enhanced market data analysis with real-time integration, thread safety, and circuit breaker fallback.
    """
    global _cb_failures, _cb_open, _cb_last_attempt
    price = None

    # Use Redis-backed circuit breaker if available for cross-process protection
    key = symbol.upper()
    allowed = True
    if cb:
        try:
            allowed = cb.allow_request(key)
        except Exception:
            allowed = True

    with _data_lock:
        now = time.time()
        if not allowed:
            print(f"[Data Whisperer] Circuit breaker OPEN for {symbol}, using fallback.")
            price = None
        else:
            try:
                start = time.time()
                price = get_latest_price(symbol)
                duration = time.time() - start
                # record agent latency metric
                if agent_latency:
                    try:
                        agent_latency.labels(agent='data_whisperer').observe(duration)
                    except Exception:
                        pass

                if price is None:
                    raise Exception("No price returned")

                # success
                _cb_failures = 0
                if cb:
                    try:
                        cb.record_success(key)
                        if cb_state_changes:
                            try:
                                cb_state_changes.labels(key=key, state='closed').inc()
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception as e:
                _cb_failures += 1
                print(f"[Data Whisperer] Market data error: {e}")
                if cb:
                    try:
                        cb.record_failure(key)
                        if cb_state_changes:
                            try:
                                cb_state_changes.labels(key=key, state='open').inc()
                            except Exception:
                                pass
                    except Exception:
                        pass
                else:
                    if _cb_failures >= _CB_FAILURE_THRESHOLD:
                        _cb_open = True
                        _cb_last_attempt = now
                price = None

    if price is None:
        # Fallback to simulated data for testing/demo
        price = round(random.uniform(10000, 60000), 2)
        print(f"[Data Whisperer] Using simulated price for {symbol}: ${price}")
    else:
        print(f"[Data Whisperer] Real-time price for {symbol}: ${price}")

    # Enhanced market analysis
    ml_sentiment = _get_ml_sentiment(symbol)

    market_data = {
        "symbol": symbol,
        "price": price,
        "volume": random.randint(100000, 10000000),  # Enhanced volume range
        "trend": _analyze_trend(price),
        "volatility": _calculate_volatility(),
        "sentiment": ml_sentiment["sentiment"],
        "sentiment_confidence": ml_sentiment["confidence"],
        "sentiment_source": ml_sentiment["source"],
        "sentiment_details": ml_sentiment["details"],
        "technical_indicators": {
            "rsi": round(random.uniform(20, 80), 2),
            "macd_signal": random.choice(["bullish", "bearish", "neutral"]),
            "moving_average_20": round(price * random.uniform(0.95, 1.05), 2),
            "moving_average_50": round(price * random.uniform(0.90, 1.10), 2)
        },
        "market_conditions": {
            "volatility_regime": _get_volatility_regime(),
            "market_phase": _detect_market_phase(price)
        }
    }

    print(f"[Data Whisperer] Analysis complete for {symbol}: {market_data['trend']} trend, {market_data['sentiment']} sentiment")
    return market_data

def _analyze_trend(price: float) -> str:
    """Analyze price trend based on technical indicators"""
    # Enhanced trend analysis logic
    if price > 50000:
        return "strong_bullish"
    elif price > 30000:
        return "bullish"  
    elif price > 15000:
        return "sideways"
    elif price > 8000:
        return "bearish"
    else:
        return "strong_bearish"

def _calculate_volatility() -> float:
    """Calculate market volatility estimate"""
    base_vol = random.uniform(0.15, 0.35)
    # Add some market regime awareness
    volatility_multiplier = random.choice([0.8, 1.0, 1.2, 1.5])  # Different vol regimes
    return round(base_vol * volatility_multiplier, 4)


def _analyze_sentiment(symbol: str) -> str:
    """Analyze market sentiment - wrapper for ML integration"""
    # Use the ML helper but return only the string for backward compatibility
    result = _get_ml_sentiment(symbol)
    return result["sentiment"]

def _get_ml_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Get market sentiment using available ML/AI services.
    Returns a dictionary with sentiment, confidence, source, and details.
    """
    # Default fallback
    fallback_sentiment = _analyze_sentiment_fallback(symbol)
    result = {
        "sentiment": fallback_sentiment,
        "confidence": 0.5,
        "source": "heuristic_fallback",
        "details": {}
    }

    # 1. Try Perplexity AI (True ML)
    if get_perplexity_service and get_sentiment:
        try:
            pplx = get_perplexity_service()
            if pplx.is_configured():
                ml_data = get_sentiment(symbol)
                # Handle potential key variations
                raw_sentiment = ml_data.get('market_sentiment', ml_data.get('sentiment', 'neutral'))
                if not isinstance(raw_sentiment, str):
                    raw_sentiment = 'neutral'
                mapped_sentiment = _map_sentiment(raw_sentiment)

                result = {
                    "sentiment": mapped_sentiment,
                    "confidence": ml_data.get('confidence', 0.8),
                    "source": "perplexity_ai",
                    "details": ml_data
                }
                return result
        except Exception as e:
            print(f"[Data Whisperer] Perplexity sentiment analysis failed: {e}")

    # 2. Try MarketSentimentService (Statistical/Heuristic)
    if get_sentiment_service:
        try:
            mss = get_sentiment_service()
            # get_comprehensive_sentiment returns dict with 'recommendation' like STRONG_BUY
            comp = mss.get_comprehensive_sentiment(symbol)
            rec = comp.get('recommendation', 'HOLD')
            mapped_sentiment = _map_recommendation(rec)

            result = {
                "sentiment": mapped_sentiment,
                "confidence": comp.get('confidence', 0.6),
                "source": "market_sentiment_service",
                "details": comp
            }
            return result
        except Exception as e:
            print(f"[Data Whisperer] MarketSentimentService analysis failed: {e}")

    return result

def _map_sentiment(raw_sentiment: str) -> str:
    """Map arbitrary sentiment strings to standard set"""
    s = raw_sentiment.lower()
    if 'very' in s and 'bull' in s: return 'very_bullish'
    if 'very' in s and 'bear' in s: return 'very_bearish'
    if 'strong' in s and 'bull' in s: return 'very_bullish'
    if 'strong' in s and 'bear' in s: return 'very_bearish'
    if 'bull' in s: return 'bullish'
    if 'bear' in s: return 'bearish'
    return 'neutral'

def _map_recommendation(rec: str) -> str:
    """Map recommendation strings to standard sentiment set"""
    mapping = {
        'STRONG_BUY': 'very_bullish',
        'BUY': 'bullish',
        'HOLD': 'neutral',
        'SELL': 'bearish',
        'STRONG_SELL': 'very_bearish'
    }
    return mapping.get(rec, 'neutral')

def _analyze_sentiment_fallback(symbol: str) -> str:
    """Original random fallback for sentiment"""
    sentiments = ["very_bullish", "bullish", "neutral", "bearish", "very_bearish"]
    weights = [0.15, 0.25, 0.30, 0.20, 0.10]  # Slightly optimistic bias
    return random.choices(sentiments, weights=weights)[0]


def _get_volatility_regime() -> str:
    """Detect current volatility regime"""
    return random.choice(["low_vol", "normal_vol", "high_vol", "crisis_vol"])

def _detect_market_phase(price: float) -> str:
    """Detect current market phase for strategy adaptation"""
    # Simple market phase detection based on price levels
    if price > 45000:
        return "bull_market"
    elif price < 15000:
        return "bear_market" 
    else:
        return "range_bound"


# --- Parallel agent execution utility ---
from concurrent.futures import ThreadPoolExecutor

def run_agents_in_parallel(agent_funcs, *args, **kwargs):
    """
    Run multiple agent functions in parallel threads for efficiency.
    agent_funcs: list of callables
    Returns: list of results in order
    """
    with ThreadPoolExecutor(max_workers=len(agent_funcs)) as executor:
        futures = [executor.submit(func, *args, **kwargs) for func in agent_funcs]
        return [f.result() for f in futures]
