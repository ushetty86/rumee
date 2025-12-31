"""
Neo4j Graph Database Service
Stores and queries knowledge graph data
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service for Neo4j graph database operations"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
        """Initialize Neo4j connection"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            logger.info("✅ Connected to Neo4j")
        except Exception as e:
            logger.warning(f"⚠️  Neo4j not available: {e}. Using in-memory fallback.")
            self.driver = None
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
    
    def create_note_node(self, note_id: str, title: str, content: str, entities: Dict[str, List[str]]):
        """Create a note node with extracted entities"""
        if not self.driver:
            return
        
        with self.driver.session() as session:
            # Create note node
            session.run(
                """
                MERGE (n:Note {id: $note_id})
                SET n.title = $title, n.content = $content, n.updated_at = datetime()
                """,
                note_id=note_id, title=title, content=content
            )
            
            # Create person nodes and relationships
            for person in entities.get('people', []):
                session.run(
                    """
                    MERGE (p:Person {name: $person})
                    WITH p
                    MATCH (n:Note {id: $note_id})
                    MERGE (n)-[:MENTIONS]->(p)
                    """,
                    person=person, note_id=note_id
                )
            
            # Create topic nodes and relationships
            for topic in entities.get('topics', []):
                session.run(
                    """
                    MERGE (t:Topic {name: $topic})
                    WITH t
                    MATCH (n:Note {id: $note_id})
                    MERGE (n)-[:DISCUSSES]->(t)
                    """,
                    topic=topic, note_id=note_id
                )
            
            # Create organization nodes
            for org in entities.get('organizations', []):
                session.run(
                    """
                    MERGE (o:Organization {name: $org})
                    WITH o
                    MATCH (n:Note {id: $note_id})
                    MERGE (n)-[:INVOLVES]->(o)
                    """,
                    org=org, note_id=note_id
                )
            
            # Create location nodes
            for loc in entities.get('locations', []):
                session.run(
                    """
                    MERGE (l:Location {name: $loc})
                    WITH l
                    MATCH (n:Note {id: $note_id})
                    MERGE (n)-[:LOCATED_AT]->(l)
                    """,
                    loc=loc, note_id=note_id
                )
            
            logger.info(f"✅ Created note node: {note_id} with {sum(len(v) for v in entities.values())} entities")
    
    def create_relationship_between_notes(self, note1_id: str, note2_id: str, relationship_type: str, strength: float):
        """Create a relationship between two notes"""
        if not self.driver:
            return
        
        with self.driver.session() as session:
            session.run(
                """
                MATCH (n1:Note {id: $note1_id}), (n2:Note {id: $note2_id})
                MERGE (n1)-[r:RELATED_TO]->(n2)
                SET r.type = $rel_type, r.strength = $strength
                """,
                note1_id=note1_id, note2_id=note2_id, rel_type=relationship_type, strength=strength
            )
    
    def get_full_graph(self) -> Dict[str, Any]:
        """Get the entire knowledge graph"""
        if not self.driver:
            return {"nodes": [], "edges": [], "total_nodes": 0, "total_edges": 0}
        
        with self.driver.session() as session:
            # Get all nodes
            nodes_result = session.run(
                """
                MATCH (n)
                RETURN id(n) as id, labels(n)[0] as type, properties(n) as props
                """
            )
            
            nodes = []
            for record in nodes_result:
                node_props = record["props"]
                nodes.append({
                    "id": str(record["id"]),
                    "label": node_props.get("title") or node_props.get("name", "Unknown"),
                    "type": record["type"].lower(),
                    "properties": node_props
                })
            
            # Get all relationships
            edges_result = session.run(
                """
                MATCH (n1)-[r]->(n2)
                RETURN id(n1) as from_id, id(n2) as to_id, type(r) as rel_type, properties(r) as props
                """
            )
            
            edges = []
            for record in edges_result:
                edges.append({
                    "from": str(record["from_id"]),
                    "to": str(record["to_id"]),
                    "type": record["rel_type"].lower(),
                    "properties": record["props"]
                })
            
            return {
                "nodes": nodes,
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
    
    def find_connections(self, note_id: str, max_depth: int = 2) -> List[Dict[str, Any]]:
        """Find all connections from a note"""
        if not self.driver:
            return []
        
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (n:Note {id: $note_id})-[*1..%d]-(connected)
                RETURN connected, path
                LIMIT 50
                """ % max_depth,
                note_id=note_id
            )
            
            connections = []
            for record in result:
                connections.append({
                    "node": dict(record["connected"]),
                    "path_length": len(record["path"])
                })
            
            return connections
    
    def get_most_connected_entities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get entities with most connections (hubs)"""
        if not self.driver:
            return []
        
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n)
                OPTIONAL MATCH (n)-[r]-()
                WITH n, labels(n)[0] as type, count(r) as connections
                WHERE connections > 0
                RETURN n, type, connections
                ORDER BY connections DESC
                LIMIT $limit
                """,
                limit=limit
            )
            
            hubs = []
            for record in result:
                node_props = dict(record["n"])
                hubs.append({
                    "id": node_props.get("id") or node_props.get("name"),
                    "type": record["type"].lower(),
                    "connections": record["connections"],
                    "label": node_props.get("title") or node_props.get("name", "Unknown")
                })
            
            return hubs
    
    def search_by_entity(self, entity_name: str, entity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for notes connected to a specific entity"""
        if not self.driver:
            return []
        
        with self.driver.session() as session:
            if entity_type:
                query = f"""
                MATCH (n:Note)-[r]-(e:{entity_type.capitalize()} {{name: $entity_name}})
                RETURN n, type(r) as rel_type
                """
            else:
                query = """
                MATCH (n:Note)-[r]-(e {name: $entity_name})
                RETURN n, type(r) as rel_type, labels(e)[0] as entity_type
                """
            
            result = session.run(query, entity_name=entity_name)
            
            notes = []
            for record in result:
                note_props = dict(record["n"])
                notes.append({
                    "note": note_props,
                    "relationship": record["rel_type"],
                    "entity_type": record.get("entity_type", entity_type)
                })
            
            return notes
    
    def clear_all(self):
        """Clear all data (use with caution!)"""
        if not self.driver:
            return
        
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("🗑️  Cleared all Neo4j data")


# Global instance (will be initialized in the app)
neo4j_service = None

def init_neo4j(uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "password"):
    """Initialize Neo4j service"""
    global neo4j_service
    neo4j_service = Neo4jService(uri, user, password)
    return neo4j_service
