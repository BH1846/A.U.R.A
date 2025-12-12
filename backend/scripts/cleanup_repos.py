#!/usr/bin/env python3
"""
Cleanup script to remove old repository clones.
Run this as a cron job: 0 */6 * * * /usr/bin/python3 /path/to/cleanup_repos.py
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
load_dotenv()

from core.storage.storage_service import StorageService
from loguru import logger

def main():
    logger.info("Starting repository cleanup...")
    
    storage = StorageService()
    max_age_hours = int(os.getenv('REPO_CLEANUP_MAX_AGE_HOURS', '24'))
    
    storage.cleanup_local_repos(max_age_hours)
    
    logger.success("Repository cleanup completed")

if __name__ == "__main__":
    main()
