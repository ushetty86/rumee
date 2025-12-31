"""
Note model with AI embeddings and entity linking
"""

from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import List, Optional
from datetime import datetime


class Note(Document):
    """Note document model with AI capabilities"""
    
    user_id: PydanticObjectId
    title: str
    content: str
    embeddings: List[float] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    linked_people: List[PydanticObjectId] = Field(default_factory=list)
    linked_meetings: List[PydanticObjectId] = Field(default_factory=list)
    entities: dict = Field(default_factory=dict)  # Extracted entities
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "notes"
        indexes = [
            "user_id",
            "created_at",
            [("user_id", 1), ("created_at", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Meeting with Sarah",
                "content": "Discussed project timeline and deliverables",
                "tags": ["work", "project"],
                "entities": {
                    "people": ["Sarah"],
                    "topics": ["project timeline", "deliverables"]
                }
            }
        }
