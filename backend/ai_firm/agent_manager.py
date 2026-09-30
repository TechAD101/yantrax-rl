"""Enhanced Agent Manager for YantraX RL

Integrates with existing Flask structure while adding 20+ agent coordination.
"""

import logging
import uuid
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.services.oracle_service import OracleService, OracleInsight


class Agent:
    """Lightweight Agent representation used by the package API."""

    def __init__(self, name: str, confidence: float = 0.5, role: str = "analyst", **kwargs):
        self.name = name
        self.confidence = confidence
        self.role = role
        for k, v in kwargs.items():
            setattr(self, k, v)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}


class AgentDecision:
    """Simple container for an agent decision/result."""

    def __init__(self, agent_name: str, decision: str, confidence: float = 0.5):
        self.agent_name = agent_name
        self.decision = decision
        self.confidence = confidence

    def as_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "decision": self.decision,
            "confidence": self.confidence,
        }


class AgentManager:
    """Manages enhanced agent coordination for YantraX."""

    def __init__(self, oracle_service: Optional[OracleService] = None):
        self.enhanced_agents = self._initialize_20_plus_agents()
        self.voting_sessions = []
        self.logger = logging.getLogger(__name__)
        self.oracle = oracle_service
        self.kb = None

    def _initialize_20_plus_agents(self) -> Dict[str, Dict]:
        return {
            "warren": {"confidence": 0.88, "performance": 24.5, "specialty": "Value Analysis", "department": "market_intelligence", "role": "director", "persona": True},
            "cathie": {"confidence": 0.82, "performance": 21.8, "specialty": "Innovation Scouting", "department": "market_intelligence", "role": "senior", "persona": True},
            "quant": {"confidence": 0.90, "performance": 26.3, "specialty": "Statistical Modeling", "department": "market_intelligence", "role": "senior", "persona": False},
            "sentiment_analyzer": {"confidence": 0.84, "performance": 22.1, "specialty": "Market Sentiment", "department": "market_intelligence", "role": "specialist", "persona": False},
            "news_interpreter": {"confidence": 0.79, "performance": 19.6, "specialty": "News Analysis", "department": "market_intelligence", "role": "analyst", "persona": False},
            "trade_executor": {"confidence": 0.91, "performance": 28.1, "specialty": "Order Execution", "department": "trade_operations", "role": "director", "persona": False},
            "portfolio_optimizer": {"confidence": 0.86, "performance": 23.7, "specialty": "Asset Allocation", "department": "trade_operations", "role": "senior", "persona": False},
            "liquidity_hunter": {"confidence": 0.79, "performance": 19.4, "specialty": "Market Timing", "department": "trade_operations", "role": "specialist", "persona": False},
            "arbitrage_scout": {"confidence": 0.75, "performance": 17.2, "specialty": "Cross-Market Analysis", "department": "trade_operations", "role": "analyst", "persona": False},
            "var_guardian": {"confidence": 0.87, "performance": 25.6, "specialty": "VaR Modeling", "department": "risk_control", "role": "senior", "persona": False},
            "correlation_detective": {"confidence": 0.81, "performance": 20.9, "specialty": "Systemic Risk", "department": "risk_control", "role": "specialist", "persona": False},
            "black_swan_sentinel": {"confidence": 0.77, "performance": 18.3, "specialty": "Tail Risk", "department": "risk_control", "role": "analyst", "persona": False},
            "stress_tester": {"confidence": 0.83, "performance": 21.7, "specialty": "Scenario Analysis", "department": "risk_control", "role": "specialist", "persona": False},
            "performance_analyst": {"confidence": 0.89, "performance": 27.4, "specialty": "Performance Attribution", "department": "performance_lab", "role": "director", "persona": False},
            "alpha_hunter": {"confidence": 0.84, "performance": 22.8, "specialty": "Alpha Generation", "department": "performance_lab", "role": "senior", "persona": False},
            "backtesting_engine": {"confidence": 0.88, "performance": 25.1, "specialty": "Strategy Validation", "department": "performance_lab", "role": "specialist", "persona": False},
            "ml_optimizer": {"confidence": 0.86, "performance": 24.3, "specialty": "ML Model Optimization", "department": "performance_lab", "role": "specialist", "persona": False},
            "macro_monk": {"confidence": 0.92, "performance": 31.2, "specialty": "Geopolitical / War Economics", "department": "market_intelligence", "role": "director", "persona": True},
            "the_ghost": {"confidence": 0.95, "performance": 42.0, "specialty": "Divine Doubt / Paradox Injection", "department": "risk_control", "role": "director", "persona": True},
            "degen_auditor": {"confidence": 0.88, "performance": 25.5, "specialty": "Degenerate Risk Mitigation", "department": "risk_control", "role": "senior", "persona": True},
            "risk_auditor": {"confidence": 0.85, "performance": 23.2, "specialty": "Risk Compliance", "department": "risk_control", "role": "specialist", "persona": False},
            "market_observer": {"confidence": 0.80, "performance": 20.5, "specialty": "Market Microstructure", "department": "market_intelligence", "role": "analyst", "persona": False},
            "compliance_officer": {"confidence": 0.82, "performance": 21.3, "specialty": "Regulatory Compliance", "department": "communications", "role": "director", "persona": False},
            "communications_lead": {"confidence": 0.78, "performance": 18.9, "specialty": "Stakeholder Relations", "department": "communications", "role": "senior", "persona": False},
        }

    def _ensure_kb(self):
        """Load KB lazily and isolate its optional failure from agent voting."""
        if self.kb is not None:
            return self.kb
        try:
            from backend.services.knowledge_base_service import get_knowledge_base
            self.kb = get_knowledge_base()
        except Exception as exc:
            self.logger.warning("Knowledge base initialization unavailable; voting will continue without KB enrichment: %s", exc)
            self.kb = False
        return self.kb

    def conduct_agent_voting(self, context: Dict[str, Any], expert_opinions: Dict[str, str] = None) -> Dict[str, Any]:
        vote_tally = {}
        total_weight = 0
        participating_agents = []

        for agent_name, agent_data in self.enhanced_agents.items():
            signal = expert_opinions[agent_name] if expert_opinions and agent_name in expert_opinions else self._generate_agent_signal(agent_name, agent_data, context)
            weight = self._get_vote_weight(agent_data["role"]) * agent_data["confidence"]
            vote_tally[signal] = vote_tally.get(signal, 0) + weight
            total_weight += weight
            participating_agents.append({
                "name": agent_name,
                "signal": signal,
                "confidence": agent_data["confidence"],
                "weight": weight,
                "department": agent_data["department"],
                "role": agent_data["role"],
                "specialty": agent_data["specialty"],
                "persona": agent_data.get("persona", False),
            })

        divine_doubt_triggered = False
        oracle_wisdom = None
        winning_signal = max(vote_tally.items(), key=lambda x: x[1])[0] if vote_tally else "HOLD"
        consensus_strength = (vote_tally[winning_signal] / total_weight) if vote_tally and total_weight > 0 else 0.5

        if vote_tally and consensus_strength > 0.9 and "the_ghost" in self.enhanced_agents:
            self.logger.info("Divine Doubt triggered: consensus too high (%s)", consensus_strength)
            winning_signal = "HOLD_FOR_CLARITY"
            consensus_strength *= 0.7
            divine_doubt_triggered = True

        if self.oracle:
            try:
                import asyncio
                symbol = context.get("symbol", "MARKET")
                try:
                    asyncio.get_running_loop()
                    self.logger.debug("Oracle call skipped inside running event loop")
                except RuntimeError:
                    oracle_insight = asyncio.run(self.oracle.get_divine_whisper(symbol, context, consensus_strength))
                    if oracle_insight:
                        oracle_wisdom = {
                            "perspective": oracle_insight.perspective,
                            "wisdom": oracle_insight.wisdom,
                            "paradox": oracle_insight.paradox,
                            "direction": oracle_insight.direction,
                        }
            except Exception as exc:
                self.logger.error("Oracle integration error: %s", exc)

        result = {
            "winning_signal": winning_signal,
            "consensus_strength": round(consensus_strength, 3),
            "vote_distribution": {k: round(v / total_weight, 3) for k, v in vote_tally.items()} if total_weight else {},
            "participating_agents": len(participating_agents),
            "total_weight": round(total_weight, 2),
            "session_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "divine_doubt_applied": divine_doubt_triggered,
            "oracle_wisdom": oracle_wisdom,
            "agent_votes": participating_agents,
        }
        self.voting_sessions.append(result)
        return result

    def _generate_agent_signal(self, agent_name: str, agent_data: Dict, context: Dict = None) -> str:
        confidence = agent_data["confidence"]
        specialty = agent_data.get("specialty", "")
        market_condition = context.get("market_trend", "neutral") if context else "neutral"
        fundamentals = context.get("fundamentals", {}) if context else {}
        pe_ratio = fundamentals.get("pe_ratio", 0)
        roe = fundamentals.get("return_on_equity", 0)
        debt_to_equity = fundamentals.get("debt_to_equity", 0)
        rsi = context.get("rsi", 50) if context else 50
        trend = context.get("market_trend", "neutral") if context else "neutral"

        kb = self._ensure_kb()
        if kb and kb is not False:
            try:
                query = f"{specialty} in {market_condition} market"
                wisdom_items = kb.query_wisdom(topic=query, archetype_filter=agent_name, max_results=1) or []
                if wisdom_items and wisdom_items[0].get("relevance_score", 0) > 0.8:
                    confidence = min(0.98, confidence + 0.05)
            except Exception as exc:
                self.logger.warning("Knowledge base query unavailable for %s; continuing without enrichment: %s", agent_name, exc)

        if agent_name == "warren" or "Value" in specialty:
            if 0 < pe_ratio < 22 and roe > 0.18 and debt_to_equity < 1.0: return "BUY"
            if pe_ratio > 40 or debt_to_equity > 3.0: return "SELL"
            return "HOLD"
        elif agent_name == "cathie" or "Innovation" in specialty:
            if rsi > 60 and trend == "bullish": return "HIGH_CONVICTION_BUY" if confidence > 0.85 else "BUY"
            if rsi < 30: return "HOLD"
            return "HOLD"
        elif agent_name == "macro_monk":
            if debt_to_equity < 0.5 and trend == "bullish": return "BUY"
            if debt_to_equity > 5.0: return "SELL"
            return "HOLD"
        elif agent_name == "degen_auditor":
            if debt_to_equity > 4.0 or pe_ratio > 100: return "REJECT"
            return "APPROVED"
        elif agent_name == "the_ghost":
            if rsi > 85: return "SELL"
            if rsi < 15: return "BUY"
            return "WHISPER_HOLD"
        elif "Statistical" in specialty or "Quant" in agent_name:
            if trend == "bullish" and rsi < 70: return "BUY"
            if trend == "bearish" or rsi > 80: return "SELL"
            return "HOLD"
        elif "Risk" in specialty or "VaR" in specialty:
            if debt_to_equity > 2.5 or trend == "bearish": return "REJECT"
            return "APPROVED" if confidence > 0.8 else "CAUTION"
        if trend == "bullish": return "BUY"
        if trend == "bearish": return "SELL"
        return "HOLD"

    def coordinate_decision_making(self, context: Dict[str, Any]) -> Dict[str, Any]:
        result = self.conduct_agent_voting(context)
        mapped = dict(result)
        if "winning_signal" in result and "winning_recommendation" not in result:
            mapped["winning_recommendation"] = result["winning_signal"]
        if "participating_agents" in result and "total_votes" not in result:
            mapped["total_votes"] = result["participating_agents"]
        return mapped

    def _get_vote_weight(self, role: str) -> float:
        if role is None:
            return 0.5
        return {"director": 1.0, "senior": 0.8, "specialist": 0.6, "analyst": 0.4}.get(role, 0.5)

    def get_agent_status(self) -> Dict[str, Any]:
        department_breakdown = {}
        for dept in ["market_intelligence", "trade_operations", "risk_control", "performance_lab", "communications"]:
            dept_agents = [(name, data) for name, data in self.enhanced_agents.items() if data.get("department") == dept]
            if dept_agents:
                department_breakdown[dept] = {
                    "agent_count": len(dept_agents),
                    "agents": [{
                        "name": name,
                        "confidence": data["confidence"],
                        "performance": data["performance"],
                        "role": data["role"],
                        "specialty": data["specialty"],
                        "persona": data.get("persona", False),
                    } for name, data in dept_agents],
                    "avg_confidence": round(np.mean([data["confidence"] for _, data in dept_agents]), 3),
                    "avg_performance": round(np.mean([data["performance"] for _, data in dept_agents]), 2),
                }
        all_agents_list = []
        for dept, info in department_breakdown.items():
            for agent in info.get("agents", []):
                all_agents_list.append({
                    "name": agent.get("name"),
                    "confidence": agent.get("confidence"),
                    "performance": agent.get("performance"),
                    "department": dept,
                    "role": agent.get("role"),
                    "specialty": agent.get("specialty"),
                    "persona": agent.get("persona", False),
                })
        departments_simple = {dept: info.get("agents", []) for dept, info in department_breakdown.items()}
        departments_counts = {dept: info.get("agent_count", len(info.get("agents", []))) for dept, info in department_breakdown.items()}
        return {
            "total_agents": len(self.enhanced_agents),
            "departments": department_breakdown,
            "departments_simple": departments_simple,
            "departments_counts": departments_counts,
            "recent_voting_sessions": len(self.voting_sessions),
            "personas_active": len([a for a in self.enhanced_agents.values() if a.get("persona", False)]),
            "all_agents": all_agents_list,
            "sample_agents": {dept: agents[0] if isinstance(agents, list) and agents else None for dept, agents in departments_simple.items()},
        }
