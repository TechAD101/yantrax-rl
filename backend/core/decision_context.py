"""
Canonical Decision Context for Yantra X.

This module establishes the single authoritative decision vocabulary and identity chain
that flows through the entire trading decision lifecycle.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import uuid


class TradingAction(Enum):
    """Trading actions - what the strategy wants to do."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    ABSTAIN = "ABSTAIN"


class GovernanceState(Enum):
    """Governance/risk states - what the risk/governance layer decides."""
    APPROVE = "APPROVE"
    BLOCK = "BLOCK"
    VETO = "VETO"
    WARNING = "WARNING"


class MarketRegime(Enum):
    """Market regime classifications."""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    VOLATILITY_CRISIS = "volatility_crisis"
    LIQUIDITY_CRUNCH = "liquidity_crunch"


@dataclass
class MarketSnapshot:
    """Immutable market snapshot at decision time."""
    symbol: str
    price: float
    timestamp: datetime
    
    # OHLCV
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[float] = None
    
    # Derived
    volatility: float = 0.0
    trend: str = "neutral"
    liquidity: float = 0.0
    bid_ask_spread: Optional[float] = None
    vix: Optional[float] = None
    
    # Source metadata
    source: str = "unknown"
    verified: bool = False
    data_age_seconds: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "volatility": self.volatility,
            "trend": self.trend,
            "liquidity": self.liquidity,
            "bid_ask_spread": self.bid_ask_spread,
            "vix": self.vix,
            "source": self.source,
            "verified": self.verified,
            "data_age_seconds": self.data_age_seconds,
        }


@dataclass
class TechnicalEvidence:
    """Technical analysis evidence package."""
    ema_fast: Optional[float] = None
    ema_slow: Optional[float] = None
    ema_crossover: str = "neutral"
    rsi: Optional[float] = None
    rsi_signal: str = "neutral"
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_signal: str = "neutral"
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    macd_signal_type: str = "neutral"
    volume_trend: str = "neutral"
    momentum_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "ema_fast": self.ema_fast,
            "ema_slow": self.ema_slow,
            "ema_crossover": self.ema_crossover,
            "rsi": self.rsi,
            "rsi_signal": self.rsi_signal,
            "bb_upper": self.bb_upper,
            "bb_middle": self.bb_middle,
            "bb_lower": self.bb_lower,
            "bb_signal": self.bb_signal,
            "macd": self.macd,
            "macd_signal": self.macd_signal,
            "macd_histogram": self.macd_histogram,
            "macd_signal_type": self.macd_signal_type,
            "volume_trend": self.volume_trend,
            "momentum_score": self.momentum_score,
        }


@dataclass
class FundamentalEvidence:
    """Fundamental analysis evidence package."""
    pe_ratio: Optional[float] = None
    return_on_equity: Optional[float] = None
    debt_to_equity: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    free_cash_flow: Optional[float] = None
    profit_margin: Optional[float] = None
    dividend_yield: Optional[float] = None
    fundamental_score: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "pe_ratio": self.pe_ratio,
            "return_on_equity": self.return_on_equity,
            "debt_to_equity": self.debt_to_equity,
            "revenue_growth": self.revenue_growth,
            "earnings_growth": self.earnings_growth,
            "free_cash_flow": self.free_cash_flow,
            "profit_margin": self.profit_margin,
            "dividend_yield": self.dividend_yield,
            "fundamental_score": self.fundamental_score,
        }


@dataclass
class SentimentEvidence:
    """Sentiment analysis evidence package."""
    fear_greed_index: float = 0.5
    fear_greed_signal: str = "neutral"
    options_flow_score: float = 0.5
    options_flow_signal: str = "neutral"
    social_sentiment_score: float = 0.5
    social_sentiment_signal: str = "neutral"
    composite_sentiment: float = 0.5
    composite_signal: str = "neutral"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "fear_greed_index": self.fear_greed_index,
            "fear_greed_signal": self.fear_greed_signal,
            "options_flow_score": self.options_flow_score,
            "options_flow_signal": self.options_flow_signal,
            "social_sentiment_score": self.social_sentiment_score,
            "social_sentiment_signal": self.social_sentiment_signal,
            "composite_sentiment": self.composite_sentiment,
            "composite_signal": self.composite_signal,
        }


@dataclass
class EvidencePackage:
    """Complete synthesized evidence for a decision."""
    technical: TechnicalEvidence = field(default_factory=TechnicalEvidence)
    fundamental: FundamentalEvidence = field(default_factory=FundamentalEvidence)
    sentiment: SentimentEvidence = field(default_factory=SentimentEvidence)
    market_regime: MarketRegime = MarketRegime.SIDEWAYS
    regime_confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "technical": self.technical.to_dict(),
            "fundamental": self.fundamental.to_dict(),
            "sentiment": self.sentiment.to_dict(),
            "market_regime": self.market_regime.value,
            "regime_confidence": self.regime_confidence,
        }


