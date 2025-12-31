"""
Meetings routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.meeting import Meeting
from models.user import User
from routes.auth import get_current_user
from services.data_linking_service import data_linking_service
from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId

router = APIRouter()


class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = None
    location: Optional[str] = None
    meeting_link: Optional[str] = None
    agenda: Optional[str] = None
    participant_ids: List[str] = []


class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    action_items: Optional[List[dict]] = None
    status: Optional[str] = None


@router.post("")
async def create_meeting(meeting_data: MeetingCreate, current_user: User = Depends(get_current_user)):
    """Create a new meeting"""
    meeting = Meeting(
        user_id=current_user.id,
        title=meeting_data.title,
        description=meeting_data.description,
        scheduled_at=meeting_data.scheduled_at,
        duration_minutes=meeting_data.duration_minutes,
        location=meeting_data.location,
        meeting_link=meeting_data.meeting_link,
        agenda=meeting_data.agenda,
        participants=[PydanticObjectId(p_id) for p_id in meeting_data.participant_ids]
    )
    await meeting.save()
    
    # Link to related notes
    await data_linking_service.link_meeting_to_notes(meeting)
    
    return {
        "id": str(meeting.id),
        "title": meeting.title,
        "scheduled_at": meeting.scheduled_at,
        "status": meeting.status
    }


@router.get("")
async def get_meetings(current_user: User = Depends(get_current_user)):
    """Get all meetings for current user"""
    meetings = await Meeting.find(
        Meeting.user_id == current_user.id
    ).sort("-scheduled_at").to_list()
    
    return [
        {
            "id": str(meeting.id),
            "title": meeting.title,
            "scheduled_at": meeting.scheduled_at,
            "duration_minutes": meeting.duration_minutes,
            "status": meeting.status,
            "participants": [str(p) for p in meeting.participants]
        }
        for meeting in meetings
    ]


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific meeting"""
    meeting = await Meeting.get(PydanticObjectId(meeting_id))
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    return {
        "id": str(meeting.id),
        "title": meeting.title,
        "description": meeting.description,
        "scheduled_at": meeting.scheduled_at,
        "duration_minutes": meeting.duration_minutes,
        "location": meeting.location,
        "meeting_link": meeting.meeting_link,
        "agenda": meeting.agenda,
        "notes": meeting.notes,
        "action_items": meeting.action_items,
        "participants": [str(p) for p in meeting.participants],
        "linked_notes": [str(n) for n in meeting.linked_notes],
        "status": meeting.status,
        "created_at": meeting.created_at
    }


@router.put("/{meeting_id}")
async def update_meeting(meeting_id: str, meeting_data: MeetingUpdate, current_user: User = Depends(get_current_user)):
    """Update a meeting"""
    meeting = await Meeting.get(PydanticObjectId(meeting_id))
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    update_data = meeting_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(meeting, field, value)
    
    await meeting.save()
    
    # If action items were updated, create reminders
    if meeting_data.action_items is not None:
        await data_linking_service.create_reminders_from_action_items(meeting)
    
    return {"message": "Meeting updated", "id": str(meeting.id)}


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str, current_user: User = Depends(get_current_user)):
    """Delete a meeting"""
    meeting = await Meeting.get(PydanticObjectId(meeting_id))
    if not meeting or meeting.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    await meeting.delete()
    
    return {"message": "Meeting deleted"}
