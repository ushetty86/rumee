"""
Reminders routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.reminder import Reminder
from models.user import User
from routes.auth import get_current_user
from typing import Optional
from datetime import datetime
from beanie import PydanticObjectId

router = APIRouter()


class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    priority: str = "medium"
    linked_note_id: Optional[str] = None
    linked_meeting_id: Optional[str] = None
    linked_person_id: Optional[str] = None


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    status: Optional[str] = None


@router.post("")
async def create_reminder(reminder_data: ReminderCreate, current_user: User = Depends(get_current_user)):
    """Create a new reminder"""
    reminder = Reminder(
        user_id=current_user.id,
        title=reminder_data.title,
        description=reminder_data.description,
        due_date=reminder_data.due_date,
        priority=reminder_data.priority,
        linked_note=PydanticObjectId(reminder_data.linked_note_id) if reminder_data.linked_note_id else None,
        linked_meeting=PydanticObjectId(reminder_data.linked_meeting_id) if reminder_data.linked_meeting_id else None,
        linked_person=PydanticObjectId(reminder_data.linked_person_id) if reminder_data.linked_person_id else None
    )
    await reminder.save()
    
    return {
        "id": str(reminder.id),
        "title": reminder.title,
        "due_date": reminder.due_date,
        "priority": reminder.priority,
        "status": reminder.status
    }


@router.get("")
async def get_reminders(status: Optional[str] = None, current_user: User = Depends(get_current_user)):
    """Get reminders for current user"""
    query = {"user_id": current_user.id}
    if status:
        query["status"] = status
    
    reminders = await Reminder.find(
        Reminder.user_id == current_user.id,
        Reminder.status == status if status else {}
    ).sort("due_date").to_list()
    
    return [
        {
            "id": str(reminder.id),
            "title": reminder.title,
            "description": reminder.description,
            "due_date": reminder.due_date,
            "priority": reminder.priority,
            "status": reminder.status,
            "created_at": reminder.created_at
        }
        for reminder in reminders
    ]


@router.get("/{reminder_id}")
async def get_reminder(reminder_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific reminder"""
    reminder = await Reminder.get(PydanticObjectId(reminder_id))
    if not reminder or reminder.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    return {
        "id": str(reminder.id),
        "title": reminder.title,
        "description": reminder.description,
        "due_date": reminder.due_date,
        "priority": reminder.priority,
        "status": reminder.status,
        "linked_note": str(reminder.linked_note) if reminder.linked_note else None,
        "linked_meeting": str(reminder.linked_meeting) if reminder.linked_meeting else None,
        "linked_person": str(reminder.linked_person) if reminder.linked_person else None,
        "created_at": reminder.created_at,
        "completed_at": reminder.completed_at
    }


@router.put("/{reminder_id}")
async def update_reminder(reminder_id: str, reminder_data: ReminderUpdate, current_user: User = Depends(get_current_user)):
    """Update a reminder"""
    reminder = await Reminder.get(PydanticObjectId(reminder_id))
    if not reminder or reminder.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    update_data = reminder_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)
    
    # Set completed_at if status is completed
    if reminder_data.status == "completed" and not reminder.completed_at:
        reminder.completed_at = datetime.utcnow()
    
    await reminder.save()
    
    return {"message": "Reminder updated", "id": str(reminder.id)}


@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: str, current_user: User = Depends(get_current_user)):
    """Delete a reminder"""
    reminder = await Reminder.get(PydanticObjectId(reminder_id))
    if not reminder or reminder.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    await reminder.delete()
    
    return {"message": "Reminder deleted"}
