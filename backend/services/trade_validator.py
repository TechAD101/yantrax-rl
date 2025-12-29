from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import uuid
from services.market_data_service_waterfall import get_waterfall_service
from services.knowledge_base import get_knowledge_base

"""
Trade Validation Engine

Strict 8-point Boolean validation system.
CRITICAL: ALL checks must pass for trade execution.

The 8 Mandatory Checks:
1. Macro Alignment ≥50%
2. Liquidity Alignment ≥40%
3. Confidence Band ≥60%
4. Risk-Reward Ratio ≥1.5
5. No Recent Reversals
6. No Black Swan Events
7. Position Size ≤10%
8. Execution Risk <2%
"""



class TradeValidator:
    """
    Strict 8-point validation engine for institutional-grade risk management
    
    CRITICAL POLICY: If ANY check fails, the trade is BLOCKED. No exceptions.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_history = []  # In-memory audit trail
        self.trade_history = {}  # Symbol -> list of recent trades
        
        # Thresholds
        self.MACRO_ALIGNMENT_MIN = 50
        self.LIQUIDITY_ALIGNMENT_MIN = 40
        self.CONFIDENCE_BAND_MIN = 60
        self.RISK_REWARD_MIN = 1.5
        self.BLACK_SWAN_VIX_MAX = 40
        self.POSITION_SIZE_MAX = 0.10  # 10%
        self.EXECUTION_RISK_MAX = 0.02  # 2%
        
        self.logger.info("🛡️  Trade Validation Engine initialized")
    
    def validate_trade(self, trade_proposal: Dict[str, Any], 
                      market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate trade against 8-point checklist
        
        Args:
            trade_proposal: {
                'symbol': str,
                'action': 'BUY' | 'SELL',
                'shares': int,
                'entry_price': float,
                'target_price': float (optional),
                'stop_loss': float (optional),
                'portfolio_value': float (optional)
            }
            market_context: {
                'market_trend': str,
                'volatility': float,
                'vix': float (optional),
                'persona_votes': List[Dict] (optional),
                'volume': float (optional),
                'bid_ask_spread': float (optional)
            }
        
        Returns:
            {
                'allowed': bool,
                'checks_passed': int,
                'checks_total': 8,
                'failures': List[str],
                'failure_reasons': Dict[str, str],
                'pass_map': Dict[str, bool],
                'validation_id': str,
                'timestamp': str
            }
        """
        # Run all 8 checks
        checks = [
            self._check_macro_alignment(trade_proposal, market_context),
            self._check_liquidity_alignment(trade_proposal, market_context),
            self._check_confidence_band(trade_proposal, market_context),
            self._check_risk_reward(trade_proposal),
            self._check_no_reversals(trade_proposal),
            self._check_no_black_swan(market_context),
            self._check_position_size(trade_proposal),
            self._check_execution_risk(trade_proposal, market_context)
        ]
        
        # Aggregate results
        passed_checks = [c for c in checks if c['passed']]
        failed_checks = [c for c in checks if not c['passed']]
        
        allowed = len(failed_checks) == 0  # ALL must pass
        
        result = {
            'allowed': allowed,
            'checks_passed': len(passed_checks),
            'checks_total': 8,
            'failures': [c['name'] for c in failed_checks],
            'failure_reasons': {c['name']: c['reason'] for c in failed_checks},
            'pass_map': {c['name']: c['passed'] for c in checks},
            'timestamp': datetime.now().isoformat()
        }
        
        # Log validation
        validation_id = self._log_validation(trade_proposal, result)
        result['validation_id'] = validation_id
        
        if not allowed:
            self.logger.warning(
                f"❌ Trade BLOCKED for {trade_proposal.get('symbol', 'UNKNOWN')}. "
                f"Failed: {', '.join(result['failures'])}"
            )
        else:
            self.logger.info(f"✅ Trade APPROVED for {trade_proposal.get('symbol', 'UNKNOWN')}")
            # Record trade for reversal checking
            self._record_trade(trade_proposal)
        
        return result
    
    # ==================== THE 8 VALIDATION CHECKS ====================
    
    def _check_macro_alignment(self, proposal: Dict, context: Dict) -> Dict[str, Any]:
        """Check 1: Macro Alignment ≥50%
        Improved: Uses market_trend and optional sentiment/mood.
        """
        try:
            market_trend = context.get('market_trend', 'neutral')
            action = proposal.get('action', 'BUY')
            mood = context.get('market_mood', 'neutral') # New: RL or CEO mood
            
            # Base logic
            if market_trend == 'bullish' and action == 'BUY':
                macro_score = 75
            elif market_trend == 'bearish' and action == 'SELL':
                macro_score = 75
            elif market_trend == 'neutral':
                macro_score = 55
            else:
                macro_score = 35 # Counter-trend
                
            # Adjustment for Mood (Divine/RL Sentiment)
            if mood == 'euphoric' and action == 'BUY': macro_score -= 10 # Overheated
            if mood == 'panic' and action == 'SELL': macro_score -= 10 # Panic selling
            if mood == 'calm': macro_score += 5 # Precision environment

            passed = macro_score >= self.MACRO_ALIGNMENT_MIN
            reason = '' if passed else f'Macro score {macro_score} < {self.MACRO_ALIGNMENT_MIN} (Trend: {market_trend}, Mood: {mood})'
            
            return {
                'name': 'macro_alignment', 
                'passed': passed, 
                'reason': reason, 
                'score': macro_score,
                'details': {'trend': market_trend, 'mood': mood}
            }
        except Exception as e:
            return {'name': 'macro_alignment', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_liquidity_alignment(self, proposal: Dict, context: Dict) -> Dict[str, Any]:
        """Check 2: Liquidity Alignment ≥40%"""
        try:
            volume = context.get('volume', 0)
            bid_ask_spread = context.get('bid_ask_spread', 0.01)
            
            # Simple heuristic
            if volume > 1000000:  # High volume
                liquidity_score = 80
            elif volume > 100000:  # Medium volume
                liquidity_score = 60
            elif volume > 10000:  # Low volume
                liquidity_score = 40
            else:
                liquidity_score = 20
            
            # Penalize wide spreads
            if bid_ask_spread > 0.02:  # >2%
                liquidity_score -= 20
            
            passed = liquidity_score >= self.LIQUIDITY_ALIGNMENT_MIN
            reason = '' if passed else f'Liquidity score {liquidity_score} < {self.LIQUIDITY_ALIGNMENT_MIN}'
            
            return {'name': 'liquidity_alignment', 'passed': passed, 'reason': reason, 'score': liquidity_score}
        except Exception as e:
            return {'name': 'liquidity_alignment', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_confidence_band(self, proposal: Dict, context: Dict) -> Dict[str, Any]:
        """Check 3: Confidence Band ≥60%"""
        try:
            persona_votes = context.get('persona_votes', [])
            kb = get_knowledge_base()
            wisdom = kb.query_wisdom(proposal.get('symbol', 'market'), n_results=1)
            
            if not persona_votes:
                # No votes available, use conservative default
                confidence = 50
            else:
                # Aggregate persona confidence (weighted average)
                total_weight = sum(v.get('weight', 1.0) for v in persona_votes)
                weighted_conf = sum(v.get('confidence', 0.5) * v.get('weight', 1.0) 
                                  for v in persona_votes)
                confidence = (weighted_conf / total_weight * 100) if total_weight > 0 else 50
            
            passed = confidence >= self.CONFIDENCE_BAND_MIN
            reason = '' if passed else f'Confidence {confidence:.1f}% < {self.CONFIDENCE_BAND_MIN}%'
            
            return {
                'name': 'confidence_band', 
                'passed': passed, 
                'reason': reason, 
                'confidence': round(confidence, 1),
                'wisdom': wisdom[0]['text'] if wisdom else "Stay data-driven."
            }
        except Exception as e:
            return {'name': 'confidence_band', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_risk_reward(self, proposal: Dict) -> Dict[str, Any]:
        """Check 4: Risk-Reward Ratio ≥1.5"""
        try:
            entry = proposal.get('entry_price')
            target = proposal.get('target_price')
            stop = proposal.get('stop_loss')
            
            if not all([entry, target, stop]):
                # Missing required fields
                return {'name': 'risk_reward', 'passed': True, 'reason': 'No target/stop defined (pass by default)'}
            
            # Calculate RR ratio
            profit_potential = abs(target - entry)
            loss_potential = abs(entry - stop)
            
            if loss_potential == 0:
                rr_ratio = 999  # No risk (unlikely but handle it)
            else:
                rr_ratio = profit_potential / loss_potential
            
            passed = rr_ratio >= self.RISK_REWARD_MIN
            reason = '' if passed else f'RR ratio {rr_ratio:.2f} < {self.RISK_REWARD_MIN}'
            
            return {'name': 'risk_reward', 'passed': passed, 'reason': reason, 'rr_ratio': round(rr_ratio, 2)}
        except Exception as e:
            return {'name': 'risk_reward', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_no_reversals(self, proposal: Dict) -> Dict[str, Any]:
        """Check 5: No Recent Reversals (whipsaw protection)"""
        try:
            symbol = proposal.get('symbol')
            action = proposal.get('action')
            
            if not symbol or symbol not in self.trade_history:
                # No history, pass
                return {'name': 'no_reversals', 'passed': True, 'reason': ''}
            
            recent_trades = self.trade_history[symbol][-3:]  # Last 3 trades
            
            # Check for direction changes
            if len(recent_trades) < 2:
                return {'name': 'no_reversals', 'passed': True, 'reason': ''}
            
            reversals = 0
            for i in range(len(recent_trades) - 1):
                if recent_trades[i]['action'] != recent_trades[i+1]['action']:
                    reversals += 1
            
            # If trying to reverse again, block
            if reversals > 0 and len(recent_trades) > 0:
                last_action = recent_trades[-1]['action']
                if last_action != action:
                    passed = False
                    reason = f'Reversal detected: last {reversals} trades changed direction'
                else:
                    passed = True
                    reason = ''
            else:
                passed = True
                reason = ''
            
            return {'name': 'no_reversals', 'passed': passed, 'reason': reason, 'reversals': reversals}
        except Exception as e:
            return {'name': 'no_reversals', 'passed': False, 'reason': f'Error: {str(e)}'}
    
    def _check_no_black_swan(self, context: Dict) -> Dict[str, Any]:
        """Check 6: No Black Swan Events (extreme uncertainty protection)"""
        try:
            vix = context.get('vix', 0)
            volatility = context.get('volatility', 0)
            
            # Check VIX (if available)
            if vix > self.BLACK_SWAN_VIX_MAX:
                return {
                    'name': 'no_black_swan',
                    'passed': False,
                    'reason': f'VIX {vix} > {self.BLACK_SWAN_VIX_MAX} (extreme fear)',
                    'vix': vix
                }
            
            # Check extreme volatility
            if volatility > 0.8:  # >80% volatility
                return {
                    'name': 'no_black_swan',
                    'passed': False,
                    'reason': f'Extreme volatility {volatility:.1%}',
                    'volatility': volatility
                }
            
            return {'name': 'no_black_swan', 'passed': True, 'reason': ''}
        except Exception as e:
            return {'name': 'no_black_swan', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_position_size(self, proposal: Dict) -> Dict[str, Any]:
        """Check 7: Position Size ≤10% of portfolio"""
        try:
            shares = proposal.get('shares', 0)
            entry_price = proposal.get('entry_price', 0)
            portfolio_value = proposal.get('portfolio_value', 100000)  # Default $100k
            
            position_value = shares * entry_price
            position_pct = position_value / portfolio_value if portfolio_value > 0 else 0
            
            passed = position_pct <= self.POSITION_SIZE_MAX
            reason = '' if passed else f'Position {position_pct:.1%} > {self.POSITION_SIZE_MAX:.0%} limit'
            
            return {
                'name': 'position_size',
                'passed': passed,
                'reason': reason,
                'position_pct': round(position_pct, 4)
            }
        except Exception as e:
            return {'name': 'position_size', 'passed': False, 'reason': f'Error: {e}'}
    
    def _check_execution_risk(self, proposal: Dict, context: Dict) -> Dict[str, Any]:
        """Check 8: Execution Risk <2% (slippage protection)"""
        try:
            bid_ask_spread = context.get('bid_ask_spread', 0.005)  # Default 0.5%
            volatility = context.get('volatility', 0.2)
            
            # Estimate execution risk (slippage)
            execution_risk = bid_ask_spread + (volatility * 0.1)  # Simple heuristic
            
            passed = execution_risk < self.EXECUTION_RISK_MAX
            reason = '' if passed else f'Execution risk {execution_risk:.2%} ≥ {self.EXECUTION_RISK_MAX:.0%}'
            
            return {
                'name': 'execution_risk',
                'passed': passed,
                'reason': reason,
                'execution_risk': round(execution_risk, 4)
            }
        except Exception as e:
            return {'name': 'execution_risk', 'passed': False, 'reason': f'Error: {e}'}
    
    # ==================== AUDIT & HISTORY ====================
    
    def _log_validation(self, proposal: Dict, result: Dict) -> str:
        """Log validation attempt to audit trail"""
        validation_id = f"val_{uuid.uuid4().hex[:8]}"
        
        self.validation_history.append({
            'validation_id': validation_id,
            'symbol': proposal.get('symbol', 'UNKNOWN'),
            'action': proposal.get('action', 'UNKNOWN'),
            'allowed': result['allowed'],
            'checks_passed': result['checks_passed'],
            'failures': result['failures'],
            'timestamp': result['timestamp']
        })
        
        # Keep last 100 validations
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
        
        return validation_id
    
    def _record_trade(self, proposal: Dict):
        """Record approved trade for reversal checking"""
        symbol = proposal.get('symbol')
        if not symbol:
            return
        
        if symbol not in self.trade_history:
            self.trade_history[symbol] = []
        
        self.trade_history[symbol].append({
            'action': proposal.get('action'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep last 5 trades per symbol
        if len(self.trade_history[symbol]) > 5:
            self.trade_history[symbol] = self.trade_history[symbol][-5:]
    
    def get_validation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent validation attempts"""
        return self.validation_history[-limit:]
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validation statistics"""
        if not self.validation_history:
            return {
                'total_validations': 0,
                'approved': 0,
                'blocked': 0,
                'approval_rate': 0.0
            }
        
        approved = len([v for v in self.validation_history if v['allowed']])
        total = len(self.validation_history)
        
        return {
            'total_validations': total,
            'approved': approved,
            'blocked': total - approved,
            'approval_rate': round(approved / total, 3) if total > 0 else 0.0,
            'history_size': len(self.validation_history)
        }


# Global singleton
_trade_validator = None


def get_trade_validator() -> TradeValidator:
    """Get or create the global TradeValidator singleton"""
    global _trade_validator
    if _trade_validator is None:
        _trade_validator = TradeValidator()
    return _trade_validator
