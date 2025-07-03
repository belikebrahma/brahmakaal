#!/usr/bin/env python3
"""
Generate Never-Expiring Token for Testing
Creates a JWT token that never expires for API testing
"""

import asyncio
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add the project root to Python path
sys.path.insert(0, ".")

from kaal_engine.db.database import get_async_session
from kaal_engine.auth.models import User
from kaal_engine.auth.jwt_handler import jwt_handler

async def generate_never_expiring_token():
    """Generate never-expiring token for Brahma user"""
    
    print("🔑 Generating Never-Expiring Token for Testing...")
    print("=" * 60)
    
    try:
        async with get_async_session() as db:
            # Find Brahma user
            stmt = select(User).where(User.username == "brahma")
            result = await db.execute(stmt)
            brahma_user = result.scalar_one_or_none()
            
            if not brahma_user:
                print("❌ Brahma user not found! Please run create_brahma_user.py first.")
                return
            
            print(f"✅ Found Brahma user: {brahma_user.email}")
            
            # Generate never-expiring token
            never_expiring_token = jwt_handler.create_never_expiring_token(
                user_id=brahma_user.id,
                email=brahma_user.email,
                role=brahma_user.role
            )
            
            print("\n🎯 NEVER-EXPIRING TOKEN GENERATED")
            print("=" * 60)
            print(f"Token: {never_expiring_token}")
            print("\n📋 Usage Instructions:")
            print("=" * 60)
            
            print("\n1. **cURL Usage:**")
            print(f'curl -H "Authorization: Bearer {never_expiring_token}" \\')
            print('     http://localhost:8000/v1/health')
            
            print("\n2. **Python requests:**")
            print("headers = {")
            print(f'    "Authorization": "Bearer {never_expiring_token}"')
            print("}")
            print("response = requests.get('http://localhost:8000/v1/panchang', headers=headers)")
            
            print("\n3. **JavaScript fetch:**")
            print("fetch('http://localhost:8000/v1/panchang', {")
            print("  headers: {")
            print(f"    'Authorization': 'Bearer {never_expiring_token}'")
            print("  }")
            print("})")
            
            print("\n🌟 Token Features:")
            print("=" * 60)
            print("✅ Never expires (valid for 100 years)")
            print("✅ Full admin access to all APIs")
            print("✅ Unlimited rate limits")
            print("✅ All premium features enabled")
            print("✅ Perfect for testing and development")
            
            # Save to file for easy access
            with open("never_expiring_token.txt", "w") as f:
                f.write(never_expiring_token)
            
            print(f"\n💾 Token saved to: never_expiring_token.txt")
            print(f"📅 Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(generate_never_expiring_token())