@dataclass
class CandidateStrategy:
    """Strategy-generated trade candidate."""
    action: TradingAction
    confidence: float
    reasoning: str
    position_size: float
    stop_loss: float
    take_profit: float
    risk_score: float
    strategy_name: str = "institutional"
    timeframe: str = "1D"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "position_size": self.position_size,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "risk_score": self.risk_score,
            "strategy_name": self.strategy_name,
            "timeframe": self.timeframe,
        }


@dataclass
class AgentVote:
    """Single agent vote in the decision process."""
    agent_name: str
    department: str
    role: str
    signal: TradingAction
    confidence: float
    weight: float
    reasoning: str
    specialty: str
    is_persona: bool = False
    
    def effective_weight(self) -> float:
        return self.weight * self.confidence
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "department": self.department,
            "role": self.role,
            "signal": self.signal.value,
            "confidence": self.confidence,
            "weight": self.weight,
            "reasoning": self.reasoning,
            "specialty": self.specialty,
            "is_persona": self.is_persona,
            "effective_weight": self.effective_weight(),
        }


@dataclass
class VotingResult:
    """Aggregated agent voting result."""
    winning_signal: TradingAction
    consensus_strength: float
    vote_distribution: Dict[str, float]
    participating_agents: int
    total_weight: float
    votes: List[AgentVote]
    divine_doubt_triggered: bool = False
    oracle_wisdom: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "winning_signal": self.winning_signal.value,
            "consensus_strength": self.consensus_strength,
            "vote_distribution": self.vote_distribution,
            "participating_agents": self.participating_agents,
            "total_weight": self.total_weight,
            "votes": [v.to_dict() for v in self.votes],
            "divine_doubt_triggered": self.divine_doubt_triggered,
            "oracle_wisdom": self.oracle_wisdom,
        }


@dataclass
class DebateResult:
    """Structured debate outcome."""
    debate_id: str
    ticker: str
    timestamp: datetime
    arguments: List[Dict[str, Any]]
    winning_signal: TradingAction
    consensus_score: float
    vote_distribution: Dict[str, float]
    perplexity_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "debate_id": self.debate_id,
            "ticker": self.ticker,
            "timestamp": self.timestamp.isoformat(),
            "arguments": self.arguments,
            "winning_signal": self.winning_signal.value,
            "consensus_score": self.consensus_score,
            "vote_distribution": self.vote_distribution,
            "perplexity_context": self.perplexity_context,
        }


@dataclass
class CEODecision:
    """CEO governance decision."""
    decision_id: str
    timestamp: datetime
    decision_type: str
    action: TradingAction
    confidence: float
    reasoning: str
    expected_impact: str
    agent_overrides: List[str]
    memory_references: List[str]
    pain_level: int
    market_mood: str
    ghost_nudge: Optional[Dict[str, Any]] = None
    philosophy_guidance: Optional[str] = None
    philosophy_veto: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "decision_type": self.decision_type,
            "action": self.action.value,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "expected_impact": self.expected_impact,
            "agent_overrides": self.agent_overrides,
            "memory_references": self.memory_references,
            "pain_level": self.pain_level,
            "market_mood": self.market_mood,
            "ghost_nudge": self.ghost_nudge,
            "philosophy_guidance": self.philosophy_guidance,
            "philosophy_veto": self.philosophy_veto,
        }


@dataclass
class PortfolioState:
    """Current portfolio state for risk context."""
    portfolio_id: int
    total_value: float
    cash: float
    positions: List[Dict[str, Any]]
    risk_profile: str
    drawdown_pct: float = 0.0
    consecutive_losses: int = 0
    peak_value: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "portfolio_id": self.portfolio_id,
            "total_value": self.total_value,
            "cash": self.cash,
            "positions": self.positions,
            "risk_profile": self.risk_profile,
            "drawdown_pct": self.drawdown_pct,
            "consecutive_losses": self.consecutive_losses,
            "peak_value": self.peak_value,
        }


@dataclass
class RiskState:
    """Current risk state from safeguards and validators."""
    emotional_state: str = "calm"
    pain_level: int = 0
    trading_allowed: bool = True
    cooling_off_until: Optional[datetime] = None
    consecutive_losses: int = 0
    overconfidence_streak: int = 0
    current_drawdown: float = 0.0
    vix_level: Optional[float] = None
    volatility_spike: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotional_state": self.emotional_state,
            "pain_level": self.pain_level,
            "trading_allowed": self.trading_allowed,
            "cooling_off_until": self.cooling_off_until.isoformat() if self.cooling_off_until else None,
            "consecutive_losses": self.consecutive_losses,
            "overconfidence_streak": self.overconfidence_streak,
            "current_drawdown": self.current_drawdown,
            "vix_level": self.vix_level,
            "volatility_spike": self.volatility_spike,
        }


