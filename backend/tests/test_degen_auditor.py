import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_agents.degen_auditor import (
    DegenAuditorAgent,
    VaRCalculator,
    DrawdownAnalyzer,
    SharpeRatioCalculator,
    VolatilityAnalyzer,
    PortfolioRiskTracker
)

class TestDegenAuditor(unittest.TestCase):
    def setUp(self):
        self.agent = DegenAuditorAgent()
        self.var_calc = VaRCalculator()
        self.drawdown_calc = DrawdownAnalyzer()
        self.sharpe_calc = SharpeRatioCalculator()
        self.vol_calc = VolatilityAnalyzer()
        self.portfolio_tracker = PortfolioRiskTracker()

    def test_var_calculator(self):
        # Low Risk
        trade_data = {"volatility": 0.01, "position_size": 0.1}
        result = self.var_calc.calculate_var(trade_data)
        # 0.01 * 0.1 * 1.645 = 0.001645 < 0.02 -> LOW
        self.assertEqual(result["risk_level"], "LOW")

        # Medium Risk
        trade_data = {"volatility": 0.02, "position_size": 1.0}
        result = self.var_calc.calculate_var(trade_data)
        # 0.02 * 1.0 * 1.645 = 0.0329 -> MEDIUM (0.02 <= x < 0.05)
        self.assertEqual(result["risk_level"], "MEDIUM")

        # High Risk
        trade_data = {"volatility": 0.05, "position_size": 1.0}
        result = self.var_calc.calculate_var(trade_data)
        # 0.05 * 1.0 * 1.645 = 0.08225 -> HIGH (>= 0.05)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_drawdown_analyzer(self):
        # Low Risk
        trade_data = {"volatility": 0.02, "leverage": 1.0}
        result = self.drawdown_calc.analyze_drawdown(trade_data)
        # 0.02 * 1.0 * 3 = 0.06 < 0.1 -> LOW
        self.assertEqual(result["risk_level"], "LOW")

        # Medium Risk
        trade_data = {"volatility": 0.05, "leverage": 1.0}
        result = self.drawdown_calc.analyze_drawdown(trade_data)
        # 0.05 * 1.0 * 3 = 0.15 -> MEDIUM (0.1 <= x < 0.2)
        self.assertEqual(result["risk_level"], "MEDIUM")

        # High Risk
        trade_data = {"volatility": 0.1, "leverage": 1.0}
        result = self.drawdown_calc.analyze_drawdown(trade_data)
        # 0.1 * 1.0 * 3 = 0.3 -> HIGH (>= 0.2)
        self.assertEqual(result["risk_level"], "HIGH")

    def test_sharpe_calculator(self):
        # Excellent
        trade_data = {"expected_return": 0.2, "volatility": 0.1}
        result = self.sharpe_calc.calculate_sharpe(trade_data)
        # (0.2 - 0.02) / 0.1 = 1.8 > 1.0 -> EXCELLENT
        self.assertEqual(result["risk_assessment"], "EXCELLENT")

        # Good
        trade_data = {"expected_return": 0.08, "volatility": 0.1}
        result = self.sharpe_calc.calculate_sharpe(trade_data)
        # (0.08 - 0.02) / 0.1 = 0.6 -> GOOD (> 0.5)
        self.assertEqual(result["risk_assessment"], "GOOD")

        # Fair
        trade_data = {"expected_return": 0.04, "volatility": 0.1}
        result = self.sharpe_calc.calculate_sharpe(trade_data)
        # (0.04 - 0.02) / 0.1 = 0.2 -> FAIR (> 0)
        self.assertEqual(result["risk_assessment"], "FAIR")

        # Poor
        trade_data = {"expected_return": 0.01, "volatility": 0.1}
        result = self.sharpe_calc.calculate_sharpe(trade_data)
        # (0.01 - 0.02) / 0.1 = -0.1 -> POOR (<= 0)
        self.assertEqual(result["risk_assessment"], "POOR")

    def test_volatility_analyzer(self):
        # Low Volatility
        trade_data = {"volatility": 0.10}
        result = self.vol_calc.analyze_volatility(trade_data)
        self.assertEqual(result["risk_level"], "LOW")

        # Normal Volatility
        trade_data = {"volatility": 0.20}
        result = self.vol_calc.analyze_volatility(trade_data)
        self.assertEqual(result["risk_level"], "MEDIUM")

        # High Volatility
        trade_data = {"volatility": 0.40}
        result = self.vol_calc.analyze_volatility(trade_data)
        self.assertEqual(result["risk_level"], "HIGH")

        # Crisis Volatility
        trade_data = {"volatility": 0.60}
        result = self.vol_calc.analyze_volatility(trade_data)
        self.assertEqual(result["risk_level"], "EXTREME")

    def test_portfolio_risk_tracker(self):
        signal = {"action": "BUY"}
        market_data = {"price": 100}
        result = self.portfolio_tracker.analyze_impact(signal, market_data)
        self.assertEqual(result["risk_increase"], 0.3)

        signal = {"action": "SELL"}
        result = self.portfolio_tracker.analyze_impact(signal, market_data)
        self.assertEqual(result["risk_increase"], 0.1)

    def test_risk_aggregation(self):
        # Test aggregation logic via private method access (for verifying magic numbers)
        # Or mock the internal calls. Let's rely on audit_risk public method.

        trade_data = {
            "volatility": 0.20, # Medium Volatility (0.5 score)
            "position_size": 1.0,
            "leverage": 1.0,
            "expected_return": 0.08
        }

        # VaR: 0.20 * 1.0 * 1.645 = 0.329 -> HIGH -> Score 0.8
        # Drawdown: 0.20 * 1.0 * 3 = 0.6 -> HIGH -> Not used in aggregation explicitly in current code?
        # Wait, let's check _aggregate_risk_assessment in degen_auditor.py

        # It uses 'var', 'sharpe', 'volatility'

        # VaR: HIGH -> 0.8
        # Sharpe: (0.08 - 0.02) / 0.20 = 0.3 -> FAIR -> 0.5
        # Volatility: 0.20 -> MEDIUM -> 0.5

        # Average: (0.8 + 0.5 + 0.5) / 3 = 1.8 / 3 = 0.6

        # Risk Level: >= 0.6 -> HIGH (if strictly >= 0.6, else MEDIUM if < 0.6)
        # Code says: elif overall_risk_score < 0.6: risk_level = "MEDIUM"; else: risk_level = "HIGH"
        # So 0.6 -> HIGH

        result = self.agent.audit_risk(trade_data)
        self.assertEqual(result["overall_risk_level"], "HIGH")
        self.assertAlmostEqual(result["risk_score"], 0.6)

if __name__ == '__main__':
    unittest.main()
