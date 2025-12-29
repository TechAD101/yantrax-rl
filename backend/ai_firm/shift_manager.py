"""Shift Manager Module

Manages 24/7 operation with 3-shift system for continuous AI firm operation.
Coordinates agent availability, shift transitions, and round-the-clock monitoring.
"""

import uuid
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import pytz

class ShiftType(Enum):
    MORNING = "morning_shift"    # 6 AM - 2 PM
    AFTERNOON = "afternoon_shift"  # 2 PM - 10 PM
    NIGHT = "night_shift"       # 10 PM - 6 AM

class ShiftStatus(Enum):
    ACTIVE = "active"
    TRANSITION = "transition"
    STANDBY = "standby"

@dataclass
class Shift:
    """Shift definition with timing and agent assignments"""
    id: str
    shift_type: ShiftType
    start_time: time
    end_time: time
    assigned_agents: List[str]
    shift_lead: str
    priority_focus: str
    timezone: str
    active: bool = True

@dataclass
class ShiftTransition:
    """Shift transition record"""
    id: str
    timestamp: datetime
    from_shift: ShiftType
    to_shift: ShiftType
    handover_notes: Dict[str, Any]
    critical_items: List[str]
    transition_duration: int  # seconds
    success: bool

class ShiftManager:
    """Manages 24/7 operation with intelligent shift coordination"""
    
    def __init__(self, timezone: str = 'UTC'):
        self.timezone = pytz.timezone(timezone)
        self.shifts: Dict[ShiftType, Shift] = {}
        self.current_shift: Optional[ShiftType] = None
        self.shift_history: List[Dict[str, Any]] = []
        self.transition_logs: List[ShiftTransition] = []
        
        # Initialize 3-shift system
        self._initialize_shift_system()
        
        # Set current shift
        self.current_shift = self._determine_current_shift()
        
    def _initialize_shift_system(self):
        """Initialize the 3-shift 24/7 operation system"""
        
        # Morning Shift (6 AM - 2 PM) - Focus: Pre-market and Market Open
        morning_shift = Shift(
            id=str(uuid.uuid4()),
            shift_type=ShiftType.MORNING,
            start_time=time(6, 0),
            end_time=time(14, 0),
            assigned_agents=[
                'Warren', 'Data_Whisperer', 'Trade_Executor', 'Performance_Analyst',
                'VaR_Guardian', 'Report_Generator', 'Market_Narrator'
            ],
            shift_lead='Warren',
            priority_focus='market_analysis_and_execution',
            timezone='UTC'
        )
        
        # Afternoon Shift (2 PM - 10 PM) - Focus: Active Trading and Analysis
        afternoon_shift = Shift(
            id=str(uuid.uuid4()),
            shift_type=ShiftType.AFTERNOON,
            start_time=time(14, 0),
            end_time=time(22, 0),
            assigned_agents=[
                'Cathie', 'Quant', 'Macro_Monk', 'Liquidity_Hunter', 'Alpha_Hunter',
                'Correlation_Detective', 'Alert_Coordinator'
            ],
            shift_lead='Cathie',
            priority_focus='active_trading_and_optimization',
            timezone='UTC'
        )
        
        # Night Shift (10 PM - 6 AM) - Focus: Risk Management and Global Markets
        night_shift = Shift(
            id=str(uuid.uuid4()),
            shift_type=ShiftType.NIGHT,
            start_time=time(22, 0),
            end_time=time(6, 0),
            assigned_agents=[
                'The_Ghost', 'Degen_Auditor', 'Black_Swan_Sentinel', 
                'Portfolio_Optimizer', 'Backtesting_Engine', 'Arbitrage_Scout'
            ],
            shift_lead='Degen_Auditor',
            priority_focus='risk_management_and_global_monitoring',
            timezone='UTC'
        )
        
        self.shifts[ShiftType.MORNING] = morning_shift
        self.shifts[ShiftType.AFTERNOON] = afternoon_shift
        self.shifts[ShiftType.NIGHT] = night_shift
        
    def _determine_current_shift(self) -> ShiftType:
        """Determine which shift should be active based on current time"""
        
        current_time = datetime.now(self.timezone).time()
        
        # Check each shift's time range
        for shift_type, shift in self.shifts.items():
            if self._is_time_in_shift(current_time, shift):
                return shift_type
        
        # Default to morning shift if no match (edge case)
        return ShiftType.MORNING
    
    def _is_time_in_shift(self, current_time: time, shift: Shift) -> bool:
        """Check if current time falls within shift hours"""
        
        start_time = shift.start_time
        end_time = shift.end_time
        
        # Handle overnight shift (night shift crosses midnight)
        if start_time > end_time:  # Overnight shift
            return current_time >= start_time or current_time <= end_time
        else:  # Regular shift
            return start_time <= current_time <= end_time
    
    def initiate_shift_transition(self, target_shift: Optional[ShiftType] = None) -> ShiftTransition:
        """Initiate transition to next shift"""
        
        if target_shift is None:
            target_shift = self._get_next_shift()
        
        # Ensure we have a valid current shift
        if self.current_shift is None:
            self.current_shift = self._determine_current_shift()

        # Create handover notes
        handover_notes = self._generate_handover_notes(current_shift_obj)
        
        # Identify critical items
        critical_items = self._identify_critical_items()
        
        # Record transition
        transition = ShiftTransition(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            from_shift=self.current_shift,
            to_shift=target_shift,
            handover_notes=handover_notes,
            critical_items=critical_items,
            transition_duration=300,  # 5 minutes standard transition
            success=True
        )
        
        # Execute transition
        self.current_shift = target_shift
        self.transition_logs.append(transition)
        
        # Log shift change
        self.shift_history.append({
            'timestamp': datetime.now(),
            'shift': target_shift,
            'transition_id': transition.id
        })
        
        return transition
    
    def _get_next_shift(self) -> ShiftType:
        """Get the next shift in sequence"""
        
        shift_sequence = {
            ShiftType.MORNING: ShiftType.AFTERNOON,
            ShiftType.AFTERNOON: ShiftType.NIGHT,
            ShiftType.NIGHT: ShiftType.MORNING
        }
        
        return shift_sequence[self.current_shift]
    
    def _generate_handover_notes(self, outgoing_shift: Shift) -> Dict[str, Any]:
        """Generate comprehensive handover notes for shift transition"""
        
        return {
            'portfolio_status': {
                'total_positions': 12,  # Mock data
                'open_orders': 3,
                'pending_alerts': 1,
                'risk_level': 'moderate'
            },
            'market_conditions': {
                'volatility': 0.18,
                'trend': 'bullish',
                'key_events': ['Fed meeting tomorrow', 'Earnings season active']
            },
            'agent_performance': {
                'top_performer': outgoing_shift.assigned_agents[0],
                'attention_needed': [],
                'recent_decisions': 15
            },
            'priority_tasks': [
                'Monitor NVDA earnings impact',
                'Review portfolio risk exposure',
                'Update client reports'
            ],
            'system_health': {
                'uptime': '99.8%',
                'response_time': '45ms',
                'error_rate': '0.2%'
            }
        }
    
    def _identify_critical_items(self) -> List[str]:
        """Identify critical items requiring immediate attention"""
        
        return [
            'High volatility alert on tech sector',
            'Portfolio approaching risk limit on crypto exposure',
            'Warren persona flagged overvaluation in 3 positions'
        ]
    
    def get_current_shift_status(self) -> Dict[str, Any]:
        """Get comprehensive current shift status"""
        
        if not self.current_shift:
            return {'error': 'No active shift determined'}
        
        current_shift_obj = self.shifts[self.current_shift]
        
        # Calculate shift progress
        shift_progress = self._calculate_shift_progress(current_shift_obj)
        
        # Get agent availability
        agent_availability = self._get_agent_availability(current_shift_obj.assigned_agents)
        
        return {
            'current_shift': {
                'type': self.current_shift.value,
                'lead_agent': current_shift_obj.shift_lead,
                'priority_focus': current_shift_obj.priority_focus,
                'progress_percentage': shift_progress,
                'time_remaining': self._calculate_time_remaining(current_shift_obj)
            },
            'agent_assignments': {
                'total_agents': len(current_shift_obj.assigned_agents),
                'active_agents': sum(1 for a in agent_availability.values() if a['available']),
                'agent_details': agent_availability
            },
            'next_shift': {
                'type': self._get_next_shift().value,
                'transition_time': self._get_next_transition_time().isoformat()
            },
            'shift_metrics': {
                'total_shifts_completed': len(self.shift_history),
                'successful_transitions': len([t for t in self.transition_logs if t.success]),
                'average_transition_time': self._calculate_avg_transition_time()
            }
        }
    
    def _calculate_shift_progress(self, shift: Shift) -> float:
        """Calculate how much of current shift has completed"""
        
        current_time = datetime.now(self.timezone).time()
        
        # Convert times to minutes for easier calculation
        def time_to_minutes(t):
            return t.hour * 60 + t.minute
        
        current_minutes = time_to_minutes(current_time)
        start_minutes = time_to_minutes(shift.start_time)
        end_minutes = time_to_minutes(shift.end_time)
        
        # Handle overnight shift
        if start_minutes > end_minutes:  # Overnight shift
            if current_minutes >= start_minutes:
                progress = (current_minutes - start_minutes) / (1440 - start_minutes + end_minutes)
            else:
                progress = (1440 - start_minutes + current_minutes) / (1440 - start_minutes + end_minutes)
        else:  # Regular shift
            if start_minutes <= current_minutes <= end_minutes:
                progress = (current_minutes - start_minutes) / (end_minutes - start_minutes)
            else:
                progress = 0  # Outside shift hours
        
        return min(1.0, max(0.0, progress))
    
    def _calculate_time_remaining(self, shift: Shift) -> str:
        """Calculate time remaining in current shift"""
        
        current_time = datetime.now(self.timezone).time()
        
        # Calculate minutes remaining
        def time_to_minutes(t):
            return t.hour * 60 + t.minute
        
        current_minutes = time_to_minutes(current_time)
        end_minutes = time_to_minutes(shift.end_time)
        
        if shift.start_time > shift.end_time:  # Overnight shift
            if current_minutes >= time_to_minutes(shift.start_time):
                remaining_minutes = 1440 - current_minutes + end_minutes
            else:
                remaining_minutes = end_minutes - current_minutes
        else:  # Regular shift
            remaining_minutes = max(0, end_minutes - current_minutes)
        
        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60
        
        return f"{hours}h {minutes}m"
    
    def _get_agent_availability(self, assigned_agents: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get availability status for assigned agents"""
        
        availability = {}
        
        for agent in assigned_agents:
            # Simulate agent availability (in production, would check real status)
            available = True  # Assume all agents are available in this shift
            workload = np.random.uniform(0.3, 0.8)  # Random workload for demo
            
            availability[agent] = {
                'available': available,
                'current_workload': round(workload, 2),
                'capacity_remaining': round(1.0 - workload, 2),
                'last_activity': datetime.now().isoformat(),
                'shift_role': self._get_agent_shift_role(agent)
            }
        
        return availability
    
    def _get_agent_shift_role(self, agent: str) -> str:
        """Get agent's specific role during current shift"""
        
        shift_roles = {
            # Morning shift roles
            'Warren': 'Pre-market Analysis Lead',
            'Data_Whisperer': 'Market Data Coordinator',
            'Trade_Executor': 'Opening Bell Execution',
            
            # Afternoon shift roles  
            'Cathie': 'Growth Opportunity Scanner',
            'Quant': 'Statistical Analysis Lead',
            'Macro_Monk': 'Strategic Decision Coordinator',
            
            # Night shift roles
            'The_Ghost': 'Overnight Sentiment Monitor',
            'Degen_Auditor': 'Risk Control Supervisor',
            'Black_Swan_Sentinel': 'Crisis Detection Lead'
        }
        
        return shift_roles.get(agent, 'Specialized Agent')
    
    def _get_next_transition_time(self) -> datetime:
        """Calculate when next shift transition should occur"""
        
        current_shift_obj = self.shifts[self.current_shift]
        end_time = current_shift_obj.end_time
        
        # Get current date
        current_date = datetime.now(self.timezone).date()
        
        # Create datetime for shift end
        shift_end = datetime.combine(current_date, end_time)
        shift_end = self.timezone.localize(shift_end)
        
        # If shift end is in the past, it's tomorrow
        if shift_end <= datetime.now(self.timezone):
            shift_end += timedelta(days=1)
        
        return shift_end
    
    def _calculate_avg_transition_time(self) -> float:
        """Calculate average transition time in seconds"""
        
        if not self.transition_logs:
            return 300.0  # 5 minutes default
        
        total_time = sum(t.transition_duration for t in self.transition_logs)
        return total_time / len(self.transition_logs)
    
    def get_24h_schedule(self) -> Dict[str, Any]:
        """Get complete 24-hour shift schedule"""
        
        schedule = {
            'timezone': str(self.timezone),
            'current_shift': self.current_shift.value,
            'schedule': {},
            'coverage_analysis': self._analyze_coverage(),
            'shift_performance': self._get_shift_performance_metrics()
        }
        
        for shift_type, shift in self.shifts.items():
            schedule['schedule'][shift_type.value] = {
                'time_range': f"{shift.start_time.strftime('%H:%M')} - {shift.end_time.strftime('%H:%M')}",
                'duration_hours': self._calculate_shift_duration(shift),
                'lead_agent': shift.shift_lead,
                'agent_count': len(shift.assigned_agents),
                'priority_focus': shift.priority_focus,
                'agents': shift.assigned_agents
            }
        
        return schedule
    
    def _calculate_shift_duration(self, shift: Shift) -> float:
        """Calculate shift duration in hours"""
        
        def time_to_hours(t):
            return t.hour + t.minute / 60
        
        start_hours = time_to_hours(shift.start_time)
        end_hours = time_to_hours(shift.end_time)
        
        if start_hours > end_hours:  # Overnight shift
            duration = (24 - start_hours) + end_hours
        else:
            duration = end_hours - start_hours
        
        return duration
    
    def _analyze_coverage(self) -> Dict[str, Any]:
        """Analyze 24-hour coverage and identify gaps"""
        
        total_hours = sum(self._calculate_shift_duration(shift) for shift in self.shifts.values())
        
        # Count unique agents across all shifts
        all_agents = set()
        for shift in self.shifts.values():
            all_agents.update(shift.assigned_agents)
        
        return {
            'total_coverage_hours': total_hours,
            'coverage_percentage': min(100.0, (total_hours / 24) * 100),
            'unique_agents_utilized': len(all_agents),
            'shift_overlap_agents': self._find_overlap_agents(),
            'coverage_gaps': [] if total_hours >= 24 else ['Potential coverage gap detected']
        }
    
    def _find_overlap_agents(self) -> List[str]:
        """Find agents assigned to multiple shifts"""
        
        agent_shift_count: Dict[str, int] = {}
        
        for shift in self.shifts.values():
            for agent in shift.assigned_agents:
                agent_shift_count[agent] = agent_shift_count.get(agent, 0) + 1
        
        return [agent for agent, count in agent_shift_count.items() if count > 1]
    
    def _get_shift_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for each shift"""
        
        shift_metrics = {}
        
        for shift_type, shift in self.shifts.items():
            # Calculate metrics for this shift
            shift_performance = {
                'agent_efficiency': 0.87,  # Mock data - would calculate from real performance
                'task_completion_rate': 0.94,
                'average_response_time': '2.3 minutes',
                'decision_accuracy': 0.82,
                'coordination_score': 0.89
            }
            
            shift_metrics[shift_type.value] = shift_performance
        
        return shift_metrics
    
    def get_shift_handover_report(self) -> Dict[str, Any]:
        """Generate comprehensive shift handover report"""
        
        if not self.transition_logs:
            return {'message': 'No recent transitions to report'}
        
        latest_transition = self.transition_logs[-1]
        
        return {
            'transition_summary': {
                'from_shift': latest_transition.from_shift.value,
                'to_shift': latest_transition.to_shift.value,
                'transition_time': latest_transition.timestamp.isoformat(),
                'duration_seconds': latest_transition.transition_duration,
                'success': latest_transition.success
            },
            'handover_details': latest_transition.handover_notes,
            'critical_items': latest_transition.critical_items,
            'next_transition': {
                'scheduled_time': self._get_next_transition_time().isoformat(),
                'target_shift': self._get_next_shift().value
            },
            'operational_continuity': {
                'systems_status': 'all_operational',
                'agent_availability': '100%',
                'data_feeds': 'active',
                'trading_systems': 'ready'
            }
        }

# Import numpy for shift calculations
import numpy as np
