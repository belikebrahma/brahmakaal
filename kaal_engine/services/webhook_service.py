"""
Webhook Service for Event Notifications
Handles webhook endpoint management and event delivery
"""

import asyncio
import json
import time
import hmac
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import aiohttp
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_settings
from ..db.database import get_async_session
from ..auth.models import WebhookEndpoint, WebhookDelivery  # Import from auth models

settings = get_settings()

class WebhookEventType(str, Enum):
    """Webhook event types"""
    USER_REGISTERED = "user.registered"
    USER_VERIFIED = "user.verified"
    SUBSCRIPTION_CREATED = "subscription.created"
    SUBSCRIPTION_UPDATED = "subscription.updated"
    SUBSCRIPTION_EXPIRED = "subscription.expired"
    API_KEY_CREATED = "api_key.created"
    API_KEY_DELETED = "api_key.deleted"
    USAGE_LIMIT_REACHED = "usage.limit_reached"
    USAGE_ALERT = "usage.alert"
    RATE_LIMIT_EXCEEDED = "rate_limit.exceeded"

class WebhookStatus(str, Enum):
    """Webhook delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"

class WebhookService:
    """Webhook service for event notifications"""
    
    def __init__(self):
        self.webhook_secret = settings.webhook_secret or "brahmakaal_webhook_secret_2025"
        self.max_retries = 3
        self.retry_delays = [60, 300, 1800]  # 1min, 5min, 30min
        self.timeout = 30
        
        print("✅ Webhook service initialized")
    
    async def register_endpoint(
        self,
        user_id: str,
        url: str,
        events: List[str],
        secret: Optional[str] = None
    ) -> str:
        """Register a new webhook endpoint for user"""
        async with get_async_session() as db:
            endpoint_id = f"wh_{int(time.time())}_{user_id[:8]}"
            
            endpoint = WebhookEndpoint(
                id=endpoint_id,
                user_id=user_id,
                url=url,
                secret=secret or self._generate_secret(),
                events=events,
                is_active=True
            )
            
            db.add(endpoint)
            await db.commit()
            
            print(f"✅ Webhook endpoint registered: {endpoint_id} for user {user_id}")
            return endpoint_id
    
    async def update_endpoint(
        self,
        endpoint_id: str,
        user_id: str,
        url: Optional[str] = None,
        events: Optional[List[str]] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """Update webhook endpoint configuration"""
        async with get_async_session() as db:
            stmt = select(WebhookEndpoint).where(
                and_(
                    WebhookEndpoint.id == endpoint_id,
                    WebhookEndpoint.user_id == user_id
                )
            )
            result = await db.execute(stmt)
            endpoint = result.scalar_one_or_none()
            
            if not endpoint:
                return False
            
            if url is not None:
                endpoint.url = url
            if events is not None:
                endpoint.events = events
            if is_active is not None:
                endpoint.is_active = is_active
            
            endpoint.updated_at = datetime.utcnow()
            await db.commit()
            
            print(f"✅ Webhook endpoint updated: {endpoint_id}")
            return True
    
    async def delete_endpoint(self, endpoint_id: str, user_id: str) -> bool:
        """Delete webhook endpoint"""
        async with get_async_session() as db:
            stmt = select(WebhookEndpoint).where(
                and_(
                    WebhookEndpoint.id == endpoint_id,
                    WebhookEndpoint.user_id == user_id
                )
            )
            result = await db.execute(stmt)
            endpoint = result.scalar_one_or_none()
            
            if not endpoint:
                return False
            
            await db.delete(endpoint)
            await db.commit()
            
            print(f"✅ Webhook endpoint deleted: {endpoint_id}")
            return True
    
    async def get_user_endpoints(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all webhook endpoints for user"""
        async with get_async_session() as db:
            stmt = select(WebhookEndpoint).where(
                and_(
                    WebhookEndpoint.user_id == user_id,
                    WebhookEndpoint.is_active == True
                )
            )
            result = await db.execute(stmt)
            endpoints = result.scalars().all()
            
            return [
                {
                    "id": ep.id,
                    "url": ep.url,
                    "events": ep.events,
                    "created_at": ep.created_at.isoformat(),
                    "last_delivery": ep.last_delivery.isoformat() if ep.last_delivery else None,
                    "failure_count": ep.failure_count
                }
                for ep in endpoints
            ]
    
    async def trigger_event(
        self,
        user_id: str,
        event_type: WebhookEventType,
        data: Dict[str, Any]
    ):
        """Trigger webhook event for user"""
        async with get_async_session() as db:
            # Get user's webhook endpoints subscribed to this event
            stmt = select(WebhookEndpoint).where(
                and_(
                    WebhookEndpoint.user_id == user_id,
                    WebhookEndpoint.is_active == True
                )
            )
            result = await db.execute(stmt)
            endpoints = result.scalars().all()
            
            # Filter endpoints subscribed to this event type
            subscribed_endpoints = [
                ep for ep in endpoints 
                if event_type.value in ep.events or "all" in ep.events
            ]
            
            if not subscribed_endpoints:
                return
            
            # Create webhook payload
            payload = {
                "event": event_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "data": data
            }
            
            # Queue deliveries for each endpoint
            for endpoint in subscribed_endpoints:
                await self._queue_delivery(endpoint, payload)
    
    async def _queue_delivery(self, endpoint: WebhookEndpoint, payload: Dict[str, Any]):
        """Queue webhook delivery"""
        async with get_async_session() as db:
            delivery_id = f"del_{int(time.time())}_{endpoint.id[:8]}"
            
            delivery = WebhookDelivery(
                id=delivery_id,
                endpoint_id=endpoint.id,
                event_type=payload["event"],
                payload=payload,
                status=WebhookStatus.PENDING.value
            )
            
            db.add(delivery)
            await db.commit()
            
            # Attempt immediate delivery
            asyncio.create_task(self._attempt_delivery(delivery_id))
    
    async def _attempt_delivery(self, delivery_id: str):
        """Attempt webhook delivery"""
        async with get_async_session() as db:
            # Get delivery record
            stmt = select(WebhookDelivery).where(WebhookDelivery.id == delivery_id)
            result = await db.execute(stmt)
            delivery = result.scalar_one_or_none()
            
            if not delivery:
                return
            
            # Get endpoint
            stmt = select(WebhookEndpoint).where(WebhookEndpoint.id == delivery.endpoint_id)
            result = await db.execute(stmt)
            endpoint = result.scalar_one_or_none()
            
            if not endpoint or not endpoint.is_active:
                delivery.status = WebhookStatus.FAILED.value
                delivery.error_message = "Endpoint not found or inactive"
                await db.commit()
                return
            
            try:
                # Prepare headers
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Brahmakaal-Webhooks/1.0",
                    "X-Brahmakaal-Event": delivery.event_type,
                    "X-Brahmakaal-Delivery": delivery_id,
                    "X-Brahmakaal-Timestamp": str(int(time.time()))
                }
                
                # Add HMAC signature if secret is configured
                if endpoint.secret:
                    payload_bytes = json.dumps(delivery.payload, sort_keys=True).encode()
                    signature = hmac.new(
                        endpoint.secret.encode(),
                        payload_bytes,
                        hashlib.sha256
                    ).hexdigest()
                    headers["X-Brahmakaal-Signature"] = f"sha256={signature}"
                
                # Make HTTP request
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=endpoint.timeout_seconds)) as session:
                    async with session.post(
                        endpoint.url,
                        data=json.dumps(payload),
                        headers=headers
                    ) as response:
                        response_text = await response.text()
                
                # Update delivery record
                delivery.http_status = response.status
                delivery.response_body = response_text[:1000]  # Truncate long responses
                delivery.delivery_time = datetime.utcnow()
                
                if 200 <= response.status < 300:
                    delivery.status = WebhookStatus.DELIVERED.value
                    endpoint.last_delivery = datetime.utcnow()
                    endpoint.failure_count = 0
                    print(f"✅ Webhook delivered: {delivery_id} to {endpoint.url}")
                else:
                    await self._handle_delivery_failure(delivery, endpoint, f"HTTP {response.status}")
                
            except Exception as e:
                await self._handle_delivery_failure(delivery, endpoint, str(e))
            
            await db.commit()
    
    async def _handle_delivery_failure(self, delivery: WebhookDelivery, endpoint: WebhookEndpoint, error: str):
        """Handle webhook delivery failure"""
        delivery.error_message = error
        delivery.retry_count += 1
        endpoint.failure_count += 1
        
        if delivery.retry_count <= self.max_retries:
            # Schedule retry
            retry_delay = self.retry_delays[min(delivery.retry_count - 1, len(self.retry_delays) - 1)]
            delivery.next_retry = datetime.utcnow() + timedelta(seconds=retry_delay)
            delivery.status = WebhookStatus.RETRYING.value
            
            print(f"⚠️ Webhook delivery failed, will retry: {delivery.id} (attempt {delivery.retry_count})")
            
            # Schedule retry task
            asyncio.create_task(self._schedule_retry(delivery.id, retry_delay))
        else:
            delivery.status = WebhookStatus.FAILED.value
            print(f"❌ Webhook delivery failed permanently: {delivery.id}")
    
    async def _schedule_retry(self, delivery_id: str, delay_seconds: int):
        """Schedule webhook retry"""
        await asyncio.sleep(delay_seconds)
        await self._attempt_delivery(delivery_id)
    
    async def process_retry_queue(self):
        """Process pending webhook retries"""
        async with get_async_session() as db:
            now = datetime.utcnow()
            stmt = select(WebhookDelivery).where(
                and_(
                    WebhookDelivery.status == WebhookStatus.RETRYING.value,
                    WebhookDelivery.next_retry <= now
                )
            )
            result = await db.execute(stmt)
            pending_deliveries = result.scalars().all()
            
            for delivery in pending_deliveries:
                asyncio.create_task(self._attempt_delivery(delivery.id))
    
    def _generate_secret(self) -> str:
        """Generate webhook secret"""
        return secrets.token_urlsafe(32)
    
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature"""
        if not signature.startswith("sha256="):
            return False
        
        expected_signature = hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        received_signature = signature[7:]  # Remove "sha256=" prefix
        return hmac.compare_digest(expected_signature, received_signature)

# Global webhook service instance
webhook_service = WebhookService()
