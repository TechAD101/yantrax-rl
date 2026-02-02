from app.ai_firm.core.agent_loop import RARVAgent, AgentTask
from app.ai_firm.core.swarm import SwarmManager

class WarrenAgent(RARVAgent):
    async def reason(self, task: AgentTask):
        # Specific logic for Warren (Value Investing)
        return {"action": "analyze_fundamentals", "target": task.context.get("symbol")}

class CathieAgent(RARVAgent):
    async def reason(self, task: AgentTask):
        # Specific logic for Cathie (Innovation/Growth)
        return {"action": "analyze_innovation_score", "target": task.context.get("symbol")}

def create_investment_swarm() -> SwarmManager:
    manager = SwarmManager("Investment Swarm")
    
    warren = WarrenAgent("Warren", "Value Investor", ["financial_stmt_analysis", "risk_assessment"])
    cathie = CathieAgent("Cathie", "Growth Investor", ["tech_trend_analysis", "volatility_tolerance"])
    
    manager.add_agent(warren)
    manager.add_agent(cathie)
    
    return manager

investment_swarm = create_investment_swarm()
