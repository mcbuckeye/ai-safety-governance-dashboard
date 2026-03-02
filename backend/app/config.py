import os


class Settings:
    """Application settings loaded from environment variables"""
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://aisafety:aisafety@localhost:5432/aisafety")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkey")
    
    # JWT Configuration - 10 year expiry
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 365 * 10


settings = Settings()
