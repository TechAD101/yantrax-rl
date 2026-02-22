import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TrustScorer:
    """
    Computes Institutional Trust Score and Confidence Bands.
    Weights: Macro (25%), Liquidity (15%), Flows (20%), Derivatives (25%), Microstructure (15%)
    """
    
    WEIGHTS = {
        'macro': 0.25,
        'liquidity': 0.15,
        'flows': 0.20,
        'derivatives': 0.25,
        'microstructure': 0.15
    }

    def __init__(self):
        self.history = {}  # In-memory history cache: ticker -> list of past scores for stdev/confidence band

    def compute_trust_score(self, data_context: Dict[str, float]) -> Dict[str, Any]:
        """
        data_context expects normalized values (0 to 100) for each category.
        e.g., {'macro': 85.0, 'liquidity': 90.0, 'flows': 75.0, 'derivatives': 80.0, 'microstructure': 88.0}
        """
        score = 0.0
        details = {}
        
        for category, weight in self.WEIGHTS.items():
            val = data_context.get(category, 50.0)  # Default neutral 50 if missing
            contrib = val * weight
            score += contrib
            details[category] = {
                'value': val,
                'weight': weight,
                'contribution': round(contrib, 2)
            }
            
        return {
            'total_trust_score': round(score, 2),
            'components': details,
            'formula': 'Sum of (Category Value * Category Weight)'
        }

    def compute_confidence_band(self, ticker: str, current_score: float) -> Dict[str, Any]:
        """
        Calculates confidence band based on historical trust scores for the given ticker.
        If history is insufficient, uses sensible defaults.
        """
        if ticker not in self.history:
            self.history[ticker] = []
            
        self.history[ticker].append(current_score)
        
        # Keep last 100 observations
        if len(self.history[ticker]) > 100:
            self.history[ticker].pop(0)
            
        history_list = self.history[ticker]
        
        if len(history_list) < 5:
            # Need at least 5 points to have a meaningful std_dev
            std_dev = 5.0  # Assumed default standard deviation
        else:
            std_dev = float(np.std(history_list))
            
        # 95% Confidence Interval (1.96 * std_dev)
        margin = 1.96 * std_dev
        
        # Determine strict Institutional Band Label
        if current_score >= 80 and std_dev < 10:
            band_label = "HIGH"
        elif current_score >= 50 and std_dev < 15:
            band_label = "MEDIUM"
        else:
            band_label = "LOW"
            
        return {
            'value': current_score,
            'margin_of_error': round(margin, 2),
            'std_dev': round(std_dev, 2),
            'upper_bound': min(100.0, round(current_score + margin, 2)),
            'lower_bound': max(0.0, round(current_score - margin, 2)),
            'band_label': band_label,
            'data_points_used': len(history_list)
        }

    def generate_full_metrics(self, ticker: str, data_context: Dict[str, float]) -> Dict[str, Any]:
        """
        Generates the full Trust and Confidence JSON output exposed in transparency reports.
        """
        trust_payload = self.compute_trust_score(data_context)
        confidence_payload = self.compute_confidence_band(ticker, trust_payload['total_trust_score'])
        
        return {
            'ticker': ticker,
            'trust_score': trust_payload,
            'confidence_band': confidence_payload,
            'algorithm_transparent': True
        }

# Singleton accessor for wide API use
_trust_scorer = TrustScorer()

def get_trust_scorer() -> TrustScorer:
    return _trust_scorer
