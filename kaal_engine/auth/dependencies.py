"""
Authentication Dependencies
FastAPI dependencies for user authentication and authorization
"""

from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..db.database import get_db
from .models import User, APIKey, Subscription, SubscriptionTier, SUBSCRIPTION_LIMITS
from .jwt_handler import jwt_handler

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from JWT token"""
    if not credentials:
        return None
    
    # Verify JWT token
    payload = jwt_handler.verify_token(credentials.credentials)
    if not payload:
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Get user from database
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        # Update last login
        user.last_login = datetime.utcnow()
        await db.commit()
    
    return user

async def get_current_user_from_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Get current user from API key"""
    if not x_api_key:
        return None
    
    # Hash the provided key
    key_hash = APIKey.hash_key(x_api_key)
    
    # Find API key in database
    stmt = select(APIKey).where(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    )
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        return None
    
    # Check if key is expired
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        return None
    
    # Update last used
    api_key.last_used = datetime.utcnow()
    
    # Get associated user
    stmt = select(User).where(
        User.id == api_key.user_id,
        User.is_active == True
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        await db.commit()
    
    return user

async def get_current_user(
    token_user: Optional[User] = Depends(get_current_user_from_token),
    api_key_user: Optional[User] = Depends(get_current_user_from_api_key)
) -> Optional[User]:
    """Get current user from either JWT token or API key"""
    return token_user or api_key_user

async def require_auth(
    current_user: Optional[User] = Depends(get_current_user)
) -> User:
    """Require authentication"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user

async def require_verified_user(
    current_user: User = Depends(require_auth)
) -> User:
    """Require verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(require_auth)
) -> User:
    """Require admin privileges"""
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_user_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Optional[Subscription]:
    """Get user subscription"""
    if not current_user:
        return None
    
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if subscription:
        # Reset usage counters if needed
        subscription.reset_usage_if_needed()
        await db.commit()
    
    return subscription

async def require_subscription(
    min_tier: SubscriptionTier = SubscriptionTier.FREE
) -> User:
    """Require specific subscription tier"""
    async def _require_subscription(
        current_user: User = Depends(require_auth),
        subscription: Optional[Subscription] = Depends(get_user_subscription)
    ) -> User:
        if not subscription or not subscription.is_active:
            # Create default free subscription if none exists
            if not subscription:
                from ..db.database import get_db
                db = await anext(get_db())
                
                subscription_config = SUBSCRIPTION_LIMITS[SubscriptionTier.FREE].copy()
                # Remove non-model fields
                subscription_config.pop('price', None)
                subscription_config.pop('features', None)
                
                subscription = Subscription(
                    user_id=current_user.id,
                    tier=SubscriptionTier.FREE.value,
                    features=SUBSCRIPTION_LIMITS[SubscriptionTier.FREE].get('features', {}),
                    **subscription_config
                )
                db.add(subscription)
                await db.commit()
            else:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail="Active subscription required"
                )
        
        # Check tier requirements
        tier_order = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.BASIC: 1,
            SubscriptionTier.PREMIUM: 2,
            SubscriptionTier.ENTERPRISE: 3
        }
        
        user_tier = SubscriptionTier(subscription.tier)
        if tier_order[user_tier] < tier_order[min_tier]:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"Subscription tier '{min_tier.value}' or higher required"
            )
        
        return current_user
    
    return _require_subscription

async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db)
) -> Optional[APIKey]:
    """Get API key from header"""
    if not x_api_key:
        return None
    
    key_hash = APIKey.hash_key(x_api_key)
    
    stmt = select(APIKey).where(
        APIKey.key_hash == key_hash,
        APIKey.is_active == True
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

# Type annotations for dependency injection
CurrentUser = Annotated[Optional[User], Depends(get_current_user)]
AuthenticatedUser = Annotated[User, Depends(require_auth)]
VerifiedUser = Annotated[User, Depends(require_verified_user)]
AdminUser = Annotated[User, Depends(require_admin)]
UserSubscription = Annotated[Optional[Subscription], Depends(get_user_subscription)] 