"""
Reminder model for tasks and notifications
"""

from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime


class Reminder(Document):
    """Reminder/Task document model"""
    
    user_id: PydanticObjectId
    title: str
    description: Optional[str] = None
    due_date: datetime
    priority: str = "medium"  # low, medium, high
    status: str = "pending"  # pending, completed, cancelled
    linked_note: Optional[PydanticObjectId] = None
    linked_meeting: Optional[PydanticObjectId] = None
    linked_person: Optional[PydanticObjectId] = None
    recurrence: Optional[str] = None  # daily, weekly, monthly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Settings:
        name = "reminders"
        indexes = [
            "user_id",
            "due_date",
            "status",
            [("user_id", 1), ("due_date", 1)],
            [("user_id", 1), ("status", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Review project proposal",
                "description": "Review and provide feedback on Q1 proposal",
                "due_date": "2024-01-20T09:00:00Z",
                "priority": "high",
                "status": "pending"
            }
        }
