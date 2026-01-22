# 🚨 URGENT FIX SUMMARY - AURA 401 Error

## The Problem
Students get **401 Unauthorized** when accessing AURA at `https://aura.i-intern.com/api/student/applications`

## Root Cause
**JWT Secret Mismatch** between I-Intern backend and AURA backend.

- I-Intern generates tokens with `AURA_JWT_SECRET`
- AURA validates tokens with `JWT_SECRET`
- **These MUST be identical!**

## THE FIX (5 minutes)

### Step 1: Check I-Intern Backend Secret

1. Go to **Render Dashboard** → **I-Intern Backend** → **Environment**
2. Find `AURA_JWT_SECRET` value
3. **Copy it** (example: `RrtAu1Jgq-jsYBdcp8xCUgApxRKS0l9r8p0MiRX7X-w`)

### Step 2: Set AURA Backend Secret

1. Go to **Render Dashboard** → **AURA Backend** → **Environment**
2. Find or Add `JWT_SECRET`
3. **Paste the EXACT same value** from Step 1
4. Click **Save Changes**

### Step 3: Update CORS (if needed)

While in AURA Backend environment, ensure `CORS_ORIGINS` includes:
```
["https://i-intern.com","https://www.i-intern.com","https://i-intern-2.onrender.com","https://aura.i-intern.com"]
```

### Step 4: Redeploy

- Render will automatically redeploy after saving environment variables
- Wait for deployment to complete (~2-3 minutes)

### Step 5: Test

1. Go to I-Intern frontend
2. Apply to an internship
3. Company invites you to AURA
4. Click "Start AURA Assessment"
5. **Should work now!** ✅

---

## If Still Not Working

### Check 1: Database Migration
Did you run the database migration from earlier?

```sql
-- Run this in Neon Console if not done yet
-- Copy from: I_INTERN/backend/migrations/add_aura_fields_safe.sql
```

### Check 2: Token in Browser
Open browser console on `https://aura.i-intern.com`:

```javascript
// Should show a token
localStorage.getItem('aura_auth_token')
```

### Check 3: Check Render Logs
1. Go to Render Dashboard → AURA Backend → Logs
2. Look for errors like:
   - `Invalid token`
   - `Token has expired`
   - `Could not validate credentials`

If you see `Invalid token`, the secrets don't match!

---

## Environment Variables Checklist

### I-Intern Backend (Render)
```
✅ AURA_JWT_SECRET=<your-secret-here>
✅ AURA_BASE_URL=https://aura.i-intern.com
```

### AURA Backend (Render)
```
✅ JWT_SECRET=<same-as-AURA_JWT_SECRET-above>
✅ JWT_ALGORITHM=HS256
✅ CORS_ORIGINS=["https://i-intern.com","https://www.i-intern.com","https://i-intern-2.onrender.com","https://aura.i-intern.com"]
✅ SECRET_KEY=<any-secret-key>
✅ GROQ_API_KEY=<your-groq-key>
✅ DATABASE_URL=<your-neon-db-url>
```

---

## Quick Visual Check

**Before Fix:**
```
I-Intern → Generate Token (Secret: ABC123)
Student → Clicks Link
AURA → Validate Token (Secret: XYZ789) ❌ MISMATCH → 401 Error
```

**After Fix:**
```
I-Intern → Generate Token (Secret: ABC123)
Student → Clicks Link
AURA → Validate Token (Secret: ABC123) ✅ MATCH → Success!
```

---

## Files Created

1. ✅ [FIX_DATABASE_NOW.md](I_INTERN/FIX_DATABASE_NOW.md) - Database migration guide
2. ✅ [run_migration.py](I_INTERN/backend/run_migration.py) - Migration script
3. ✅ [FIX_AURA_AUTH.md](FIX_AURA_AUTH.md) - Detailed auth fix guide
4. ✅ [test_auth_flow.py](backend/test_auth_flow.py) - Test script
5. ✅ [RENDER_CRON_JOBS.md](RENDER_CRON_JOBS.md) - Cron job setup (your original request)

---

## Priority Order

1. **FIRST:** Fix database (run migration) ← Required
2. **SECOND:** Fix JWT secrets ← Required  
3. **THIRD:** Set up cron jobs ← Optional/Later

---

**Need help?** Check [FIX_AURA_AUTH.md](FIX_AURA_AUTH.md) for detailed steps!
