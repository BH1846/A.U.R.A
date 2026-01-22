# 🔒 Fix AURA Authentication (401 Unauthorized)

## Problem Summary

When students click "Start AURA Assessment" from I-Intern, they get redirected to:
```
https://aura.i-intern.com/student/dashboard?token=<JWT>
```

But the AURA frontend is making API calls to `/api/student/applications` **without the JWT token**, causing 401 Unauthorized errors.

## Root Cause

The AURA frontend's `StudentDashboard` component is using `fetch('/api/student/applications')` with the `authHeader`, but:

1. The token is extracted from URL and stored in `localStorage`
2. The `useAuthHeader` hook returns the token
3. **BUT** the backend expects the token in `Authorization: Bearer <token>` header
4. The AURA backend URL configuration might not be set correctly for production

## Quick Fixes

### Fix 1: Update AURA Frontend API Calls

The AURA frontend needs to properly include the Authorization header. Update [frontend/src/pages/StudentDashboard.tsx](frontend/src/pages/StudentDashboard.tsx):

```typescript
const fetchApplications = async () => {
  try {
    // Get the full headers object
    const headers = {
      'Content-Type': 'application/json',
      ...authHeader  // This should be { Authorization: 'Bearer <token>' }
    };
    
    console.log('Making request with headers:', headers); // Debug log
    
    const response = await fetch('/api/student/applications', {
      headers,
      credentials: 'include'  // Important for CORS
    });
    
    if (!response.ok) {
      console.error('Response status:', response.status);
      console.error('Response:', await response.text());
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    setApplications(data.items);
  } catch (error) {
    console.error('Failed to fetch applications:', error);
  } finally {
    setLoading(false);
  }
};
```

### Fix 2: Set CORS Headers on AURA Backend

