import asyncio
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AgentState(str, Enum):
    IDLE = "IDLE"
    REASONING = "REASONING"
    ACTING = "ACTING"
    REFLECTING = "REFLECTING"
    VERIFYING = "VERIFYING"
    ERROR = "ERROR"

class AgentTask(BaseModel):
    id: str
    description: str
    status: str = "pending"
    context: Dict[str, Any] = {}

class RARVAgent:
    """
    Base Agent implementing the Loki RARV Cycle:
    1. REASON: Analyze task, check memory.
    2. ACT: Execute tools/actions.
    3. REFLECT: Update memory, check goal.
    4. VERIFY: Test output, critique self.
    """
    
    def __init__(self, name: str, role: str, capabilities: List[str]):
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self.memory: List[Dict[str, Any]] = [] # Episodic memory trace

    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a full RARV cycle for a task"""
        self.current_task = task
        self.log_state(AgentState.REASONING)
        
        try:
            # 1. REASON
            plan = await self.reason(task)
            
            # 2. ACT
            self.log_state(AgentState.ACTING)
            result = await self.act(plan)
            
            # 3. REFLECT
            self.log_state(AgentState.REFLECTING)
            reflection = await self.reflect(result)
            
            # 4. VERIFY
            self.log_state(AgentState.VERIFYING)
            verified = await self.verify(result, reflection)
            
            self.log_state(AgentState.IDLE)
            return {
                "status": "success" if verified else "failed_verification",
                "result": result,
                "cycles": 1 
            }
            
        except Exception as e:
            self.log_state(AgentState.ERROR)
            logger.error(f"Agent {self.name} failed: {e}")
            return {"status": "error", "error": str(e)}

    # --- Override these in specific agents ---
    
    async def reason(self, task: AgentTask) -> Dict[str, Any]:
        """Plan the approach"""
        # Placeholder for LLM Planning
        return {"action": "default_action", "confidence": 0.9}

    async def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action"""
        return {"output": "Done", "metadata": {}}

    async def reflect(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Update memory"""
        self.memory.append({"task": self.current_task.id, "result": result})
        return {"learned": "Task completed"}

    async def verify(self, result: Dict[str, Any], reflection: Dict[str, Any]) -> bool:
        """Self-critique"""
        return True

    def log_state(self, new_state: AgentState):
        self.state = new_state
        logger.info(f"[{self.name}] State change -> {new_state.value}")
