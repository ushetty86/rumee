"""
Configuration with optional OpenAI (for testing without API key)
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Rumee"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    PORT: int = int(os.getenv("PORT", "5000"))
    
    # Database
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/rumee")
    
    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "demo-secret-key-for-testing")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 30
    
    # OpenAI (Optional for testing)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8501",  # Streamlit default port
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ]
    
    def has_openai(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY != "your-openai-api-key-here")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
