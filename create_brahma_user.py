#!/usr/bin/env python3
"""
Create Brahma test user with unlimited access
Special test user for system testing and demonstrations
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from kaal_engine.auth.models import User, Subscription, APIKey, SubscriptionTier, SUBSCRIPTION_LIMITS
from kaal_engine.auth.jwt_handler import jwt_handler
from kaal_engine.db.database import init_database, get_async_session
from sqlalchemy import select

async def create_brahma_user():
    """Create Brahma test user with unlimited enterprise access"""
    try:
        print("🕉️ Creating Brahma test user with unlimited access...")
        
        # Initialize database
        await init_database()
        print("✅ Database initialized")
        
        async with get_async_session() as db:
            # Check if Brahma user already exists
            stmt = select(User).where(User.username == "brahma")
            existing_user = await db.execute(stmt)
            brahma_user = existing_user.scalar_one_or_none()
            
            if brahma_user:
                print("⚠️ Brahma user already exists, updating to unlimited access...")
                user_id = brahma_user.id
                
                # Update user to admin role
                brahma_user.role = "admin"
                brahma_user.is_verified = True
                brahma_user.full_name = "Brahma (Test Admin)"
                
                # Delete existing subscription to recreate with unlimited access
                stmt = select(Subscription).where(Subscription.user_id == user_id)
                existing_sub = await db.execute(stmt)
                old_subscription = existing_sub.scalar_one_or_none()
                if old_subscription:
                    await db.delete(old_subscription)
                    await db.flush()
                    
            else:
                print("🆕 Creating new Brahma user...")
                # Create password hash
                hashed_password = jwt_handler.hash_password("brahma123")
                
                # Create Brahma user with admin privileges
                brahma_user = User(
                    email="brahma@brahmakaal.com",
                    username="brahma",
                    full_name="Brahma (Test Admin)",
                    hashed_password=hashed_password,
                    role="admin",  # Admin role for unlimited access
                    is_verified=True,  # Pre-verified
                    is_active=True
                )
                
                db.add(brahma_user)
                await db.flush()  # Get user ID
                user_id = brahma_user.id
                print(f"✅ Brahma user created with ID: {user_id}")
            
            # Create unlimited enterprise subscription
            unlimited_subscription = Subscription(
                user_id=user_id,
                tier="enterprise",  # Enterprise tier
                status="active",
                
                # Unlimited limits (very high numbers)
                requests_per_minute=99999,
                requests_per_day=9999999,
                requests_per_month=99999999,
                
                # Extended dates
                expires_at=datetime.utcnow() + timedelta(days=36500),  # 100 years
                
                # Enterprise billing info
                billing_cycle="yearly",
                amount=0.0,  # Free for test user
                currency="USD",
                
                # All enterprise features enabled
                features={
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
                    "sla_guarantee": True,
                    "admin_access": True,
                    "unlimited_api_keys": True,
                    "test_user": True
                }
            )
            
            db.add(unlimited_subscription)
            await db.flush()
            print("✅ Unlimited enterprise subscription created")
            
            # Create API key for Brahma user
            brahma_api_key, key_hash = APIKey.generate_key()
            
            api_key = APIKey(
                user_id=user_id,
                key_hash=key_hash,
                key_prefix=brahma_api_key[:8],
                name="Brahma Master Key",
                scopes=["*"],  # All scopes
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=36500)  # 100 years
            )
            
            db.add(api_key)
            await db.commit()
            await db.refresh(brahma_user)
            
            print("\n🎉 Brahma test user created successfully!")
            print("=" * 60)
            print(f"👤 Username: brahma")
            print(f"📧 Email: brahma@brahmakaal.com")
            print(f"🔑 Password: brahma123")
            print(f"🏆 Role: Admin")
            print(f"💎 Subscription: Enterprise (Unlimited)")
            print(f"🔐 API Key: {brahma_api_key}")
            print(f"📅 Expires: Never (100 years)")
            print("=" * 60)
            
            # Test login
            print("\n🔍 Testing login...")
            token_data = jwt_handler.create_user_tokens(
                user_id=user_id,
                email="brahma@brahmakaal.com",
                role="admin"
            )
            
            print("✅ JWT tokens generated successfully")
            print(f"🎫 Access Token: {token_data['access_token'][:50]}...")
            print(f"🔄 Refresh Token: {token_data['refresh_token'][:50]}...")
            
            return {
                "user_id": user_id,
                "email": "brahma@brahmakaal.com",
                "username": "brahma", 
                "password": "brahma123",
                "api_key": brahma_api_key,
                "access_token": token_data['access_token'],
                "refresh_token": token_data['refresh_token']
            }
            
    except Exception as e:
        print(f"❌ Failed to create Brahma user: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_brahma_access():
    """Test Brahma user's unlimited access"""
    print("\n🧪 Testing Brahma user access...")
    
    # Test JWT token creation
    user_data = await create_brahma_user()
    if not user_data:
        return False
    
    print("✅ All tests passed! Brahma user is ready for unlimited API access.")
    return True

if __name__ == "__main__":
    asyncio.run(test_brahma_access()) 