"""
Configuration management for AURA system
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # LLM Configuration - Groq
    GROQ_API_KEY: str
    MODEL_NAME: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    TEMPERATURE: float = 0.7
    
    # GitHub Configuration
    GITHUB_TOKEN: str = ""
    
    # Database Configuration
    # For Neon PostgreSQL: postgresql://user:password@host/database?sslmode=require
    # For SQLite (local): sqlite:///./aura.db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aura.db")
    CHROMA_DB_PATH: str = "../data/vector_db"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # File Storage
    REPOS_DIR: str = "../data/repos"
    REPORTS_DIR: str = "../data/reports"
    TEMP_DIR: str = "../data/temp"
    
    # Evaluation Configuration
    MAX_QUESTIONS: int = 10
    MIN_QUESTIONS: int = 6
    EVALUATION_TIMEOUT: int = 300
    
    # Scoring Weights
    WEIGHT_UNDERSTANDING: float = 0.4
    WEIGHT_REASONING: float = 0.3
    WEIGHT_COMMUNICATION: float = 0.2
    WEIGHT_LOGIC: float = 0.1
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.REPOS_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
