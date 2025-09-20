"""Department Manager Module

Manages the 5-department structure of the AI firm:
Market Intelligence, Trade Operations, Risk Control, Performance Lab, Communications
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DepartmentType(Enum):
    MARKET_INTELLIGENCE = "market_intelligence"
    TRADE_OPERATIONS = "trade_operations" 
    RISK_CONTROL = "risk_control"
    PERFORMANCE_LAB = "performance_lab"
    COMMUNICATIONS = "communications"

@dataclass
class DepartmentMetrics:
    """Department performance and operational metrics"""
    department: DepartmentType
    agent_count: int
    average_performance: float
    total_decisions: int
    success_rate: float
    workload_distribution: Dict[str, float]
    efficiency_score: float
    coordination_rating: float
    uptime_percentage: float

class DepartmentManager:
    """Manages the 5-department AI firm structure"""
    
    def __init__(self):
        self.departments = {}
        self.department_metrics = {}
        self.coordination_matrix = {}
        self.workload_balancer = WorkloadBalancer()
        
        # Initialize departments
        self._initialize_departments()
        
    def _initialize_departments(self):
        """Initialize all 5 departments with proper structure"""
        
        department_configs = {
            DepartmentType.MARKET_INTELLIGENCE: {
                'agents': ['Warren', 'Cathie', 'Quant', 'Data_Whisperer', 'Macro_Monk'],
                'responsibilities': ['market_analysis', 'trend_identification', 'data_synthesis'],
                'priority_level': 'high',
                'coordination_dependencies': ['trade_operations', 'risk_control']
            },
            DepartmentType.TRADE_OPERATIONS: {
                'agents': ['Trade_Executor', 'Portfolio_Optimizer', 'Liquidity_Hunter', 'Arbitrage_Scout'],
                'responsibilities': ['order_execution', 'portfolio_management', 'liquidity_analysis'],
                'priority_level': 'critical',
                'coordination_dependencies': ['market_intelligence', 'risk_control']
            },
            DepartmentType.RISK_CONTROL: {
                'agents': ['Degen_Auditor', 'VaR_Guardian', 'Correlation_Detective', 'Black_Swan_Sentinel'],
                'responsibilities': ['risk_assessment', 'compliance', 'audit_trails'],
                'priority_level': 'critical',
                'coordination_dependencies': ['all']
            },
            DepartmentType.PERFORMANCE_LAB: {
                'agents': ['Performance_Analyst', 'Alpha_Hunter', 'Backtesting_Engine', 'The_Ghost'],
                'responsibilities': ['performance_attribution', 'strategy_testing', 'optimization'],
                'priority_level': 'medium',
                'coordination_dependencies': ['market_intelligence', 'trade_operations']
            },
            DepartmentType.COMMUNICATIONS: {
                'agents': ['Report_Generator', 'Market_Narrator', 'Alert_Coordinator'],
                'responsibilities': ['report_generation', 'stakeholder_communication', 'alerts'],
                'priority_level': 'medium',
                'coordination_dependencies': ['all']
            }
        }
        
        for dept_type, config in department_configs.items():
            self.departments[dept_type] = Department(
                dept_type, config['agents'], config['responsibilities'],
                config['priority_level'], config['coordination_dependencies']
            )
    
    def coordinate_inter_department(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate task execution across departments"""
        
        task_type = task.get('type', 'general')
        priority = task.get('priority', 'medium')
        
        # Determine which departments need to be involved
        involved_departments = self._determine_department_involvement(task_type)
        
        # Execute coordination
        coordination_result = {
            'task_id': str(uuid.uuid4()),
            'task_type': task_type,
            'priority': priority,
            'involved_departments': [dept.value for dept in involved_departments],
            'coordination_timeline': self._estimate_coordination_time(involved_departments),
            'department_assignments': {},
            'success_probability': 0.0
        }
        
        total_success_prob = 0
        for dept_type in involved_departments:
            department = self.departments[dept_type]
            assignment = department.process_task(task)
            
            coordination_result['department_assignments'][dept_type.value] = assignment
            total_success_prob += assignment['success_probability']
        
        coordination_result['success_probability'] = total_success_prob / len(involved_departments)
        
        # Update coordination matrix
        self._update_coordination_matrix(involved_departments, coordination_result)
        
        return coordination_result
    
    def get_department_status(self, department_type: Optional[DepartmentType] = None) -> Dict[str, Any]:
        """Get comprehensive department status"""
        
        if department_type:
            if department_type in self.departments:
                dept = self.departments[department_type]
                return self._get_single_department_status(dept)
            else:
                return {'error': f'Department {department_type.value} not found'}
        
        # Return all departments
        status = {
            'total_departments': len(self.departments),
            'operational_departments': sum(1 for d in self.departments.values() if d.is_operational()),
            'departments': {}
        }
        
        for dept_type, department in self.departments.items():
            status['departments'][dept_type.value] = self._get_single_department_status(department)
        
        return status
    
    def _get_single_department_status(self, department) -> Dict[str, Any]:
        """Get detailed status for single department"""
        
        metrics = department.get_performance_metrics()
        
        return {
            'name': department.name.value,
            'agent_count': len(department.agents),
            'operational_agents': len([a for a in department.agents if department.agent_status.get(a, {}).get('active', True)]),
            'average_performance': metrics['average_performance'],
            'total_decisions': metrics['total_decisions'],
            'success_rate': metrics['success_rate'],
            'current_workload': metrics['current_workload'],
            'efficiency_score': metrics['efficiency_score'],
            'specialties': department.responsibilities,
            'priority_level': department.priority_level,
            'last_activity': datetime.now().isoformat()
        }
    
    def _determine_department_involvement(self, task_type: str) -> List[DepartmentType]:
        """Determine which departments should be involved in a task"""
        
        task_mappings = {
            'trading_decision': [DepartmentType.MARKET_INTELLIGENCE, DepartmentType.TRADE_OPERATIONS, DepartmentType.RISK_CONTROL],
            'risk_assessment': [DepartmentType.RISK_CONTROL, DepartmentType.MARKET_INTELLIGENCE],
            'performance_analysis': [DepartmentType.PERFORMANCE_LAB, DepartmentType.MARKET_INTELLIGENCE],
            'report_generation': [DepartmentType.COMMUNICATIONS, DepartmentType.PERFORMANCE_LAB],
            'market_analysis': [DepartmentType.MARKET_INTELLIGENCE, DepartmentType.PERFORMANCE_LAB],
            'portfolio_optimization': [DepartmentType.TRADE_OPERATIONS, DepartmentType.RISK_CONTROL, DepartmentType.PERFORMANCE_LAB]
        }
        
        return task_mappings.get(task_type, [DepartmentType.MARKET_INTELLIGENCE])
    
    def _estimate_coordination_time(self, departments: List[DepartmentType]) -> Dict[str, Any]:
        """Estimate time required for inter-department coordination"""
        
        base_time = 30  # seconds
        complexity_multiplier = len(departments) * 0.5
        
        estimated_seconds = base_time + (len(departments) * 10) + (complexity_multiplier * 5)
        
        return {
            'estimated_seconds': estimated_seconds,
            'complexity_level': 'low' if len(departments) <= 2 else 'medium' if len(departments) <= 4 else 'high'
        }
    
    def _update_coordination_matrix(self, departments: List[DepartmentType], result: Dict[str, Any]):
        """Update inter-department coordination tracking"""
        
        coordination_key = '_'.join(sorted([d.value for d in departments]))
        
        if coordination_key not in self.coordination_matrix:
            self.coordination_matrix[coordination_key] = {
                'coordination_count': 0,
                'average_success_rate': 0,
                'total_success_rate': 0
            }
        
        matrix_entry = self.coordination_matrix[coordination_key]
        matrix_entry['coordination_count'] += 1
        matrix_entry['total_success_rate'] += result['success_probability']
        matrix_entry['average_success_rate'] = matrix_entry['total_success_rate'] / matrix_entry['coordination_count']

