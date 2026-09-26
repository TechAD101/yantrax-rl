"""
Attribution Engine for Yantra X.

Decomposes realized P&L into attributable components across the decision lifecycle.
Preserves data lineage from decision_id through outcome.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class AttributionComponent(Enum):
    """Components that can receive attribution."""
    MARKET_BETA = "market_beta"           # Market movement contribution
    STRATEGY_ALPHA = "strategy_alpha"     # Strategy-specific edge
    REGIME_TIMING = "regime_timing"       # Regime detection accuracy
    TECHNICAL_SIGNAL = "technical_signal" # Technical analysis contribution
    FUNDAMENTAL_SIGNAL = "fundamental_signal"  # Fundamental analysis contribution
    SENTIMENT_SIGNAL = "sentiment_signal" # Sentiment analysis contribution
    AGENT_CONSENSUS = "agent_consensus"   # Agent voting contribution
    CEO_INTERVENTION = "ceo_intervention" # CEO override/adjustment
    RISK_GATES = "risk_gates"             # Risk gate effects (block/size adjustment)
    EXECUTION_COST = "execution_cost"     # Slippage, commission, spread
    RESIDUAL = "residual"                 # Unexplained variance


class AttributionMethod(Enum):
    """Attribution methodology."""
    BRINSON_HOOD_BEEBOWER = "brinson_hood_beebower"  # Classic equity attribution
    MULTIFACTOR_REGRESSION = "multifactor_regression"  # Factor model attribution
    SHAPLEY_VALUE = "shapley_value"  # Game-theoretic fair attribution
    SIMPLE_DECOMPOSITION = "simple_decomposition"  # Direct component subtraction


@dataclass
class AttributionResult:
    """Single attribution component result."""
    component: AttributionComponent
    value: float  # P&L contribution in base currency
    percentage: float  # Percentage of total P&L
    confidence: float  # Confidence in this attribution (0-1)
    method: AttributionMethod
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutcomeRecord:
    """Complete outcome record linking back to originating decision."""
    outcome_id: str
    decision_id: str
    order_id: str
    fill_id: Optional[str]
    
    # Trade details
    symbol: str
    action: str  # BUY/SELL
    requested_size: float
    filled_size: float
    requested_price: float
    filled_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    
    # Timing
    decision_timestamp: datetime
    order_timestamp: datetime
    fill_timestamp: datetime
    close_timestamp: Optional[datetime]
    
    # P&L
    gross_pnl: float
    net_pnl: float
    commission: float
    slippage: float
    spread_cost: float
    
    # Market context at decision
    market_price_at_decision: float
    market_regime_at_decision: str
    volatility_at_decision: float
    
    # Market context at close
    market_price_at_close: float
    market_regime_at_close: str
    volatility_at_close: float
    
    # Decision provenance (preserved from decision context)
    strategy_name: str
    strategy_confidence: float
    agent_votes: Dict[str, Any]
    debate_result: Optional[Dict[str, Any]]
    ceo_decision: Optional[Dict[str, Any]]
    risk_governance: str
    position_size_method: str
    
    # Attribution
    attributions: List[AttributionResult] = field(default_factory=list)
    total_attributed_pnl: float = 0.0
    residual_pnl: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    provenance_complete: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for storage."""
        return {
            'outcome_id': self.outcome_id,
            'decision_id': self.decision_id,
            'order_id': self.order_id,
            'fill_id': self.fill_id,
            'symbol': self.symbol,
            'action': self.action,
            'requested_size': self.requested_size,
            'filled_size': self.filled_size,
            'requested_price': self.requested_price,
            'filled_price': self.filled_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'decision_timestamp': self.decision_timestamp.isoformat(),
            'order_timestamp': self.order_timestamp.isoformat(),
            'fill_timestamp': self.fill_timestamp.isoformat(),
            'close_timestamp': self.close_timestamp.isoformat() if self.close_timestamp else None,
            'gross_pnl': self.gross_pnl,
            'net_pnl': self.net_pnl,
            'commission': self.commission,
            'slippage': self.slippage,
            'spread_cost': self.spread_cost,
            'market_price_at_decision': self.market_price_at_decision,
            'market_regime_at_decision': self.market_regime_at_decision,
            'volatility_at_decision': self.volatility_at_decision,
            'market_price_at_close': self.market_price_at_close,
            'market_regime_at_close': self.market_regime_at_close,
            'volatility_at_close': self.volatility_at_close,
            'strategy_name': self.strategy_name,
            'strategy_confidence': self.strategy_confidence,
            'agent_votes': self.agent_votes,
            'debate_result': self.debate_result,
            'ceo_decision': self.ceo_decision,
            'risk_governance': self.risk_governance,
            'position_size_method': self.position_size_method,
            'attributions': [
                {
                    'component': a.component.value,
                    'value': a.value,
                    'percentage': a.percentage,
                    'confidence': a.confidence,
                    'method': a.method.value,
                    'metadata': a.metadata
                }
                for a in self.attributions
            ],
            'total_attributed_pnl': self.total_attributed_pnl,
            'residual_pnl': self.residual_pnl,
            'created_at': self.created_at.isoformat(),
            'provenance_complete': self.provenance_complete,
        }


