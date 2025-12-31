"""
Meeting model for scheduling and notes
"""

from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import List, Optional
from datetime import datetime


class Meeting(Document):
    """Meeting document model"""
    
    user_id: PydanticObjectId
    title: str
    description: Optional[str] = None
    participants: List[PydanticObjectId] = Field(default_factory=list)  # Person IDs
    scheduled_at: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    agenda: Optional[str] = None
    notes: Optional[str] = None
    action_items: List[dict] = Field(default_factory=list)
    linked_notes: List[PydanticObjectId] = Field(default_factory=list)
    status: str = "scheduled"  # scheduled, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "meetings"
        indexes = [
            "user_id",
            "scheduled_at",
            [("user_id", 1), ("scheduled_at", -1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Kickoff Meeting",
                "scheduled_at": "2024-01-15T10:00:00Z",
                "duration_minutes": 60,
                "agenda": "Discuss project goals and timeline",
                "action_items": [
                    {"task": "Prepare requirements doc", "assignee": "Sarah", "due_date": "2024-01-20"}
                ],
                "status": "scheduled"
            }
        }
