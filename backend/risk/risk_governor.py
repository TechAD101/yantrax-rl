"""
Risk Governor for Yantra X.

Orchestrates existing risk components into a coherent governance pipeline.
Does not duplicate logic - orchestrates TradeValidator, EmotionalSafeguards, and portfolio-level checks.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import logging

from backend.core.decision_context import (
    DecisionContext, GovernanceState, TradingAction, PortfolioState, RiskState
)
from backend.services.trade_validator import get_trade_validator
from backend.services.emotional_safeguards import get_emotional_safeguards

logger = logging.getLogger(__name__)


class RiskGate(Enum):
    """Individual risk gates in the pipeline."""
    TRADE_VALIDATION = "trade_validation"
    EMOTIONAL_SAFEGUARDS = "emotional_safeguards"
    POSITION_LIMITS = "position_limits"
    CONCENTRATION = "concentration"
    CORRELATION = "correlation"
    PORTFOLIO_RISK = "portfolio_risk"
    LIQUIDITY = "liquidity"
    EXECUTION_RISK = "execution_risk"
    STRESS_TEST = "stress_test"
    TAIL_RISK = "tail_risk"


@dataclass
class RiskGateResult:
    """Result of a single risk gate."""
    gate: RiskGate
    passed: bool
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    severity: str = "error"  # "error" | "warning" | "info"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate": self.gate.value,
            "passed": self.passed,
            "reason": self.reason,
            "details": self.details,
            "severity": self.severity,
        }


@dataclass
class RiskGovernanceResult:
    """Complete risk governance outcome."""
    overall: GovernanceState
    gates: List[RiskGateResult]
    blocked_by: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": self.overall.value,
            "gates": [g.to_dict() for g in self.gates],
            "blocked_by": self.blocked_by,
            "warnings": self.warnings,
        }
    
    def is_blocked(self) -> bool:
        return self.overall in (GovernanceState.BLOCK, GovernanceState.VETO)
    
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


class RiskGovernor:
    """
    Orchestrates risk checks in a pipeline.
    
    Key principle: Sizing affects risk, so we run:
    1. Preliminary constraints (before sizing)
    2. Sizing
    3. Final validation (after sizing)
    """
    
    def __init__(self):
        self.trade_validator = get_trade_validator()
        self.emotional_safeguards = get_emotional_safeguards()
        
        # Risk thresholds
        self.max_position_pct = 0.10  # 10% per position
        self.max_portfolio_risk = 0.20  # 20% total portfolio risk
        self.max_concentration_pct = 0.25  # 25% in single asset
        self.max_correlation = 0.70  # Max correlation between positions
        self.max_sector_exposure = 0.40  # 40% in single sector
    
    def evaluate_preliminary(self, ctx: DecisionContext) -> RiskGovernanceResult:
        """
        Run risk checks that MUST pass BEFORE position sizing.
        These are structural/regulatory checks.
        """
        gates = []
        
        # Gate 1: Trade Validation (8-point checklist)
        if ctx.candidate_strategy and ctx.candidate_strategy.action != TradingAction.HOLD:
            val_result = self._run_trade_validation(ctx)
            gates.append(RiskGateResult(
                gate=RiskGate.TRADE_VALIDATION,
                passed=val_result.get('allowed', False),
                reason="; ".join(val_result.get('failures', [])) if not val_result.get('allowed') else "",
                details=val_result,
            ))
        else:
            gates.append(RiskGateResult(
                gate=RiskGate.TRADE_VALIDATION,
                passed=True,
                reason="HOLD action - validation skipped",
                severity="info",
            ))
        
        # Gate 2: Emotional Safeguards
        safeguard_result = self.emotional_safeguards.is_trading_allowed()
        gates.append(RiskGateResult(
            gate=RiskGate.EMOTIONAL_SAFEGUARDS,
            passed=safeguard_result.get('allowed', False),
            reason=safeguard_result.get('reason', ''),
            details=safeguard_result,
            severity="error" if not safeguard_result.get('allowed') else "info",
        ))
        
        # Gate 3: Position Limits (preliminary - using candidate size if available)
        pos_check = self._check_position_limits_preliminary(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.POSITION_LIMITS,
            passed=pos_check[0],
            reason=pos_check[1],
            details=pos_check[2],
        ))
        
        # Gate 4: Liquidity Check
        liq_check = self._check_liquidity(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.LIQUIDITY,
            passed=liq_check[0],
            reason=liq_check[1],
            details=liq_check[2],
        ))
        
        # Determine overall
        overall = self._determine_overall(gates)
        
        return RiskGovernanceResult(
            overall=overall,
            gates=gates,
            blocked_by=[g.gate.value for g in gates if not g.passed and g.severity == "error"],
            warnings=[g.reason for g in gates if not g.passed and g.severity == "warning"],
        )
    
    def evaluate_final(self, ctx: DecisionContext) -> RiskGovernanceResult:
        """
        Run risk checks AFTER position sizing.
        These use the final calculated position size.
        """
        gates = []
        
        # Gate 1: Position Limits (final - with actual calculated size)
        pos_check = self._check_position_limits_final(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.POSITION_LIMITS,
            passed=pos_check[0],
            reason=pos_check[1],
            details=pos_check[2],
        ))
        
        # Gate 2: Concentration Risk
        conc_check = self._check_concentration(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.CONCENTRATION,
            passed=conc_check[0],
            reason=conc_check[1],
            details=conc_check[2],
        ))
        
        # Gate 3: Correlation Risk
        corr_check = self._check_correlation(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.CORRELATION,
            passed=corr_check[0],
            reason=corr_check[1],
            details=corr_check[2],
        ))
        
        # Gate 4: Portfolio Risk / VaR
        port_check = self._check_portfolio_risk(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.PORTFOLIO_RISK,
            passed=port_check[0],
            reason=port_check[1],
            details=port_check[2],
        ))
        
        # Gate 5: Execution Risk
        exec_check = self._check_execution_risk(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.EXECUTION_RISK,
            passed=exec_check[0],
            reason=exec_check[1],
            details=exec_check[2],
        ))
        
        # Gate 6: Stress Test (if we have the data)
        stress_check = self._check_stress_test(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.STRESS_TEST,
            passed=stress_check[0],
            reason=stress_check[1],
            details=stress_check[2],
            severity="warning",
        ))
        
        # Gate 7: Tail Risk
        tail_check = self._check_tail_risk(ctx)
        gates.append(RiskGateResult(
            gate=RiskGate.TAIL_RISK,
            passed=tail_check[0],
            reason=tail_check[1],
            details=tail_check[2],
            severity="warning",
        ))
        
        overall = self._determine_overall(gates)
        
        return RiskGovernanceResult(
            overall=overall,
            gates=gates,
            blocked_by=[g.gate.value for g in gates if not g.passed and g.severity == "error"],
            warnings=[g.reason for g in gates if not g.passed and g.severity == "warning"],
        )
    
    def evaluate_all(self, ctx: DecisionContext) -> RiskGovernanceResult:
        """Run complete risk pipeline (preliminary + final)."""
        prelim = self.evaluate_preliminary(ctx)
        
        # If preliminary blocks, don't continue
        if prelim.is_blocked():
            return prelim
        
        # Run final checks
        final = self.evaluate_final(ctx)
        
        # Combine results
        all_gates = prelim.gates + final.gates
        overall = self._determine_overall(all_gates)
        
        return RiskGovernanceResult(
            overall=overall,
            gates=all_gates,
            blocked_by=prelim.blocked_by + final.blocked_by,
            warnings=prelim.warnings + final.warnings,
        )
    
    # ──────────────────────────────────────────────────────────────
    # Individual Gate Checks
    # ──────────────────────────────────────────────────────────────
    
    def _run_trade_validation(self, ctx: DecisionContext) -> Dict[str, Any]:
        """Run the 8-point TradeValidator checklist."""
        if not self.trade_validator or not ctx.candidate_strategy:
            return {'allowed': True, 'failures': [], 'checks_passed': 0}
        
        # Build trade proposal from candidate strategy
        proposal = {
            'symbol': ctx.symbol,
            'action': ctx.candidate_strategy.action.value,
            'shares': max(1, int(ctx.candidate_strategy.position_size / max(ctx.market_snapshot.price, 1))) if ctx.market_snapshot else 1,
            'entry_price': ctx.market_snapshot.price if ctx.market_snapshot else 100,
            'target_price': ctx.candidate_strategy.take_profit,
            'stop_loss': ctx.candidate_strategy.stop_loss,
            'portfolio_value': ctx.portfolio_state.total_value if ctx.portfolio_state else 100000,
        }
        
        # Build market context
        market_context = {
            'market_trend': ctx.market_snapshot.trend if ctx.market_snapshot else 'neutral',
            'volatility': ctx.market_snapshot.volatility if ctx.market_snapshot else 0.02,
            'vix': ctx.market_snapshot.vix,
            'persona_votes': [v.to_dict() for v in ctx.voting_result.votes] if ctx.voting_result else [],
            'volume': ctx.market_snapshot.volume if ctx.market_snapshot else 1000000,
            'bid_ask_spread': ctx.market_snapshot.bid_ask_spread or 0.005,
            'market_mood': ctx.risk_state.emotional_state if ctx.risk_state else 'calm',
        }
        
        try:
            return self.trade_validator.validate_trade(proposal, market_context)
        except Exception as e:
            logger.error(f"Trade validation error: {e}")
            return {'allowed': False, 'failures': [f'validation_error: {e}']}
    
    def _check_position_limits_preliminary(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Preliminary position limit check using candidate size estimate."""
        if not ctx.candidate_strategy or not ctx.portfolio_state:
            return True, "No candidate or portfolio state", {}
        
        portfolio_value = ctx.portfolio_state.total_value
        if portfolio_value <= 0:
            return False, "Invalid portfolio value", {}
        
        # Estimate position value from candidate
        position_value = ctx.candidate_strategy.position_size
        position_pct = position_value / portfolio_value
        
        if position_pct > self.max_position_pct:
            return False, f"Position {position_pct:.1%} exceeds {self.max_position_pct:.0%} limit", {
                "position_pct": position_pct,
                "limit": self.max_position_pct,
            }
        
        return True, f"Position {position_pct:.1%} within limits", {
            "position_pct": position_pct,
            "limit": self.max_position_pct,
        }
    
    def _check_position_limits_final(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Final position limit check using calculated final size."""
        if not ctx.final_position_size or not ctx.portfolio_state or not ctx.market_snapshot:
            return True, "Insufficient data for final check", {}
        
        portfolio_value = ctx.portfolio_state.total_value
        if portfolio_value <= 0:
            return False, "Invalid portfolio value", {}
        
        position_value = ctx.final_position_size * ctx.market_snapshot.price
        position_pct = position_value / portfolio_value
        
        if position_pct > self.max_position_pct:
            return False, f"Final position {position_pct:.1%} exceeds {self.max_position_pct:.0%} limit", {
                "position_pct": position_pct,
                "limit": self.max_position_pct,
                "position_value": position_value,
            }
        
        return True, f"Final position {position_pct:.1%} within limits", {
            "position_pct": position_pct,
            "limit": self.max_position_pct,
        }
    
    def _check_concentration(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check portfolio concentration risk."""
        if not ctx.portfolio_state or not ctx.market_snapshot:
            return True, "Insufficient portfolio data", {}
        
        portfolio_value = ctx.portfolio_state.total_value
        if portfolio_value <= 0:
            return True, "No portfolio value", {}
        
        # Calculate existing position in this symbol
        existing_qty = 0
        for pos in ctx.portfolio_state.positions:
            if pos.get('symbol', '').upper() == ctx.symbol.upper():
                existing_qty = pos.get('quantity', 0)
                break
        
        # Add proposed position
        proposed_qty = ctx.final_position_size if ctx.final_position_size else 0
        total_qty = existing_qty + proposed_qty
        
        if total_qty <= 0:
            return True, "No position", {}
        
        position_value = total_qty * ctx.market_snapshot.price
        concentration_pct = position_value / portfolio_value
        
        if concentration_pct > self.max_concentration_pct:
            return False, f"Concentration {concentration_pct:.1%} exceeds {self.max_concentration_pct:.0%}", {
                "concentration_pct": concentration_pct,
                "limit": self.max_concentration_pct,
                "symbol": ctx.symbol,
            }
        
        return True, f"Concentration {concentration_pct:.1%} within limits", {
            "concentration_pct": concentration_pct,
        }
    
    def _check_correlation(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check correlation risk with existing positions."""
        # Simplified: check if adding this position would create high correlation
        # In production, would use actual correlation matrix
        if not ctx.portfolio_state or len(ctx.portfolio_state.positions) < 2:
            return True, "Insufficient positions for correlation check", {}
        
        # For now, return warning-level check
        # Real implementation would compute correlation with existing positions
        return True, "Correlation check passed (simplified)", {
            "note": "Full correlation matrix not implemented",
            "severity": "warning",
        }
    
    def _check_portfolio_risk(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check portfolio-level risk (VaR approximation)."""
        if not ctx.portfolio_state:
            return True, "No portfolio state", {}
        
        # Simplified VaR: position * volatility * 2.33 (99% VaR)
        if ctx.final_position_size and ctx.market_snapshot:
            position_value = ctx.final_position_size * ctx.market_snapshot.price
            volatility = ctx.market_snapshot.volatility
            var_99 = position_value * volatility * 2.33
            portfolio_value = ctx.portfolio_state.total_value
            var_pct = var_99 / portfolio_value if portfolio_value > 0 else 0
            
            if var_pct > self.max_portfolio_risk:
                return False, f"Portfolio VaR {var_pct:.1%} exceeds {self.max_portfolio_risk:.0%}", {
                    "var_pct": var_pct,
                    "limit": self.max_portfolio_risk,
                }
            
            return True, f"Portfolio VaR {var_pct:.1%} within limits", {
                "var_pct": var_pct,
                "limit": self.max_portfolio_risk,
            }
        
        return True, "Insufficient data for VaR", {}
    
    def _check_liquidity(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check liquidity for execution."""
        if not ctx.market_snapshot:
            return True, "No market snapshot", {}
        
        volume = ctx.market_snapshot.volume or 0
        min_liquidity = ctx.execution_constraints.min_liquidity
        
        if volume < min_liquidity:
            return False, f"Volume {volume:,.0f} below minimum {min_liquidity:,.0f}", {
                "volume": volume,
                "min_liquidity": min_liquidity,
            }
        
        spread = ctx.market_snapshot.bid_ask_spread or 0
        max_spread = ctx.execution_constraints.max_bid_ask_spread
        
        if spread > max_spread:
            return False, f"Spread {spread:.2%} exceeds {max_spread:.0%}", {
                "spread": spread,
                "max_spread": max_spread,
            }
        
        return True, f"Liquidity adequate: volume {volume:,.0f}, spread {spread:.2%}", {
            "volume": volume,
            "spread": spread,
        }
    
    def _check_execution_risk(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check execution risk (slippage + commission)."""
        if not ctx.market_snapshot or not ctx.final_position_size:
            return True, "Insufficient data", {}
        
        spread = ctx.market_snapshot.bid_ask_spread or 0.005
        volatility = ctx.market_snapshot.volatility or 0.02
        
        # Estimate slippage: spread/2 + volatility * position_impact
        position_value = ctx.final_position_size * ctx.market_snapshot.price
        portfolio_value = ctx.portfolio_state.total_value if ctx.portfolio_state else 100000
        position_pct = position_value / portfolio_value if portfolio_value > 0 else 0
        
        # Market impact estimate
        impact = position_pct * 0.1  # 10% of position size as impact
        est_slippage = (spread / 2) + (volatility * impact)
        
        max_slippage = ctx.execution_constraints.max_slippage_pct
        
        if est_slippage > max_slippage:
            return False, f"Estimated slippage {est_slippage:.2%} exceeds {max_slippage:.0%}", {
                "est_slippage": est_slippage,
                "max_slippage": max_slippage,
            }
        
        return True, f"Execution risk acceptable: est. slippage {est_slippage:.2%}", {
            "est_slippage": est_slippage,
            "max_slippage": max_slippage,
        }
    
    def _check_stress_test(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Stress test the position under adverse scenarios."""
        if not ctx.market_snapshot or not ctx.final_position_size or not ctx.portfolio_state:
            return True, "Insufficient data for stress test", {}
        
        position_value = ctx.final_position_size * ctx.market_snapshot.price
        portfolio_value = ctx.portfolio_state.total_value
        
        # Stress scenarios
        scenarios = {
            "market_crash_20pct": -0.20,
            "volatility_spike_3x": ctx.market_snapshot.volatility * 3,
            "liquidity_dry_up": 0.05,  # 5% slippage
        }
        
        worst_case_loss = 0
        for name, shock in scenarios.items():
            if name == "market_crash_20pct":
                loss = position_value * abs(shock)
            elif name == "volatility_spike_3x":
                loss = position_value * shock * 2.33  # VaR at 3x vol
            else:
                loss = position_value * shock
            worst_case_loss = max(worst_case_loss, loss)
        
        worst_case_pct = worst_case_loss / portfolio_value if portfolio_value > 0 else 0
        
        # Warning only - don't block on stress test
        details = {
            "worst_case_pct": worst_case_pct,
            "scenarios": scenarios,
            "severity": "warning" if worst_case_pct > 0.10 else "info",
        }
        
        if worst_case_pct > 0.10:  # >10% portfolio loss in stress
            return True, f"Stress test warning: worst case {worst_case_pct:.1%} portfolio loss", details
        
        return True, f"Stress test passed: worst case {worst_case_pct:.1%}", details
    
    def _check_tail_risk(self, ctx: DecisionContext) -> Tuple[bool, str, Dict]:
        """Check for tail risk (black swan conditions)."""
        if not ctx.market_snapshot:
            return True, "No market data", {}
        
        vix = ctx.market_snapshot.vix or 20
        volatility = ctx.market_snapshot.volatility
        
        # Extreme conditions
        is_extreme = vix > 40 or volatility > 0.5
        details = {
            "vix": vix,
            "volatility": volatility,
            "severity": "warning" if is_extreme else "info",
        }
        
        if is_extreme:
            return True, f"Tail risk warning: VIX {vix}, vol {volatility:.1%}", details
        
        return True, "Tail risk within normal bounds", details
    
    def _determine_overall(self, gates: List[RiskGateResult]) -> GovernanceState:
        """Determine overall governance state from gate results."""
        # Any error-severity failure = BLOCK
        for gate in gates:
            if not gate.passed and gate.severity == "error":
                return GovernanceState.BLOCK
        
        # Any VETO from emotional safeguards = VETO
        for gate in gates:
            if gate.gate == RiskGate.EMOTIONAL_SAFEGUARDS and not gate.passed:
                if gate.details.get('emotional_state') == 'mouna':
                    return GovernanceState.VETO
                return GovernanceState.BLOCK
        
        # Warning-severity failures = WARNING
        for gate in gates:
            if not gate.passed and gate.severity == "warning":
                return GovernanceState.WARNING
        
        return GovernanceState.APPROVE