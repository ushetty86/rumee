"""
Simple test server - works with local Ollama for AI features
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
import uvicorn
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

# Import background processor and AI agents
from services.background_processor import processor
from services.neo4j_service import init_neo4j
from services.agent_orchestrator import orchestrator
from services.knowledge_graph import knowledge_graph
from persistence import persistence

# Load persistent storage from files
users_db = persistence.load('users')
notes_db = persistence.load('notes')
people_db = persistence.load('people')
reminders_db = persistence.load('reminders')
meetings_db = persistence.load('meetings')
token_store = persistence.load('tokens')

# Set storage references for background processor
import services.background_processor as bp_module
bp_module.notes_db = notes_db
bp_module.people_db = people_db
bp_module.reminders_db = reminders_db
bp_module.meetings_db = meetings_db
bp_module.save_callback = lambda: persistence.save_all({
    'notes': notes_db,
    'people': people_db,
    'reminders': reminders_db,
    'meetings': meetings_db
})

# Helper function to save data
def save_data():
    """Save all data to disk"""
    persistence.save_all({
        'users': users_db,
        'notes': notes_db,
        'people': people_db,
        'reminders': reminders_db,
        'meetings': meetings_db,
        'tokens': token_store
    })

async def periodic_save():
    """Periodically save data to disk"""
    while True:
        await asyncio.sleep(60)  # Save every 60 seconds
        try:
            save_data()
            logger.info("💾 Auto-saved data")
        except Exception as e:
            logger.error(f"Error in periodic save: {e}")

# Initialize Neo4j (will fallback gracefully if not available)
neo4j = init_neo4j(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="neo4j123"  # Change this!
)
bp_module.neo4j_service = neo4j

app = FastAPI(title="Rumee Test API", version="1.0.0-test")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []

class MessageInfer(BaseModel):
    message: str

# Startup event
@app.on_event("startup")
async def startup_event():
    """Start background processor and AI agents on startup"""
    await processor.start()
    # Start the processing loop
    asyncio.create_task(processor._process_loop())
    print("✨ Background AI processor started with Ollama")
    
    # Initialize Knowledge Graph with existing data
    print("🕸️ Initializing Knowledge Graph...")
    for note in notes_db.values():
        knowledge_graph.ingest_note(note)
    for person in people_db.values():
        knowledge_graph.ingest_person(person)
    for meeting in meetings_db.values():
        knowledge_graph.ingest_meeting(meeting)
    for reminder in reminders_db.values():
        knowledge_graph.ingest_reminder(reminder)
    
    graph_stats = knowledge_graph.get_stats()
    print(f"   Graph: {graph_stats['total_nodes']} nodes, {graph_stats['total_edges']} edges")
    
    # Start comprehensive multi-agent AI engine
    await orchestrator.start(
        notes_db=notes_db,
        people_db=people_db,
        reminders_db=reminders_db,
        meetings_db=meetings_db
    )
    print("🧠 Multi-agent AI orchestrator started (6 agents active)")
    
    # Log loaded data
    print(f"📂 Loaded persistent data:")
    print(f"   - Users: {len(users_db)}")
    print(f"   - Notes: {len(notes_db)}")
    print(f"   - People: {len(people_db)}")
    print(f"   - Reminders: {len(reminders_db)}")
    print(f"   - Meetings: {len(meetings_db)}")
    
    # Start periodic auto-save (every 60 seconds)
    asyncio.create_task(periodic_save())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background processor and AI agents on shutdown"""
    await processor.stop()
    await orchestrator.stop()
    # Save all data before shutdown
    print("💾 Saving all data before shutdown...")
    save_data()
    print("✅ Data saved successfully")

# Routes
@app.get("/health")
def health():
    return {"status": "healthy", "mode": "test"}

@app.get("/")
def root():
    return {"message": "Rumee Test API", "version": "1.0.0", "docs": "/docs"}

@app.post("/api/auth/register")
def register(data: RegisterRequest):
    if data.email in users_db:
        raise HTTPException(400, "Email already registered")
    
    user_id = f"user_{len(users_db) + 1}"
    users_db[data.email] = {
        "id": user_id,
        "email": data.email,
        "name": data.name,
        "password": data.password
    }
    token = f"token_{user_id}"
    token_store[token] = user_id
    
    # Save to disk
    save_data()
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user_id, "email": data.email, "name": data.name}
    }

