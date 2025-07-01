"""
Authentication Middleware
Middleware for handling authentication and setting request state
"""

from typing import Optional
from fastapi import Request, HTTPException
from fastapi.security.utils import get_authorization_scheme_param
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..db.database import get_async_session
from .models import User, APIKey, Subscription, SubscriptionTier
from .jwt_handler import jwt_handler

class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self):
        pass
    
    async def __call__(self, request: Request, call_next):
        """Process authentication for requests"""
        # Skip authentication for health and docs endpoints
        if request.url.path in ["/v1/health", "/docs", "/redoc", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # Initialize request state
        request.state.user_id = None
        request.state.user = None
        request.state.subscription_tier = SubscriptionTier.FREE
        request.state.api_key = None
        
        # Try to authenticate user
        user = await self._authenticate_request(request)
        if user:
            request.state.user_id = user.id
            request.state.user = user
            
            # Get user subscription
            subscription = await self._get_user_subscription(user.id)
            if subscription and subscription.is_active:
                request.state.subscription_tier = SubscriptionTier(subscription.tier)
        
        response = await call_next(request)
        return response
    
    async def _authenticate_request(self, request: Request) -> Optional[User]:
        """Authenticate request using JWT token or API key"""
        # Try JWT token first
        authorization = request.headers.get("Authorization")
        if authorization:
            scheme, token = get_authorization_scheme_param(authorization)
            if scheme.lower() == "bearer":
                user = await self._authenticate_with_jwt(token)
                if user:
                    return user
        
        # Try API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            user = await self._authenticate_with_api_key(api_key)
            if user:
                request.state.api_key = api_key
                return user
        
        return None
    
    async def _authenticate_with_jwt(self, token: str) -> Optional[User]:
        """Authenticate with JWT token"""
        payload = jwt_handler.verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        async with get_async_session() as db:
            stmt = select(User).where(User.id == user_id, User.is_active == True)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
    
    async def _authenticate_with_api_key(self, api_key: str) -> Optional[User]:
        """Authenticate with API key"""
        key_hash = APIKey.hash_key(api_key)
        
        async with get_async_session() as db:
            # Find API key
            stmt = select(APIKey).where(
                APIKey.key_hash == key_hash,
                APIKey.is_active == True
            )
            result = await db.execute(stmt)
            api_key_obj = result.scalar_one_or_none()
            
            if not api_key_obj:
                return None
            
            # Check expiration
            from datetime import datetime
            if api_key_obj.expires_at and api_key_obj.expires_at < datetime.utcnow():
                return None
            
            # Get user
            stmt = select(User).where(
                User.id == api_key_obj.user_id,
                User.is_active == True
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Update last used
                api_key_obj.last_used = datetime.utcnow()
                await db.commit()
            
            return user
    
    async def _get_user_subscription(self, user_id: str) -> Optional[Subscription]:
        """Get user subscription"""
        async with get_async_session() as db:
            stmt = select(Subscription).where(Subscription.user_id == user_id)
            result = await db.execute(stmt)
            subscription = result.scalar_one_or_none()
            
            if subscription:
                subscription.reset_usage_if_needed()
                await db.commit()
            
            return subscription 