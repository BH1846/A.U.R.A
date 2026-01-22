"""
Database Migration Script - Add Job Description Support
Adds JobDescription table and updates Question, Internship tables
Run this after updating models
"""
from sqlalchemy import create_engine, text
from loguru import logger
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

def run_migration():
    """Run database migration to add JD support"""
    
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as conn:
            logger.info("Starting database migration...")
            
            # 1. Create job_descriptions table
            logger.info("Creating job_descriptions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS job_descriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    internship_id INTEGER NOT NULL UNIQUE,
                    description_text TEXT NOT NULL,
                    role_type VARCHAR(50) NOT NULL,
                    required_skills JSON,
                    preferred_skills JSON,
                    questions_data JSON NOT NULL,
                    created_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (internship_id) REFERENCES internships(id),
                    FOREIGN KEY (created_by) REFERENCES users(id)
                )
            """))
            conn.commit()
            logger.success("Created job_descriptions table")
            
            # 2. Add columns to questions table
            logger.info("Adding columns to questions table...")
            
            # Check if columns exist
            result = conn.execute(text("PRAGMA table_info(questions)"))
            columns = [row[1] for row in result]
            
            if 'job_description_id' not in columns:
                conn.execute(text("""
                    ALTER TABLE questions 
                    ADD COLUMN job_description_id INTEGER
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_questions_job_description 
                    ON questions(job_description_id)
                """))
                logger.success("Added job_description_id to questions")
            else:
                logger.info("job_description_id already exists in questions")
            
            if 'source' not in columns:
                conn.execute(text("""
                    ALTER TABLE questions 
                    ADD COLUMN source VARCHAR(20) DEFAULT 'github'
                """))
                logger.success("Added source to questions")
            else:
                logger.info("source already exists in questions")
            
            conn.commit()
            
            # 3. Add column to internships table
            logger.info("Adding column to internships table...")
            
            result = conn.execute(text("PRAGMA table_info(internships)"))
            columns = [row[1] for row in result]
            
            if 'use_jd_questions' not in columns:
                conn.execute(text("""
                    ALTER TABLE internships 
                    ADD COLUMN use_jd_questions BOOLEAN DEFAULT 0
                """))
                logger.success("Added use_jd_questions to internships")
            else:
                logger.info("use_jd_questions already exists in internships")
            
            conn.commit()
            
            logger.success("✅ Migration completed successfully!")
            
            # Print summary
            print("\n" + "="*60)
            print("MIGRATION SUMMARY")
            print("="*60)
            print("✅ Created job_descriptions table")
            print("✅ Added job_description_id to questions table")
            print("✅ Added source column to questions table")
            print("✅ Added use_jd_questions to internships table")
            print("="*60 + "\n")
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    run_migration()
