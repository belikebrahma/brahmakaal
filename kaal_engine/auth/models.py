"""
Authentication and Subscription Models
Database models for user management, API keys, and subscription tiers
"""

from datetime import datetime as DateTime, timedelta
from typing import Optional, Dict, Any
from enum import Enum
import uuid
import hashlib
import secrets
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, DateTime as SQLDateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, EmailStr

# Import Base from our database module
from ..db.database import Base

class SubscriptionTier(str, Enum):
    """Subscription tier levels with different API limits"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class UserRole(str, Enum):
    """User role levels"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

# Database Models
class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    updated_at = Column(SQLDateTime, default=DateTime.utcnow, onupdate=DateTime.utcnow)
    last_login = Column(SQLDateTime, nullable=True)
    
    # Relationships
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    usage_logs = relationship("UsageLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email='{self.email}', tier='{self.subscription.tier if self.subscription else 'none'}')>"

class APIKey(Base):
    """API key model for authentication"""
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String, nullable=False, unique=True, index=True)
    key_prefix = Column(String(8), nullable=False)  # First 8 chars for identification
    name = Column(String, nullable=False)  # User-defined name for the key
    scopes = Column(JSON, nullable=False, default=list)  # API scopes/permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    last_used = Column(SQLDateTime, nullable=True)
    expires_at = Column(SQLDateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    @classmethod
    def generate_key(cls) -> tuple[str, str]:
        """Generate a new API key and its hash"""
        # Format: bk_live_<32 random chars> or bk_test_<32 random chars>
        key = f"bk_live_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, key_hash
    
    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for storage"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def __repr__(self):
        return f"<APIKey(name='{self.name}', prefix='{self.key_prefix}')>"

class Subscription(Base):
    """User subscription model"""
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    tier = Column(String, default=SubscriptionTier.FREE.value, nullable=False)
    status = Column(String, default="active")  # active, cancelled, expired, suspended
    
    # Limits based on subscription tier
    requests_per_minute = Column(Integer, default=10)
    requests_per_day = Column(Integer, default=1000)
    requests_per_month = Column(Integer, default=10000)
    
    # Subscription dates
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    started_at = Column(SQLDateTime, default=DateTime.utcnow)
    expires_at = Column(SQLDateTime, nullable=True)
    cancelled_at = Column(SQLDateTime, nullable=True)
    
    # Usage tracking
    current_month_usage = Column(Integer, default=0)
    current_day_usage = Column(Integer, default=0)
    total_usage = Column(Integer, default=0)
    last_reset_date = Column(SQLDateTime, default=DateTime.utcnow)
    
    # Billing information
    billing_email = Column(String, nullable=True)
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    amount = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    
    # Features
    features = Column(JSON, default=dict)  # Custom features per subscription
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active"""
        if self.status != "active":
            return False
        if self.expires_at and self.expires_at < DateTime.utcnow():
            return False
        return True
    
    @property
    def days_remaining(self) -> Optional[int]:
        """Get days remaining in subscription"""
        if not self.expires_at:
            return None
        delta = self.expires_at - DateTime.utcnow()
        return max(0, delta.days)
    
    def reset_usage_if_needed(self):
        """Reset usage counters if new billing period"""
        now = DateTime.utcnow()
        if self.last_reset_date.month != now.month or self.last_reset_date.year != now.year:
            self.current_month_usage = 0
            self.last_reset_date = now
        
        if self.last_reset_date.date() != now.date():
            self.current_day_usage = 0
    
    def __repr__(self):
        return f"<Subscription(tier='{self.tier}', status='{self.status}')>"

class UsageLog(Base):
    """API usage logging for analytics and billing"""
    __tablename__ = "usage_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    api_key_id = Column(String, ForeignKey("api_keys.id"), nullable=True)
    
    # Request details
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    
    # Client information
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    referer = Column(String, nullable=True)
    
    # Usage metrics
    request_size_bytes = Column(Integer, default=0)
    response_size_bytes = Column(Integer, default=0)
    cache_hit = Column(Boolean, default=False)
    
    # Timestamp
    timestamp = Column(SQLDateTime, default=DateTime.utcnow, index=True)
    
    # Additional request metadata
    request_metadata = Column(JSON, default=dict)
    
    # Relationships
    user = relationship("User", back_populates="usage_logs")
    
    def __repr__(self):
        return f"<UsageLog(endpoint='{self.endpoint}', status='{self.status_code}')>"

# Pydantic Models for API

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, description="Password")

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    """User response model"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: DateTime
    last_login: Optional[DateTime]
    
    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    """Subscription response model"""
    id: str
    tier: str
    status: str
    requests_per_minute: int
    requests_per_day: int
    requests_per_month: int
    current_month_usage: int
    current_day_usage: int
    total_usage: int
    expires_at: Optional[DateTime]
    days_remaining: Optional[int]
    features: Dict[str, Any]
    
    class Config:
        from_attributes = True

class APIKeyCreate(BaseModel):
    """API key creation model"""
    name: str = Field(..., min_length=1, max_length=100, description="Key name")
    scopes: list[str] = Field(default=[], description="API scopes")
    expires_in_days: Optional[int] = Field(None, ge=1, le=3650, description="Expiration in days")

class APIKeyResponse(BaseModel):
    """API key response model"""
    id: str
    name: str
    key_prefix: str
    scopes: list[str]
    is_active: bool
    created_at: DateTime
    last_used: Optional[DateTime]
    expires_at: Optional[DateTime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    """Subscription update model"""
    tier: Optional[SubscriptionTier] = None
    billing_email: Optional[EmailStr] = None
    billing_cycle: Optional[str] = None

class UsageStats(BaseModel):
    """Usage statistics model"""
    total_requests: int
    requests_today: int
    requests_this_month: int
    average_response_time: float
    cache_hit_rate: float
    top_endpoints: list[Dict[str, Any]]
    usage_by_day: list[Dict[str, Any]]

# Subscription Tier Configurations
SUBSCRIPTION_LIMITS = {
    SubscriptionTier.FREE: {
        "requests_per_minute": 10,
        "requests_per_day": 100,
        "requests_per_month": 1000,
        "features": {
            "panchang_api": True,
            "festivals_api": True,
            "ayanamsha_api": True,
            "muhurta_api": False,
            "export_formats": ["json"],
            "historical_data": False,
            "priority_support": False,
            "rate_limit": "standard"
        },
        "price": 0.0
    },
    SubscriptionTier.BASIC: {
        "requests_per_minute": 60,
        "requests_per_day": 5000,
        "requests_per_month": 50000,
        "features": {
            "panchang_api": True,
            "festivals_api": True,
            "ayanamsha_api": True,
            "muhurta_api": True,
            "export_formats": ["json", "ical"],
            "historical_data": True,
            "priority_support": False,
            "rate_limit": "standard"
        },
        "price": 29.0
    },
    SubscriptionTier.PREMIUM: {
        "requests_per_minute": 300,
        "requests_per_day": 50000,
        "requests_per_month": 500000,
        "features": {
            "panchang_api": True,
            "festivals_api": True,
            "ayanamsha_api": True,
            "muhurta_api": True,
            "export_formats": ["json", "ical", "csv"],
            "historical_data": True,
            "priority_support": True,
            "rate_limit": "enhanced",
            "webhook_support": True,
            "batch_processing": True
        },
        "price": 99.0
    },
    SubscriptionTier.ENTERPRISE: {
        "requests_per_minute": 1000,
        "requests_per_day": 200000,
        "requests_per_month": 2000000,
        "features": {
            "panchang_api": True,
            "festivals_api": True,
            "ayanamsha_api": True,
            "muhurta_api": True,
            "export_formats": ["json", "ical", "csv", "xml"],
            "historical_data": True,
            "priority_support": True,
            "rate_limit": "unlimited",
            "webhook_support": True,
            "batch_processing": True,
            "custom_integration": True,
            "dedicated_support": True,
            "sla_guarantee": True
        },
        "price": 299.0
    }
}

# Webhook Models
class WebhookEndpoint(Base):
    """Customer webhook endpoint configuration"""
    __tablename__ = "webhook_endpoints"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=True)  # HMAC secret
    events = Column(JSON, default=list)  # List of subscribed events
    is_active = Column(Boolean, default=True)
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    updated_at = Column(SQLDateTime, default=DateTime.utcnow, onupdate=DateTime.utcnow)
    last_delivery = Column(SQLDateTime, nullable=True)
    failure_count = Column(Integer, default=0)
    
    # Delivery settings
    timeout_seconds = Column(Integer, default=30)
    retry_attempts = Column(Integer, default=3)

class WebhookDelivery(Base):
    """Webhook delivery attempt log"""
    __tablename__ = "webhook_deliveries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    endpoint_id = Column(String, nullable=False, index=True)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending")  # pending, delivered, failed, retrying
    
    # Delivery details
    http_status = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    delivery_time = Column(SQLDateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    next_retry = Column(SQLDateTime, nullable=True)

# Email Verification Models
class EmailVerification(Base):
    """Email verification tokens"""
    __tablename__ = "email_verifications"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    verified_at = Column(SQLDateTime, nullable=True)
    expires_at = Column(SQLDateTime, nullable=False)

class PasswordReset(Base):
    """Password reset tokens"""
    __tablename__ = "password_resets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(SQLDateTime, default=DateTime.utcnow)
    used_at = Column(SQLDateTime, nullable=True)
    expires_at = Column(SQLDateTime, nullable=False) 