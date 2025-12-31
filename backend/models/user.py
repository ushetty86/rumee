"""
User model for authentication and preferences
"""

from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Document):
    """User document model"""
    
    email: EmailStr = Field(..., unique=True)
    password_hash: str
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    preferences: dict = Field(default_factory=dict)
    
    class Settings:
        name = "users"
        indexes = ["email"]
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "name": "John Doe",
                "preferences": {
                    "theme": "light",
                    "notifications": True
                }
            }
        }