@app.post("/api/auth/login")
def login(data: LoginRequest):
    user = users_db.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(401, "Invalid credentials")
    
    token = f"token_{user['id']}"
    token_store[token] = user['id']
    
    # Save tokens
    persistence.save('tokens', token_store)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user["id"], "email": user["email"], "name": user["name"]}
    }

@app.post("/api/notes")
async def create_note(note: NoteCreate, background_tasks: BackgroundTasks):
    note_id = f"note_{len(notes_db) + 1}"
    note_data = {
        "id": note_id,
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "entities": {"people": [], "topics": []},
        "created_at": datetime.utcnow().isoformat(),
        "ai_processed": False
    }
    notes_db[note_id] = note_data
    
    # Process in background with AI
    await processor.add_to_queue("note", note_data, "current_user")
    
    # Ingest into Knowledge Graph
    knowledge_graph.ingest_note(note_data)
    
    # Save to disk
    persistence.save('notes', notes_db)
    
    return note_data

@app.get("/api/notes")
def get_notes():
    return list(notes_db.values())

@app.get("/api/people")
def get_people():
    return list(people_db.values())

@app.get("/api/meetings")
def get_meetings():
    return list(meetings_db.values())

@app.get("/api/reminders")
def get_reminders():
    return list(reminders_db.values())

@app.get("/api/summary/daily")
def daily_summary():
    return {
        "summary": "Test mode: No activity yet. Create some notes to see summaries!",
        "notes_count": len(notes_db),
        "meetings_count": 0,
        "reminders_count": 0
    }

@app.get("/api/knowledge-graph/full")
async def get_legacy_knowledge_graph():
    """Generate knowledge graph from Neo4j or notes (LEGACY)"""
    
    # Try Neo4j first
    if neo4j and neo4j.driver:
        try:
            graph = neo4j.get_full_graph()
            # Get hubs/clusters
            hubs = neo4j.get_most_connected_entities(limit=10)
            graph['clusters'] = hubs
            return graph
        except Exception as e:
            logger.error(f"Neo4j error: {e}, falling back to in-memory")
    
    # Fallback to in-memory graph generation
    import ollama
    from collections import defaultdict
    
    # Build nodes from notes
    nodes = []
    edges = []
    people_found = set()
    topics_found = set()
    
    # Create nodes for each note
    for note_id, note in notes_db.items():
        nodes.append({
            "id": note_id,
            "label": note["title"],
            "type": "note",
            "content": note["content"][:100] + "..." if len(note["content"]) > 100 else note["content"],
            "created_at": note["created_at"]
        })
        
        # Extract entities from note using AI if not already processed
        if not note.get("ai_processed") and note.get("content"):
            try:
                response = ollama.chat(
                    model='llama3.2:latest',
                    messages=[{
                        'role': 'system',
                        'content': 'Extract entities from text. Return ONLY a JSON object with keys: people (array), topics (array), organizations (array). Keep it concise.'
                    }, {
                        'role': 'user',
                        'content': f"{note['title']} {note['content']}"
                    }],
                    options={'temperature': 0.3}
                )
                
                import json
                content = response['message']['content']
                # Clean up markdown if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                entities = json.loads(content)
                
                # Store entities
                if "people" in entities:
                    for person in entities["people"]:
                        people_found.add(person)
                        edges.append({
                            "from": note_id,
                            "to": f"person_{person}",
                            "type": "mentions"
                        })
                
                if "topics" in entities:
                    for topic in entities["topics"]:
                        topics_found.add(topic)
                        edges.append({
                            "from": note_id,
                            "to": f"topic_{topic}",
                            "type": "discusses"
                        })
                        
            except Exception as e:
                print(f"Error extracting entities: {e}")
    
    # Add people nodes
    for person in people_found:
        nodes.append({
            "id": f"person_{person}",
            "label": person,
            "type": "person"
        })
    
    # Add topic nodes
    for topic in topics_found:
        nodes.append({
            "id": f"topic_{topic}",
            "label": topic,
            "type": "topic"
        })
    
    # Find relationships between notes using embeddings
    if len(notes_db) > 1:
        note_list = list(notes_db.values())
        for i in range(len(note_list)):
            for j in range(i + 1, len(note_list)):
                note1 = note_list[i]
                note2 = note_list[j]
                
                # Simple similarity: check for common words
                words1 = set(note1["content"].lower().split())
                words2 = set(note2["content"].lower().split())
                common = words1.intersection(words2)
                
                # If they share significant words, connect them
                if len(common) > 3:
                    edges.append({
                        "from": note1["id"],
                        "to": note2["id"],
                        "type": "related_to",
                        "strength": min(len(common) / 10, 1.0)
                    })
    
    return {
        "nodes": nodes,
        "edges": edges,
        "clusters": [],
        "total_nodes": len(nodes),
        "total_edges": len(edges)
    }

