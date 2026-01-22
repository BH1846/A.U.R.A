#!/usr/bin/env python3
"""
Test AURA authentication flow
Verifies JWT token generation and decoding works correctly
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

import jwt
from config import settings
from datetime import datetime, timedelta

def test_token_flow():
    """Test complete token generation and validation"""
    print("=" * 70)
    print("  AURA Authentication Flow Test")
    print("=" * 70)
    print()
    
    # Display current configuration
    print("📋 Current Configuration:")
    print(f"   JWT Secret: {settings.JWT_SECRET[:10]}... (hidden)")
    print(f"   JWT Algorithm: {settings.JWT_ALGORITHM}")
    print(f"   CORS Origins: {settings.CORS_ORIGINS}")
    print()
    
    # Test token generation
    print("🔐 Generating test token...")
    payload = {
        "user_id": "123",
        "email": "test@example.com",
        "name": "Test Student",
        "role": "student",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    try:
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        print(f"✅ Token generated successfully")
        print(f"   Token (first 50 chars): {token[:50]}...")
        print()
    except Exception as e:
        print(f"❌ Failed to generate token: {e}")
        return
    
    # Test token decoding
    print("🔓 Decoding token...")
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        print(f"✅ Token decoded successfully")
        print(f"   User ID: {decoded.get('user_id')}")
        print(f"   Email: {decoded.get('email')}")
        print(f"   Name: {decoded.get('name')}")
        print(f"   Role: {decoded.get('role')}")
        print(f"   Expires: {datetime.fromtimestamp(decoded.get('exp'))}")
        print()
    except jwt.ExpiredSignatureError:
        print(f"❌ Token has expired")
        return
    except jwt.InvalidTokenError as e:
        print(f"❌ Failed to decode token: {e}")
        return
    
    # Test AURA auth module
    print("🔍 Testing AURA auth module...")
    try:
        from core.auth.auth import decode_i_intern_token
        decoded_payload = decode_i_intern_token(token)
        print(f"✅ AURA auth module works correctly")
        print(f"   Decoded payload: {decoded_payload}")
        print()
    except Exception as e:
        print(f"❌ AURA auth module failed: {e}")
        return
    
    # Generate test URLs
    print("🔗 Test URLs:")
    print()
    print("Student Dashboard:")
    print(f"https://aura.i-intern.com/student/dashboard?token={token}")
    print()
    print("Company Applications:")
    payload_company = {
        "user_id": "456",
        "email": "recruiter@company.com",
        "name": "Test Recruiter",
        "role": "recruiter",
        "company_id": 1,
        "company_name": "Test Company",
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token_company = jwt.encode(payload_company, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    print(f"https://aura.i-intern.com/company/applications?token={token_company}")
    print()
    
    # Test curl command
    print("🧪 Test with curl:")
    print(f"""
curl -X GET "https://aura.i-intern.com/api/student/applications" \\
  -H "Authorization: Bearer {token}" \\
  -H "Content-Type: application/json"
    """)
    print()
    
    print("=" * 70)
    print("✅ All tests passed!")
    print("=" * 70)
    print()
    print("📝 Next steps:")
    print("1. Copy the test URL above")
    print("2. Open it in your browser")
    print("3. Check browser console for any errors")
    print("4. Verify localStorage has 'aura_auth_token'")
    print("5. Check Network tab for Authorization header")

if __name__ == "__main__":
    test_token_flow()
