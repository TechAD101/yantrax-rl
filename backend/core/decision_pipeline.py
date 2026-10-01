"""
Canonical Decision Pipeline for Yantra X.

Orchestrates the complete decision lifecycle:
Market Snapshot → Regime → Evidence → Strategy → Agents → Debate → CEO → Risk → Sizing → Final Risk → Execution
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import asyncio

from backend.core.decision_context import (
    DecisionContext, TradingAction, GovernanceState, MarketSnapshot,
    EvidencePackage, CandidateStrategy, VotingResult, DebateResult,
    CEODecision, PortfolioState, RiskState, ExecutionConstraints,
    create_decision_context, AgentVote
)
from backend.core.evidence_synthesizer import EvidenceSynthesizer, build_market_snapshot
from backend.risk.risk_governor import RiskGovernor
from backend.risk.position_sizer import PositionSizer, SizingMethod, calculate_position_size

# Import existing intelligence components
from backend.ai_firm.agent_manager import AgentManager
from backend.ai_firm.debate_engine import DebateEngine
from backend.ai_firm.ceo import AutonomousCEO, CEOPersonality
from backend.ai_firm.ghost_layer import GhostLayer
from backend.ai_firm.philosophy import PhilosophyManager
from backend.services.institutional_strategy_engine import (
    InstitutionalStrategyEngine, get_strategy_engine
)
from backend.services.market_sentiment_service import get_sentiment_service
MarketDataService = Any
from backend.services.oracle_service import OracleService
from backend.order_manager import create_order
from backend.db import get_session
from backend.models import Portfolio

logger = logging.getLogger(__name__)


class DecisionPipeline:
    """
    Canonical decision pipeline that connects all Yantra X intelligence components.
    
    This is the single authoritative path for trading decisions.
    """
    
    def __init__(
        self,
        market_data: Optional[MarketDataService] = None,
        strategy_engine: Optional[InstitutionalStrategyEngine] = None,
        agent_manager: Optional[AgentManager] = None,
        debate_engine: Optional[DebateEngine] = None,
        ceo: Optional[AutonomousCEO] = None,
        ghost_layer: Optional[GhostLayer] = None,
        oracle: Optional[OracleService] = None,
        sentiment_service: Optional[Any] = None,
        portfolio_id: int = 1,
    ):
        # Core services
        self.market_data = market_data
        self.strategy_engine = strategy_engine or get_strategy_engine()
        self.agent_manager = agent_manager
        self.debate_engine = debate_engine
        self.ceo = ceo
        self.ghost_layer = ghost_layer
        self.oracle = oracle
        self._sentiment_service = sentiment_service
        self.portfolio_id = portfolio_id
        
        # Pipeline components
        self.evidence_synthesizer = EvidenceSynthesizer(
            strategy_engine=self.strategy_engine,
            market_data=self.market_data,
            sentiment_service=self._sentiment_service,
        )
        self.risk_governor = RiskGovernor()
        self.position_sizer = PositionSizer(strategy_engine=self.strategy_engine)
        
        # State
        self._initialized = False
    
    def initialize(self):
        """Initialize all components."""
        if self._initialized:
            return
        
        # Initialize AgentManager if not provided
        if not self.agent_manager:
            self.agent_manager = AgentManager(oracle_service=self.oracle)
        
        # Initialize DebateEngine if not provided
        if not self.debate_engine:
            self.debate_engine = DebateEngine(self.agent_manager)
        
        # Initialize CEO if not provided
        if not self.ceo:
            self.ceo = AutonomousCEO(personality=CEOPersonality.BALANCED)
            self.ceo.agent_manager = self.agent_manager
            self.ceo.debate_engine = self.debate_engine
            self.ceo.ghost_layer = self.ghost_layer or GhostLayer()
            self.ceo.philosophy = PhilosophyManager()
        
        # Initialize GhostLayer if not provided
        if not self.ghost_layer:
            self.ghost_layer = GhostLayer()
        
        self._initialized = True
        logger.info("✅ DecisionPipeline initialized")
    
    async def execute_decision(self, symbol: str) -> DecisionContext:
        """
        Execute the complete canonical decision pipeline for a symbol.
        
        Returns the DecisionContext with all stages populated.
        """
        self.initialize()
        
        # Create decision context
        ctx = create_decision_context(symbol)
        ctx.add_provenance("pipeline_start", {"symbol": symbol})
        
        try:
            # ──────────────────────────────────────────────────────
            # STAGE 1: MARKET SNAPSHOT
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_market_snapshot(ctx)
            if not ctx.market_snapshot:
                ctx.final_action = TradingAction.ABSTAIN
                return ctx
            
            # ──────────────────────────────────────────────────────
            # STAGE 2: EVIDENCE SYNTHESIS (includes Regime)
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_evidence_synthesis(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 3: STRATEGY CANDIDATE
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_strategy_candidate(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 4: AGENT ANALYSIS & VOTING
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_agent_voting(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 5: DEBATE / DISSENT
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_debate(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 6: CEO GOVERNANCE
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_ceo_governance(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 7: PRELIMINARY RISK GOVERNANCE
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_preliminary_risk(ctx)
            
            # If blocked at preliminary, stop here
            if ctx.risk_governance == GovernanceState.BLOCK or ctx.risk_governance == GovernanceState.VETO:
                ctx.final_action = TradingAction.HOLD
                ctx.add_provenance("blocked_risk", {"governance": ctx.risk_governance.value})
                return ctx
            
            # ──────────────────────────────────────────────────────
            # STAGE 8: POSITION SIZING
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_position_sizing(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 9: FINAL RISK GOVERNANCE (post-sizing)
            # ──────────────────────────────────────────────────────
            ctx = await self._stage_final_risk(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 10: FINAL DECISION
            # ──────────────────────────────────────────────────────
            ctx = self._finalize_decision(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 11: EXECUTION (if approved)
            # ──────────────────────────────────────────────────────
            if ctx.final_action in (TradingAction.BUY, TradingAction.SELL):
                ctx = await self._stage_execution(ctx)
            
            # ──────────────────────────────────────────────────────
            # STAGE 12: OUTCOME + ATTRIBUTION (for completed trades)
            # ──────────────────────────────────────────────────────
            if ctx.final_action in (TradingAction.BUY, TradingAction.SELL) and ctx.order_id:
                ctx = await self._stage_outcome_attribution(ctx)

            ctx.add_provenance("pipeline_complete", {
                "final_action": ctx.final_action.value if ctx.final_action else None,
                "governance": ctx.risk_governance.value if ctx.risk_governance else None,
            })
            
            return ctx
            
        except Exception as e:
            logger.error(f"Pipeline error for {symbol}: {e}", exc_info=True)
            ctx.add_provenance("pipeline_error", {"error": str(e)})
            ctx.final_action = TradingAction.ABSTAIN
            return ctx
    
    # ──────────────────────────────────────────────────────────────
    # Pipeline Stages
    # ──────────────────────────────────────────────────────────────
    
    async def _stage_market_snapshot(self, ctx: DecisionContext) -> DecisionContext:
        """Fetch and build canonical market snapshot."""
        symbol = ctx.symbol
        
        # The canonical pipeline requires an explicit market-data provider.
        # No global, dummy, cached, or synthetic provider may be substituted here.
        if not self.market_data:
            logger.error("No market-data provider configured for canonical decision pipeline")
            ctx.final_action = TradingAction.ABSTAIN
            ctx.add_provenance("market_snapshot_error", {
                "error": "market_data_provider_not_configured",
                "action": TradingAction.ABSTAIN.value,
            })
            return ctx

        try:
            price_data = self.market_data.get_stock_price(symbol)
        except Exception as e:
            logger.error(f"Market data error for {symbol}: {e}")
            ctx.final_action = TradingAction.ABSTAIN
            ctx.add_provenance("market_snapshot_error", {
                "error": str(e),
                "action": TradingAction.ABSTAIN.value,
            })
            return ctx

        # Get fundamentals
        fundamentals = {}
        if self.market_data and hasattr(self.market_data, 'get_fundamentals'):
            try:
                fundamentals = self.market_data.get_fundamentals(symbol) or {}
            except Exception:
                pass
        
        current_price = price_data.get('price', 0)
        if current_price <= 0:
            logger.warning(f"No valid price for {symbol}")
            return ctx
        
        # Build canonical snapshot
        ctx.market_snapshot = build_market_snapshot(symbol, self.market_data, price_data, fundamentals)
        ctx.add_provenance("market_snapshot", {
            "price": current_price,
            "source": ctx.market_snapshot.source,
            "verified": ctx.market_snapshot.verified,
        })
        
        return ctx
    
    async def _stage_evidence_synthesis(self, ctx: DecisionContext) -> DecisionContext:
        """Synthesize evidence package (technical + fundamental + sentiment + regime)."""
        if not ctx.market_snapshot:
            return ctx
        
        ctx.evidence = self.evidence_synthesizer.synthesize(ctx.symbol, ctx.market_snapshot)
        ctx.add_provenance("evidence_synthesis", {
            "regime": ctx.evidence.market_regime.value,
            "regime_confidence": ctx.evidence.regime_confidence,
            "technical_signals": ctx.evidence.technical.__dict__,
            "fundamental_score": ctx.evidence.fundamental.fundamental_score,
            "composite_sentiment": ctx.evidence.sentiment.composite_sentiment,
        })
        
        return ctx
    
    async def _stage_strategy_candidate(self, ctx: DecisionContext) -> DecisionContext:
        """Generate candidate strategy signal using InstitutionalStrategyEngine."""
        if not ctx.evidence or not ctx.market_snapshot:
            return ctx
        
        try:
            # Get portfolio state
            portfolio_state = await self._get_portfolio_state()
            
            # Build market data for strategy engine
            price_history = self._get_price_history(ctx.symbol)
            enhanced_market_data = {
                'price': ctx.market_snapshot.price,
                'price_history': price_history,
                'volatility': ctx.market_snapshot.volatility,
                'volume': ctx.market_snapshot.volume or 1000000,
                'trend': ctx.market_snapshot.trend,
                'volume_trend': 'stable',
            }
            
            # Get fundamentals
            fundamentals = {}
            if self.market_data and hasattr(self.market_data, 'get_fundamentals'):
                try:
                    fundamentals = self.market_data.get_fundamentals(ctx.symbol) or {}
                except Exception:
                    pass
            
            # Get sentiment
            sentiment = {}
            if self.sentiment_service:
                try:
                    sentiment = self.sentiment_service.get_comprehensive_sentiment(ctx.symbol).get('components', {})
                except Exception:
                    pass
            
            # Generate institutional signal
            signal = self.strategy_engine.generate_institutional_signal(
                ctx.symbol, enhanced_market_data, fundamentals, sentiment, portfolio_state
            )
            
            # Map to canonical candidate strategy
            action_map = {
                'BUY': TradingAction.BUY,
                'SELL': TradingAction.SELL,
                'HOLD': TradingAction.HOLD,
            }
            
            ctx.candidate_strategy = CandidateStrategy(
                action=action_map.get(signal.action, TradingAction.HOLD),
                confidence=signal.confidence,
                reasoning=signal.reasoning,
                position_size=signal.position_size,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                risk_score=signal.risk_score,
                strategy_name="institutional",
                timeframe=signal.timeframe,
            )
            
            ctx.add_provenance("strategy_candidate", {
                "action": ctx.candidate_strategy.action.value,
                "confidence": ctx.candidate_strategy.confidence,
                "position_size": ctx.candidate_strategy.position_size,
                "stop_loss": ctx.candidate_strategy.stop_loss,
                "take_profit": ctx.candidate_strategy.take_profit,
            })
            
        except Exception as e:
            logger.error(f"Strategy candidate generation failed: {e}")
            # Fallback: create neutral candidate
            ctx.candidate_strategy = CandidateStrategy(
                action=TradingAction.HOLD,
                confidence=0.5,
                reasoning=f"Strategy engine error: {e}",
                position_size=0.0,
                stop_loss=0.0,
                take_profit=0.0,
                risk_score=0.5,
            )
        
        return ctx
    
    async def _stage_agent_voting(self, ctx: DecisionContext) -> DecisionContext:
            """Run agent voting through AgentManager."""
            if not ctx.evidence or not ctx.market_snapshot:
                return ctx

            # Build context for agents
            agent_context = {
                'symbol': ctx.symbol,
                'decision_type': 'trading',
                'market_trend': ctx.market_snapshot.trend,
                'volatility': ctx.market_snapshot.volatility,
                'fundamentals': {
                    'pe_ratio': ctx.evidence.fundamental.pe_ratio,
                    'return_on_equity': ctx.evidence.fundamental.return_on_equity,
                    'debt_to_equity': ctx.evidence.fundamental.debt_to_equity,
                },
                'rsi': ctx.evidence.technical.rsi,
                'market_data': {'current_price': ctx.market_snapshot.price},
                'sentiment': ctx.evidence.sentiment.__dict__,
                'fear_greed_index': ctx.evidence.sentiment.fear_greed_index,
                'options_flow': ctx.evidence.sentiment.options_flow_signal,
                'social_sentiment': ctx.evidence.sentiment.social_sentiment_signal,
                'composite_sentiment': ctx.evidence.sentiment.composite_sentiment,
                'timestamp': datetime.now().isoformat(),
            }

            try:
                # Get expert opinions from personas if available
                expert_opinions = {}
                if hasattr(self.agent_manager, 'enhanced_agents'):
                    for name in ['warren', 'cathie', 'macro_monk']:
                        if name in self.agent_manager.enhanced_agents:
                            # These are handled inside _generate_agent_signal
                            pass

                voting_result = self.agent_manager.conduct_agent_voting(agent_context, expert_opinions)

                # Normalize winning signal to canonical TradingAction
                raw_winning = voting_result['winning_signal']
                canonical_signal = self._normalize_signal_to_trading_action(raw_winning)

                # Build individual AgentVote objects from agent_votes
                agent_votes = []
                for av in voting_result.get('agent_votes', []):
                    signal = av['signal']
                    canonical_signal = self._normalize_signal_to_trading_action(signal)
                    # Map role to weight
                    weight = av['weight']
                    agent_votes.append(AgentVote(
                        agent_name=av['name'],
                        department=av['department'],
                        role=av['role'],
                        signal=canonical_signal,
                        confidence=av['confidence'],
                        weight=weight,
                        reasoning=f"Signal: {signal}, Specialty: {av.get('specialty', '')}",
                        specialty=av.get('specialty', ''),
                        is_persona=av.get('persona', False)
                    ))

                # Convert to canonical VotingResult
                ctx.voting_result = VotingResult(
                    winning_signal=canonical_signal,
                    consensus_strength=voting_result['consensus_strength'],
                    vote_distribution=voting_result['vote_distribution'],
                    participating_agents=voting_result['participating_agents'],
                    total_weight=voting_result['total_weight'],
                    votes=agent_votes,
                    divine_doubt_triggered=voting_result.get('divine_doubt_applied', False),
                    oracle_wisdom=voting_result.get('oracle_wisdom'),
                )

                ctx.add_provenance("agent_voting", {
                    "winning_signal": ctx.voting_result.winning_signal.value,
                    "consensus_strength": ctx.voting_result.consensus_strength,
                    "participating_agents": ctx.voting_result.participating_agents,
                    "divine_doubt": ctx.voting_result.divine_doubt_triggered,
                    "vote_count": len(agent_votes),
                })

            except Exception as e:
                logger.error(f"Agent voting failed: {e}")
                ctx.voting_result = VotingResult(
                    winning_signal=TradingAction.HOLD,
                    consensus_strength=0.0,
                    vote_distribution={},
                    participating_agents=0,
                    total_weight=0.0,
                    votes=[],
                )

            return ctx

    def _normalize_signal_to_trading_action(self, signal: str) -> TradingAction:
        """Normalize various signal strings to canonical TradingAction enum."""
        signal_upper = signal.upper()

        # Direct mappings
        if signal_upper in ('BUY', 'HIGH_CONVICTION_BUY'):
            return TradingAction.BUY
        elif signal_upper in ('SELL',):
            return TradingAction.SELL
        elif signal_upper in ('HOLD', 'HOLD_FOR_CLARITY', 'WHISPER_HOLD'):
            return TradingAction.HOLD
        elif signal_upper in ('ABSTAIN', 'REJECT', 'APPROVED', 'CAUTION'):
            return TradingAction.ABSTAIN

        # Default
        return TradingAction.HOLD

    async def _stage_debate(self, ctx: DecisionContext) -> DecisionContext:
        """Run debate through DebateEngine."""
        try:
            debate_context = {
                'symbol': ctx.symbol,
                'market_trend': ctx.market_snapshot.trend if ctx.market_snapshot else 'neutral',
                'volatility': ctx.market_snapshot.volatility if ctx.market_snapshot else 0.02,
                'evidence': ctx.evidence.to_dict() if ctx.evidence else {},
                'agent_votes': [v.to_dict() for v in ctx.voting_result.votes] if ctx.voting_result else [],
            }
            
            # DebateEngine is async
            debate_result = await self.debate_engine.conduct_debate(ctx.symbol, debate_context)
            
            ctx.debate_result = DebateResult(
                debate_id=debate_result.get('id', f"deb_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                ticker=ctx.symbol,
                timestamp=datetime.now(),
                arguments=debate_result.get('arguments', []),
                winning_signal=TradingAction(debate_result['winning_signal']) if debate_result['winning_signal'] in [a.value for a in TradingAction] else TradingAction.HOLD,
                consensus_score=debate_result['consensus_score'],
                vote_distribution=debate_result['vote_distribution'],
                perplexity_context=debate_result.get('perplexity_context'),
            )
            
            ctx.add_provenance("debate", {
                "winning_signal": ctx.debate_result.winning_signal.value,
                "consensus_score": ctx.debate_result.consensus_score,
            })
            
        except Exception as e:
            logger.error(f"Debate failed: {e}")
            ctx.debate_result = DebateResult(
                debate_id=f"deb_err_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                ticker=ctx.symbol,
                timestamp=datetime.now(),
                arguments=[],
                winning_signal=TradingAction.HOLD,
                consensus_score=0.0,
                vote_distribution={},
            )
        
        return ctx
    
    async def _stage_ceo_governance(self, ctx: DecisionContext) -> DecisionContext:
        """Run CEO governance decision."""
        try:
            # Build context for CEO
            ceo_context = {
                'type': 'strategic_trading_decision',
                'symbol': ctx.symbol,
                'ticker': ctx.symbol,
                'market_trend': ctx.market_snapshot.trend if ctx.market_snapshot else 'neutral',
                'volatility': ctx.market_snapshot.volatility if ctx.market_snapshot else 0.02,
                'evidence': ctx.evidence.to_dict() if ctx.evidence else {},
                'agent_recommendation': ctx.voting_result.winning_signal.value if ctx.voting_result else 'HOLD',
                'consensus_strength': ctx.voting_result.consensus_strength if ctx.voting_result else 0.0,
                'debate_result': ctx.debate_result.to_dict() if ctx.debate_result else {},
                'candidate_strategy': ctx.candidate_strategy.to_dict() if ctx.candidate_strategy else {},
                'portfolio_state': ctx.portfolio_state.to_dict() if ctx.portfolio_state else {},
                'timestamp': datetime.now().isoformat(),
            }
            
            # CEO decision (async)
            ceo_decision = await self.ceo.make_strategic_decision(ceo_context)
            
            # CEO decision_type is a workflow classification, not trade direction.
            # Preserve the explicit candidate strategy action; governance vetoes remain
            # separate and are enforced by risk/finalization stages.
            strategy_action = ceo_decision.context.get('strategy_action')
            if strategy_action in [a.value for a in TradingAction]:
                ceo_action = TradingAction(strategy_action)
            elif ceo_decision.decision_type == 'defensive_lockdown':
                ceo_action = TradingAction.HOLD
            else:
                ceo_action = ctx.candidate_strategy.action if ctx.candidate_strategy else TradingAction.HOLD

            ctx.ceo_decision = CEODecision(
                decision_id=ceo_decision.id,
                timestamp=ceo_decision.timestamp,
                decision_type=ceo_decision.decision_type,
                action=ceo_action,
                confidence=ceo_decision.confidence,
                reasoning=ceo_decision.reasoning,
                expected_impact=ceo_decision.expected_impact,
                agent_overrides=ceo_decision.agent_overrides,
                memory_references=ceo_decision.memory_references,
                pain_level=self.ceo._calculate_pain_level(ceo_context),
                market_mood=self.ceo._determine_market_mood(),
            )
            
            ctx.add_provenance("ceo_governance", {
                "action": ctx.ceo_decision.action.value,
                "action_source": "strategy_action" if strategy_action in [a.value for a in TradingAction] else "candidate_strategy",
                "confidence": ctx.ceo_decision.confidence,
                "pain_level": ctx.ceo_decision.pain_level,
                "ghost_nudge": ctx.ceo_decision.ghost_nudge is not None,
                "philosophy_veto": ctx.ceo_decision.philosophy_veto,
            })
            
        except Exception as e:
            logger.error(f"CEO governance failed: {e}")
            ctx.ceo_decision = CEODecision(
                decision_id=f"ceo_err_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                timestamp=datetime.now(),
                decision_type='error',
                action=TradingAction.HOLD,
                confidence=0.0,
                reasoning=f"CEO error: {e}",
                expected_impact="Unknown",
                agent_overrides=[],
                memory_references=[],
                pain_level=0,
                market_mood="unknown",
            )
        
        return ctx
    
    async def _stage_preliminary_risk(self, ctx: DecisionContext) -> DecisionContext:
        """Run preliminary risk checks (before sizing)."""
        # Build risk state from emotional safeguards
        ctx.risk_state = RiskState()
        if self.risk_governor.emotional_safeguards:
            try:
                safeguard_status = self.risk_governor.emotional_safeguards.get_status()
                ctx.risk_state = RiskState(
                    emotional_state=safeguard_status.get('emotional_state', 'calm'),
                    pain_level=safeguard_status.get('pain_level', 0),
                    trading_allowed=safeguard_status.get('trading_allowed', True),
                    cooling_off_until=datetime.fromisoformat(safeguard_status['cooling_off_until']) if safeguard_status.get('cooling_off_until') else None,
                    consecutive_losses=safeguard_status.get('consecutive_losses', 0),
                    overconfidence_streak=safeguard_status.get('overconfidence_streak', 0),
                    current_drawdown=safeguard_status.get('current_drawdown_pct', 0.0) / 100,
                )
            except Exception:
                pass
        
        # Build portfolio state
        ctx.portfolio_state = await self._get_portfolio_state()
        
        # Run preliminary risk governance
        risk_result = self.risk_governor.evaluate_preliminary(ctx)
        ctx.risk_governance = risk_result.overall
        ctx.risk_reasons = risk_result.blocked_by + risk_result.warnings
        
        ctx.add_provenance("risk", {
            "governance": risk_result.overall.value,
            "blocked_by": risk_result.blocked_by,
            "warnings": risk_result.warnings,
            "gates": [g.to_dict() for g in risk_result.gates],
        })
        
        return ctx
    
    async def _stage_position_sizing(self, ctx: DecisionContext) -> DecisionContext:
        """Calculate position size using PositionSizer."""
        if not ctx.candidate_strategy or ctx.candidate_strategy.action == TradingAction.HOLD:
            return ctx
        
        sizing_result = self.position_sizer.calculate(ctx)
        
        ctx.final_position_size = sizing_result.position_size
        ctx.final_stop_loss = sizing_result.stop_loss
        ctx.final_take_profit = sizing_result.take_profit
        
        ctx.add_provenance("position_sizing", sizing_result.to_dict())
        
        return ctx
    
    async def _stage_final_risk(self, ctx: DecisionContext) -> DecisionContext:
        """Run final risk checks (after sizing)."""
        risk_result = self.risk_governor.evaluate_final(ctx)
        
        # Combine with preliminary result - more restrictive wins
        if risk_result.is_blocked():
            ctx.risk_governance = risk_result.overall
        elif ctx.risk_governance == GovernanceState.APPROVE and risk_result.has_warnings():
            ctx.risk_governance = GovernanceState.WARNING
        
        ctx.risk_reasons.extend(risk_result.blocked_by)
        ctx.risk_reasons.extend(risk_result.warnings)
        
        ctx.add_provenance("risk", {
            "governance": risk_result.overall.value,
            "blocked_by": risk_result.blocked_by,
            "warnings": risk_result.warnings,
            "gates": [g.to_dict() for g in risk_result.gates],
        })
        
        return ctx
    
    def _finalize_decision(self, ctx: DecisionContext) -> DecisionContext:
        """Determine final action based on all inputs."""
        # Start with CEO decision as baseline
        if ctx.ceo_decision:
            ctx.final_action = ctx.ceo_decision.action
            ctx.final_confidence = ctx.ceo_decision.confidence
        elif ctx.candidate_strategy:
            ctx.final_action = ctx.candidate_strategy.action
            ctx.final_confidence = ctx.candidate_strategy.confidence
        elif ctx.voting_result:
            ctx.final_action = ctx.voting_result.winning_signal
            ctx.final_confidence = ctx.voting_result.consensus_strength
        else:
            ctx.final_action = TradingAction.HOLD
            ctx.final_confidence = 0.5
        
        # Risk governance can override
        if ctx.risk_governance == GovernanceState.BLOCK or ctx.risk_governance == GovernanceState.VETO:
            ctx.final_action = TradingAction.HOLD
            ctx.final_confidence = 0.0
        elif ctx.risk_governance == GovernanceState.WARNING:
            # Reduce confidence on warnings
            ctx.final_confidence *= 0.7
        
        # Ensure we have sizing for BUY/SELL
        if ctx.final_action in (TradingAction.BUY, TradingAction.SELL):
            if not ctx.final_position_size or ctx.final_position_size <= 0:
                ctx.final_action = TradingAction.HOLD
                ctx.final_confidence = 0.0
        
        ctx.add_provenance("final_decision", {
            "action": ctx.final_action.value,
            "confidence": ctx.final_confidence,
            "governance": ctx.risk_governance.value if ctx.risk_governance else None,
        })
        
        return ctx
    
    async def _stage_execution(self, ctx: DecisionContext) -> DecisionContext:
        """Execute the approved trade via OrderManager."""
        if ctx.final_action not in (TradingAction.BUY, TradingAction.SELL):
            return ctx
        
        try:
            # Calculate USD amount
            usd_amount = ctx.final_position_size
            
            # Create order through existing order manager
            order = create_order(ctx.symbol, usd_amount)
            
            ctx.order_id = order.get('id')
            ctx.execution_id = f"exec_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            ctx.fill_price = order.get('price')
            ctx.fill_quantity = order.get('quantity')
            ctx.execution_timestamp = datetime.now()
            
            # Store decision provenance in order meta
            # (Order model already supports meta JSON field)
            
            ctx.add_provenance("execution", {
                "order_id": ctx.order_id,
                "execution_id": ctx.execution_id,
                "fill_price": ctx.fill_price,
                "fill_quantity": ctx.fill_quantity,
            })
            
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            ctx.add_provenance("execution_error", {"error": str(e)})
        
        return ctx
    
    async def _stage_outcome_attribution(self, ctx: DecisionContext) -> DecisionContext:
        """Create OPEN paper position record at entry."""
        try:
            # Import attribution engine
            from backend.attribution.attribution_engine import (
                AttributionEngine, create_outcome_from_decision
            )
            from backend.models import PaperPosition
            import uuid
            
            # Build order/fill results for paper trading
            order_result = {
                'order_id': ctx.order_id,
                'timestamp': ctx.execution_timestamp.isoformat() if ctx.execution_timestamp else datetime.now().isoformat(),
            }
            
            fill_result = {
                'fill_id': ctx.execution_id,
                'filled_price': ctx.fill_price or ctx.market_snapshot.price,
                'filled_size': ctx.fill_quantity or ctx.final_position_size,
                'commission': 0.0,
                'slippage': 0.0,
                'spread_cost': 0.0,
                'timestamp': datetime.now().isoformat(),
            }
            
            # Create PaperPosition (OPEN position at entry)
            position_id = f"pos_{uuid.uuid4().hex[:12]}"
            position = PaperPosition(
                id=position_id,
                decision_id=ctx.decision_id,
                symbol=ctx.symbol,
                side=ctx.final_action.value if ctx.final_action else 'BUY',
                quantity=ctx.fill_quantity or ctx.final_position_size,
                entry_order_id=ctx.order_id,
                entry_fill_id=ctx.execution_id,
                entry_price=ctx.fill_price or ctx.market_snapshot.price,
                entry_timestamp=ctx.execution_timestamp or datetime.now(),
                status='OPEN',
                strategy_id=ctx.candidate_strategy.strategy_name if ctx.candidate_strategy else 'unknown',
                regime=ctx.evidence.market_regime.value if ctx.evidence and ctx.evidence.market_regime else 'unknown',
            )
            
            # Store position to database
            session = get_session()
            try:
                session.add(position)
                session.commit()
            finally:
                session.close()
            
            # Store position ID in context
            ctx.position_id = position_id
            ctx.position_status = 'OPEN'
            
            ctx.add_provenance("position_opened", {
                "position_id": position_id,
                "symbol": ctx.symbol,
                "side": position.side,
                "quantity": position.quantity,
                "entry_price": position.entry_price,
                "entry_order_id": ctx.order_id,
                "entry_fill_id": ctx.execution_id,
            })
            
            logger.info(f"OPEN position created for {ctx.decision_id}: {position_id}")
            
        except Exception as e:
            logger.error(f"Position creation failed: {e}")
            ctx.add_provenance("position_error", {"error": str(e)})
        
        return ctx
    
    def _generate_learning_events(self, outcome) -> List:
        """Generate LearningEvent objects from outcome and attribution results."""
        from backend.core.decision_context import LearningEvent
        from datetime import datetime
        import uuid
        
        events = []
        
        # Event 1: Agent confidence updates based on attribution
        if outcome.agent_votes:
            for agent_name, vote_data in outcome.agent_votes.get('vote_distribution', {}).items():
                if isinstance(vote_data, dict):
                    signal = vote_data.get('signal', 'HOLD')
                    confidence = vote_data.get('confidence', 0.5)
                    
                    # Determine if agent was "right" based on outcome
                    # BUY with positive P&L = correct, SELL with negative P&L = correct (for short)
                    was_correct = False
                    if signal == 'BUY' and outcome.net_pnl > 0:
                        was_correct = True
                    elif signal == 'SELL' and outcome.net_pnl < 0:
                        was_correct = True
                    elif signal == 'HOLD':
                        was_correct = True  # HOLD is correct if no action was best
                    
                    # Simple confidence adjustment
                    new_confidence = confidence * (1.02 if was_correct else 0.98)
                    new_confidence = max(0.1, min(0.99, new_confidence))
                    
                    event = LearningEvent(
                        event_id=f"le_agent_{agent_name}_{outcome.outcome_id}",
                        outcome_id=outcome.outcome_id,
                        event_type="confidence_update",
                        target_type="agent",
                        target_id=agent_name,
                        old_value=str(confidence),
                        new_value=str(new_confidence),
                        metadata={
                            'agent_signal': signal,
                            'was_correct': was_correct,
                            'outcome_pnl': outcome.net_pnl,
                            'attribution_components': len(outcome.attributions)
                        },
                        timestamp=datetime.now()
                    )
                    events.append(event)
        
        # Event 2: Strategy performance update
        if outcome.strategy_name and outcome.strategy_name != 'unknown':
            event = LearningEvent(
                event_id=f"le_strategy_{outcome.strategy_name}_{outcome.outcome_id}",
                outcome_id=outcome.outcome_id,
                event_type="strategy_metric_update",
                target_type="strategy",
                target_id=outcome.strategy_name,
                old_value=str(outcome.strategy_confidence),
                new_value=str(min(0.99, outcome.strategy_confidence * (1.01 if outcome.net_pnl > 0 else 0.99))),
                metadata={
                    'outcome_pnl': outcome.net_pnl,
                    'regime': outcome.market_regime_at_decision,
                    'attribution_summary': {a.component.value: a.value for a in outcome.attributions}
                },
                timestamp=datetime.now()
            )
            events.append(event)
        
        # Event 3: Market regime learning
        event = LearningEvent(
            event_id=f"le_regime_{outcome.market_regime_at_decision}_{outcome.outcome_id}",
            outcome_id=outcome.outcome_id,
            event_type="knowledge_update",
            target_type="market_regime",
            target_id=outcome.market_regime_at_decision,
            old_value=None,
            new_value=None,
            metadata={
                'outcome_pnl': outcome.net_pnl,
                'volatility': outcome.volatility_at_decision,
                'strategy': outcome.strategy_name,
                'action': outcome.action,
                'correct': outcome.net_pnl > 0
            },
            timestamp=datetime.now()
        )
        events.append(event)
        
        return events
    
    async def _store_outcome(self, outcome) -> None:
        """Store outcome record to database - Outcome, Attribution, and LearningEvent ORM models."""
        try:
            from backend.db import get_session
            from backend.models import TradeHistory, JournalEntry, Outcome, Attribution, LearningEvent
            from datetime import datetime
            
            session = get_session()
            try:
                # 1. Store Outcome ORM record (OPEN position at entry)
                outcome_orm = Outcome(
                    id=outcome.outcome_id,
                    decision_id=outcome.decision_id,
                    order_id=int(outcome.order_id) if outcome.order_id.isdigit() else None,
                    entry_fill_id=outcome.fill_id,  # entry fill
                    exit_fill_id=None,  # not closed yet
                    symbol=outcome.symbol,
                    action=outcome.action,
                    quantity=outcome.filled_size,
                    entry_price=outcome.filled_price,
                    exit_price=None,  # NULL until closed
                    fees=outcome.commission,
                    commission=outcome.commission,
                    slippage=outcome.slippage,
                    spread_cost=outcome.spread_cost,
                    pnl=None,  # NULL until closed
                    status='OPEN',
                    timestamp=outcome.fill_timestamp,
                    close_timestamp=None
                )
                session.add(outcome_orm)
                
                # 2. Store Attribution ORM records (initial attribution at entry)
                for attr in outcome.attributions:
                    attribution_orm = Attribution(
                        id=f"attr_{attr.component.value}_{outcome.outcome_id}",
                        outcome_id=outcome.outcome_id,
                        component=attr.component.value,
                        value=attr.value,
                        percentage=attr.percentage,
                        confidence=attr.confidence,
                        details=attr.details
                    )
                    session.add(attribution_orm)
                
                # 3. Store LearningEvent ORM records (initial learning at entry)
                learning_events = self._generate_learning_events(outcome)
                for le in learning_events:
                    learning_event_orm = LearningEvent(
                        id=le.event_id,
                        outcome_id=le.outcome_id,
                        event_type=le.event_type,
                        target_type=le.target_type,
                        target_id=le.target_id,
                        old_value=le.old_value,
                        new_value=le.new_value,
                        event_metadata=le.metadata,
                        timestamp=le.timestamp
                    )
                    session.add(learning_event_orm)
                # 4. Store in TradeHistory
                trade = TradeHistory(
                    decision_id=outcome.decision_id,
                    outcome_id=outcome.outcome_id,
                    order_id=outcome.order_id,
                    symbol=outcome.symbol,
                    action=outcome.action,
                    quantity=outcome.filled_size,
                    price=outcome.filled_price,
                    pnl=None,  # No P&L until closed
                    commission=outcome.commission,
                    slippage=outcome.slippage,
                    timestamp=outcome.fill_timestamp,
                    meta=outcome.to_dict()
                )
                session.add(trade)
                
                # 5. Store in JournalEntry for human review
                journal = JournalEntry(
                    trade_id=outcome.outcome_id,
                    decision_id=outcome.decision_id,
                    symbol=outcome.symbol,
                    action=outcome.action,
                    result='OPEN',  # Position is open
                    pnl=None,
                    confidence=outcome.strategy_confidence,
                    notes=f"Position opened. Attribution: {len(outcome.attributions)} components."
                )
                session.add(journal)
                
                session.commit()
                logger.info(f"Stored OPEN position {outcome.outcome_id} with {len(outcome.attributions)} attributions and {len(learning_events)} learning events to database")
                
            finally:
                session.close()
        except Exception as e:
            logger.error(f"Failed to store outcome: {e}")

    async def close_position(self, ctx: DecisionContext, exit_price: float, exit_timestamp: datetime = None) -> DecisionContext:
            """Close an open position and create realized outcome with attribution."""
            try:
                if not ctx.position_id:
                    logger.warning(f"No position_id to close for decision {ctx.decision_id}")
                    return ctx
            
                from backend.db import get_session
                from backend.models import TradeHistory, JournalEntry, Outcome, Attribution, LearningEvent, PaperPosition
                from backend.attribution.attribution_engine import AttributionEngine, AttributionResult, AttributionComponent
            
                session = get_session()
                try:
                    # Get the open position
                    position = session.query(PaperPosition).filter_by(id=ctx.position_id).first()
                    if not position:
                        logger.error(f"Position {ctx.position_id} not found")
                        return ctx
                
                    if position.status == 'CLOSED':
                        logger.warning(f"Position {ctx.position_id} already closed")
                        return ctx
                
                    # Calculate P&L
                    entry_price = position.entry_price
                    quantity = position.quantity
                    action = position.side
                
                    direction_mult = 1 if action == 'BUY' else -1
                    price_change = exit_price - entry_price
                    gross_pnl = price_change * quantity * direction_mult
                
                    commission = position.commission or 0.0
                    slippage = position.slippage or 0.0
                    spread_cost = position.spread_cost or 0.0
                    net_pnl = gross_pnl - commission - slippage - spread_cost
                
                    # Update position record
                    position.exit_price = exit_price
                    position.realized_pnl = net_pnl
                    position.status = 'CLOSED'
                    position.exit_timestamp = exit_timestamp or datetime.now()
                
                    # Create Outcome record (realized outcome)
                    outcome_id = f"out_{ctx.decision_id.split('_')[-1]}_{datetime.now().strftime('%H%M%S')}"
                    outcome = Outcome(
                        id=outcome_id,
                        decision_id=position.decision_id,
                        position_id=position.id,
                        symbol=position.symbol,
                        action=position.side,
                        quantity=position.quantity,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        commission=commission,
                        slippage=slippage,
                        spread_cost=spread_cost,
                        pnl=net_pnl,
                        timestamp=position.exit_timestamp,
                    )
                    session.add(outcome)
                
                    # Run attribution on realized outcome
                    from backend.attribution.attribution_engine import create_outcome_from_decision, OutcomeRecord
                
                    # Rebuild the context needed for attribution
                    attributed_outcome = OutcomeRecord(
                        outcome_id=outcome_id,
                        decision_id=position.decision_id,
                        order_id=str(position.entry_order_id) if position.entry_order_id else '',
                        fill_id=position.entry_fill_id or '',
                        symbol=position.symbol,
                        action=position.side,
                        requested_size=quantity,
                        filled_size=quantity,
                        requested_price=entry_price,
                        filled_price=entry_price,
                        stop_loss=None,
                        take_profit=None,
                        decision_timestamp=position.entry_timestamp,
                        order_timestamp=position.entry_timestamp,
                        fill_timestamp=position.entry_timestamp,
                        close_timestamp=position.exit_timestamp,
                        gross_pnl=gross_pnl,
                        net_pnl=net_pnl,
                        commission=commission,
                        slippage=slippage,
                        spread_cost=spread_cost,
                        market_price_at_decision=entry_price,
                        market_regime_at_decision=position.regime or 'unknown',
                        volatility_at_decision=0.0,
                        market_price_at_close=exit_price,
                        market_regime_at_close='unknown',
                        volatility_at_close=0.0,
                        strategy_name=position.strategy_id or 'unknown',
                        strategy_confidence=0.5,
                        agent_votes={},
                        debate_result=None,
                        ceo_decision=None,
                        risk_governance='APPROVE',
                        position_size_method='unknown'
                    )
                
                    attribution_engine = AttributionEngine(
                        market_data=self.market_data,
                        strategy_engine=self.strategy_engine
                    )
                    attributed_outcome = attribution_engine.attribute_outcome(attributed_outcome)
                
                    # Store attribution records
                    for attr in attributed_outcome.attributions:
                        attribution_orm = Attribution(
                            id=f"attr_{attr.component.value}_{outcome_id}",
                            outcome_id=outcome_id,
                            component=attr.component.value,
                            value=attr.value,
                            percentage=attr.percentage,
                            confidence=attr.confidence,
                            details=attr.details
                        )
                        session.add(attribution_orm)
                
                    # Generate and store learning events from realized outcome
                    learning_events = self._generate_learning_events(attributed_outcome)
                    for le in learning_events:
                        learning_event_orm = LearningEvent(
                            id=le.event_id,
                            outcome_id=le.outcome_id,
                            event_type=le.event_type,
                            target_type=le.target_type,
                            target_id=le.target_id,
                            old_value=le.old_value,
                            new_value=le.new_value,
                            event_metadata=le.metadata,
                            timestamp=le.timestamp
                        )
                        session.add(learning_event_orm)
                
                    # Update TradeHistory
                    trade = session.query(TradeHistory).filter_by(outcome_id=outcome_id).first()
                    if not trade:
                        trade = TradeHistory(
                            decision_id=outcome.decision_id,
                            outcome_id=outcome_id,
                            order_id=position.entry_order_id,
                            symbol=position.symbol,
                            action=position.side,
                            quantity=position.quantity,
                            price=entry_price,
                            pnl=net_pnl,
                            commission=commission,
                            slippage=slippage,
                            timestamp=position.exit_timestamp,
                            meta=attributed_outcome.to_dict()
                        )
                        session.add(trade)
                    else:
                        trade.pnl = net_pnl
                        trade.meta = attributed_outcome.to_dict()
                
                    # Update JournalEntry
                    journal = session.query(JournalEntry).filter_by(trade_id=outcome_id).first()
                    if not journal:
                        journal = JournalEntry(
                            trade_id=outcome_id,
                            decision_id=outcome.decision_id,
                            symbol=position.symbol,
                            action=position.side,
                            result='WIN' if net_pnl > 0 else 'LOSS',
                            pnl=net_pnl,
                            confidence=0.5,
                            notes=f"Position closed. Attribution: {len(attributed_outcome.attributions)} components. "
                                    f"Market Beta: {next((a.value for a in attributed_outcome.attributions if a.component.value == 'market_beta'), 0):.2f}, "
                                    f"Strategy Alpha: {next((a.value for a in attributed_outcome.attributions if a.component.value == 'strategy_alpha'), 0):.2f}, "
                                    f"Execution Cost: {next((a.value for a in attributed_outcome.attributions if a.component.value == 'execution_cost'), 0):.2f}"
                        )
                        session.add(journal)
                
                    session.commit()
                
                    # Update context
                    ctx.outcome_id = outcome_id
                    ctx.realized_pnl = net_pnl
                    ctx.attribution_ids = [a.id for a in attributed_outcome.attributions]
                    ctx.learning_event_ids = [le.event_id for le in learning_events]
                    if learning_events:
                        ctx.learning_event_id = learning_events[0].event_id
                    ctx.position_status = 'CLOSED'
                
                    ctx.add_provenance("position_closed", {
                        "outcome_id": outcome_id,
                        "exit_price": exit_price,
                        "net_pnl": net_pnl,
                        "attribution_components": len(attributed_outcome.attributions),
                        "learning_events": len(learning_events)
                    })
                
                    logger.info(f"Closed position {position.id}: P&L={net_pnl:.2f}")
                
                finally:
                    session.close()
               
            except Exception as e:
                logger.error(f"Failed to close position: {e}")
                ctx.add_provenance("close_error", {"error": str(e)})
        
            return ctx
    
    def _get_price_history(self, symbol: str, days: int = 50) -> List[float]:
        """Get price history for technical analysis."""
        if self.market_data and hasattr(self.market_data, 'get_price_history'):
            try:
                history = self.market_data.get_price_history(symbol, days)
                if history:
                    return [h['close'] for h in history]
            except Exception:
                pass
        
        raise ValueError(f"Real price history unavailable for {symbol}")
    
    async def _get_portfolio_state(self) -> PortfolioState:
        """Get current portfolio state from database."""
        session = get_session()
        try:
            portfolio = session.query(Portfolio).get(self.portfolio_id)
            if not portfolio:
                # Create default
                return PortfolioState(
                    portfolio_id=self.portfolio_id,
                    total_value=100000.0,
                    cash=100000.0,
                    positions=[],
                    risk_profile='moderate',
                    peak_value=100000.0,
                )
            
            positions = []
            for pos in portfolio.positions:
                positions.append({
                    'symbol': pos.symbol,
                    'quantity': pos.quantity,
                    'avg_price': pos.avg_price,
                })
            
            # Calculate drawdown
            peak = portfolio.current_value or portfolio.initial_capital
            current = portfolio.current_value or portfolio.initial_capital
            drawdown = (peak - current) / peak if peak > 0 else 0
            
            return PortfolioState(
                portfolio_id=portfolio.id,
                total_value=portfolio.current_value or portfolio.initial_capital,
                cash=portfolio.current_value or portfolio.initial_capital - sum(p['quantity'] * p['avg_price'] for p in positions),
                positions=positions,
                risk_profile=portfolio.risk_profile,
                drawdown_pct=drawdown,
                peak_value=peak,
            )
        finally:
            session.close()
    
    @property
    def sentiment_service(self):
        """Return the injected sentiment service or lazily create the shared service."""
        return self._sentiment_service or get_sentiment_service()


# Convenience function for direct pipeline execution
async def run_canonical_decision(symbol: str, **kwargs) -> DecisionContext:
    """Run canonical decision pipeline for a symbol."""
    pipeline = DecisionPipeline(**kwargs)
    return await pipeline.execute_decision(symbol)


# Synchronous wrapper for use in Flask routes
def run_canonical_decision_sync(symbol: str, **kwargs) -> DecisionContext:
    """Synchronous wrapper for canonical decision pipeline."""
    pipeline = DecisionPipeline(**kwargs)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(pipeline.execute_decision(symbol))
    finally:
        loop.close()