@app.post("/api/infer")
async def infer_message(data: MessageInfer):
    """Infer user intent from free-form message"""
    try:
        # Process message and infer intent
        intent = await processor._process_message(data.message, "current_user")
        return {
            "message": data.message,
            "intent": intent,
            "status": "processed"
        }
    except Exception as e:
        return {
            "message": data.message,
            "error": str(e),
            "status": "error"
        }

@app.post("/api/query")
async def query_insights(data: MessageInfer):
    """Query your data and get insights"""
    try:
        import ollama
        
        # Gather context from all notes
        context_parts = []
        for note in notes_db.values():
            context_parts.append(f"Note '{note['title']}': {note['content'][:200]}")
            if note.get('ai_entities'):
                entities = note['ai_entities']
                if isinstance(entities, dict):
                    context_parts.append(f"  - People: {', '.join(entities.get('people', []))}")
                    context_parts.append(f"  - Topics: {', '.join(entities.get('topics', []))}")
        
        context = "\n".join(context_parts[:10])  # Limit context
        
        # Query with context
        response = ollama.chat(
            model='llama3.2:latest',
            messages=[{
                'role': 'system',
                'content': f'''You are a personal assistant with access to the user's notes. 
                Answer questions based on this context:
                
                {context}
                
                Provide concise, helpful insights. If you don't have enough information, say so.'''
            }, {
                'role': 'user',
                'content': data.message
            }],
            options={'temperature': 0.4, 'num_predict': 300}
        )
        
        return {
            "query": data.message,
            "answer": response['message']['content'],
            "sources": len(notes_db),
            "status": "success"
        }
    except Exception as e:
        return {
            "query": data.message,
            "error": str(e),
            "status": "error"
        }

# Comprehensive AI Engine Routes
@app.get("/api/ai/insights")
async def get_ai_insights():
    """Get comprehensive insights from all AI agents"""
    insights = orchestrator.shared_memory.get('insights_queue', [])
    # Return most recent 10 insights, sorted by priority
    sorted_insights = sorted(
        insights[-20:], 
        key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 0),
        reverse=True
    )[:10]
    return {"insights": sorted_insights, "status": "success"}

@app.get("/api/ai/context")
async def get_current_context():
    """Get current user context built by AI agents"""
    context = orchestrator.shared_memory.get('user_context', {})
    return {"context": context, "status": "success"}

@app.get("/api/ai/connections/{note_id}")
async def get_note_connections(note_id: str):
    """Get AI-discovered connections for a specific note"""
    connections = orchestrator.shared_memory.get('cross_references', {}).get(note_id, [])
    
    # Enrich with note details
    enriched = []
    for conn in connections:
        target_note = notes_db.get(conn['target_id'])
        if target_note:
            enriched.append({
                'connection_type': conn.get('type', 'related_to'),
                'strength': conn.get('strength', 0),
                'reason': conn.get('reason', ''),
                'target_id': conn['target_id'],
                'target_title': target_note.get('title', 'Untitled'),
                'target_preview': target_note.get('content', '')[:200],
                'target_created': target_note.get('created_at')
            })
    
    return {
        "note_id": note_id,
        "connections": enriched,
        "count": len(enriched),
        "status": "success"
    }

