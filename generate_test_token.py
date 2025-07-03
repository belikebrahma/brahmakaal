#!/usr/bin/env python3
"""
Generate Never-Expiring Test Token
Creates a JWT token for testing without database dependency
"""

import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, ".")

from kaal_engine.auth.jwt_handler import jwt_handler

def generate_test_token():
    """Generate never-expiring token for testing"""
    
    print("🔑 Generating Never-Expiring Test Token...")
    print("=" * 60)
    
    # Use Brahma user details (matching create_brahma_user.py)
    brahma_user_id = "brahma_admin_2025"
    brahma_email = "brahma@brahmakaal.com"
    brahma_role = "admin"
    
    try:
        # Generate never-expiring token
        never_expiring_token = jwt_handler.create_never_expiring_token(
            user_id=brahma_user_id,
            email=brahma_email,
            role=brahma_role
        )
        
        print("\n🎯 NEVER-EXPIRING TEST TOKEN GENERATED")
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
        
        print(f"\n�� Token saved to: never_expiring_token.txt")
        print(f"📅 Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        return never_expiring_token
        
    except Exception as e:
        print(f"❌ Error generating token: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    token = generate_test_token()
    if token:
        print(f"\n🚀 Ready for deployment testing!")
        print("Use this token with any hosting platform:")
        print(f"Bearer {token}")
