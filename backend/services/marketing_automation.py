"""
Marketing Automation Service
============================
Comprehensive marketing automation system providing:
- Lead capture and management
- Drip campaign automation
- Customer journey event tracking
- Email template system
- Segmentation and targeting

Author: YantraX-RL Platform
Created: August 28, 2025
"""

import logging
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from uuid import uuid4
import redis
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"
    NURTURING = "nurturing"

class CampaignStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class EventType(Enum):
    PAGE_VIEW = "page_view"
    FORM_SUBMIT = "form_submit"
    EMAIL_OPEN = "email_open"
    EMAIL_CLICK = "email_click"
    PURCHASE = "purchase"
    DOWNLOAD = "download"
    CUSTOM = "custom"

@dataclass
class Lead:
    """Lead data model."""
    id: str
    email: str
    first_name: str = ""
    last_name: str = ""
    company: str = ""
    phone: str = ""
    status: LeadStatus = LeadStatus.NEW
    source: str = ""
    score: int = 0
    tags: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class EmailTemplate:
    """Email template model."""
    id: str
    name: str
    subject: str
    html_content: str
    text_content: str = ""
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CampaignStep:
    """Individual step in a drip campaign."""
    id: str
    name: str
    email_template_id: str
    delay_days: int
    delay_hours: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DripCampaign:
    """Drip campaign model."""
    id: str
    name: str
    description: str
    status: CampaignStatus
    steps: List[CampaignStep]
    target_segments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class JourneyEvent:
    """Customer journey event model."""
    id: str
    lead_id: str
    event_type: EventType
    event_name: str
    properties: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    campaign_id: Optional[str] = None

class IEmailProvider(ABC):
    """Abstract interface for email providers."""
    
    @abstractmethod
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        pass

class SMTPEmailProvider(IEmailProvider):
    """SMTP email provider implementation."""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = "") -> bool:
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

class LeadCaptureService:
    """Service for capturing and managing leads."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def capture_lead(self, lead_data: Dict[str, Any], source: str = "unknown") -> Lead:
        """Capture a new lead."""
        lead_id = str(uuid4())
        
        lead = Lead(
            id=lead_id,
            email=lead_data.get('email', ''),
            first_name=lead_data.get('first_name', ''),
            last_name=lead_data.get('last_name', ''),
            company=lead_data.get('company', ''),
            phone=lead_data.get('phone', ''),
            source=source,
            custom_fields=lead_data.get('custom_fields', {})
        )
        
        await self._store_lead(lead)
        logger.info(f"Captured lead {lead_id} from source {source}")
        return lead
    
    async def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Retrieve lead by ID."""
        try:
            lead_data = self.redis.hgetall(f"lead:{lead_id}")
            if not lead_data:
                return None
            
            return Lead(
                id=lead_data['id'],
                email=lead_data['email'],
                first_name=lead_data.get('first_name', ''),
                last_name=lead_data.get('last_name', ''),
                company=lead_data.get('company', ''),
                phone=lead_data.get('phone', ''),
                status=LeadStatus(lead_data.get('status', 'new')),
                source=lead_data.get('source', ''),
                score=int(lead_data.get('score', 0)),
                tags=json.loads(lead_data.get('tags', '[]')),
                custom_fields=json.loads(lead_data.get('custom_fields', '{}')),
                created_at=datetime.fromisoformat(lead_data['created_at']),
                updated_at=datetime.fromisoformat(lead_data['updated_at'])
            )
        except Exception as e:
            logger.error(f"Error retrieving lead {lead_id}: {e}")
            return None
    
    async def update_lead_status(self, lead_id: str, status: LeadStatus) -> bool:
        """Update lead status."""
        try:
            self.redis.hset(f"lead:{lead_id}", "status", status.value)
            self.redis.hset(f"lead:{lead_id}", "updated_at", datetime.now().isoformat())
            return True
        except Exception as e:
            logger.error(f"Error updating lead status: {e}")
            return False
    
    async def _store_lead(self, lead: Lead) -> bool:
        """Store lead in Redis."""
        try:
            lead_data = {
                'id': lead.id,
                'email': lead.email,
                'first_name': lead.first_name,
                'last_name': lead.last_name,
                'company': lead.company,
                'phone': lead.phone,
                'status': lead.status.value,
                'source': lead.source,
                'score': lead.score,
                'tags': json.dumps(lead.tags),
                'custom_fields': json.dumps(lead.custom_fields),
                'created_at': lead.created_at.isoformat(),
                'updated_at': lead.updated_at.isoformat()
            }
            
            self.redis.hmset(f"lead:{lead.id}", lead_data)
            self.redis.sadd(f"leads_by_status:{lead.status.value}", lead.id)
            self.redis.sadd(f"leads_by_source:{lead.source}", lead.id)
            
            return True
        except Exception as e:
            logger.error(f"Error storing lead {lead.id}: {e}")
            return False

