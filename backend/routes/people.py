"""
People routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from beanie import PydanticObjectId
from models.person import Person
from models.user import User
from routes.auth import get_current_user
from typing import List, Optional
from beanie import PydanticObjectId

router = APIRouter()


class PersonCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    tags: List[str] = []
    notes: Optional[str] = None


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


@router.post("")
async def create_person(person_data: PersonCreate, current_user: User = Depends(get_current_user)):
    """Create a new person/contact"""
    person = Person(
        user_id=current_user.id,
        **person_data.model_dump()
    )
    await person.save()
    
    return {
        "id": str(person.id),
        "name": person.name,
        "email": person.email,
        "company": person.company,
        "role": person.role,
        "created_at": person.created_at
    }


@router.get("")
async def get_people(current_user: User = Depends(get_current_user)):
    """Get all people for current user"""
    people = await Person.find(
        Person.user_id == current_user.id
    ).sort("name").to_list()
    
    return [
        {
            "id": str(person.id),
            "name": person.name,
            "email": person.email,
            "company": person.company,
            "role": person.role,
            "tags": person.tags,
            "last_contact": person.last_contact
        }
        for person in people
    ]


@router.get("/{person_id}")
async def get_person(person_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific person"""
    person = await Person.get(PydanticPydanticObjectId(person_id))
    if not person or person.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return {
        "id": str(person.id),
        "name": person.name,
        "email": person.email,
        "phone": person.phone,
        "company": person.company,
        "role": person.role,
        "tags": person.tags,
        "notes": person.notes,
        "linked_notes": [str(n) for n in person.linked_notes],
        "linked_meetings": [str(m) for m in person.linked_meetings],
        "last_contact": person.last_contact,
        "created_at": person.created_at
    }


@router.put("/{person_id}")
async def update_person(person_id: str, person_data: PersonUpdate, current_user: User = Depends(get_current_user)):
    """Update a person"""
    person = await Person.get(PydanticPydanticObjectId(person_id))
    if not person or person.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found")
    
    update_data = person_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(person, field, value)
    
    await person.save()
    
    return {"message": "Person updated", "id": str(person.id)}


@router.delete("/{person_id}")
async def delete_person(person_id: str, current_user: User = Depends(get_current_user)):
    """Delete a person"""
    person = await Person.get(PydanticPydanticObjectId(person_id))
    if not person or person.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Person not found")
    
    await person.delete()
    
    return {"message": "Person deleted"}