@dataclass
class ExecutionConstraints:
    """Execution constraints and assumptions."""
    max_position_pct: float = 0.10
    max_portfolio_risk: float = 0.20
    max_slippage_pct: float = 0.02
    commission_per_share: float = 0.005
    min_liquidity: float = 100000
    max_bid_ask_spread: float = 0.02
    execution_horizon: str = "immediate"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_position_pct": self.max_position_pct,
            "max_portfolio_risk": self.max_portfolio_risk,
            "max_slippage_pct": self.max_slippage_pct,
            "commission_per_share": self.commission_per_share,
            "min_liquidity": self.min_liquidity,
            "max_bid_ask_spread": self.max_bid_ask_spread,
            "execution_horizon": self.execution_horizon,
        }


@dataclass
class DecisionContext:
    """
    Canonical decision context - the single source of truth for one trading decision.
    
    Flows through: Market Snapshot → Regime → Evidence → Strategy → Agents → Debate → CEO → Risk → Sizing → Execution
    """
    # Identity
    decision_id: str = field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Market
    symbol: str = ""
    market_snapshot: Optional[MarketSnapshot] = None
    
    # Intelligence
    evidence: Optional[EvidencePackage] = None
    candidate_strategy: Optional[CandidateStrategy] = None
    
    # Agent Intelligence
    voting_result: Optional[VotingResult] = None
    
    # Debate
    debate_result: Optional[DebateResult] = None
    
    # Governance
    ceo_decision: Optional[CEODecision] = None
    
    # Portfolio & Risk
    portfolio_state: Optional[PortfolioState] = None
    risk_state: Optional[RiskState] = None
    execution_constraints: ExecutionConstraints = field(default_factory=ExecutionConstraints)
    
    # Governance Decisions
    risk_governance: Optional[GovernanceState] = None
    risk_reasons: List[str] = field(default_factory=list)
    
    # Final Decision
    final_action: Optional[TradingAction] = None
    final_confidence: float = 0.0
    final_position_size: float = 0.0
    final_stop_loss: float = 0.0
    final_take_profit: float = 0.0
    
    # Execution
    order_id: Optional[int] = None
    execution_id: Optional[str] = None
    fill_price: Optional[float] = None
    fill_quantity: Optional[float] = None
    execution_timestamp: Optional[datetime] = None
    
    # Outcome
    outcome_id: Optional[str] = None
    realized_pnl: Optional[float] = None
    
    # Attribution
    attribution_ids: List[str] = field(default_factory=list)  # Can have multiple attribution records per outcome
    
    # Learning
    learning_event_ids: List[str] = field(default_factory=list)  # All learning event IDs
    learning_event_id: Optional[str] = None  # Backward compatibility - first event
    
    # Position lifecycle
    position_id: Optional[str] = None
    position_status: Optional[str] = None  # OPEN, CLOSED
    
    # Provenance tracking
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/persistence."""
        return {
            "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "symbol": self.symbol,
            "market_snapshot": self.market_snapshot.to_dict() if self.market_snapshot else None,
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "candidate_strategy": self.candidate_strategy.to_dict() if self.candidate_strategy else None,
            "voting_result": self.voting_result.to_dict() if self.voting_result else None,
            "debate_result": self.debate_result.to_dict() if self.debate_result else None,
            "ceo_decision": self.ceo_decision.to_dict() if self.ceo_decision else None,
            "portfolio_state": self.portfolio_state.to_dict() if self.portfolio_state else None,
            "risk_state": self.risk_state.to_dict() if self.risk_state else None,
            "execution_constraints": self.execution_constraints.to_dict(),
            "risk_governance": self.risk_governance.value if self.risk_governance else None,
            "risk_reasons": self.risk_reasons,
            "final_action": self.final_action.value if self.final_action else None,
            "final_confidence": self.final_confidence,
            "final_position_size": self.final_position_size,
            "final_stop_loss": self.final_stop_loss,
            "final_take_profit": self.final_take_profit,
            "order_id": self.order_id,
            "execution_id": self.execution_id,
            "fill_price": self.fill_price,
            "fill_quantity": self.fill_quantity,
            "execution_timestamp": self.execution_timestamp.isoformat() if self.execution_timestamp else None,
            "outcome_id": self.outcome_id,
            "realized_pnl": self.realized_pnl,
            "attribution_ids": self.attribution_ids,
            "learning_event_ids": self.learning_event_ids,
            "learning_event_id": self.learning_event_id,
            "position_id": self.position_id,
            "position_status": self.position_status,
            "provenance": self.provenance,
        }
    
    def add_provenance(self, stage: str, details: Dict[str, Any]):
        """Add provenance entry for audit trail."""
        self.provenance[stage] = {
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }


def create_decision_context(symbol: str) -> DecisionContext:
    """Factory function to create a new decision context."""
    ctx = DecisionContext(symbol=symbol.upper())
    ctx.add_provenance("created", {"symbol": symbol})
    return ctx