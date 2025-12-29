"""
API Monetization Service
========================

Comprehensive API monetization system supporting:
- API key management and authentication
- Real-time usage tracking and analytics
- Configurable rate limiting
- Quota-based billing logic
- Extensible pricing models

Author: YantraX-RL Platform
Created: August 28, 2025
"""

import hashlib
import logging
import time
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import redis
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APITier(Enum):
    """API service tiers with different limits and pricing."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class BillingModel(Enum):
    """Different billing models supported."""
    PAY_PER_REQUEST = "pay_per_request"
    MONTHLY_QUOTA = "monthly_quota"
    TIERED_USAGE = "tiered_usage"
    CUSTOM_PRICING = "custom_pricing"


class RateLimitWindow(Enum):
    """Rate limiting time windows."""
    SECOND = 1
    MINUTE = 60
    HOUR = 3600
    DAY = 86400
    MONTH = 2592000


@dataclass
class APIQuota:
    """API quota configuration for different endpoints."""
    requests_per_second: int = 10
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    requests_per_month: int = 100000
    bandwidth_mb_per_month: int = 1000
    concurrent_requests: int = 5


@dataclass
class PricingTier:
    """Pricing tier configuration."""
    name: str
    tier: APITier
    quota: APIQuota
    price_per_request: Decimal = Decimal('0.001')
    monthly_fee: Decimal = Decimal('0.00')
    overage_rate: Decimal = Decimal('0.002')
    billing_model: BillingModel = BillingModel.PAY_PER_REQUEST
    features: List[str] = field(default_factory=list)


@dataclass
class UsageRecord:
    """Individual API usage record."""
    api_key_id: str
    endpoint: str
    method: str
    timestamp: datetime
    response_time_ms: int
    status_code: int
    request_size_bytes: int = 0
    response_size_bytes: int = 0
    cost: Decimal = Decimal('0.00')
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIKey:
    """API key model with associated metadata."""
    key_id: str
    api_key: str
    user_id: str
    name: str
    tier: APITier
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    allowed_ips: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    scopes: List[str] = field(default_factory=list)
    rate_limit_overrides: Optional[APIQuota] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IPricingCalculator(ABC):
    """Abstract interface for pricing calculations."""
    
    @abstractmethod
    async def calculate_cost(self, usage_record: UsageRecord, tier: PricingTier) -> Decimal:
        """Calculate cost for a single usage record."""
        pass
    
    @abstractmethod
    async def calculate_monthly_bill(self, usage_records: List[UsageRecord], tier: PricingTier) -> Decimal:
        """Calculate total monthly bill."""
        pass


class StandardPricingCalculator(IPricingCalculator):
    """Standard pricing calculator implementation."""
    
    async def calculate_cost(self, usage_record: UsageRecord, tier: PricingTier) -> Decimal:
        """Calculate cost based on pricing tier and usage."""
        base_cost = tier.price_per_request
        
        # Add size-based pricing for large requests/responses
        if usage_record.request_size_bytes > 1024:  # 1KB threshold
            size_factor = Decimal(str(usage_record.request_size_bytes / 1024))
            base_cost *= size_factor
        
        # Discount for failed requests (debugging costs)
        if usage_record.status_code >= 400:
            base_cost *= Decimal('0.5')
        
        return base_cost
    
    async def calculate_monthly_bill(self, usage_records: List[UsageRecord], tier: PricingTier) -> Decimal:
        """Calculate monthly bill with tier-based logic."""
        total_requests = len(usage_records)
        base_requests = tier.quota.requests_per_month
        total_cost = tier.monthly_fee
        
        if tier.billing_model == BillingModel.PAY_PER_REQUEST:
            for record in usage_records:
                total_cost += await self.calculate_cost(record, tier)
        elif tier.billing_model == BillingModel.MONTHLY_QUOTA:
            if total_requests > base_requests:
                overage = total_requests - base_requests
                total_cost += Decimal(str(overage)) * tier.overage_rate
        
        return total_cost


class RateLimiter:
    """Redis-based distributed rate limiter."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def is_rate_limited(self, api_key: str, quota: APIQuota, endpoint: str = "default") -> Tuple[bool, Dict[str, int]]:
        """Check if API key is rate limited."""
        current_time = int(time.time())
        limits = {
            'second': (quota.requests_per_second, RateLimitWindow.SECOND.value),
            'minute': (quota.requests_per_minute, RateLimitWindow.MINUTE.value),
            'hour': (quota.requests_per_hour, RateLimitWindow.HOUR.value),
        }
        
        remaining_limits = {}
        
        for window_name, (limit, window_seconds) in limits.items():
            key = f"rate_limit:{api_key}:{endpoint}:{window_name}:{current_time // window_seconds}"
            
            try:
                pipe = self.redis.pipeline()
                pipe.incr(key)
                pipe.expire(key, window_seconds)
                results = pipe.execute()
                
                current_count = results[0]
                remaining_limits[window_name] = max(0, limit - current_count)
                
                if current_count > limit:
                    return True, remaining_limits
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                remaining_limits[window_name] = limit
        
        return False, remaining_limits


