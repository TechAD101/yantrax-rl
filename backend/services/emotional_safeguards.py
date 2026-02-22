"""
YantraX Emotional Safeguards Service v1.0
==========================================
Psychological protection layer preventing emotionally-driven trading decisions.

Features:
- Fear/Greed state tracking with multi-signal input
- Drawdown-triggered lockdown (Mouna Mode)
- Overconfidence suppressor
- Revenge-trade detector
- Cooling-off periods with timestamps
- Full audit trail for every intervention
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json


class EmotionalState(Enum):
    CALM      = "calm"
    ANXIOUS   = "anxious"
    FEARFUL   = "fearful"
    GREEDY    = "greedy"
    EUPHORIC  = "euphoric"
    PANICKED  = "panicked"
    MOUNA     = "mouna"      # Silent mode — no trades allowed


class SafeguardTrigger(Enum):
    DRAWDOWN_5PCT    = "drawdown_5pct"
    DRAWDOWN_10PCT   = "drawdown_10pct"
    DRAWDOWN_20PCT   = "drawdown_20pct"
    RAPID_LOSSES     = "rapid_losses_3_consecutive"
    OVERCONFIDENCE   = "overconfidence_>90pct"
    REVENGE_TRADE    = "revenge_trade_detected"
    VOLATILITY_SPIKE = "volatility_spike"
    MANUAL_OVERRIDE  = "manual_override"


@dataclass
class SafeguardEvent:
    """Immutable record of a safeguard intervention"""
    id: str
    timestamp: str
    trigger: str
    emotional_state: str
    action_taken: str
    context: Dict[str, Any]
    cooling_off_until: Optional[str] = None
    overridden: bool = False


class EmotionalSafeguardsService:
    """
    Psychological safeguard layer for the YantraX AI trading firm.
    
    Monitors emotional indicators and enforces trading restrictions
    when psychologically unsafe conditions are detected.
    """

    # Cooling-off durations per trigger severity
    COOLING_OFF_DURATIONS = {
        SafeguardTrigger.DRAWDOWN_5PCT:    timedelta(minutes=30),
        SafeguardTrigger.DRAWDOWN_10PCT:   timedelta(hours=2),
        SafeguardTrigger.DRAWDOWN_20PCT:   timedelta(hours=24),
        SafeguardTrigger.RAPID_LOSSES:     timedelta(hours=1),
        SafeguardTrigger.OVERCONFIDENCE:   timedelta(minutes=15),
        SafeguardTrigger.REVENGE_TRADE:    timedelta(hours=4),
        SafeguardTrigger.VOLATILITY_SPIKE: timedelta(minutes=45),
        SafeguardTrigger.MANUAL_OVERRIDE:  timedelta(hours=6),
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._state: EmotionalState = EmotionalState.CALM
        self._pain_level: int = 0           # 0-100
        self._events: List[SafeguardEvent]  = []
        self._cooling_off_until: Optional[datetime] = None
        self._consecutive_losses: int = 0
        self._last_trade_result: Optional[str] = None   # "win" | "loss"
        self._peak_portfolio_value: float = 0.0
        self._current_portfolio_value: float = 0.0
        self._overconfidence_streak: int = 0
        self.logger.info("✅ Emotional Safeguards Service initialized")

    # ─────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────

    def update_state(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update emotional state from market/portfolio context.
        Call this after every god-cycle or trade event.

        Expected keys in context:
          portfolio_value, peak_portfolio_value, trade_result ("win"|"loss"),
          market_volatility (0-1), agent_confidence (0-1)
        """
        # 1. Update portfolio tracking
        portfolio_value = context.get("portfolio_value", self._current_portfolio_value)
        peak_value      = context.get("peak_portfolio_value", self._peak_portfolio_value)

        if portfolio_value > 0:
            self._current_portfolio_value = portfolio_value
        if peak_value > self._peak_portfolio_value:
            self._peak_portfolio_value = peak_value

        # 2. Calculate drawdown
        drawdown_pct = self._calculate_drawdown()

        # 3. Update consecutive loss counter
        trade_result = context.get("trade_result")
        if trade_result == "loss":
            self._consecutive_losses += 1
        elif trade_result == "win":
            self._consecutive_losses = 0
        self._last_trade_result = trade_result

        # 4. Overconfidence tracking
        agent_confidence = context.get("agent_confidence", 0.0)
        if agent_confidence > 0.9:
            self._overconfidence_streak += 1
        else:
            self._overconfidence_streak = 0

        # 5. Determine emotional state
        prev_state = self._state
        self._state = self._classify_emotional_state(
            drawdown_pct=drawdown_pct,
            consecutive_losses=self._consecutive_losses,
            market_volatility=context.get("market_volatility", 0.3),
            agent_confidence=agent_confidence,
        )

        # 6. Update pain level (0-100)
        self._pain_level = self._calculate_pain_level(drawdown_pct)

        # 7. Trigger safeguards if needed
        triggered = self._check_triggers(context, drawdown_pct)

        if prev_state != self._state:
            self.logger.info(f"🧠 Emotional state: {prev_state.value} → {self._state.value}")

        return self.get_status()

    def is_trading_allowed(self) -> Dict[str, Any]:
        """
        Gate check — call before every trade attempt.
        Returns {allowed: bool, reason: str, cooling_off_remaining_seconds: int}
        """
        if self._state == EmotionalState.MOUNA:
            return {
                "allowed": False,
                "reason": "MOUNA_MODE: System in silent cooling-off period",
                "cooling_off_remaining_seconds": self._cooling_off_remaining(),
                "emotional_state": self._state.value,
            }

        if self._cooling_off_until and datetime.now() < self._cooling_off_until:
            remaining = int((self._cooling_off_until - datetime.now()).total_seconds())
            return {
                "allowed": False,
                "reason": f"COOLING_OFF: Safeguard active for {remaining}s",
                "cooling_off_remaining_seconds": remaining,
                "emotional_state": self._state.value,
            }

        if self._state == EmotionalState.PANICKED:
            return {
                "allowed": False,
                "reason": "PANIC_LOCK: Emotional state is PANICKED. Waiting for calm.",
                "cooling_off_remaining_seconds": 0,
                "emotional_state": self._state.value,
            }

        return {
            "allowed": True,
            "reason": "CLEAR",
            "cooling_off_remaining_seconds": 0,
            "emotional_state": self._state.value,
            "pain_level": self._pain_level,
        }

    def record_trade_outcome(self, outcome: str, pnl: float, ticker: str) -> None:
        """Record a completed trade outcome for safeguard tracking"""
        self._last_trade_result = outcome
        if outcome == "loss":
            self._consecutive_losses += 1
            self.logger.warning(f"❌ Loss recorded: {ticker} PnL={pnl:.2f} | Streak={self._consecutive_losses}")
            # Revenge trade detection: rapid trade attempt right after a max loss
            if abs(pnl) > 0.05 * self._current_portfolio_value:
                self._trigger_safeguard(SafeguardTrigger.REVENGE_TRADE, {
                    "ticker": ticker, "pnl": pnl, "reason": "Large single-trade loss"
                })
        else:
            self._consecutive_losses = 0

    def manual_override(self, reason: str = "User override") -> Dict[str, Any]:
        """Manually triggers a 6-hour Mouna Mode (emergency stop)"""
        self._trigger_safeguard(SafeguardTrigger.MANUAL_OVERRIDE, {"reason": reason})
        return self.get_status()

    def get_status(self) -> Dict[str, Any]:
        """Full status snapshot for API and frontend"""
        cooling_remaining = self._cooling_off_remaining()
        return {
            "emotional_state": self._state.value,
            "pain_level": self._pain_level,
            "trading_allowed": self.is_trading_allowed()["allowed"],
            "cooling_off_active": cooling_remaining > 0,
            "cooling_off_remaining_seconds": cooling_remaining,
            "consecutive_losses": self._consecutive_losses,
            "overconfidence_streak": self._overconfidence_streak,
            "current_drawdown_pct": round(self._calculate_drawdown() * 100, 2),
            "safeguard_events_count": len(self._events),
            "recent_events": [
                {
                    "trigger": e.trigger,
                    "action": e.action_taken,
                    "timestamp": e.timestamp,
                    "cooling_off_until": e.cooling_off_until,
                }
                for e in self._events[-5:]
            ],
            "timestamp": datetime.now().isoformat(),
        }

    def get_event_log(self) -> List[Dict[str, Any]]:
        """Full immutable audit log of all safeguard interventions"""
        return [
            {
                "id": e.id,
                "trigger": e.trigger,
                "emotional_state": e.emotional_state,
                "action_taken": e.action_taken,
                "context": e.context,
                "timestamp": e.timestamp,
                "cooling_off_until": e.cooling_off_until,
            }
            for e in self._events
        ]

    # ─────────────────────────────────────────────────────────────
    # Private Helpers
    # ─────────────────────────────────────────────────────────────

    def _calculate_drawdown(self) -> float:
        """Fraction from peak (0.0 = no drawdown, 0.2 = 20% down from peak)"""
        if self._peak_portfolio_value <= 0 or self._current_portfolio_value <= 0:
            return 0.0
        dd = (self._peak_portfolio_value - self._current_portfolio_value) / self._peak_portfolio_value
        return max(0.0, dd)

    def _calculate_pain_level(self, drawdown_pct: float) -> int:
        """Map drawdown + consecutive losses to 0-100 pain level"""
        base = drawdown_pct * 300  # 10% DD → 30 pain
        loss_bonus = self._consecutive_losses * 8
        pain = min(100, int(base + loss_bonus))
        return pain

    def _classify_emotional_state(
        self,
        drawdown_pct: float,
        consecutive_losses: int,
        market_volatility: float,
        agent_confidence: float,
    ) -> EmotionalState:
        """Rule-based emotional state machine"""
        if drawdown_pct >= 0.20 or consecutive_losses >= 5:
            return EmotionalState.PANICKED
        if self._cooling_off_until and datetime.now() < self._cooling_off_until:
            return EmotionalState.MOUNA
        if drawdown_pct >= 0.10 or consecutive_losses >= 3:
            return EmotionalState.FEARFUL
        if drawdown_pct >= 0.05 or market_volatility > 0.7:
            return EmotionalState.ANXIOUS
        if agent_confidence > 0.9 and drawdown_pct < 0.02:
            return EmotionalState.EUPHORIC
        if agent_confidence > 0.75:
            return EmotionalState.GREEDY
        return EmotionalState.CALM

    def _check_triggers(self, context: Dict[str, Any], drawdown_pct: float) -> List[str]:
        """Check all trigger conditions and fire appropriate safeguards"""
        triggered = []

        if drawdown_pct >= 0.20:
            t = self._trigger_safeguard(SafeguardTrigger.DRAWDOWN_20PCT, context)
            if t: triggered.append(t)
        elif drawdown_pct >= 0.10:
            t = self._trigger_safeguard(SafeguardTrigger.DRAWDOWN_10PCT, context)
            if t: triggered.append(t)
        elif drawdown_pct >= 0.05:
            t = self._trigger_safeguard(SafeguardTrigger.DRAWDOWN_5PCT, context)
            if t: triggered.append(t)

        if self._consecutive_losses >= 3:
            t = self._trigger_safeguard(SafeguardTrigger.RAPID_LOSSES, context)
            if t: triggered.append(t)

        if self._overconfidence_streak >= 3:
            t = self._trigger_safeguard(SafeguardTrigger.OVERCONFIDENCE, context)
            if t: triggered.append(t)

        volatility = context.get("market_volatility", 0.0)
        if volatility > 0.8:
            t = self._trigger_safeguard(SafeguardTrigger.VOLATILITY_SPIKE, context)
            if t: triggered.append(t)

        return triggered

    def _trigger_safeguard(self, trigger: SafeguardTrigger, context: Dict[str, Any]) -> Optional[str]:
        """Fire a safeguard — sets cooling-off, logs event, updates state"""
        duration = self.COOLING_OFF_DURATIONS.get(trigger, timedelta(hours=1))
        now = datetime.now()
        cooling_until = now + duration

        # Don't re-trigger if already cooling off for same or longer period
        if self._cooling_off_until and self._cooling_off_until >= cooling_until:
            return None

        self._cooling_off_until = cooling_until
        self._state = EmotionalState.MOUNA

        action = f"TRADING_SUSPENDED for {int(duration.total_seconds()/60)} minutes"

        import uuid
        event = SafeguardEvent(
            id=str(uuid.uuid4())[:8],
            timestamp=now.isoformat(),
            trigger=trigger.value,
            emotional_state=self._state.value,
            action_taken=action,
            context={k: v for k, v in context.items() if isinstance(v, (str, int, float, bool))},
            cooling_off_until=cooling_until.isoformat(),
        )
        self._events.append(event)
        self.logger.warning(f"🛡️ SAFEGUARD TRIGGERED: {trigger.value} | {action}")
        return trigger.value

    def _cooling_off_remaining(self) -> int:
        """Seconds remaining in cooling-off period"""
        if not self._cooling_off_until:
            return 0
        remaining = (self._cooling_off_until - datetime.now()).total_seconds()
        return max(0, int(remaining))


# ─────────────────────────────────────────────────────────────
# Global singleton
# ─────────────────────────────────────────────────────────────
_safeguards_service: Optional[EmotionalSafeguardsService] = None

def get_emotional_safeguards() -> EmotionalSafeguardsService:
    """Get or create the global EmotionalSafeguardsService singleton"""
    global _safeguards_service
    if _safeguards_service is None:
        _safeguards_service = EmotionalSafeguardsService()
    return _safeguards_service