class AttributionEngine:
    """
    Decomposes trade outcomes into attributable components.
    
    Uses multiple methodologies depending on available data:
    1. Simple decomposition (always available)
    2. Brinson-Hood-Beebower (when benchmark data available)
    3. Factor regression (when factor data available)
    """
    
    def __init__(
        self,
        market_data=None,
        strategy_engine=None,
        default_method: AttributionMethod = AttributionMethod.SIMPLE_DECOMPOSITION
    ):
        self.market_data = market_data
        self.strategy_engine = strategy_engine
        self.default_method = default_method
        self.logger = logging.getLogger(__name__)
    
    def attribute_outcome(self, outcome: OutcomeRecord) -> OutcomeRecord:
        """
        Perform full attribution on an outcome record.
        Modifies and returns the outcome with attributions populated.
        """
        self.logger.info(f"Attributing outcome {outcome.outcome_id} for decision {outcome.decision_id}")
        
        # Clear existing attributions
        outcome.attributions = []
        
        # Method 1: Simple Decomposition (always available)
        self._attribute_simple_decomposition(outcome)
        
        # Method 2: Market Beta / Alpha split (if benchmark available)
        if self.market_data:
            self._attribute_market_beta_alpha(outcome)
        
        # Method 3: Strategy-specific attribution
        if self.strategy_engine:
            self._attribute_strategy_components(outcome)
        
        # Method 4: Execution cost attribution (always available)
        self._attribute_execution_costs(outcome)
        
        # Calculate totals
        outcome.total_attributed_pnl = sum(a.value for a in outcome.attributions)
        outcome.residual_pnl = outcome.net_pnl - outcome.total_attributed_pnl
        
        # Add residual if significant
        if abs(outcome.residual_pnl) > 0.01 * abs(outcome.net_pnl):
            outcome.attributions.append(AttributionResult(
                component=AttributionComponent.RESIDUAL,
                value=outcome.residual_pnl,
                percentage=(outcome.residual_pnl / outcome.net_pnl * 100) if outcome.net_pnl != 0 else 0,
                confidence=0.3,
                method=AttributionMethod.SIMPLE_DECOMPOSITION,
                metadata={'note': 'Unexplained variance after component attribution'}
            ))
        
        self.logger.info(
            f"Attribution complete for {outcome.outcome_id}: "
            f"{len(outcome.attributions)} components, "
            f"total={outcome.total_attributed_pnl:.2f}, "
            f"residual={outcome.residual_pnl:.2f}"
        )
        
        return outcome
    
    def _attribute_simple_decomposition(self, outcome: OutcomeRecord) -> None:
        """Simple direct decomposition using decision metadata."""
        net_pnl = outcome.net_pnl
        
        # Market Beta: Price movement from decision to close * position size
        price_change = outcome.market_price_at_close - outcome.market_price_at_decision
        direction_mult = 1 if outcome.action == 'BUY' else -1
        market_beta_pnl = price_change * outcome.filled_size * direction_mult
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.MARKET_BETA,
            value=market_beta_pnl,
            percentage=(market_beta_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.9,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={
                'price_change': price_change,
                'filled_size': outcome.filled_size,
                'direction': outcome.action
            }
        ))
        
        # Strategy Alpha = Net PnL - Market Beta - Execution Costs
        execution_costs = outcome.commission + outcome.slippage + outcome.spread_cost
        strategy_alpha = net_pnl - market_beta_pnl - execution_costs
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.STRATEGY_ALPHA,
            value=strategy_alpha,
            percentage=(strategy_alpha / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.7,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={
                'strategy': outcome.strategy_name,
                'confidence': outcome.strategy_confidence
            }
        ))
    
    def _attribute_market_beta_alpha(self, outcome: OutcomeRecord) -> None:
        """Refined market beta/alpha using benchmark if available."""
        try:
            # Could fetch benchmark (SPY, etc.) return over same period
            # For now, use simple approximation
            pass
        except Exception as e:
            self.logger.debug(f"Benchmark attribution unavailable: {e}")
    
    def _attribute_strategy_components(self, outcome: OutcomeRecord) -> None:
        """Attribute strategy alpha to sub-components using decision provenance."""
        net_pnl = outcome.net_pnl
        strategy_alpha = next(
            (a.value for a in outcome.attributions if a.component == AttributionComponent.STRATEGY_ALPHA),
            0
        )
        
        if strategy_alpha == 0:
            return
        
        # Regime Timing Attribution
        regime_match = outcome.market_regime_at_decision == outcome.market_regime_at_close
        regime_confidence = 0.8 if regime_match else 0.4
        regime_pnl = strategy_alpha * 0.3 * regime_confidence  # Heuristic allocation
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.REGIME_TIMING,
            value=regime_pnl,
            percentage=(regime_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=regime_confidence,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={
                'regime_at_decision': outcome.market_regime_at_decision,
                'regime_at_close': outcome.market_regime_at_close,
                'match': regime_match
            }
        ))
        
        # Technical Signal Attribution
        tech_confidence = outcome.agent_votes.get('technical_confidence', 0.5) if outcome.agent_votes else 0.5
        tech_pnl = strategy_alpha * 0.25 * tech_confidence
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.TECHNICAL_SIGNAL,
            value=tech_pnl,
            percentage=(tech_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.6,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={'source': 'agent_votes_technical'}
        ))
        
        # Fundamental Signal Attribution
        fund_confidence = outcome.agent_votes.get('fundamental_confidence', 0.5) if outcome.agent_votes else 0.5
        fund_pnl = strategy_alpha * 0.25 * fund_confidence
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.FUNDAMENTAL_SIGNAL,
            value=fund_pnl,
            percentage=(fund_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.6,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={'source': 'agent_votes_fundamental'}
        ))
        
        # Sentiment Signal Attribution
        sent_confidence = outcome.agent_votes.get('sentiment_confidence', 0.5) if outcome.agent_votes else 0.5
        sent_pnl = strategy_alpha * 0.2 * sent_confidence
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.SENTIMENT_SIGNAL,
            value=sent_pnl,
            percentage=(sent_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.5,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={'source': 'agent_votes_sentiment'}
        ))
        
        # Agent Consensus Attribution
        consensus = outcome.agent_votes.get('consensus_strength', 0.5) if outcome.agent_votes else 0.5
        agent_pnl = strategy_alpha * 0.15 * consensus
        
        outcome.attributions.append(AttributionResult(
            component=AttributionComponent.AGENT_CONSENSUS,
            value=agent_pnl,
            percentage=(agent_pnl / net_pnl * 100) if net_pnl != 0 else 0,
            confidence=0.7,
            method=AttributionMethod.SIMPLE_DECOMPOSITION,
            metadata={'consensus_strength': consensus}
        ))
        
        # CEO Intervention Attribution
        ceo_override = outcome.ceo_decision.get('override_applied', False) if outcome.ceo_decision else False
        ceo_confidence = outcome.ceo_decision.get('confidence', 0.5) if outcome.ceo_decision else 0.5
        ceo_pnl = strategy_alpha * 0.1 * (1.0 if ceo_override else 0.0) * ceo_confidence
        
        if ceo_pnl != 0:
            outcome.attributions.append(AttributionResult(
                component=AttributionComponent.CEO_INTERVENTION,
                value=ceo_pnl,
                percentage=(ceo_pnl / net_pnl * 100) if net_pnl != 0 else 0,
                confidence=0.8 if ceo_override else 0.3,
                method=AttributionMethod.SIMPLE_DECOMPOSITION,
                metadata={
                    'override_applied': ceo_override,
                    'ceo_confidence': ceo_confidence
                }
            ))
    
    def _attribute_execution_costs(self, outcome: OutcomeRecord) -> None:
        """Attribute execution costs (always available)."""
        net_pnl = outcome.net_pnl
        total_exec_cost = outcome.commission + outcome.slippage + outcome.spread_cost
        
        if total_exec_cost > 0:
            outcome.attributions.append(AttributionResult(
                component=AttributionComponent.EXECUTION_COST,
                value=-total_exec_cost,  # Negative impact
                percentage=(-total_exec_cost / net_pnl * 100) if net_pnl != 0 else 0,
                confidence=0.95,
                method=AttributionMethod.SIMPLE_DECOMPOSITION,
                metadata={
                    'commission': outcome.commission,
                    'slippage': outcome.slippage,
                    'spread_cost': outcome.spread_cost
                }
            ))
        
        # Risk Gates Attribution (size adjustments, blocks)
        if outcome.risk_governance in ('BLOCK', 'VETO', 'WARNING'):
            # Trade was modified by risk gates - estimate impact
            risk_impact = net_pnl * 0.1 * (1 if outcome.risk_governance == 'APPROVE' else -0.5)
            outcome.attributions.append(AttributionResult(
                component=AttributionComponent.RISK_GATES,
                value=risk_impact,
                percentage=(risk_impact / net_pnl * 100) if net_pnl != 0 else 0,
                confidence=0.6,
                method=AttributionMethod.SIMPLE_DECOMPOSITION,
                metadata={'risk_governance': outcome.risk_governance}
            ))