@app.get("/api/ai/patterns")
async def get_detected_patterns():
    """Get patterns detected by Pattern Detector agent"""
    patterns = orchestrator.shared_memory.get('recent_patterns', [])
    # Return most recent pattern analysis
    latest = patterns[-1] if patterns else {}
    return {"patterns": latest, "status": "success"}

@app.get("/api/ai/entity-graph")
async def get_entity_graph():
    """Get entity relationship graph built by AI"""
    graph = dict(orchestrator.shared_memory.get('entity_graph', {}))
    
    # Convert to node-edge format for visualization
    nodes = set()
    edges = []
    
    for source, relationships in graph.items():
        nodes.add(source)
        for rel in relationships:
            nodes.add(rel['target'])
            edges.append({
                'source': source,
                'target': rel['target'],
                'type': rel['type'],
                'source_note': rel.get('source_note')
            })
    
    return {
        "graph": {
            "nodes": [{
                'id': node, 
                'label': node.split(':', 1)[1] if ':' in node else node,
                'type': node.split(':', 1)[0] if ':' in node else 'unknown'
            } for node in nodes],
            "edges": edges,
            "stats": {
                'total_nodes': len(nodes),
                'total_edges': len(edges)
            }
        },
        "status": "success"
    }

@app.get("/api/ai/brain-status")
async def get_brain_status():
    """Get status of all AI agents"""
    return {
        "status": "active" if orchestrator.is_running else "inactive",
        "agents": {
            'signal_sorter': 'Classifying and prioritizing data',
            'mind_weaver': 'Finding hidden connections',
            'context_builder': 'Building current context',
            'pattern_detector': 'Detecting patterns and trends',
            'insight_generator': 'Generating proactive insights',
            'relationship_mapper': 'Mapping entity relationships'
        },
        "memory": {
            'insights_queued': len(orchestrator.shared_memory.get('insights_queue', [])),
            'connections_found': sum(len(v) for v in orchestrator.shared_memory.get('cross_references', {}).values()),
            'active_topics': len(orchestrator.shared_memory.get('active_topics', [])),
            'patterns_detected': len(orchestrator.shared_memory.get('recent_patterns', []))
        }
    }

# Knowledge Graph Routes - THE BRAIN
@app.get("/api/graph/stats")
async def get_graph_stats():
    """Get knowledge graph statistics"""
    stats = knowledge_graph.get_stats()
    return {"stats": stats, "status": "success"}

@app.get("/api/graph/visualize")
async def get_graph_visualization(node_types: Optional[str] = None, limit: int = 100):
    """Get graph data for visualization"""
    types = node_types.split(',') if node_types else None
    graph_data = knowledge_graph.export_for_visualization(types, limit)
    return {"graph": graph_data, "status": "success"}

@app.get("/api/graph/context/{node_id}")
async def get_node_context(node_id: str, depth: int = 2):
    """Get full context around a node"""
    context = knowledge_graph.find_context(node_id, depth)
    return {"context": context, "status": "success"}

@app.get("/api/graph/path")
async def find_graph_path(start: str, end: str, max_depth: int = 4):
    """Find path between two entities"""
    paths = knowledge_graph.find_path(start, end, max_depth)
    
    # Enrich paths with node details
    enriched_paths = []
    for path in paths:
        enriched = []
        for node_id in path:
            node = knowledge_graph.get_node(node_id)
            if node:
                enriched.append({
                    'id': node.id,
                    'type': node.type,
                    'label': node.properties.get('name') or node.properties.get('title', node.id)
                })
        if enriched:
            enriched_paths.append(enriched)
    
    return {
        "paths": enriched_paths,
        "count": len(enriched_paths),
        "status": "success"
    }

@app.get("/api/graph/central-nodes")
async def get_central_nodes(node_type: Optional[str] = None, limit: int = 10):
    """Get most connected nodes (influencers)"""
    central = knowledge_graph.get_central_nodes(node_type, limit)
    
    # Enrich with node details
    enriched = []
    for node_id, degree in central:
        node = knowledge_graph.get_node(node_id)
        if node:
            enriched.append({
                'id': node.id,
                'type': node.type,
                'label': node.properties.get('name') or node.properties.get('title', node.id),
                'connections': degree,
                'properties': node.properties
            })
    
    return {"central_nodes": enriched, "status": "success"}

