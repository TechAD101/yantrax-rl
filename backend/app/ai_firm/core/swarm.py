from typing import Dict, List, Any
from app.ai_firm.core.agent_loop import RARVAgent, AgentTask

class SwarmManager:
    """
    Orchestrates a collection of agents (Swarm).
    Handles task dispatch and status aggregation.
    """
    def __init__(self, name: str):
        self.name = name
        self.agents: Dict[str, RARVAgent] = {}

    def add_agent(self, agent: RARVAgent):
        self.agents[agent.name] = agent

    def get_swarm_status(self) -> Dict[str, Any]:
        return {
            "swarm": self.name,
            "agent_count": len(self.agents),
            "agents": {name: agent.state for name, agent in self.agents.items()}
        }

    async def dispatch_task(self, agent_name: str, task: AgentTask):
        if agent_name in self.agents:
            return await self.agents[agent_name].execute_task(task)
        raise ValueError(f"Agent {agent_name} not found in swarm {self.name}")
