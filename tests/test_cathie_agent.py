import os
import sys
import pytest
from datetime import datetime
from unittest.mock import patch

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai_agents.personas.cathie import CathieAgent
from ai_agents.base_persona import PersonaArchetype, VoteType, PersonaAnalysis, PersonaVote

class TestCathieAgent:
    @pytest.fixture
    def agent(self):
        return CathieAgent()

    def test_initialization(self, agent):
        assert agent.name == "Cathie"
        assert agent.archetype == PersonaArchetype.GROWTH
        assert agent.voting_weight == 1.0
        assert "innovation_investing" in agent.preferred_strategies
        assert agent.department == "performance_lab"
        assert agent.specialty == "Disruptive Innovation"

    def test_analyze_high_innovation(self, agent):
        context = {
            'symbol': 'TSLA',
            'company_data': {
                'rd_spending_ratio': 0.4,
                'patent_portfolio_score': 0.9,
                'technology_leadership_score': 0.9,
                'revenue_growth_3yr': 0.6,
                'projected_tam_5yr': 5000000000,
                'total_addressable_market': 1000000000,
                'tech_superiority_score': 0.9,
                'cost_advantage_score': 0.8,
                'ux_improvement_score': 0.9,
                'business_model_score': 0.9
            },
            'market_data': {
                'current_price': 200.0
            },
            'sector_data': {
                'innovation_momentum': 0.8,
                'adoption_stage': 'early_growth'
            }
        }
        analysis = agent.analyze(context)
        assert isinstance(analysis, PersonaAnalysis)
        assert analysis.symbol == 'TSLA'
        assert analysis.recommendation in ['BUY', 'HIGH_CONVICTION_BUY']
        assert analysis.confidence >= 0.8
        assert 'innovation' in analysis.scores
        assert analysis.scores['innovation'] > 0.7

    def test_analyze_low_innovation(self, agent):
        context = {
            'symbol': 'OLD_CORP',
            'company_data': {
                'rd_spending_ratio': 0.05,
                'patent_portfolio_score': 0.2,
                'technology_leadership_score': 0.2,
                'revenue_growth_3yr': 0.02,
                'projected_tam_5yr': 1100000000,
                'total_addressable_market': 1000000000,
                'tech_superiority_score': 0.2,
                'cost_advantage_score': 0.3,
                'ux_improvement_score': 0.2,
                'business_model_score': 0.3
            },
            'market_data': {},
            'sector_data': {
                'adoption_stage': 'maturity'
            }
        }
        analysis = agent.analyze(context)
        assert analysis.recommendation == 'RESEARCH'
        assert analysis.scores['innovation'] < 0.5

    def test_analyze_missing_context(self, agent):
        # Test with empty context to ensure robust default handling
        context = {}
        analysis = agent.analyze(context)
        assert analysis.symbol == 'UNKNOWN'
        assert analysis.recommendation == 'RESEARCH'
        assert analysis.confidence == 0.6

    def test_vote_alignment(self, agent):
        proposal = {'symbol': 'NVDA', 'action': 'BUY'}
        market_context = {
            'company_data': {
                'rd_spending_ratio': 0.4,
                'revenue_growth_3yr': 0.5,
            },
            'sector_data': {'adoption_stage': 'early_growth'}
        }
        # Force a BUY recommendation through context
        vote = agent.vote(proposal, market_context)
        assert isinstance(vote, PersonaVote)
        assert vote.vote in [VoteType.BUY, VoteType.STRONG_BUY, VoteType.HOLD]
        # In CathieAgent.vote, if analysis says BUY and proposal says BUY, it stays BUY.
        # But if analysis says RESEARCH (which happens for low scores) and proposal says BUY, it becomes HOLD.

    def test_vote_misalignment(self, agent):
        proposal = {'symbol': 'COAL', 'action': 'BUY'}
        market_context = {
            'company_data': {
                'rd_spending_ratio': 0.01,
                'revenue_growth_3yr': -0.05,
            },
            'sector_data': {'adoption_stage': 'decline'}
        }
        vote = agent.vote(proposal, market_context)
        assert vote.vote == VoteType.HOLD
        assert "Cautious" in vote.reasoning

    def test_dynamic_weight_adjustment(self, agent):
        # Default weight
        assert agent.get_vote_weight() == 1.0

        # Bullish market
        context = {'market_trend': 'bullish'}
        assert agent.get_vote_weight(context) == 1.3

        # High innovation sentiment
        context = {'innovation_sentiment': 0.8}
        assert agent.get_vote_weight(context) == 1.2

        # Both (capped at 2.0)
        context = {'market_trend': 'bullish', 'innovation_sentiment': 0.8}
        # 1.0 * 1.3 = 1.3
        # Then _adjust_weight_for_context is called
        # if market_trend == 'bullish': base_weight *= 1.3 -> 1.3 * 1.3 = 1.69
        # elif innovation_sentiment > 0.75: base_weight *= 1.2
        # Wait, let's check CathieAgent._adjust_weight_for_context
        # if market_trend == 'bullish': base_weight *= 1.3
        # elif innovation_sentiment > 0.75: base_weight *= 1.2
        # It's an elif, so it doesn't do both if the first one matches.
        assert agent.get_vote_weight(context) == 1.3

    def test_cathie_memory(self, agent):
        context = {
            'symbol': 'ARKK',
            'company_data': {'rd_spending_ratio': 0.5},
            'sector_data': {'sector': 'Technology'}
        }
        agent.analyze(context)

        summary = agent.memory.get_performance_summary()
        assert summary['total_analyses'] == 1
        assert 'average_innovation_score' in summary

        # Test PersonaAgent metrics too
        assert agent.performance_metrics['total_analyses'] == 1