class UsageTracker:
    """Tracks API usage and stores analytics data."""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
    
    async def record_usage(self, usage_record: UsageRecord) -> bool:
        """Record API usage event."""
        try:
            record_key = f"usage:{usage_record.api_key_id}:{usage_record.timestamp.isoformat()}"
            record_data = {
                'endpoint': usage_record.endpoint,
                'method': usage_record.method,
                'timestamp': usage_record.timestamp.isoformat(),
                'response_time_ms': usage_record.response_time_ms,
                'status_code': usage_record.status_code,
                'cost': str(usage_record.cost)
            }
            
            self.redis.hmset(record_key, record_data)
            self.redis.expire(record_key, 7776000)  # 90 days
            return True
        except Exception as e:
            logger.error(f"Error recording usage: {e}")
            return False


class APIMonetizationService:
    """Main API monetization service orchestrating all components."""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        """Initialize the API monetization service."""
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.rate_limiter = RateLimiter(self.redis)
        self.usage_tracker = UsageTracker(self.redis)
        self.pricing_calculator = StandardPricingCalculator()
        self.pricing_tiers = self._initialize_default_tiers()
    
    def _initialize_default_tiers(self) -> Dict[APITier, PricingTier]:
        """Initialize default pricing tiers."""
        return {
            APITier.FREE: PricingTier(
                name="Free Tier",
                tier=APITier.FREE,
                quota=APIQuota(requests_per_day=1000, requests_per_month=10000),
                price_per_request=Decimal('0.00'),
                billing_model=BillingModel.MONTHLY_QUOTA
            ),
            APITier.BASIC: PricingTier(
                name="Basic Tier",
                tier=APITier.BASIC,
                quota=APIQuota(requests_per_day=10000, requests_per_month=100000),
                monthly_fee=Decimal('29.99'),
                billing_model=BillingModel.MONTHLY_QUOTA
            ),
            APITier.PRO: PricingTier(
                name="Pro Tier",
                tier=APITier.PRO,
                quota=APIQuota(requests_per_day=100000, requests_per_month=1000000),
                monthly_fee=Decimal('99.99'),
                billing_model=BillingModel.TIERED_USAGE
            )
        }
    
    async def generate_api_key(self, user_id: str, name: str, tier: APITier) -> APIKey:
        """Generate a new API key for a user."""
        key_id = str(uuid4())
        key_data = f"{user_id}:{key_id}:{time.time()}"
        api_key = f"yx_{hashlib.sha256(key_data.encode()).hexdigest()[:32]}"
        
        api_key_obj = APIKey(
            key_id=key_id,
            api_key=api_key,
            user_id=user_id,
            name=name,
            tier=tier,
            created_at=datetime.now()
        )
        
        # Store in Redis
        key_data = {
            'key_id': key_id,
            'user_id': user_id,
            'name': name,
            'tier': tier.value,
            'created_at': api_key_obj.created_at.isoformat(),
            'is_active': str(api_key_obj.is_active)
        }
        
        self.redis.hmset(f"api_key:{api_key}", key_data)
        self.redis.sadd(f"user_keys:{user_id}", api_key)
        
        logger.info(f"Generated API key {key_id} for user {user_id}")
        return api_key_obj
    
    async def validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate an API key and return key details."""
        try:
            key_data = self.redis.hgetall(f"api_key:{api_key}")
            if not key_data or key_data.get('is_active') != 'True':
                return None
            
            return APIKey(
                key_id=key_data['key_id'],
                api_key=api_key,
                user_id=key_data['user_id'],
                name=key_data['name'],
                tier=APITier(key_data['tier']),
                created_at=datetime.fromisoformat(key_data['created_at'])
            )
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    async def check_rate_limits(self, api_key: str, endpoint: str = "default") -> Tuple[bool, Dict[str, int]]:
        """Check if API key is within rate limits."""
        key_obj = await self.validate_api_key(api_key)
        if not key_obj:
            return True, {}  # Invalid key = rate limited
        
        tier = self.pricing_tiers[key_obj.tier]
        return await self.rate_limiter.is_rate_limited(api_key, tier.quota, endpoint)
    
    async def record_api_usage(self, api_key: str, endpoint: str, method: str, 
                             response_time_ms: int, status_code: int) -> bool:
        """Record API usage for billing and analytics."""
        key_obj = await self.validate_api_key(api_key)
        if not key_obj:
            return False
        
        tier = self.pricing_tiers[key_obj.tier]
        usage_record = UsageRecord(
            api_key_id=key_obj.key_id,
            endpoint=endpoint,
            method=method,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            status_code=status_code,
            request_size_bytes=0,
            response_size_bytes=0,
            cost=Decimal('0.00'),
            metadata={}
        )

        # Calculate cost (best-effort). If pricing calculation fails, continue and record with zero cost.
        try:
            cost = await self.pricing_calculator.calculate_cost(usage_record, tier)
            usage_record.cost = cost
        except Exception as e:
            logger.warning(f"Pricing calculation failed: {e}. Recording usage with zero cost.")

        # Record usage in Redis/analytics (best-effort)
        try:
            await self.usage_tracker.record_usage(usage_record)
            return True
        except Exception as e:
            logger.error(f"Failed to record API usage: {e}")
            return False
