# 🕐 Render Cron Jobs Setup for AURA

## Overview

Render provides cron jobs as a service type that can run scheduled tasks for your application. This guide covers setting up cron jobs for AURA's repository cleanup and maintenance tasks.

## Available Cron Jobs for AURA

### 1. Repository Cleanup Job
- **Purpose**: Remove old cloned repositories to save disk space
- **Script**: `backend/scripts/cleanup_repos.py`
- **Recommended Schedule**: Every 6 hours
- **Cron Expression**: `0 */6 * * *`

### 2. Database Cleanup (Optional)
- **Purpose**: Clean up orphaned records and old data
- **Recommended Schedule**: Daily at 2 AM UTC
- **Cron Expression**: `0 2 * * *`

## Setup Methods

### Method 1: Using Render Dashboard (Recommended)

1. **Navigate to Render Dashboard**
   - Go to https://dashboard.render.com
   - Select your AURA project

2. **Create New Cron Job**
   - Click "New +" button
   - Select "Cron Job"

3. **Configure the Cron Job**
   
   **Basic Settings:**
   - **Name**: `aura-repo-cleanup`
   - **Environment**: `Python 3`
   - **Region**: Same as your web service (e.g., Singapore)
   - **Branch**: `main`
   - **Plan**: Free (sufficient for most cleanup tasks)

   **Build & Run:**
   - **Build Command**: 
     ```bash
     pip install -r backend/requirements.txt
     ```
   
   - **Command**: 
     ```bash
     python backend/scripts/cleanup_repos.py
     ```
   
   - **Schedule**: `0 */6 * * *` (every 6 hours)

4. **Add Environment Variables**
   Copy the same environment variables from your web service:
   - `REPO_CLEANUP_MAX_AGE_HOURS` = `24`
   - `GITHUB_TOKEN` (if needed for API calls)
   - `DATABASE_URL` (if cleanup needs database access)
   - Any other required variables from your main service

5. **Deploy**
   - Click "Create Cron Job"
   - Render will automatically run on the specified schedule

### Method 2: Using render.yaml (Infrastructure as Code)

Create or update `render.yaml` in your project root:

```yaml
services:
  # Your existing web service
  - type: web
    name: aura-backend
    env: python
    region: singapore
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SECRET_KEY
        sync: false
      - key: GITHUB_TOKEN
        sync: false
      - key: DATABASE_URL
        sync: false
      # ... other env vars

  # Cron Job for Repository Cleanup
  - type: cron
    name: aura-repo-cleanup
    env: python
    region: singapore
    plan: free
    schedule: "0 */6 * * *"  # Every 6 hours
    buildCommand: pip install -r backend/requirements.txt
    command: python backend/scripts/cleanup_repos.py
    envVars:
      - key: REPO_CLEANUP_MAX_AGE_HOURS
        value: "24"
      - key: GITHUB_TOKEN
        sync: false
      - key: DATABASE_URL
        sync: false
      # Add other required env vars

  # Optional: Database Cleanup Cron Job
  - type: cron
    name: aura-db-cleanup
    env: python
    region: singapore
    plan: free
    schedule: "0 2 * * *"  # Daily at 2 AM UTC
    buildCommand: pip install -r backend/requirements.txt
    command: python backend/scripts/db_cleanup.py
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: SECRET_KEY
        sync: false
```

Then commit and push this file to trigger automatic deployment.

## Cron Schedule Examples

Common cron expressions for Render:

- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour
- `0 */6 * * *` - Every 6 hours
- `0 0 * * *` - Daily at midnight UTC
- `0 2 * * *` - Daily at 2 AM UTC
- `0 0 * * 0` - Weekly on Sunday at midnight UTC
- `0 0 1 * *` - Monthly on the 1st at midnight UTC

## Creating Additional Cleanup Scripts

### Database Cleanup Script

Create `backend/scripts/db_cleanup.py`:

```python
#!/usr/bin/env python3
"""
Database cleanup script for AURA
Removes old evaluations, orphaned records, etc.
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

from models import get_db
from models.database import Candidate, Repository, Evaluation
from loguru import logger

def cleanup_old_data(days: int = 90):
    """Remove data older than specified days"""
    db = next(get_db())
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Clean up old evaluations
        old_evals = db.query(Evaluation).filter(
            Evaluation.created_at < cutoff_date
        ).delete()
        
        logger.info(f"Deleted {old_evals} old evaluations")
        
        db.commit()
        logger.success("Database cleanup completed")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_old_data()
```

### Storage Cleanup Script

Create `backend/scripts/storage_cleanup.py`:

```python
#!/usr/bin/env python3
"""
Storage cleanup for AURA - removes old reports and vector DB data
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import shutil

backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from loguru import logger

def cleanup_old_reports(days: int = 30):
    """Remove reports older than specified days"""
    reports_dir = Path("data/reports")
    if not reports_dir.exists():
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for report in reports_dir.glob("*.json"):
        if report.stat().st_mtime < cutoff_date.timestamp():
            report.unlink()
            deleted += 1
    
    logger.info(f"Deleted {deleted} old reports")

def cleanup_temp_files():
    """Remove all temporary files"""
    temp_dir = Path("data/temp")
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        logger.info("Cleaned up temp directory")

if __name__ == "__main__":
    logger.info("Starting storage cleanup...")
    cleanup_old_reports()
    cleanup_temp_files()
    logger.success("Storage cleanup completed")
```

