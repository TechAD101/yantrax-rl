"""
YantraX Marketplace Service ("The Social Layer")

Handles:
1. Strategy Publishing (Metadata + Code/Logic)
2. Copy-Trading Logic (Subscribing to a strategy)
3. Quant Contests (Leaderboards & Scoring)
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class MarketplaceService:
    def __init__(self):
        self.strategies = self._seed_mock_strategies()
        self.copiers = {} # map strategy_id -> list of copier_user_ids
        self.contests = self._init_contests()

    def _seed_mock_strategies(self) -> Dict[str, Dict]:
        """Seed with some 'World Class' strategies for the leaderboard"""
        return {
            "strat_001": {
                "id": "strat_001",
                "name": "Momemtum Alpha Prime",
                "author": "DeepMindQuant",
                "description": "High-frequency momentum scalping on BTC/ETH pairs.",
                "win_rate": 0.68,
                "sharpe_ratio": 2.4,
                "aum": 1540000, # $1.5M mocked
                "type": "MOMENTUM",
                "created_at": (datetime.now() - timedelta(days=45)).isoformat()
            },
            "strat_002": {
                "id": "strat_002",
                "name": "Slow Turtle Value",
                "author": "WarrenFan99",
                "description": "Long-term value investing based on P/E and FCF.",
                "win_rate": 0.55,
                "sharpe_ratio": 1.8,
                "aum": 4200000, 
                "type": "VALUE",
                "created_at": (datetime.now() - timedelta(days=120)).isoformat()
            },
             "strat_003": {
                "id": "strat_003",
                "name": "Degen Moonshot v4",
                "author": "CryptoKing",
                "description": "Memecoin rotation strategy. High risk, extreme reward.",
                "win_rate": 0.35, # Low win rate
                "sharpe_ratio": 1.1,
                "aum": 50000, 
                "type": "DEGEN",
                "created_at": (datetime.now() - timedelta(days=10)).isoformat()
            }
        }
    
    def _init_contests(self) -> Dict[str, Dict]:
        return {
            "contest_weekly": {
                "id": "contest_2026_01_w2",
                "title": "Weekly Alpha Hunt",
                "prize_pool": "$5,000",
                "participants": 124,
                "rules": "Max drawdown < 10%. Sharpe > 1.5.",
                "status": "ACTIVE",
                "ends_in": "3 days"
            }
        }

    def publish_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a new user strategy"""
        strat_id = str(uuid.uuid4())[:8]
        new_strat = {
            "id": strat_id,
            "name": data.get("name", "Untitled Strategy"),
            "author": data.get("author", "Anonymous"),
            "description": data.get("description", ""),
            "win_rate": 0.0, # Fresh strategy
            "sharpe_ratio": 0.0,
            "aum": 0,
            "type": data.get("type", "CUSTOM"),
            "created_at": datetime.now().isoformat()
        }
        self.strategies[strat_id] = new_strat
        return new_strat

    def get_top_strategies(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard sorted by Sharpe Ratio"""
        # Convert dict to list
        strat_list = list(self.strategies.values())
        # Sort desc by sharpe
        strat_list.sort(key=lambda x: x['sharpe_ratio'], reverse=True)
        return strat_list[:limit]

    def copy_strategy(self, strategy_id: str, user_id: str, amount: float) -> Dict[str, Any]:
        """Register a user as a copier of a strategy"""
        if strategy_id not in self.strategies:
            return {"error": "Strategy not found", "success": False}
        
        if strategy_id not in self.copiers:
            self.copiers[strategy_id] = []
            
        self.copiers[strategy_id].append({
            "user_id": user_id,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        
        # Mock AUM update
        self.strategies[strategy_id]['aum'] += amount
        
        return {
            "success": True,
            "message": f"Successfully copied {self.strategies[strategy_id]['name']}",
            "allocated": amount
        }
        
    def get_active_contest(self) -> Dict[str, Any]:
        return self.contests["contest_weekly"]