class JourneyTrackingService:
    """Service for tracking customer journey events."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def track_event(self, lead_id: str, event_type: EventType, event_name: str, 
                         properties: Optional[Dict[str, Any]] = None) -> JourneyEvent:
        """Track a customer journey event."""
        event_id = str(uuid4())
        
        event = JourneyEvent(
            id=event_id,
            lead_id=lead_id,
            event_type=event_type,
            event_name=event_name,
            properties=properties or {}
        )
        
        await self._store_event(event)
        logger.info(f"Tracked event {event_name} for lead {lead_id}")
        return event
    
    async def get_lead_journey(self, lead_id: str, limit: int = 100) -> List[JourneyEvent]:
        """Get journey events for a lead."""
        try:
            event_ids = self.redis.lrange(f"lead_events:{lead_id}", 0, limit - 1)
            events = []
            
            for event_id in event_ids:
                event_data = self.redis.hgetall(f"event:{event_id}")
                if event_data:
                    event = JourneyEvent(
                        id=event_data['id'],
                        lead_id=event_data['lead_id'],
                        event_type=EventType(event_data['event_type']),
                        event_name=event_data['event_name'],
                        properties=json.loads(event_data['properties']),
                        timestamp=datetime.fromisoformat(event_data['timestamp'])
                    )
                    events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error getting lead journey: {e}")
            return []
    
    async def _store_event(self, event: JourneyEvent) -> bool:
        """Store event in Redis."""
        try:
            event_data = {
                'id': event.id,
                'lead_id': event.lead_id,
                'event_type': event.event_type.value,
                'event_name': event.event_name,
                'properties': json.dumps(event.properties),
                'timestamp': event.timestamp.isoformat()
            }
            
            self.redis.hmset(f"event:{event.id}", event_data)
            self.redis.lpush(f"lead_events:{event.lead_id}", event.id)
            self.redis.ltrim(f"lead_events:{event.lead_id}", 0, 999)
            
            return True
        except Exception as e:
            logger.error(f"Error storing event {event.id}: {e}")
            return False

class DripCampaignService:
    """Service for managing drip campaigns."""
    
    def __init__(self, redis_client: redis.Redis, email_provider: IEmailProvider):
        self.redis = redis_client
        self.email_provider = email_provider
    
    async def create_campaign(self, campaign_data: Dict[str, Any]) -> DripCampaign:
        """Create a new drip campaign."""
        campaign_id = str(uuid4())
        
        steps = []
        for step_data in campaign_data.get('steps', []):
            step = CampaignStep(
                id=str(uuid4()),
                name=step_data['name'],
                email_template_id=step_data['email_template_id'],
                delay_days=step_data.get('delay_days', 0),
                delay_hours=step_data.get('delay_hours', 0),
                conditions=step_data.get('conditions', {})
            )
            steps.append(step)
        
        campaign = DripCampaign(
            id=campaign_id,
            name=campaign_data['name'],
            description=campaign_data.get('description', ''),
            status=CampaignStatus.DRAFT,
            steps=steps,
            target_segments=campaign_data.get('target_segments', [])
        )
        
        await self._store_campaign(campaign)
        logger.info(f"Created campaign {campaign_id}: {campaign.name}")
        return campaign
    
    async def start_campaign(self, campaign_id: str) -> bool:
        """Start a campaign."""
        try:
            self.redis.hset(f"campaign:{campaign_id}", "status", CampaignStatus.ACTIVE.value)
            logger.info(f"Started campaign {campaign_id}")
            return True
        except Exception as e:
            logger.error(f"Error starting campaign: {e}")
            return False
