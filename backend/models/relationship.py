"""
Relationship model for knowledge graph connections
"""

from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional, Literal
from datetime import datetime


RelationshipType = Literal[
    "mentions",
    "related_to",
    "discusses",
    "follows_up",
    "similar_to",
    "caused_by",
    "derived_from"
]


class Relationship(Document):
    """Relationship document for knowledge graph"""
    
    user_id: PydanticObjectId
    source_type: str  # note, meeting, person, reminder
    source_id: PydanticObjectId
    target_type: str
    target_id: PydanticObjectId
    relationship_type: RelationshipType
    strength: float = Field(ge=0.0, le=1.0, default=0.5)  # Confidence score
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "relationships"
        indexes = [
            "user_id",
            "source_id",
            "target_id",
            [("user_id", 1), ("source_id", 1)],
            [("user_id", 1), ("target_id", 1)],
            [("source_id", 1), ("target_id", 1)],
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "source_type": "note",
                "target_type": "person",
                "relationship_type": "mentions",
                "strength": 0.85,
                "metadata": {
                    "reasoning": "Note explicitly mentions person's name",
                    "context": "Project discussion"
                }
            }
        }