The AURA backend needs to allow credentials from I-Intern domains. In [backend/config.py](backend/config.py#L31), verify CORS origins include:

```python
CORS_ORIGINS: List[str] = [
    "http://localhost:3000", 
    "http://localhost:5173",
    "https://i-intern.com",
    "https://www.i-intern.com",
    "https://i-intern-2.onrender.com",  # I-Intern frontend
    "https://aura.i-intern.com"         # AURA frontend
]
```

And in [backend/main.py](backend/main.py#L47):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,  # ✅ MUST be True for cookies/auth
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # Add this
)
```

### Fix 3: Check Environment Variables on Render

Your AURA backend on Render needs these environment variables:

1. **Go to Render Dashboard** → AURA Backend Service → Environment

2. **Add/Update these variables:**
   ```
   CORS_ORIGINS=["https://i-intern.com","https://www.i-intern.com","https://i-intern-2.onrender.com","https://aura.i-intern.com"]
   
   JWT_SECRET=<same as I-Intern backend>
   
   JWT_ALGORITHM=HS256
   ```

3. **CRITICAL:** The `JWT_SECRET` must match between I-Intern and AURA backends!

### Fix 4: Verify Token Decoding

The issue might be in how AURA decodes the token. Check [backend/core/auth/auth.py](backend/core/auth/auth.py#L63):

```python
def decode_i_intern_token(token: str) -> dict:
    """Decode JWT token from I-Intern platform"""
    try:
        # Make sure settings.JWT_SECRET matches I-Intern's AURA_JWT_SECRET
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET,  # Must match I-Intern's secret
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        # Add more detailed error logging
        print(f"Invalid token error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

## Testing Steps

### 1. Test Token Generation (I-Intern Backend)

```python
# I_INTERN/backend - test in Python shell
from app.utils.aura import generate_aura_student_token
from app.models.user import User

# Create test user
user = User(id=1, email="test@example.com", full_name="Test User")
token = generate_aura_student_token(user)
print(f"Generated token: {token}")

# Decode it
import jwt
from app.core.config import settings
payload = jwt.decode(token, settings.AURA_JWT_SECRET, algorithms=["HS256"])
print(f"Decoded: {payload}")
```

### 2. Test Token Reception (AURA Backend)

```python
# backend - test in Python shell
from core.auth.auth import decode_i_intern_token
from config import settings

# Use the token from I-Intern
test_token = "eyJ..."  # Copy from I-Intern test
try:
    payload = decode_i_intern_token(test_token)
    print(f"✅ Token valid: {payload}")
except Exception as e:
    print(f"❌ Token invalid: {e}")
```

### 3. Test in Browser

1. **Generate auth URL:**
   - In I-Intern backend, get a student's AURA URL
   - Copy the full URL with token

2. **Open in browser:**
   ```
   https://aura.i-intern.com/student/dashboard?token=<JWT>
   ```

3. **Check browser console:**
   - Token should be stored in `localStorage['aura_auth_token']`
   - Check request headers in Network tab
   - Should see `Authorization: Bearer <token>`

4. **Check AURA backend logs:**
   - Should see incoming request with token
   - No authentication errors

## Environment Variable Sync

Make sure these match:

### I-Intern Backend (.env or Render)
```env
AURA_JWT_SECRET=your-shared-secret-here
AURA_BASE_URL=https://aura.i-intern.com
```

### AURA Backend (.env or Render)
```env
JWT_SECRET=your-shared-secret-here  # MUST MATCH ABOVE
JWT_ALGORITHM=HS256
CORS_ORIGINS=["https://i-intern.com","https://www.i-intern.com","https://i-intern-2.onrender.com","https://aura.i-intern.com"]
```

## Deployment Checklist

- [ ] Update AURA backend `config.py` with correct CORS origins
- [ ] Set `JWT_SECRET` on Render (match I-Intern's `AURA_JWT_SECRET`)
- [ ] Set `CORS_ORIGINS` on Render environment variables
- [ ] Update AURA frontend fetch calls to include credentials
- [ ] Redeploy AURA backend on Render
- [ ] Redeploy AURA frontend on Render
- [ ] Test end-to-end flow
- [ ] Check browser console for errors
- [ ] Check Render logs for backend errors

## Debug Commands

### Check localStorage in Browser Console
```javascript
localStorage.getItem('aura_auth_token')
```

### Check token in Network tab
```
Request Headers:
Authorization: Bearer eyJ...
```

### Test API call manually
```javascript
const token = localStorage.getItem('aura_auth_token');
fetch('/api/student/applications', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  credentials: 'include'
})
.then(r => r.json())
.then(d => console.log(d))
.catch(e => console.error(e));
```

## Common Issues

### Issue: "Invalid token"
**Cause:** JWT secrets don't match between I-Intern and AURA
**Fix:** Ensure `AURA_JWT_SECRET` (I-Intern) = `JWT_SECRET` (AURA)

### Issue: "Token has expired"
**Cause:** Token generated more than 24 hours ago
**Fix:** Generate new token or increase `AURA_TOKEN_EXPIRE_HOURS`

### Issue: "CORS error"
**Cause:** AURA backend not allowing I-Intern frontend origin
**Fix:** Add I-Intern frontend URL to `CORS_ORIGINS`

### Issue: "No Authorization header"
**Cause:** Frontend not including token in requests
**Fix:** Check `useAuthHeader` hook and fetch call headers

## Quick Test Script

Create `test_auth_flow.py` in AURA backend:

```python
#!/usr/bin/env python3
"""Test AURA authentication flow"""
import os
import sys
from pathlib import Path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

import jwt
from config import settings
from datetime import datetime, timedelta

# Test token generation
payload = {
    "user_id": "123",
    "email": "test@example.com",
    "name": "Test User",
    "role": "student",
    "exp": datetime.utcnow() + timedelta(hours=24)
}

token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
print(f"✅ Generated token: {token}\n")

# Test token decoding
try:
    decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    print(f"✅ Decoded successfully: {decoded}\n")
except Exception as e:
    print(f"❌ Failed to decode: {e}\n")

# Test URL
print(f"🔗 Test URL:")
print(f"https://aura.i-intern.com/student/dashboard?token={token}")
```

Run it:
```bash
cd backend
python test_auth_flow.py
```

## Next Steps

1. **Immediate:** Set matching JWT secrets on both backends
2. **Deploy:** Redeploy AURA backend with updated CORS
3. **Test:** Click "Start AURA" from I-Intern and verify it works
4. **Monitor:** Check Render logs for any auth errors

---

**Related Files:**
- [backend/config.py](backend/config.py) - CORS and JWT settings
- [backend/core/auth/auth.py](backend/core/auth/auth.py) - Token decoding
- [frontend/src/contexts/AuthContext.tsx](frontend/src/contexts/AuthContext.tsx) - Token management
- [frontend/src/pages/StudentDashboard.tsx](frontend/src/pages/StudentDashboard.tsx) - API calls
