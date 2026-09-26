"""
Position Sizing for Yantra X.

Connects the Institutional Strategy Engine's sizing logic to the canonical pipeline.
Supports multiple sizing methodologies with risk-adjusted outputs.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import math

# Try to import numpy, provide fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    class _NumpyFallback:
        @staticmethod
        def sqrt(x):
            return math.sqrt(x)
    np = _NumpyFallback()

from backend.core.decision_context import (
    DecisionContext, TradingAction, PortfolioState, RiskState, ExecutionConstraints
)
from backend.services.institutional_strategy_engine import InstitutionalStrategyEngine

logger = logging.getLogger(__name__)


class SizingMethod(Enum):
    """Position sizing methodologies."""
    FIXED_FRACTIONAL = "fixed_fractional"      # Fixed % of portfolio
    KELLY_CRITERION = "kelly_criterion"        # Kelly optimal sizing
    VOLATILITY_TARGETING = "volatility_targeting"  # Target portfolio vol
    RISK_PARITY = "risk_parity"                # Equal risk contribution
    CONFIDENCE_WEIGHTED = "confidence_weighted"    # Size by signal confidence
    STRATEGY_ENGINE = "strategy_engine"        # Use Strategy Engine's calculation


@dataclass
class SizingResult:
    """Result of position sizing calculation."""
    position_size: float          # Dollar amount
    quantity: float              # Number of shares/contracts
    stop_loss: float
    take_profit: float
    risk_amount: float           # Dollar risk (position * (entry - stop))
    risk_pct_portfolio: float    # Risk as % of portfolio
    method: SizingMethod
    confidence_adjustment: float
    volatility_adjustment: float
    portfolio_heat: float        # Total portfolio risk after this position
    details: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "position_size": self.position_size,
            "quantity": self.quantity,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_amount": self.risk_amount,
            "risk_pct_portfolio": self.risk_pct_portfolio,
            "method": self.method.value,
            "confidence_adjustment": self.confidence_adjustment,
            "volatility_adjustment": self.volatility_adjustment,
            "portfolio_heat": self.portfolio_heat,
            "details": self.details,
        }


class PositionSizer:
    """
    Calculates position size using multiple methodologies.
    
    Primary: Uses InstitutionalStrategyEngine's calculation as baseline
    Fallback: Multiple alternative methods
    """
    
    def __init__(
        self,
        strategy_engine: Optional[InstitutionalStrategyEngine] = None,
        default_method: SizingMethod = SizingMethod.STRATEGY_ENGINE
    ):
        self.strategy_engine = strategy_engine
        self.default_method = default_method
        
        # Sizing parameters
        self.max_position_risk = 0.02      # 2% max risk per trade
        self.max_portfolio_risk = 0.20     # 20% max total portfolio risk
        self.kelly_fraction = 0.25         # Fractional Kelly (25%)
        self.target_portfolio_vol = 0.15   # 15% target portfolio volatility
    
    def calculate(
        self,
        ctx: DecisionContext,
        method: Optional[SizingMethod] = None
    ) -> SizingResult:
        """
        Calculate position size for the decision context.
        
        Uses candidate strategy's SL/TP as anchors, adjusts size based on method.
        """
        method = method or self.default_method
        
        if not ctx.candidate_strategy:
            return self._empty_result("No candidate strategy")
        
        if ctx.candidate_strategy.action == TradingAction.HOLD:
            return self._empty_result("HOLD action")
        
        if not ctx.market_snapshot or not ctx.portfolio_state:
            return self._empty_result("Missing market or portfolio data")
        
        # Extract key parameters
        entry_price = ctx.market_snapshot.price
        stop_loss = ctx.candidate_strategy.stop_loss
        take_profit = ctx.candidate_strategy.take_profit
        confidence = ctx.candidate_strategy.confidence
        volatility = ctx.market_snapshot.volatility or 0.02
        portfolio_value = ctx.portfolio_state.total_value
        
        if portfolio_value <= 0 or entry_price <= 0:
            return self._empty_result("Invalid portfolio or price")
        
        # Validate SL/TP
        if stop_loss <= 0 or take_profit <= 0:
            # Generate default SL/TP if missing
            stop_loss, take_profit = self._generate_default_exits(
                entry_price, volatility, ctx.candidate_strategy.action
            )
        
        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss)
        if risk_per_share <= 0:
            return self._empty_result("Invalid stop loss")
        
        # Dispatch to sizing method
        if method == SizingMethod.STRATEGY_ENGINE and self.strategy_engine:
            return self._size_strategy_engine(ctx, entry_price, stop_loss, take_profit, risk_per_share)
        elif method == SizingMethod.FIXED_FRACTIONAL:
            return self._size_fixed_fractional(ctx, entry_price, stop_loss, take_profit, risk_per_share)
        elif method == SizingMethod.KELLY_CRITERION:
            return self._size_kelly(ctx, entry_price, stop_loss, take_profit, risk_per_share, confidence)
        elif method == SizingMethod.VOLATILITY_TARGETING:
            return self._size_volatility_targeting(ctx, entry_price, stop_loss, take_profit, risk_per_share)
        elif method == SizingMethod.CONFIDENCE_WEIGHTED:
            return self._size_confidence_weighted(ctx, entry_price, stop_loss, take_profit, risk_per_share)
        else:
            return self._size_fixed_fractional(ctx, entry_price, stop_loss, take_profit, risk_per_share)
    
    def _size_strategy_engine(
        self,
        ctx: DecisionContext,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_per_share: float
    ) -> SizingResult:
        """Use InstitutionalStrategyEngine's position sizing."""
        try:
            portfolio_state = {
                'total_value': ctx.portfolio_state.total_value,
                'positions': ctx.portfolio_state.positions,
            } if ctx.portfolio_state else None
            
            risk_assessment = {
                'volatility': ctx.market_snapshot.volatility,
                'overall_risk': ctx.candidate_strategy.risk_score,
            }
            
            position_value = self.strategy_engine._calculate_position_size(
                action=ctx.candidate_strategy.action.value,
                confidence=ctx.candidate_strategy.confidence,
                risk_assessment=risk_assessment,
                portfolio_state=portfolio_state
            )
            
            quantity = position_value / entry_price if entry_price > 0 else 0
            risk_amount = quantity * risk_per_share
            risk_pct = risk_amount / ctx.portfolio_state.total_value if ctx.portfolio_state.total_value > 0 else 0
            
            return SizingResult(
                position_size=position_value,
                quantity=quantity,
                stop_loss=stop_loss,
                take_profit=take_profit,
                risk_amount=risk_amount,
                risk_pct_portfolio=risk_pct,
                method=SizingMethod.STRATEGY_ENGINE,
                confidence_adjustment=ctx.candidate_strategy.confidence,
                volatility_adjustment=1.0 / (1.0 + ctx.market_snapshot.volatility * 10),
                portfolio_heat=self._calculate_portfolio_heat(ctx, risk_amount),
                details={"engine": "InstitutionalStrategyEngine"},
            )
        except Exception as e:
            logger.warning(f"Strategy Engine sizing failed: {e}, falling back")
            return self._size_fixed_fractional(ctx, entry_price, stop_loss, take_profit, risk_per_share)
    
    def _size_fixed_fractional(
        self,
        ctx: DecisionContext,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_per_share: float
    ) -> SizingResult:
        """Fixed fractional position sizing (classic 2% risk per trade)."""
        portfolio_value = ctx.portfolio_state.total_value
        
        # Base risk amount
        risk_amount = portfolio_value * self.max_position_risk
        
        # Adjust by confidence
        confidence_adj = ctx.candidate_strategy.confidence / 0.8  # Normalize to 80% baseline
        risk_amount *= confidence_adj
        
        # Adjust by volatility
        vol_adj = 1.0 / (1.0 + (ctx.market_snapshot.volatility or 0.02) * 10)
        risk_amount *= vol_adj
        
        # Calculate quantity
        quantity = risk_amount / risk_per_share if risk_per_share > 0 else 0
        position_value = quantity * entry_price
        risk_pct = risk_amount / portfolio_value
        
        return SizingResult(
            position_size=position_value,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount,
            risk_pct_portfolio=risk_pct,
            method=SizingMethod.FIXED_FRACTIONAL,
            confidence_adjustment=confidence_adj,
            volatility_adjustment=vol_adj,
            portfolio_heat=self._calculate_portfolio_heat(ctx, risk_amount),
            details={"base_risk_pct": self.max_position_risk},
        )
    
    def _size_kelly(
        self,
        ctx: DecisionContext,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_per_share: float,
        confidence: float
    ) -> SizingResult:
        """Kelly Criterion sizing (fractional)."""
        portfolio_value = ctx.portfolio_state.total_value
        
        # Estimate win probability from confidence
        win_prob = confidence
        lose_prob = 1 - win_prob
        
        # Win/loss ratio from SL/TP
        reward_per_share = abs(take_profit - entry_price)
        win_loss_ratio = reward_per_share / risk_per_share if risk_per_share > 0 else 1
        
        # Kelly fraction: f* = (p * b - q) / b = p - q/b
        kelly_f = win_prob - (lose_prob / win_loss_ratio) if win_loss_ratio > 0 else 0
        kelly_f = max(0, kelly_f)  # No negative sizing
        
        # Apply fractional Kelly
        fractional_kelly = kelly_f * self.kelly_fraction
        
        # Cap at max position risk
        risk_fraction = min(fractional_kelly, self.max_position_risk)
        risk_amount = portfolio_value * risk_fraction
        
        quantity = risk_amount / risk_per_share if risk_per_share > 0 else 0
        position_value = quantity * entry_price
        risk_pct = risk_amount / portfolio_value
        
        return SizingResult(
            position_size=position_value,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount,
            risk_pct_portfolio=risk_pct,
            method=SizingMethod.KELLY_CRITERION,
            confidence_adjustment=confidence,
            volatility_adjustment=1.0,
            portfolio_heat=self._calculate_portfolio_heat(ctx, risk_amount),
            details={
                "kelly_fraction": kelly_f,
                "fractional_kelly": fractional_kelly,
                "win_prob": win_prob,
                "win_loss_ratio": win_loss_ratio,
            },
        )
    
    def _size_volatility_targeting(
        self,
        ctx: DecisionContext,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_per_share: float
    ) -> SizingResult:
        """Volatility targeting - size to achieve target portfolio volatility."""
        portfolio_value = ctx.portfolio_state.total_value
        asset_vol = ctx.market_snapshot.volatility or 0.02
        
        # Target position volatility contribution
        # position_vol = position_pct * asset_vol
        # We want position_vol = target_portfolio_vol / sqrt(n_positions)
        n_positions = max(1, len(ctx.portfolio_state.positions) + 1)
        target_position_vol = self.target_portfolio_vol / np.sqrt(n_positions)
        
        position_pct = target_position_vol / asset_vol if asset_vol > 0 else 0
        position_pct = min(position_pct, self.max_position_risk * 5)  # Cap
        
        position_value = portfolio_value * position_pct
        quantity = position_value / entry_price if entry_price > 0 else 0
        risk_amount = quantity * risk_per_share
        risk_pct = risk_amount / portfolio_value
        
        return SizingResult(
            position_size=position_value,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount,
            risk_pct_portfolio=risk_pct,
            method=SizingMethod.VOLATILITY_TARGETING,
            confidence_adjustment=1.0,
            volatility_adjustment=target_position_vol / asset_vol if asset_vol > 0 else 1.0,
            portfolio_heat=self._calculate_portfolio_heat(ctx, risk_amount),
            details={
                "target_portfolio_vol": self.target_portfolio_vol,
                "asset_vol": asset_vol,
                "target_position_vol": target_position_vol,
                "n_positions": n_positions,
            },
        )
    
    def _size_confidence_weighted(
        self,
        ctx: DecisionContext,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        risk_per_share: float
    ) -> SizingResult:
        """Size purely by signal confidence (for comparison)."""
        portfolio_value = ctx.portfolio_state.total_value
        confidence = ctx.candidate_strategy.confidence
        
        # Linear scaling from 0.5 to 1.0 confidence
        base_risk = self.max_position_risk * 0.5  # 1% base
        confidence_risk = base_risk * (confidence - 0.5) * 2  # 0-1% additional
        risk_fraction = base_risk + confidence_risk
        risk_fraction = min(risk_fraction, self.max_position_risk)
        
        risk_amount = portfolio_value * risk_fraction
        quantity = risk_amount / risk_per_share if risk_per_share > 0 else 0
        position_value = quantity * entry_price
        risk_pct = risk_amount / portfolio_value
        
        return SizingResult(
            position_size=position_value,
            quantity=quantity,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk_amount=risk_amount,
            risk_pct_portfolio=risk_pct,
            method=SizingMethod.CONFIDENCE_WEIGHTED,
            confidence_adjustment=confidence,
            volatility_adjustment=1.0,
            portfolio_heat=self._calculate_portfolio_heat(ctx, risk_amount),
            details={"risk_fraction": risk_fraction},
        )
    
    def _generate_default_exits(
        self,
        entry_price: float,
        volatility: float,
        action: TradingAction
    ) -> tuple:
        """Generate default stop loss and take profit if missing."""
        if action == TradingAction.BUY:
            stop_loss = entry_price * (1 - volatility * 2)
            take_profit = entry_price * (1 + volatility * 6)  # 3:1 reward/risk
        else:  # SELL
            stop_loss = entry_price * (1 + volatility * 2)
            take_profit = entry_price * (1 - volatility * 6)
        
        return stop_loss, take_profit
    
    def _calculate_portfolio_heat(self, ctx: DecisionContext, new_risk_amount: float) -> float:
        """Calculate total portfolio risk after adding this position."""
        if not ctx.portfolio_state:
            return 0.0
        
        # Sum existing position risks (simplified)
        existing_risk = 0.0
        for pos in ctx.portfolio_state.positions:
            # Estimate: position_value * avg_volatility * 2.33
            pos_value = pos.get('quantity', 0) * pos.get('avg_price', 0)
            existing_risk += pos_value * 0.02 * 2.33  # Assume 2% vol
        
        total_risk = existing_risk + new_risk_amount
        portfolio_value = ctx.portfolio_state.total_value
        
        return total_risk / portfolio_value if portfolio_value > 0 else 0.0
    
    def _empty_result(self, reason: str) -> SizingResult:
        """Return empty sizing result."""
        return SizingResult(
            position_size=0.0,
            quantity=0.0,
            stop_loss=0.0,
            take_profit=0.0,
            risk_amount=0.0,
            risk_pct_portfolio=0.0,
            method=self.default_method,
            confidence_adjustment=0.0,
            volatility_adjustment=0.0,
            portfolio_heat=0.0,
            details={"reason": reason},
        )


def calculate_position_size(
    ctx: DecisionContext,
    strategy_engine: Optional[InstitutionalStrategyEngine] = None
) -> SizingResult:
    """Convenience function for position sizing."""
    sizer = PositionSizer(strategy_engine=strategy_engine)
    return sizer.calculate(ctx)