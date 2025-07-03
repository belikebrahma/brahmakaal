"""
Webhook Management Routes
Webhook endpoint management for Premium+ customers
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl

from ...db.database import get_db
from ...auth.dependencies import require_auth, require_subscription
from ...auth.models import User, SubscriptionTier
from ...services.webhook_service import webhook_service, WebhookEventType

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# Pydantic models
class WebhookEndpointCreate(BaseModel):
    """Create webhook endpoint request"""
    url: HttpUrl
    events: List[str]
    secret: Optional[str] = None

class WebhookEndpointUpdate(BaseModel):
    """Update webhook endpoint request"""
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None

class WebhookEndpointResponse(BaseModel):
    """Webhook endpoint response"""
    id: str
    url: str
    events: List[str]
    created_at: str
    last_delivery: Optional[str]
    failure_count: int

class WebhookTestPayload(BaseModel):
    """Test webhook payload"""
    endpoint_id: str

@router.post("/endpoints", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_webhook_endpoint(
    endpoint_data: WebhookEndpointCreate,
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """Create new webhook endpoint (Premium+ only)"""
    
    # Validate event types
    valid_events = [e.value for e in WebhookEventType] + ["all"]
    invalid_events = [e for e in endpoint_data.events if e not in valid_events]
    if invalid_events:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event types: {invalid_events}. Valid events: {valid_events}"
        )
    
    # Create webhook endpoint
    endpoint_id = await webhook_service.register_endpoint(
        user_id=current_user.id,
        url=str(endpoint_data.url),
        events=endpoint_data.events,
        secret=endpoint_data.secret
    )
    
    return {
        "endpoint_id": endpoint_id,
        "message": "Webhook endpoint created successfully",
        "events_subscribed": endpoint_data.events
    }

@router.get("/endpoints", response_model=List[WebhookEndpointResponse])
async def list_webhook_endpoints(
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """List user's webhook endpoints (Premium+ only)"""
    
    endpoints = await webhook_service.get_user_endpoints(current_user.id)
    return endpoints

@router.put("/endpoints/{endpoint_id}", response_model=dict)
async def update_webhook_endpoint(
    endpoint_id: str,
    endpoint_data: WebhookEndpointUpdate,
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """Update webhook endpoint (Premium+ only)"""
    
    # Validate event types if provided
    if endpoint_data.events:
        valid_events = [e.value for e in WebhookEventType] + ["all"]
        invalid_events = [e for e in endpoint_data.events if e not in valid_events]
        if invalid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event types: {invalid_events}"
            )
    
    # Update endpoint
    success = await webhook_service.update_endpoint(
        endpoint_id=endpoint_id,
        user_id=current_user.id,
        url=str(endpoint_data.url) if endpoint_data.url else None,
        events=endpoint_data.events,
        is_active=endpoint_data.is_active
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    return {"message": "Webhook endpoint updated successfully"}

@router.delete("/endpoints/{endpoint_id}", response_model=dict)
async def delete_webhook_endpoint(
    endpoint_id: str,
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """Delete webhook endpoint (Premium+ only)"""
    
    success = await webhook_service.delete_endpoint(endpoint_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    return {"message": "Webhook endpoint deleted successfully"}

@router.post("/test/{endpoint_id}", response_model=dict)
async def test_webhook_endpoint(
    endpoint_id: str,
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """Test webhook endpoint with sample payload (Premium+ only)"""
    
    # Trigger test event
    test_data = {
        "test": True,
        "message": "This is a test webhook from Brahmakaal",
        "timestamp": datetime.utcnow().isoformat(),
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username
        }
    }
    
    await webhook_service.trigger_event(
        user_id=current_user.id,
        event_type=WebhookEventType.USER_VERIFIED,  # Use as test event
        data=test_data
    )
    
    return {
        "message": "Test webhook sent successfully",
        "endpoint_id": endpoint_id,
        "test_data": test_data
    }

@router.get("/events", response_model=dict)
async def list_webhook_events(
    current_user: User = Depends(require_subscription(SubscriptionTier.PREMIUM))
):
    """List available webhook event types (Premium+ only)"""
    
    events = {
        "available_events": [
            {
                "type": event.value,
                "description": event.value.replace(".", " ").replace("_", " ").title()
            }
            for event in WebhookEventType
        ],
        "special_events": [
            {
                "type": "all",
                "description": "Subscribe to all webhook events"
            }
        ]
    }
    
    return events
