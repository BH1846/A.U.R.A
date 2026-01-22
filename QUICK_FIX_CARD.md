# 🎯 AURA Production Issues - Quick Fix Card

## Issue 1: Database Error (500 - column does not exist)
**Error:** `column applications.aura_invited does not exist`

**Fix:**
1. Go to https://console.neon.tech
2. Open SQL Editor
3. Copy & paste SQL from `I_INTERN/backend/migrations/add_aura_fields_safe.sql`
4. Click Run
5. Done! (No redeploy needed)

---

## Issue 2: Authentication Error (401 Unauthorized)
**Error:** `GET https://aura.i-intern.com/api/student/applications 401`

**Fix:**
1. Render → I-Intern Backend → Environment
2. Copy value of `AURA_JWT_SECRET`
3. Render → AURA Backend → Environment  
4. Set `JWT_SECRET` = (paste value from step 2)
5. Save → Auto redeploys

---

## Issue 3: Cron Jobs Setup (Your Original Request)

**See:** [RENDER_CRON_JOBS.md](RENDER_CRON_JOBS.md)

**Quick Setup:**
1. Render Dashboard → New + → Cron Job
2. Command: `python backend/scripts/cleanup_repos.py`
3. Schedule: `0 */6 * * *` (every 6 hours)
4. Environment: Copy from AURA web service
5. Deploy!

---

## Order to Fix

1. ✅ Database migration (takes 1 min)
2. ✅ JWT secret sync (takes 2 min)
3. ⏰ Cron jobs (takes 5 min, optional)

---

## All Documentation

| File | Purpose |
|------|---------|
| [URGENT_FIX_SUMMARY.md](URGENT_FIX_SUMMARY.md) | This file - Quick fixes |
| [FIX_DATABASE_NOW.md](I_INTERN/FIX_DATABASE_NOW.md) | Database migration steps |
| [FIX_AURA_AUTH.md](FIX_AURA_AUTH.md) | Auth troubleshooting |
| [RENDER_CRON_JOBS.md](RENDER_CRON_JOBS.md) | Cron job setup guide |
| [run_migration.py](I_INTERN/backend/run_migration.py) | Migration script |
| [test_auth_flow.py](backend/test_auth_flow.py) | Auth testing |

---

**Current Status:**
- ❌ Database missing AURA columns
- ❌ JWT secrets not synced
- ❓ Cron jobs not set up

**After Fixes:**
- ✅ Database has AURA columns
- ✅ Authentication works
- ✅ Cron jobs running (optional)
