"""
Person/Contact model for relationship management
"""

from beanie import Document, PydanticObjectId
from pydantic import Field, EmailStr
from typing import List, Optional
from datetime import datetime


class Person(Document):
    """Person/Contact document model"""
    
    user_id: PydanticObjectId
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    linked_notes: List[PydanticObjectId] = Field(default_factory=list)
    linked_meetings: List[PydanticObjectId] = Field(default_factory=list)
    last_contact: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "people"
        indexes = [
            "user_id",
            "name",
            [("user_id", 1), ("name", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sarah Johnson",
                "email": "sarah@example.com",
                "company": "Tech Corp",
                "role": "Product Manager",
                "tags": ["colleague", "project-lead"]
            }
        }
