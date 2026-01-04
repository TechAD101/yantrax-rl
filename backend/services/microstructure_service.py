import logging
import random
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

class MicrostructureService:
    """
    Simulates high-frequency microstructure signals using statistical models.
    Provides:
    - VWAP Clusters (Institutional Liquidity Pools)
    - Order Book Imbalance (OBI)
    - Net Flow Delta (Institutional vs Retail)
    - Fair Value Gaps (FVG)
    
    NOTE: In a production environment with L2/L3 data, this would connect to 
    tick/orderbook feeds. Currently simulates based on price action signatures.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_microstructure_analytics(self, ticker: str, current_price: float, volume: float) -> Dict[str, Any]:
        """
        Aggregates all microstructure metrics for a ticker.
        """
        vwap = self._calculate_vwap_clusters(current_price, volume)
        obi = self._calculate_obi(volume) # Order Book Imbalance
        flows = self._simulate_net_flows(volume)
        fvg = self._detect_fvg(current_price)
        
        return {
            'ticker': ticker,
            'price': current_price,
            'vwap_clusters': vwap,
            'obi': obi,
            'net_flows': flows,
            'fvg': fvg,
            'timestamp': datetime.now().isoformat()
        }

    def _calculate_vwap_clusters(self, price: float, volume: float) -> Dict[str, Any]:
        """
        Simulates VWAP clusters where "smart money" is supposedly trapped.
        """
        # Simulate an anchored VWAP level
        anchor_vwap = price * random.uniform(0.98, 1.02)
        dev_1 = anchor_vwap + (anchor_vwap * 0.01)
        dev_minus_1 = anchor_vwap - (anchor_vwap * 0.01)
        
        # Determine if price is above/below VWAP
        status = "Bullish" if price > anchor_vwap else "Bearish"
        
        return {
            'anchored_vwap': round(anchor_vwap, 2),
            'upper_band_1': round(dev_1, 2),
            'lower_band_1': round(dev_minus_1, 2),
            'status': status,
            'narrative': f"Price is {'holding above' if status == 'Bullish' else 'rejected by'} institutional VWAP."
        }

    def _calculate_obi(self, volume: float) -> Dict[str, Any]:
        """
        Simulates Order Book Imbalance (OBI).
        OBI = (Bid Vol - Ask Vol) / (Bid Vol + Ask Vol)
        Range: -1 to +1
        """
        # Random noise with slight bias based on volume
        # High volume often implies imbalance
        bias = random.uniform(-0.3, 0.3)
        obi_val = bias + random.uniform(-0.1, 0.1)
        obi_val = max(-1, min(1, obi_val)) # Clamp
        
        signal = "Neutral"
        if obi_val > 0.2: signal = "Buying Pressure"
        elif obi_val < -0.2: signal = "Selling Pressure"
        
        return {
            'value': round(obi_val, 2),
            'signal': signal,
            'interpretation': f"Order book shows net {'bids' if obi_val > 0 else 'offers'} dominating."
        }

    def _simulate_net_flows(self, volume: float) -> Dict[str, Any]:
        """
        Simulates Institutional (Smart Money) vs Retail (Dumb Money) flows.
        """
        # Institutional flow usually correlates with price direction but is 'stickier'
        inst_flow_mm = (volume * random.uniform(0.1, 0.4)) / 1_000_000 # Fake $ value
        retail_flow_mm = (volume * random.uniform(0.05, 0.2)) / 1_000_000
        
        # Randomize direction
        if random.random() > 0.5: inst_flow_mm *= -1
        if random.random() > 0.5: retail_flow_mm *= -1
        
        return {
            'institutional_mm': round(inst_flow_mm, 2),
            'retail_mm': round(retail_flow_mm, 2),
            'net_delta': round(inst_flow_mm + retail_flow_mm, 2),
            'divergence': "Yes" if (inst_flow_mm > 0 and retail_flow_mm < 0) or (inst_flow_mm < 0 and retail_flow_mm > 0) else "No"
        }

    def _detect_fvg(self, price: float) -> Dict[str, Any]:
        """
        Detects simulated Fair Value Gaps (inefficiencies).
        """
        has_fvg = random.random() > 0.7 # 30% chance of FVG nearby
        
        if has_fvg:
            direction = "Bullish" if random.random() > 0.5 else "Bearish"
            gap_price = price * (1.02 if direction == "Bearish" else 0.98)
            return {
                'detected': True,
                'type': direction,
                'target_price': round(gap_price, 2),
                'gap_size_pct': 2.0
            }
        
        return {
            'detected': False,
            'type': "None",
            'target_price': None,
            'gap_size_pct': 0
        }