class Department:
    """Individual department within the AI firm"""
    
    def __init__(self, name: DepartmentType, agents: List[str], responsibilities: List[str], 
                 priority_level: str, coordination_deps: List[str]):
        self.name = name
        self.agents = agents
        self.responsibilities = responsibilities
        self.priority_level = priority_level
        self.coordination_dependencies = coordination_deps
        self.agent_status = {agent: {'active': True, 'workload': 0.5} for agent in agents}
        self.task_history = []
        
    def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task within department"""
        
        # Assign to most available agent
        available_agent = min(self.agents, key=lambda a: self.agent_status[a]['workload'])
        
        # Calculate success probability based on agent expertise and workload
        agent_performance = 0.8  # Base performance
        workload_penalty = self.agent_status[available_agent]['workload'] * 0.2
        success_probability = max(0.1, agent_performance - workload_penalty)
        
        # Create task assignment
        assignment = {
            'assigned_agent': available_agent,
            'estimated_completion': (datetime.now() + timedelta(minutes=30)).isoformat(),
            'success_probability': success_probability,
            'resource_allocation': self._calculate_resource_allocation(task),
            'dependencies_resolved': self._check_dependencies(task)
        }
        
        # Update agent workload
        self.agent_status[available_agent]['workload'] = min(1.0, 
            self.agent_status[available_agent]['workload'] + 0.1)
        
        # Record task
        self.task_history.append({
            'task_id': task.get('id', str(uuid.uuid4())),
            'timestamp': datetime.now(),
            'assignment': assignment
        })
        
        return assignment
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get department performance metrics"""
        
        if not self.task_history:
            return {
                'average_performance': 0.75,
                'total_decisions': 0,
                'success_rate': 0.0,
                'current_workload': 0.5,
                'efficiency_score': 0.8
            }
        
        recent_tasks = [t for t in self.task_history if 
                       (datetime.now() - t['timestamp']).days < 7]
        
        avg_success = sum(t['assignment']['success_probability'] for t in recent_tasks) / len(recent_tasks) if recent_tasks else 0.75
        avg_workload = sum(self.agent_status[agent]['workload'] for agent in self.agents) / len(self.agents)
        
        return {
            'average_performance': avg_success,
            'total_decisions': len(self.task_history),
            'success_rate': avg_success,
            'current_workload': avg_workload,
            'efficiency_score': min(1.0, avg_success / max(avg_workload, 0.1))
        }
    
    def is_operational(self) -> bool:
        """Check if department is operational"""
        active_agents = sum(1 for agent in self.agents if self.agent_status[agent]['active'])
        return active_agents >= len(self.agents) * 0.5  # At least 50% of agents active
    
    def _calculate_resource_allocation(self, task: Dict[str, Any]) -> Dict[str, float]:
        """Calculate resource allocation for task"""
        
        task_complexity = task.get('complexity', 'medium')
        
        allocations = {
            'simple': {'cpu': 0.2, 'memory': 0.1, 'network': 0.1},
            'medium': {'cpu': 0.4, 'memory': 0.3, 'network': 0.2},
            'complex': {'cpu': 0.7, 'memory': 0.6, 'network': 0.4}
        }
        
        return allocations.get(task_complexity, allocations['medium'])
    
    def _check_dependencies(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are resolved"""
        
        # Simple dependency check - in production would check actual dependencies
        dependencies = task.get('dependencies', [])
        
        # For now, assume dependencies are resolved if less than 3
        return len(dependencies) <= 2

class WorkloadBalancer:
    """Balances workload across departments and agents"""
    
    def __init__(self):
        self.load_history = []
        
    def balance_workload(self, departments: Dict[DepartmentType, Department]) -> Dict[str, Any]:
        """Balance workload across all departments"""
        
        department_loads = {}
        
        for dept_type, department in departments.items():
            total_workload = sum(department.agent_status[agent]['workload'] for agent in department.agents)
            avg_workload = total_workload / len(department.agents)
            
            department_loads[dept_type.value] = {
                'total_workload': total_workload,
                'average_workload': avg_workload,
                'agent_count': len(department.agents),
                'overloaded_agents': [agent for agent in department.agents 
                                    if department.agent_status[agent]['workload'] > 0.8]
            }
        
        # Identify rebalancing opportunities
        rebalancing_recommendations = self._identify_rebalancing_opportunities(department_loads)
        
        return {
            'department_loads': department_loads,
            'overall_balance_score': self._calculate_balance_score(department_loads),
            'rebalancing_recommendations': rebalancing_recommendations,
            'timestamp': datetime.now().isoformat()
        }
    
    def _identify_rebalancing_opportunities(self, loads: Dict[str, Dict]) -> List[str]:
        """Identify opportunities for workload rebalancing"""
        
        recommendations = []
        
        # Check for overloaded departments
        for dept_name, load_data in loads.items():
            if load_data['average_workload'] > 0.8:
                recommendations.append(f"Consider redistributing tasks from {dept_name}")
            elif len(load_data['overloaded_agents']) > 0:
                recommendations.append(f"Rebalance agent workload in {dept_name}")
        
        return recommendations
    
    def _calculate_balance_score(self, loads: Dict[str, Dict]) -> float:
        """Calculate overall workload balance score"""
        
        workloads = [load_data['average_workload'] for load_data in loads.values()]
        
        if not workloads:
            return 1.0
        
        # Calculate standard deviation of workloads
        mean_workload = sum(workloads) / len(workloads)
        variance = sum((w - mean_workload) ** 2 for w in workloads) / len(workloads)
        std_dev = variance ** 0.5
        
        # Balance score: lower std dev = higher balance
        balance_score = max(0.0, 1.0 - (std_dev / 0.5))  # Normalize to 0-1
        
        return balance_score