def create_outcome_from_decision(
    decision_ctx,  # DecisionContext
    order_result: Dict[str, Any],
    fill_result: Dict[str, Any],
    close_price: Optional[float] = None,
    close_timestamp: Optional[datetime] = None
) -> OutcomeRecord:
    """Factory to create OutcomeRecord from decision context + execution results.
    
    For paper trading:
    - If close_price is provided: creates a CLOSED outcome with realized P&L
    - If close_price is None: creates an OPEN position with no P&L (NULL until closed)
    """
    import uuid
    
    outcome_id = f"out_{uuid.uuid4().hex[:12]}"
    
    # Extract from decision context
    symbol = decision_ctx.symbol
    decision_id = decision_ctx.decision_id
    order_id = order_result.get('order_id', '')
    fill_id = fill_result.get('fill_id', '')
    
    action = decision_ctx.final_action.value if decision_ctx.final_action else 'HOLD'
    requested_size = decision_ctx.final_position_size
    filled_size = fill_result.get('filled_size', requested_size)
    requested_price = decision_ctx.market_snapshot.price if decision_ctx.market_snapshot else 0
    filled_price = fill_result.get('filled_price', requested_price)
    stop_loss = decision_ctx.final_stop_loss
    take_profit = decision_ctx.final_take_profit
    
    decision_ts = datetime.fromisoformat(decision_ctx.timestamp.replace('Z', '+00:00'))
    order_ts = datetime.fromisoformat(order_result.get('timestamp', datetime.now().isoformat()))
    fill_ts = datetime.fromisoformat(fill_result.get('timestamp', datetime.now().isoformat()))
    
    # P&L calculation - ONLY if close_price is provided (position closed)
    direction_mult = 1 if action == 'BUY' else -1
    
    if close_price is not None:
        # Position is CLOSED - calculate realized P&L
        price_change = close_price - filled_price
        gross_pnl = price_change * filled_size * direction_mult
        commission = fill_result.get('commission', 0)
        slippage = abs(filled_price - requested_price) * filled_size
        spread_cost = fill_result.get('spread_cost', 0)
        net_pnl = gross_pnl - commission - slippage - spread_cost
        
        market_price_at_close = close_price
        market_regime_at_close = market_regime_at_decision  # Simplified
        volatility_at_close = volatility_at_decision
        status = 'CLOSED'
    else:
        # Position is OPEN - no realized P&L yet
        gross_pnl = 0.0
        net_pnl = 0.0
        commission = fill_result.get('commission', 0)
        slippage = abs(filled_price - requested_price) * filled_size
        spread_cost = fill_result.get('spread_cost', 0)
        
        market_price_at_close = None
        market_regime_at_close = 'unknown'
        volatility_at_close = 0.0
        status = 'OPEN'
    
    # Market context at decision
    market_price_at_decision = decision_ctx.market_snapshot.price if decision_ctx.market_snapshot else 0
    market_regime_at_decision = decision_ctx.evidence.regime.regime_name if decision_ctx.evidence and decision_ctx.evidence.regime else 'unknown'
    volatility_at_decision = decision_ctx.market_snapshot.volatility if decision_ctx.market_snapshot else 0
    
    # Strategy info
    strategy_name = decision_ctx.candidate_strategy.strategy_name if decision_ctx.candidate_strategy else 'unknown'
    strategy_confidence = decision_ctx.candidate_strategy.confidence if decision_ctx.candidate_strategy else 0
    
    # Agent votes
    agent_votes = {}
    if decision_ctx.voting_result:
        agent_votes = {
            'consensus_strength': decision_ctx.voting_result.consensus_strength,
            'winning_signal': decision_ctx.voting_result.winning_signal.value,
            'vote_distribution': decision_ctx.voting_result.vote_distribution,
            'technical_confidence': 0.5,  # Would need more detail from voting
            'fundamental_confidence': 0.5,
            'sentiment_confidence': 0.5,
        }
    
    # Debate result
    debate_result = None
    if decision_ctx.debate_result:
        debate_result = {
            'winning_signal': decision_ctx.debate_result.winning_signal.value if decision_ctx.debate_result.winning_signal else None,
            'consensus_score': decision_ctx.debate_result.consensus_score,
        }
    
    # CEO decision
    ceo_decision = None
    if decision_ctx.ceo_decision:
        ceo_decision = {
            'final_signal': decision_ctx.ceo_decision.final_signal.value if decision_ctx.ceo_decision.final_signal else None,
            'confidence': decision_ctx.ceo_decision.confidence,
            'override_applied': decision_ctx.ceo_decision.override_applied,
            'reasoning': decision_ctx.ceo_decision.reasoning,
        }
    
    return OutcomeRecord(
        outcome_id=outcome_id,
        decision_id=decision_id,
        order_id=order_id,
        fill_id=fill_id,
        symbol=symbol,
        action=action,
        requested_size=requested_size,
        filled_size=filled_size,
        requested_price=requested_price,
        filled_price=filled_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        decision_timestamp=decision_ts,
        order_timestamp=order_ts,
        fill_timestamp=fill_ts,
        close_timestamp=close_timestamp,
        gross_pnl=gross_pnl,
        net_pnl=net_pnl,
        commission=commission,
        slippage=slippage,
        spread_cost=spread_cost,
        market_price_at_decision=market_price_at_decision,
        market_regime_at_decision=market_regime_at_decision,
        volatility_at_decision=volatility_at_decision,
        market_price_at_close=market_price_at_close,
        market_regime_at_close=market_regime_at_close,
        volatility_at_close=volatility_at_close,
        strategy_name=strategy_name,
        strategy_confidence=strategy_confidence,
        agent_votes=agent_votes,
        debate_result=debate_result,
        ceo_decision=ceo_decision,
        risk_governance=decision_ctx.risk_governance.value if decision_ctx.risk_governance else 'UNKNOWN',
        position_size_method=decision_ctx.position_size_method if hasattr(decision_ctx, 'position_size_method') else 'unknown',
    )