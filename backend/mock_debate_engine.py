class MockDebateEngine:
    async def conduct_debate(self, ticker, context):
        return {
            'ticker': ticker,
            'winning_signal': 'HOLD',
            'consensus_score': 0.5,
            'arguments': [],
            'mock': True
        }
    def set_perplexity_service(self, service):
        pass
