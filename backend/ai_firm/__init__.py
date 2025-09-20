"""AI Firm Architecture Module

Sophisticated 20+ agent AI firm structure with autonomous CEO,
multi-department coordination, and advanced report generation.
"""

from .ceo import AutonomousCEO
from .agent_manager import AgentManager
from .department_manager import DepartmentManager
from .shift_manager import ShiftManager
from .report_generation import AdvancedReportGenerator
from .memory_system import FirmMemorySystem

__all__ = [
    'AutonomousCEO',
    'AgentManager', 
    'DepartmentManager',
    'ShiftManager',
    'AdvancedReportGenerator',
    'FirmMemorySystem'
]
