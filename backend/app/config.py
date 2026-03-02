import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables"""
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://aisafety:aisafety@localhost:5432/aisafety")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    
    # Additional configuration
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
