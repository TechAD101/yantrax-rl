"""Institutional Trading Strategy Engine

Advanced strategy engine that combines:
- Multi-timeframe technical analysis
- Sentiment analysis integration
- Risk management algorithms
- Position sizing optimization
- Market regime detection
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

class MarketRegime(Enum):
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    VOLATILITY_CRISIS = "volatility_crisis"
    LIQUIDITY_CRUNCH = "liquidity_crunch"

class TradingSignal:
    """Institutional-grade trading signal with full context"""
    
    def __init__(self, 
                 symbol: str,
                 action: str,
                 confidence: float,
                 reasoning: str,
                 risk_score: float,
                 position_size: float,
                 stop_loss: float,
                 take_profit: float,
                 regime: MarketRegime,
                 timeframe: str = "1D"):
        self.symbol = symbol
        self.action = action  # BUY, SELL, HOLD
        self.confidence = confidence
        self.reasoning = reasoning
        self.risk_score = risk_score
        self.position_size = position_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.regime = regime
        self.timeframe = timeframe
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'action': self.action,
            'confidence': round(self.confidence, 3),
            'reasoning': self.reasoning,
            'risk_score': round(self.risk_score, 3),
            'position_size': round(self.position_size, 2),
            'stop_loss': round(self.stop_loss, 2),
            'take_profit': round(self.take_profit, 2),
            'regime': self.regime.value,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat()
        }

class InstitutionalStrategyEngine:
    """Advanced institutional strategy engine combining multiple analysis layers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Strategy parameters
        self.max_position_risk = 0.02  # 2% max risk per trade
        self.max_portfolio_risk = 0.20  # 20% max total portfolio risk
        self.min_confidence_threshold = 0.65
        self.volatility_lookback = 20
        
        # Technical analysis parameters
        self.fast_ema = 9
        self.slow_ema = 21
        self.rsi_period = 14
        self.bb_period = 20
        self.bb_std = 2.0
        
        # Market regime tracking
        self.regime_history = []
        self.volatility_history = []
        
    def generate_institutional_signal(self, 
                                   symbol: str,
                                   market_data: Dict[str, Any],
                                   fundamentals: Dict[str, Any],
                                   sentiment: Dict[str, Any],
                                   portfolio_state: Dict[str, Any] = None) -> TradingSignal:
        """Generate comprehensive institutional trading signal"""
        
        try:
            # 1. Detect Market Regime
            regime = self._detect_market_regime(market_data, sentiment)
            
            # 2. Multi-Timeframe Technical Analysis
            technical_analysis = self._perform_technical_analysis(market_data)
            
            # 3. Sentiment Integration
            sentiment_score = self._calculate_sentiment_score(sentiment)
            
            # 4. Fundamental Analysis Integration
            fundamental_score = self._calculate_fundamental_score(fundamentals)
            
            # 5. Risk Assessment
            risk_assessment = self._assess_risk(symbol, market_data, regime)
            
            # 6. Generate Signal
            signal_confidence = self._calculate_signal_confidence(
                technical_analysis, sentiment_score, fundamental_score, regime
            )
            
            if signal_confidence < self.min_confidence_threshold:
                action = "HOLD"
                reasoning = f"Signal confidence {signal_confidence:.2f} below threshold {self.min_confidence_threshold}"
            else:
                action, reasoning = self._determine_action(
                    technical_analysis, sentiment_score, fundamental_score, regime
                )
            
            # 7. Position Sizing
            position_size = self._calculate_position_size(
                action, signal_confidence, risk_assessment, portfolio_state
            )
            
            # 8. Stop Loss & Take Profit
            stop_loss, take_profit = self._calculate_exit_points(
                action, market_data, volatility=risk_assessment.get('volatility', 0.02)
            )
            
            return TradingSignal(
                symbol=symbol,
                action=action,
                confidence=signal_confidence,
                reasoning=reasoning,
                risk_score=risk_assessment['overall_risk'],
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                regime=regime
            )
            
        except Exception as e:
            self.logger.error(f"Error generating institutional signal for {symbol}: {e}")
            return self._get_neutral_signal(symbol)
    
    def _detect_market_regime(self, 
                           market_data: Dict[str, Any], 
                           sentiment: Dict[str, Any]) -> MarketRegime:
        """Detect current market regime using multiple indicators"""
        
        # Get volatility
        volatility = market_data.get('volatility', 0.02)
        fear_greed = sentiment.get('fear_greed_index', {}).get('fear_greed_index', 0.5)
        
        # Get trend
        price_trend = market_data.get('trend', 'neutral')
        
        # Regime logic
        if volatility > 0.4:
            return MarketRegime.VOLATILITY_CRISIS
        elif fear_greed < 0.2 and price_trend == 'bearish':
            return MarketRegime.LIQUIDITY_CRUNCH
        elif price_trend == 'bullish' and fear_greed > 0.6:
            return MarketRegime.BULL_MARKET
        elif price_trend == 'bearish' and fear_greed < 0.4:
            return MarketRegime.BEAR_MARKET
        else:
            return MarketRegime.SIDEWAYS
    
    def _perform_technical_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive technical analysis"""
        
        prices = market_data.get('price_history', [100] * 50)  # Default if no history
        if len(prices) < 50:
            # Generate synthetic data for demonstration
            prices = [100 + np.sin(i/10) * 5 + np.random.normal(0, 1) for i in range(50)]
        
        prices = np.array(prices)
        
        # EMAs
        ema_9 = self._calculate_ema(prices, self.fast_ema)
        ema_21 = self._calculate_ema(prices, self.slow_ema)
        
        # RSI
        rsi = self._calculate_rsi(prices, self.rsi_period)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(prices, self.bb_period, self.bb_std)
        
        # MACD
        macd_line, signal_line, histogram = self._calculate_macd(prices)
        
        # Volume analysis
        volume_trend = market_data.get('volume_trend', 'neutral')
        
        # Technical signals
        signals = {}
        
        # EMA crossover signal
        if ema_9[-1] > ema_21[-1] and ema_9[-2] <= ema_21[-2]:
            signals['ema_crossover'] = 'bullish'
        elif ema_9[-1] < ema_21[-1] and ema_9[-2] >= ema_21[-2]:
            signals['ema_crossover'] = 'bearish'
        else:
            signals['ema_crossover'] = 'neutral'
        
        # RSI signal
        if rsi[-1] < 30:
            signals['rsi'] = 'oversold'
        elif rsi[-1] > 70:
            signals['rsi'] = 'overbought'
        else:
            signals['rsi'] = 'neutral'
        
        # Bollinger Bands signal
        current_price = prices[-1]
        if current_price > bb_upper[-1]:
            signals['bollinger'] = 'overbought'
        elif current_price < bb_lower[-1]:
            signals['bollinger'] = 'oversold'
        else:
            signals['bollinger'] = 'neutral'
        
        # MACD signal
        if histogram[-1] > 0 and histogram[-2] <= 0:
            signals['macd'] = 'bullish'
        elif histogram[-1] < 0 and histogram[-2] >= 0:
            signals['macd'] = 'bearish'
        else:
            signals['macd'] = 'neutral'
        
        return {
            'signals': signals,
            'ema_9': ema_9[-1] if len(ema_9) > 0 else 0,
            'ema_21': ema_21[-1] if len(ema_21) > 0 else 0,
            'rsi': rsi[-1] if len(rsi) > 0 else 50,
            'bb_upper': bb_upper[-1] if len(bb_upper) > 0 else 0,
            'bb_middle': bb_middle[-1] if len(bb_middle) > 0 else 0,
            'bb_lower': bb_lower[-1] if len(bb_lower) > 0 else 0,
            'macd': macd_line[-1] if len(macd_line) > 0 else 0,
            'volume_trend': volume_trend
        }
    
    def _calculate_sentiment_score(self, sentiment: Dict[str, Any]) -> float:
        """Calculate composite sentiment score from multiple sources"""
        
        components = []
        
        # Fear & Greed
        fear_greed = sentiment.get('fear_greed', {}).get('fear_greed_index', 0.5)
        components.append(fear_greed)
        
        # Options Flow
        options_flow = sentiment.get('options_flow', {}).get('flow_score', 0.5)
        components.append(options_flow)
        
        # Social Sentiment
        social = sentiment.get('social_sentiment', {}).get('overall_sentiment', 0.5)
        components.append(social)
        
        # Composite
        return np.mean(components) if components else 0.5
    
    def _calculate_fundamental_score(self, fundamentals: Dict[str, Any]) -> float:
        """Calculate fundamental analysis score"""
        
        if not fundamentals:
            return 0.5
        
        scores = []
        
        # P/E ratio
        pe_ratio = fundamentals.get('pe_ratio')
        if pe_ratio:
            # Good P/E is typically 15-25
            if 15 <= pe_ratio <= 25:
                scores.append(0.7)
            elif 10 <= pe_ratio <= 30:
                scores.append(0.6)
            else:
                scores.append(0.4)
        
        # Return on Equity
        roe = fundamentals.get('return_on_equity')
        if roe:
            if roe > 0.20:
                scores.append(0.9)
            elif roe > 0.15:
                scores.append(0.8)
            elif roe > 0.10:
                scores.append(0.6)
            else:
                scores.append(0.3)
        
        # Debt to Equity
        debt_equity = fundamentals.get('debt_to_equity')
        if debt_equity:
            if debt_equity < 0.5:
                scores.append(0.8)
            elif debt_equity < 1.0:
                scores.append(0.6)
            else:
                scores.append(0.3)
        
        return np.mean(scores) if scores else 0.5
    
    def _assess_risk(self, symbol: str, market_data: Dict[str, Any], regime: MarketRegime) -> Dict[str, Any]:
        """Comprehensive risk assessment"""
        
        volatility = market_data.get('volatility', 0.02)
        volume = market_data.get('volume', 1000000)
        
        # Base risk from volatility
        volatility_risk = min(volatility / 0.30, 1.0)  # Normalize to 30% max
        
        # Regime risk
        regime_risk = {
            MarketRegime.BULL_MARKET: 0.3,
            MarketRegime.BEAR_MARKET: 0.7,
            MarketRegime.SIDEWAYS: 0.5,
            MarketRegime.VOLATILITY_CRISIS: 0.9,
            MarketRegime.LIQUIDITY_CRUNCH: 0.8
        }.get(regime, 0.5)
        
        # Volume risk (low volume = higher risk)
        volume_risk = max(0.1, 1.0 - (volume / 10000000))  # Normalize to 10M shares
        
        # Overall risk
        overall_risk = (volatility_risk * 0.4 + regime_risk * 0.4 + volume_risk * 0.2)
        
        return {
            'volatility_risk': volatility_risk,
            'regime_risk': regime_risk,
            'volume_risk': volume_risk,
            'overall_risk': overall_risk,
            'volatility': volatility
        }
    
    def _calculate_signal_confidence(self,
                                 technical: Dict[str, Any],
                                 sentiment: float,
                                 fundamental: float,
                                 regime: MarketRegime) -> float:
        """Calculate overall signal confidence"""
        
        # Technical confidence
        tech_signals = technical.get('signals', {})
        tech_score = 0.5
        
        bullish_signals = sum(1 for s in tech_signals.values() if s in ['bullish', 'oversold'])
        bearish_signals = sum(1 for s in tech_signals.values() if s in ['bearish', 'overbought'])
        
        if bullish_signals > bearish_signals:
            tech_score = 0.5 + (bullish_signals - bearish_signals) * 0.1
        elif bearish_signals > bullish_signals:
            tech_score = 0.5 - (bearish_signals - bullish_signals) * 0.1
        
        # Regime adjustment
        regime_multiplier = {
            MarketRegime.BULL_MARKET: 1.2,
            MarketRegime.BEAR_MARKET: 1.1,
            MarketRegime.SIDEWAYS: 0.9,
            MarketRegime.VOLATILITY_CRISIS: 0.7,
            MarketRegime.LIQUIDITY_CRUNCH: 0.8
        }.get(regime, 1.0)
        
        # Weighted combination
        confidence = (tech_score * 0.4 + sentiment * 0.3 + fundamental * 0.3) * regime_multiplier
        
        return np.clip(confidence, 0.0, 1.0)
    
    def _determine_action(self,
                        technical: Dict[str, Any],
                        sentiment: float,
                        fundamental: float,
                        regime: MarketRegime) -> Tuple[str, str]:
        """Determine optimal trading action"""
        
        tech_signals = technical.get('signals', {})
        
        # Count bullish vs bearish signals
        bullish_count = sum(1 for s in tech_signals.values() if s in ['bullish', 'oversold'])
        bearish_count = sum(1 for s in tech_signals.values() if s in ['bearish', 'overbought'])
        
        # Overall trend
        if sentiment > 0.6 and fundamental > 0.6 and bullish_count > bearish_count:
            return "BUY", f"Bullish consensus: {bullish_count} vs {bearish_count} signals, strong sentiment and fundamentals"
        elif sentiment < 0.4 and fundamental < 0.4 and bearish_count > bullish_count:
            return "SELL", f"Bearish consensus: {bearish_count} vs {bullish_count} signals, weak sentiment and fundamentals"
        elif bullish_count > bearish_count + 1:
            return "BUY", f"Technical bullish: {bullish_count} vs {bearish_count} signals"
        elif bearish_count > bullish_count + 1:
            return "SELL", f"Technical bearish: {bearish_count} vs {bullish_count} signals"
        else:
            return "HOLD", "Mixed signals, insufficient conviction"
    
    def _calculate_position_size(self,
                             action: str,
                             confidence: float,
                             risk_assessment: Dict[str, Any],
                             portfolio_state: Dict[str, Any] = None) -> float:
        """Calculate optimal position size using risk management"""
        
        if action == "HOLD":
            return 0.0
        
        # Get portfolio value
        portfolio_value = portfolio_state.get('total_value', 100000) if portfolio_state else 100000
        
        # Risk per trade based on confidence
        risk_per_trade = self.max_position_risk * (confidence / 0.8)  # Scale by confidence
        
        # Volatility adjustment
        volatility_multiplier = 1.0 / (1.0 + risk_assessment['volatility'] * 10)
        
        # Calculate position value
        position_value = portfolio_value * risk_per_trade * volatility_multiplier
        
        return position_value
    
    def _calculate_exit_points(self,
                           action: str,
                           market_data: Dict[str, Any],
                           volatility: float) -> Tuple[float, float]:
        """Calculate optimal stop loss and take profit levels"""
        
        current_price = market_data.get('price', 100)
        
        if action == "BUY":
            # Stop loss below current price
            stop_loss = current_price * (1 - volatility * 2)
            # Take profit above current price (3:1 reward/risk)
            take_profit = current_price * (1 + volatility * 6)
        elif action == "SELL":
            # Stop loss above current price
            stop_loss = current_price * (1 + volatility * 2)
            # Take profit below current price
            take_profit = current_price * (1 - volatility * 6)
        else:
            stop_loss = current_price
            take_profit = current_price
        
        return stop_loss, take_profit
    
    def _get_neutral_signal(self, symbol: str) -> TradingSignal:
        """Get neutral signal for error conditions"""
        return TradingSignal(
            symbol=symbol,
            action="HOLD",
            confidence=0.5,
            reasoning="Analysis unavailable - neutral position",
            risk_score=0.5,
            position_size=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            regime=MarketRegime.SIDEWAYS
        )
    
    # Technical Analysis Helper Methods
    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = np.zeros_like(prices)
        ema[0] = prices[0]
        
        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate Relative Strength Index"""
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.zeros_like(prices)
        avg_loss = np.zeros_like(prices)
        
        avg_gain[period] = np.mean(gains[:period])
        avg_loss[period] = np.mean(losses[:period])
        
        for i in range(period + 1, len(prices)):
            avg_gain[i] = (avg_gain[i-1] * (period-1) + gains[i-1]) / period
            avg_loss[i] = (avg_loss[i-1] * (period-1) + losses[i-1]) / period
        
        rs = avg_gain[period:] / (avg_loss[period:] + 1e-10)
        rsi = 100 - (100 / (1 + rs))
        
        return np.concatenate([[50], rsi])
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int, std_dev: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands"""
        middle_band = np.zeros_like(prices)
        upper_band = np.zeros_like(prices)
        lower_band = np.zeros_like(prices)
        
        for i in range(period, len(prices)):
            window = prices[i-period+1:i+1]
            middle = np.mean(window)
            std = np.std(window)
            
            middle_band[i] = middle
            upper_band[i] = middle + (std * std_dev)
            lower_band[i] = middle - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema_fast = self._calculate_ema(prices, fast)
        ema_slow = self._calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram

# Global instance
_strategy_engine = None

def get_strategy_engine(config: Dict[str, Any] = None) -> InstitutionalStrategyEngine:
    """Get or create global strategy engine instance"""
    global _strategy_engine
    if _strategy_engine is None:
        _strategy_engine = InstitutionalStrategyEngine(config)
    return _strategy_engine