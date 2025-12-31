"""
Knowledge Graph routes
"""

from fastapi import APIRouter, HTTPException, Depends
from models.user import User
from routes.auth import get_current_user
from services.knowledge_graph_service import knowledge_graph_service
from beanie import PydanticObjectId

router = APIRouter()


@router.get("/full")
async def get_full_graph(current_user: User = Depends(get_current_user)):
    """Get complete knowledge graph for user"""
    graph = await knowledge_graph_service.build_knowledge_graph(current_user.id)
    return graph


@router.get("/entity/{entity_id}/connections")
async def get_entity_connections(entity_id: str, depth: int = 2, current_user: User = Depends(get_current_user)):
    """Get connections for a specific entity"""
    connections = await knowledge_graph_service.get_entity_connections(
        PydanticObjectId(entity_id),
        current_user.id,
        depth
    )
    return {"entity_id": entity_id, "connections": connections}


@router.get("/entity/{entity_id}/mindmap")
async def get_entity_mindmap(entity_id: str, current_user: User = Depends(get_current_user)):
    """Get mind map centered on a specific entity"""
    mindmap = await knowledge_graph_service.get_mind_map(
        current_user.id,
        PydanticObjectId(entity_id)
    )
    return mindmap


@router.get("/discover")
async def discover_relationships(limit: int = 10, current_user: User = Depends(get_current_user)):
    """Discover new potential relationships"""
    discovered = await knowledge_graph_service.discover_new_relationships(
        current_user.id,
        limit
    )
    return {"discovered": discovered, "count": len(discovered)}
