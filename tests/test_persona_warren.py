import sys
import os
import unittest

# Setup sys.path to include backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ai_agents.personas.warren import WarrenAgent
from ai_agents.base_persona import VoteType, PersonaAnalysis, PersonaVote

class TestWarrenAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WarrenAgent()

    def test_analyze_ideal_fundamentals(self):
        # Good fundamentals: High ROE, high profit margin, low debt, low PE
        context = {
            'symbol': 'AAPL',
            'fundamentals': {
                'return_on_equity': 0.25,
                'profit_margin': 0.20,
                'debt_to_equity': 0.3,
                'pe_ratio': 12,
                'earnings_volatility': 0.1
            },
            'market_data': {
                'current_price': 150.0
            },
            'company_data': {
                'brand_score': 0.9,
                'switching_cost_score': 0.8,
                'network_effect_score': 0.9,
                'cost_advantage_score': 0.7,
                'regulatory_score': 0.8
            }
        }

        analysis = self.agent.analyze(context)

        self.assertIsInstance(analysis, PersonaAnalysis)
        self.assertIn(analysis.recommendation, ['BUY', 'STRONG_BUY'])
        self.assertEqual(analysis.symbol, 'AAPL')
        self.assertGreater(analysis.confidence, 0.7)
        self.assertEqual(analysis.risk_assessment['overall_risk'], 'Low')

    def test_analyze_poor_fundamentals(self):
        # Poor fundamentals: Low ROE, low margin, high debt, high PE
        context = {
            'symbol': 'GME',
            'fundamentals': {
                'return_on_equity': 0.05,
                'profit_margin': 0.02,
                'debt_to_equity': 1.5,
                'pe_ratio': 80,
                'earnings_volatility': 0.6
            },
            'market_data': {
                'current_price': 20.0
            },
            'company_data': {
                'brand_score': 0.4,
                'switching_cost_score': 0.2,
                'network_effect_score': 0.1,
                'cost_advantage_score': 0.3,
                'regulatory_score': 0.5
            }
        }

        analysis = self.agent.analyze(context)

        self.assertIsInstance(analysis, PersonaAnalysis)
        self.assertEqual(analysis.recommendation, 'AVOID')
        self.assertEqual(analysis.symbol, 'GME')
        self.assertEqual(analysis.risk_assessment['overall_risk'], 'Moderate')
        self.assertGreater(analysis.confidence, 0.7)

    def test_vote_aligned(self):
        proposal = {
            'symbol': 'BRK.B',
            'action': 'BUY'
        }
        market_context = {
            'fundamentals': {
                'return_on_equity': 0.20,
                'profit_margin': 0.15,
                'debt_to_equity': 0.2,
                'pe_ratio': 14,
                'earnings_volatility': 0.1
            },
            'market_data': {
                'current_price': 300.0
            },
            'company_data': {
                'brand_score': 0.9,
                'switching_cost_score': 0.8,
                'network_effect_score': 0.8,
                'cost_advantage_score': 0.9,
                'regulatory_score': 0.8
            },
            'market_trend': 'neutral',
            'volatility': 0.3
        }

        vote = self.agent.vote(proposal, market_context)

        self.assertIsInstance(vote, PersonaVote)
        self.assertIn(vote.vote, [VoteType.BUY, VoteType.STRONG_BUY])
        self.assertIn('Aligned', vote.reasoning)
        self.assertGreater(vote.weight, 1.0)

    def test_vote_opposed(self):
        proposal = {
            'symbol': 'TSLA',
            'action': 'BUY'
        }
        market_context = {
            'fundamentals': {
                'return_on_equity': 0.10,
                'profit_margin': 0.05,
                'debt_to_equity': 1.2,
                'pe_ratio': 100,
                'earnings_volatility': 0.5
            },
            'market_data': {
                'current_price': 250.0
            },
            'company_data': {
                'brand_score': 0.9,
                'switching_cost_score': 0.4,
                'network_effect_score': 0.3,
                'cost_advantage_score': 0.4,
                'regulatory_score': 0.6
            },
            'market_trend': 'bullish',
            'volatility': 0.8
        }

        vote = self.agent.vote(proposal, market_context)

        self.assertIsInstance(vote, PersonaVote)
        self.assertEqual(vote.vote, VoteType.STRONG_SELL)
        self.assertIn('Opposed', vote.reasoning)

if __name__ == '__main__':
    unittest.main()
