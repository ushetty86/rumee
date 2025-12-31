"""
Summary routes for daily/weekly summaries
"""

from fastapi import APIRouter, HTTPException, Depends
from models.note import Note
from models.meeting import Meeting
from models.reminder import Reminder
from models.user import User
from routes.auth import get_current_user
from services.ai_service import ai_service
from datetime import datetime, timedelta
from beanie import PydanticObjectId

router = APIRouter()


@router.get("/daily")
async def get_daily_summary(date: str = None, current_user: User = Depends(get_current_user)):
    """Get daily summary for a specific date"""
    try:
        target_date = datetime.fromisoformat(date) if date else datetime.utcnow()
        start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Get notes from that day
        notes = await Note.find(
            Note.user_id == current_user.id,
            Note.created_at >= start_of_day,
            Note.created_at < end_of_day
        ).to_list()
        
        # Get meetings from that day
        meetings = await Meeting.find(
            Meeting.user_id == current_user.id,
            Meeting.scheduled_at >= start_of_day,
            Meeting.scheduled_at < end_of_day
        ).to_list()
        
        # Get reminders due that day
        reminders = await Reminder.find(
            Reminder.user_id == current_user.id,
            Reminder.due_date >= start_of_day,
            Reminder.due_date < end_of_day
        ).to_list()
        
        # Build content for summary
        content_parts = []
        
        if notes:
            notes_text = "\n".join([f"- {note.title}: {note.content[:100]}" for note in notes])
            content_parts.append(f"Notes:\n{notes_text}")
        
        if meetings:
            meetings_text = "\n".join([
                f"- {meeting.title} at {meeting.scheduled_at.strftime('%H:%M')}"
                for meeting in meetings
            ])
            content_parts.append(f"Meetings:\n{meetings_text}")
        
        if reminders:
            reminders_text = "\n".join([f"- {reminder.title} ({reminder.priority})" for reminder in reminders])
            content_parts.append(f"Reminders:\n{reminders_text}")
        
        if not content_parts:
            return {
                "date": target_date.isoformat(),
                "summary": "No activity on this day.",
                "notes_count": 0,
                "meetings_count": 0,
                "reminders_count": 0
            }
        
        full_content = "\n\n".join(content_parts)
        
        # Generate AI summary
        summary = await ai_service.generate_summary(full_content, "detailed")
        
        return {
            "date": target_date.isoformat(),
            "summary": summary,
            "notes_count": len(notes),
            "meetings_count": len(meetings),
            "reminders_count": len(reminders),
            "notes": [{"id": str(n.id), "title": n.title} for n in notes[:5]],
            "meetings": [{"id": str(m.id), "title": m.title, "time": m.scheduled_at} for m in meetings],
            "reminders": [{"id": str(r.id), "title": r.title, "priority": r.priority} for r in reminders]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/weekly")
async def get_weekly_summary(current_user: User = Depends(get_current_user)):
    """Get weekly summary"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        # Get all content from the week
        notes = await Note.find(
            Note.user_id == current_user.id,
            Note.created_at >= start_date,
            Note.created_at < end_date
        ).to_list()
        
        meetings = await Meeting.find(
            Meeting.user_id == current_user.id,
            Meeting.scheduled_at >= start_date,
            Meeting.scheduled_at < end_date
        ).to_list()
        
        reminders = await Reminder.find(
            Reminder.user_id == current_user.id,
            Reminder.due_date >= start_date,
            Reminder.due_date < end_date
        ).to_list()
        
        # Build content
        content = f"""Weekly Summary ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}):

Notes ({len(notes)} total):
{chr(10).join([f"- {note.title}" for note in notes[:10]])}

Meetings ({len(meetings)} total):
{chr(10).join([f"- {meeting.title}" for meeting in meetings])}

Tasks/Reminders ({len(reminders)} total):
{chr(10).join([f"- {reminder.title} ({reminder.status})" for reminder in reminders[:10]])}
"""
        
        # Generate AI summary
        summary = await ai_service.generate_summary(content, "detailed")
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "summary": summary,
            "stats": {
                "total_notes": len(notes),
                "total_meetings": len(meetings),
                "total_reminders": len(reminders),
                "completed_reminders": len([r for r in reminders if r.status == "completed"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")
