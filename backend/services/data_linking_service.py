"""
Data Linking Service
Automatically links related entities based on content analysis
"""

from services.ai_service import ai_service
from models.note import Note
from models.person import Person
from models.meeting import Meeting
from models.reminder import Reminder
from models.relationship import Relationship
from beanie import PydanticObjectId
from typing import List
import logging

logger = logging.getLogger(__name__)


class DataLinkingService:
    """Service for automatic data linking"""
    
    @staticmethod
    async def link_note_to_entities(note: Note) -> None:
        """Link a note to related people, meetings, and other entities"""
        try:
            # Extract entities from note content
            entities = await ai_service.extract_entities(
                f"{note.title}\n\n{note.content}"
            )
            
            # Update note with extracted entities
            note.entities = entities
            
            # Link to people mentioned
            if entities.get("people"):
                people_mentioned = await Person.find(
                    Person.user_id == note.user_id,
                    {"$or": [{"name": {"$regex": name, "$options": "i"}} for name in entities["people"]]}
                ).to_list()
                
                note.linked_people = [person.id for person in people_mentioned]
                
                # Create relationships
                for person in people_mentioned:
                    await DataLinkingService._create_relationship(
                        user_id=note.user_id,
                        source_type="note",
                        source_id=note.id,
                        target_type="person",
                        target_id=person.id,
                        relationship_type="mentions",
                        strength=0.8
                    )
            
            await note.save()
            logger.info(f"Linked note {note.id} to entities")
            
        except Exception as e:
            logger.error(f"Error linking note to entities: {e}")
    
    @staticmethod
    async def link_meeting_to_notes(meeting: Meeting) -> None:
        """Link a meeting to related notes"""
        try:
            # Find notes around the meeting time
            # This could be enhanced with semantic search
            meeting_content = f"{meeting.title} {meeting.description or ''} {meeting.agenda or ''}"
            
            # Find similar notes
            notes = await Note.find(
                Note.user_id == meeting.user_id
            ).to_list()
            
            if not notes:
                return
            
            # Generate embedding for meeting
            meeting_embedding = await ai_service.generate_embeddings(meeting_content)
            
            if meeting_embedding:
                # Get note embeddings
                note_embeddings = [(note.id, note.embeddings) for note in notes if note.embeddings]
                
                # Find similar notes
                similar_notes = await ai_service.find_similar_content(
                    meeting_embedding,
                    note_embeddings
                )
                
                # Link top 5 most similar notes (with similarity > 0.7)
                linked_notes = [
                    note_id for note_id, similarity in similar_notes[:5]
                    if similarity > 0.7
                ]
                
                meeting.linked_notes = linked_notes
                await meeting.save()
                
                # Create relationships
                for note_id in linked_notes:
                    await DataLinkingService._create_relationship(
                        user_id=meeting.user_id,
                        source_type="meeting",
                        source_id=meeting.id,
                        target_type="note",
                        target_id=note_id,
                        relationship_type="discusses",
                        strength=0.7
                    )
            
            logger.info(f"Linked meeting {meeting.id} to notes")
            
        except Exception as e:
            logger.error(f"Error linking meeting to notes: {e}")
    
    @staticmethod
    async def create_reminders_from_action_items(meeting: Meeting) -> List[Reminder]:
        """Automatically create reminders from meeting action items"""
        reminders = []
        
        try:
            for item in meeting.action_items:
                reminder = Reminder(
                    user_id=meeting.user_id,
                    title=item.get("task", "Action item from meeting"),
                    description=f"From meeting: {meeting.title}",
                    due_date=item.get("due_date", meeting.scheduled_at),
                    priority=item.get("priority", "medium"),
                    linked_meeting=meeting.id
                )
                
                await reminder.save()
                reminders.append(reminder)
                
                # Create relationship
                await DataLinkingService._create_relationship(
                    user_id=meeting.user_id,
                    source_type="reminder",
                    source_id=reminder.id,
                    target_type="meeting",
                    target_id=meeting.id,
                    relationship_type="derived_from",
                    strength=1.0
                )
            
            logger.info(f"Created {len(reminders)} reminders from meeting {meeting.id}")
            
        except Exception as e:
            logger.error(f"Error creating reminders from action items: {e}")
        
        return reminders
    
    @staticmethod
    async def _create_relationship(user_id: PydanticObjectId, source_type: str, source_id: PydanticObjectId,
                                   target_type: str, target_id: PydanticObjectId,
                                   relationship_type: str, strength: float) -> None:
        """Create or update a relationship"""
        try:
            # Check if relationship already exists
            existing = await Relationship.find_one(
                Relationship.user_id == user_id,
                Relationship.source_id == source_id,
                Relationship.target_id == target_id
            )
            
            if existing:
                # Update existing relationship
                existing.relationship_type = relationship_type
                existing.strength = max(existing.strength, strength)
                await existing.save()
            else:
                # Create new relationship
                relationship = Relationship(
                    user_id=user_id,
                    source_type=source_type,
                    source_id=source_id,
                    target_type=target_type,
                    target_id=target_id,
                    relationship_type=relationship_type,
                    strength=strength
                )
                await relationship.save()
                
        except Exception as e:
            logger.error(f"Error creating relationship: {e}")


data_linking_service = DataLinkingService()
