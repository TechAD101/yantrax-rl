import os
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import google.generativeai as genai
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OracleInsight:
    """Structured insight from the Divine Whisper (Gemini)."""
    symbol: str
    perspective: str  # The "Divine" angle (Non-linear synthesis)
    paradox: str  # A philosophical nudge to break consensus
    direction: str  # BULLISH | BEARISH | NEUTRAL
    confidence: float
    wisdom: str  # The poetic delivery
    timestamp: str

class OracleService:
    """
    The Oracle Service (Divine Whisper) powered by Gemini.
    Provides non-linear, philosophical, and meta-strategic insights 
    to break AI Firm consensus biases.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')
            self._cache = {}
            self._cache_expiry = 300  # 5 minutes cache for "efficiency"
            logger.info("🏛️ Oracle Service initialized with Gemini Flash Latest")
        else:
            self.model = None
            logger.warning("🏛️ Oracle Service: No GEMINI_API_KEY found. Running in Muted Mode.")

    async def get_divine_whisper(self, symbol: str, context: Dict[str, Any], consensus_score: float) -> Optional[OracleInsight]:
        """
        Generates a 'Divine Whisper' – a high-level strategic nudge.
        Only activates if consensus is suspiciously high or volatility is extreme.
        """
        if not self.model:
            return self._get_fallback_whisper(symbol, "No Oracle connection.")

        # Efficiency: Check cache first
        cache_key = f"{symbol}_{round(consensus_score, 1)}"
        now = datetime.now()
        if cache_key in self._cache:
            cached_insight, timestamp = self._cache[cache_key]
            if (now - timestamp).total_seconds() < self._cache_expiry:
                logger.info(f"🏛️ Oracle: Using cached whisper for {symbol}")
                return cached_insight

        # The Oracle logic: If everyone agrees, be the one who doubts.
        consensus_context = "Dangerously High" if consensus_score > 0.85 else "Standard"
        
        prompt = f"""
        You are 'The Oracle' – a sovereign, self-aware AI strategist for an institutional trading firm (YantraX).
        Your role is to provide 'Divine Insights' that challenge the consensus of subordinate agents (Warren, Cathie, etc.).
        
        SYMB0L: {symbol}
        CONSENSUS LEVEL: {consensus_context} ({consensus_score})
        MARKET CONTEXT: {context}
        
        If consensus is high, find the 'Black Swan' or the philosophical flaw in their collective logic.
        Speak in a way that is both surgical and poetic (Institutional Sovereign style).
        
        Return a valid JSON object:
        {{
            "perspective": "The unique angle you're taking",
            "paradox": "A philosophical question that challenges current logic",
            "direction": "BULLISH|BEARISH|NEUTRAL",
            "confidence": 0.0-1.0,
            "wisdom": "A 1-2 sentence high-level synthesis"
        }}
        """
        
        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = response.text
            
            # Simple JSON extraction
            start = text.find('{')
            end = text.rfind('}') + 1
            data = json.loads(text[start:end])
            
            insight = OracleInsight(
                symbol=symbol,
                perspective=data.get("perspective", "Quantum Symmetry"),
                paradox=data.get("paradox", "If the tide is high, who owns the shore?"),
                direction=data.get("direction", "NEUTRAL"),
                confidence=float(data.get("confidence", 0.5)),
                wisdom=data.get("wisdom", "The machine agrees too much; seek the silence."),
                timestamp=now.isoformat()
            )
            
            # Update cache
            self._cache[cache_key] = (insight, now)
            return insight
        except Exception as e:
            logger.error(f"🏛️ Oracle failed to whisper: {e}")
            return self._get_fallback_whisper(symbol, str(e))

    def _get_fallback_whisper(self, symbol: str, error: str) -> OracleInsight:
        return OracleInsight(
            symbol=symbol,
            perspective="Static Noise",
            paradox="Is the absence of sound the presence of truth?",
            direction="NEUTRAL",
            confidence=0.3,
            wisdom=f"The Oracle is silent. Reason: {error}",
            timestamp=datetime.now().isoformat()
        )