## Monitoring Cron Jobs

### Check Logs in Render Dashboard

1. Go to your cron job in the Render dashboard
2. Click on the "Logs" tab
3. View execution history and output

### Add Logging to Scripts

Ensure your scripts use proper logging:

```python
from loguru import logger

# Configure logger to output to stdout (Render will capture this)
logger.add(sys.stdout, level="INFO")

logger.info("Starting cleanup...")
logger.success("Cleanup completed")
logger.error("Error occurred: {}", error)
```

### Email Notifications

Add email notifications for failures:

```python
import smtplib
from email.mime.text import MIMEText

def send_error_notification(error_msg):
    """Send email notification on failure"""
    msg = MIMEText(f"Cron job failed: {error_msg}")
    msg['Subject'] = 'AURA Cron Job Failure'
    msg['From'] = os.getenv('FROM_EMAIL')
    msg['To'] = os.getenv('ADMIN_EMAIL')
    
    # Use your SMTP settings
    with smtplib.SMTP(os.getenv('SMTP_SERVER'), 587) as server:
        server.starttls()
        server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASS'))
        server.send_message(msg)
```

## Best Practices

### 1. **Error Handling**
Always wrap main logic in try-except blocks:

```python
def main():
    try:
        # Your cleanup logic
        logger.info("Starting...")
        cleanup_repos()
        logger.success("Completed")
    except Exception as e:
        logger.error(f"Failed: {e}")
        # Optional: send notification
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    main()
```

### 2. **Idempotency**
Ensure scripts can be run multiple times safely:
- Check if files/records exist before deletion
- Use transactions for database operations
- Don't assume clean state

### 3. **Timeouts**
Keep cron jobs under 10 minutes on free tier:
- Process in batches
- Add early exit conditions
- Monitor execution time

### 4. **Resource Management**
- Close database connections properly
- Clean up temporary files
- Limit memory usage

### 5. **Testing Locally**
Test cron scripts before deploying:

```bash
# Test cleanup script
cd backend
python scripts/cleanup_repos.py

# Check logs
tail -f logs/cleanup.log
```

## Common Issues & Solutions

### Issue: Cron job not running

**Solution:**
- Check cron expression syntax
- Verify environment variables are set
- Check logs for build errors
- Ensure script has proper permissions

### Issue: Script fails with import errors

**Solution:**
```python
# Add proper path handling
import sys
from pathlib import Path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
```

### Issue: Database connection fails

**Solution:**
- Verify `DATABASE_URL` is set in cron job env vars
- Check if database allows connections from Render's IPs
- Use connection pooling with timeouts

### Issue: Out of disk space

**Solution:**
- Reduce `REPO_CLEANUP_MAX_AGE_HOURS` 
- Add more aggressive cleanup schedules
- Monitor disk usage in logs

## Quick Start Checklist

- [ ] Create cleanup script in `backend/scripts/`
- [ ] Test script locally
- [ ] Add logging and error handling
- [ ] Create cron job in Render dashboard
- [ ] Set schedule (e.g., `0 */6 * * *`)
- [ ] Copy environment variables from web service
- [ ] Deploy and test
- [ ] Monitor logs for first few runs
- [ ] Set up failure notifications (optional)

## Render Cron Job Limits

**Free Tier:**
- Maximum runtime: 10 minutes
- No concurrent executions
- Runs in same region as created

**Paid Tiers:**
- Longer runtimes available
- Better reliability
- Priority scheduling

## Example: Complete Cron Job Setup

For AURA repository cleanup:

1. **Create in Render Dashboard:**
   - Name: `aura-repo-cleanup`
   - Environment: Python 3
   - Schedule: `0 */6 * * *`
   - Command: `python backend/scripts/cleanup_repos.py`

2. **Environment Variables:**
   ```
   REPO_CLEANUP_MAX_AGE_HOURS=24
   GITHUB_TOKEN=<your-token>
   DATABASE_URL=<your-db-url>
   ```

3. **Monitor:**
   - Check logs after first run
   - Verify disk usage decreases
   - Ensure no errors

## Next Steps

1. Set up basic repo cleanup cron job
2. Monitor for a few days
3. Add database cleanup if needed
4. Add storage cleanup for reports
5. Set up monitoring/alerting
6. Consider upgrading if you need longer run times

## Related Documentation

- [DEPLOYMENT.md](DEPLOYMENT.md) - Main deployment guide
- [CLOUD_STORAGE.md](CLOUD_STORAGE.md) - Storage configuration
- [backend/scripts/cleanup_repos.py](backend/scripts/cleanup_repos.py) - Cleanup script

---

**Need Help?**
- Render Cron Jobs Docs: https://render.com/docs/cronjobs
- Check logs in Render dashboard
- Test scripts locally first
