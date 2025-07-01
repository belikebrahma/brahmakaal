"""
Authentication Routes
User registration, login, API key management, and subscription handling
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Response
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, EmailStr

from ...db.database import get_db
from ...auth.models import (
    User, APIKey, Subscription, SubscriptionTier, SUBSCRIPTION_LIMITS,
    UserCreate, UserLogin, UserResponse, TokenResponse, APIKeyCreate, 
    APIKeyResponse, SubscriptionResponse, SubscriptionUpdate
)
from ...auth.jwt_handler import jwt_handler
from ...auth.dependencies import (
    get_current_user, require_auth, require_admin,
    AuthenticatedUser, AdminUser, CurrentUser
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Additional models for auth routes
class APIKeyWithSecret(BaseModel):
    """API key response with secret (only shown once)"""
    key: str
    api_key: APIKeyResponse

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# User Authentication Endpoints

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account"""
    # Check if email already exists
    stmt = select(User).where(User.email == user_data.email)
    existing_user = await db.execute(stmt)
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    stmt = select(User).where(User.username == user_data.username)
    existing_username = await db.execute(stmt)
    if existing_username.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = jwt_handler.hash_password(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_verified=False  # Email verification required
    )
    
    db.add(user)
    await db.flush()  # Get user ID
    
    # Create default free subscription
    subscription_config = SUBSCRIPTION_LIMITS[SubscriptionTier.FREE].copy()
    # Remove non-model fields
    subscription_config.pop('price', None)
    subscription_config.pop('features', None)
    
    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.FREE.value,
        features=SUBSCRIPTION_LIMITS[SubscriptionTier.FREE].get('features', {}),
        **subscription_config
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(user)
    
    return user

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """User login with email and password"""
    # Find user by email
    stmt = select(User).where(User.email == user_credentials.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not jwt_handler.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    token_data = jwt_handler.create_user_tokens(
        user_id=user.id,
        email=user.email,
        role=user.role
    )
    
    return TokenResponse(**token_data)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    # Verify refresh token
    payload = jwt_handler.verify_token(refresh_data.refresh_token, "refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    token_data = jwt_handler.create_user_tokens(
        user_id=user.id,
        email=user.email,
        role=user.role
    )
    
    return TokenResponse(**token_data)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: AuthenticatedUser
):
    """Get current user information"""
    return current_user

@router.get("/subscription", response_model=SubscriptionResponse)
async def get_user_subscription(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """Get current user's subscription information"""
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        # Create default free subscription
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
        await db.refresh(subscription)
    
    return subscription

# API Key Management

@router.post("/api-keys", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """Create a new API key for the current user"""
    # Check if user already has too many keys (limit to 10)
    stmt = select(func.count(APIKey.id)).where(
        APIKey.user_id == current_user.id,
        APIKey.is_active == True
    )
    result = await db.execute(stmt)
    active_keys_count = result.scalar()
    
    if active_keys_count >= 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum number of API keys reached (10)"
        )
    
    # Generate new API key
    key, key_hash = APIKey.generate_key()
    
    # Calculate expiration
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key
    api_key = APIKey(
        user_id=current_user.id,
        key_hash=key_hash,
        key_prefix=key[:8],
        name=key_data.name,
        scopes=key_data.scopes,
        expires_at=expires_at
    )
    
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    
    return APIKeyWithSecret(
        key=key,
        api_key=APIKeyResponse.from_orm(api_key)
    )

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """List all API keys for the current user"""
    stmt = select(APIKey).where(
        APIKey.user_id == current_user.id
    ).order_by(APIKey.created_at.desc())
    
    result = await db.execute(stmt)
    api_keys = result.scalars().all()
    
    return [APIKeyResponse.from_orm(key) for key in api_keys]

@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: str,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete an API key"""
    stmt = select(APIKey).where(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    )
    result = await db.execute(stmt)
    api_key = result.scalar_one_or_none()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    await db.commit()

# Subscription Management

@router.post("/subscription/upgrade", response_model=SubscriptionResponse)
async def upgrade_subscription(
    subscription_data: SubscriptionUpdate,
    current_user: AuthenticatedUser,
    db: AsyncSession = Depends(get_db)
):
    """Upgrade user subscription (placeholder for payment integration)"""
    stmt = select(Subscription).where(Subscription.user_id == current_user.id)
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    # Update subscription (in real implementation, this would integrate with payment processor)
    if subscription_data.tier:
        limits = SUBSCRIPTION_LIMITS[subscription_data.tier]
        subscription.tier = subscription_data.tier.value
        subscription.requests_per_minute = limits["requests_per_minute"]
        subscription.requests_per_day = limits["requests_per_day"]
        subscription.requests_per_month = limits["requests_per_month"]
        subscription.features = limits["features"]
        subscription.amount = limits["price"]
    
    if subscription_data.billing_email:
        subscription.billing_email = subscription_data.billing_email
    
    if subscription_data.billing_cycle:
        subscription.billing_cycle = subscription_data.billing_cycle
    
    await db.commit()
    await db.refresh(subscription)
    
    return subscription

# Admin Endpoints

@router.get("/admin/users", response_model=List[UserResponse])
async def list_all_users(
    admin_user: AdminUser,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)"""
    stmt = select(User).offset(offset).limit(limit).order_by(User.created_at.desc())
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    return [UserResponse.from_orm(user) for user in users]

@router.post("/admin/users/{user_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: str,
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a user account (admin only)"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = False
    await db.commit()

@router.post("/admin/users/{user_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_user(
    user_id: str,
    admin_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """Activate a user account (admin only)"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_active = True
    await db.commit() 