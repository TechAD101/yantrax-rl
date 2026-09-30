    async def _stage_ceo_governance(self, ctx: DecisionContext) -> DecisionContext:
        """Run CEO governance without conflating workflow type and trade direction."""
        try:
            ceo_context = {
                'type': 'strategic_trading_decision',
                'symbol': ctx.symbol,
                'ticker': ctx.symbol,
                'market_trend': ctx.market_snapshot.trend if ctx.market_snapshot else 'neutral',
                'volatility': ctx.market_snapshot.volatility if ctx.market_snapshot else 0.02,
                'evidence': ctx.evidence.to_dict() if ctx.evidence else {},
                'agent_recommendation': ctx.voting_result.winning_signal.value if ctx.voting_result else 'HOLD',
                'consensus_strength': ctx.voting_result.consensus_strength if ctx.voting_result else 0.0,
                'debate_result': ctx.debate_result.to_dict() if ctx.debate_result else {},
                'candidate_strategy': ctx.candidate_strategy.to_dict() if ctx.candidate_strategy else {},
                'portfolio_state': ctx.portfolio_state.to_dict() if ctx.portfolio_state else {},
                'timestamp': datetime.now().isoformat(),
            }

            ceo_decision = await self.ceo.make_strategic_decision(ceo_context)

            # The current CEO API returns a workflow decision_type. Direction
            # remains the candidate strategy action unless the CEO explicitly
            # returns a directional type or defensive lockdown.
            if ceo_decision.decision_type in ('BUY', 'SELL', 'HOLD'):
                action = TradingAction(ceo_decision.decision_type)
            elif ceo_decision.decision_type == 'defensive_lockdown':