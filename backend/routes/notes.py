"""
Notes routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from beanie import PydanticObjectId
from models.note import Note
from models.user import User
from routes.auth import get_current_user
from services.ai_service import ai_service
from services.data_linking_service import data_linking_service
from typing import List, Optional

router = APIRouter()


class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


@router.post("")
async def create_note(note_data: NoteCreate, current_user: User = Depends(get_current_user)):
    """Create a new note with AI processing"""
    # Create note
    note = Note(
        user_id=current_user.id,
        title=note_data.title,
        content=note_data.content,
        tags=note_data.tags
    )
    
    # Generate embeddings
    note.embeddings = await ai_service.generate_embeddings(
        f"{note.title}\n{note.content}"
    )
    
    await note.save()
    
    # Link to entities in background
    await data_linking_service.link_note_to_entities(note)
    
    return {
        "id": str(note.id),
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "entities": note.entities,
        "created_at": note.created_at
    }


@router.get("")
async def get_notes(current_user: User = Depends(get_current_user)):
    """Get all notes for current user"""
    notes = await Note.find(
        Note.user_id == current_user.id
    ).sort("-created_at").to_list()
    
    return [
        {
            "id": str(note.id),
            "title": note.title,
            "content": note.content,
            "tags": note.tags,
            "entities": note.entities,
            "created_at": note.created_at
        }
        for note in notes
    ]


@router.get("/{note_id}")
async def get_note(note_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific note"""
    note = await Note.get(PydanticPydanticObjectId(note_id))
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return {
        "id": str(note.id),
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "entities": note.entities,
        "linked_people": [str(p) for p in note.linked_people],
        "linked_meetings": [str(m) for m in note.linked_meetings],
        "created_at": note.created_at,
        "updated_at": note.updated_at
    }


@router.put("/{note_id}")
async def update_note(note_id: str, note_data: NoteUpdate, current_user: User = Depends(get_current_user)):
    """Update a note"""
    note = await Note.get(PydanticPydanticObjectId(note_id))
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content
    if note_data.tags is not None:
        note.tags = note_data.tags
    
    # Regenerate embeddings if content changed
    if note_data.title is not None or note_data.content is not None:
        note.embeddings = await ai_service.generate_embeddings(
            f"{note.title}\n{note.content}"
        )
        await data_linking_service.link_note_to_entities(note)
    
    await note.save()
    
    return {"message": "Note updated", "id": str(note.id)}


@router.delete("/{note_id}")
async def delete_note(note_id: str, current_user: User = Depends(get_current_user)):
    """Delete a note"""
    note = await Note.get(PydanticPydanticObjectId(note_id))
    if not note or note.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await note.delete()
    
    return {"message": "Note deleted"}


@router.post("/search")
async def search_notes(query: str, current_user: User = Depends(get_current_user)):
    """Semantic search for notes"""
    # Generate query embedding
    query_embedding = await ai_service.generate_embeddings(query)
    
    if not query_embedding:
        raise HTTPException(status_code=400, detail="Could not generate embedding")
    
    # Get all notes with embeddings
    notes = await Note.find(Note.user_id == current_user.id).to_list()
    note_embeddings = [(note.id, note.embeddings) for note in notes if note.embeddings]
    
    # Find similar notes
    similar = await ai_service.find_similar_content(query_embedding, note_embeddings)
    
    # Get top 10 results
    results = []
    for note_id, similarity in similar[:10]:
        if similarity > 0.5:  # Threshold
            note = await Note.get(note_id)
            if note:
                results.append({
                    "id": str(note.id),
                    "title": note.title,
                    "content": note.content[:200] + "...",
                    "similarity": similarity,
                    "created_at": note.created_at
                })
    
    return results