@app.get("/api/graph/clusters")
async def get_clusters(node_type: str = 'topic'):
    """Get clusters of related entities"""
    clusters = knowledge_graph.get_clusters(node_type)
    
    # Enrich with node details
    enriched_clusters = {}
    for cluster_id, node_ids in clusters.items():
        enriched_clusters[cluster_id] = []
        for node_id in node_ids:
            node = knowledge_graph.get_node(node_id)
            if node:
                enriched_clusters[cluster_id].append({
                    'id': node.id,
                    'label': node.properties.get('name') or node.properties.get('title', node.id),
                    'properties': node.properties
                })
    
    return {"clusters": enriched_clusters, "status": "success"}

@app.get("/api/graph/timeline/{entity_id}")
async def get_entity_timeline(entity_id: str):
    """Get timeline of all activities related to an entity"""
    timeline = knowledge_graph.get_timeline(entity_id)
    return {"timeline": timeline, "count": len(timeline), "status": "success"}

@app.get("/api/graph/neighbors/{node_id}")
async def get_node_neighbors(node_id: str, edge_type: Optional[str] = None, direction: str = 'both'):
    """Get neighboring nodes"""
    neighbors = knowledge_graph.get_neighbors(node_id, edge_type, direction)
    
    enriched = []
    for node in neighbors:
        enriched.append({
            'id': node.id,
            'type': node.type,
            'label': node.properties.get('name') or node.properties.get('title', node.id),
            'properties': node.properties
        })
    
    return {"neighbors": enriched, "count": len(enriched), "status": "success"}

@app.post("/api/graph/query")
async def query_graph(data: Dict[str, Any]):
    """Query graph by properties"""
    node_type = data.get('node_type')
    filters = data.get('filters', {})
    
    results = knowledge_graph.query_by_properties(node_type, filters)
    
    enriched = []
    for node in results:
        enriched.append({
            'id': node.id,
            'type': node.type,
            'properties': node.properties,
            'created_at': node.created_at
        })
    
    return {"results": enriched, "count": len(enriched), "status": "success"}

# Creative Muse Routes (Legacy - using new engine now)
@app.get("/api/muse/insights")
async def get_proactive_insights():
    """Get proactive insights from Creative Muse"""
    try:
        from services.creative_muse import creative_muse
        
        notes = list(notes_db.values())
        people = list(people_db.values())
        reminders = list(reminders_db.values())
        
        insights = await creative_muse.suggest_proactive_insights(
            notes, people, reminders
        )
        
        return {
            "insights": insights,
            "status": "success"
        }
    except Exception as e:
        return {
            "insights": {},
            "error": str(e),
            "status": "error"
        }

@app.post("/api/muse/relevant-ideas")
async def find_relevant_ideas(data: MessageInfer):
    """Find past ideas relevant to current context"""
    try:
        from services.creative_muse import creative_muse
        
        notes = list(notes_db.values())
        relevant = await creative_muse.find_relevant_past_ideas(
            data.message, notes
        )
        
        return {
            "current_context": data.message,
            "relevant_ideas": relevant,
            "count": len(relevant),
            "status": "success"
        }
    except Exception as e:
        return {
            "relevant_ideas": [],
            "error": str(e),
            "status": "error"
        }

@app.get("/api/muse/themes")
async def detect_themes():
    """Detect evolving themes over time"""
    try:
        from services.creative_muse import creative_muse
        
        notes = list(notes_db.values())
        themes = await creative_muse.detect_themes_over_time(notes)
        
        return {
            "themes": themes,
            "status": "success"
        }
    except Exception as e:
        return {
            "themes": [],
            "error": str(e),
            "status": "error"
        }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 RUMEE TEST SERVER WITH OLLAMA")
    print("="*60)
    print("Running with LOCAL AI (Ollama)")
    print("Models: llama3.2:latest, embeddinggemma:latest")
    print("API: http://localhost:8000")
    print("Docs: http://localhost:8000/docs")
    print("="*60 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
