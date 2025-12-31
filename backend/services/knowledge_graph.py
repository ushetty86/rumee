"""
Knowledge Graph - The Central Brain
Connects ALL data: notes, people, topics, meetings, reminders, tasks
Powers all AI insights, context, and discovery
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Node:
    """Graph node representing any entity"""
    def __init__(self, node_id: str, node_type: str, properties: Dict[str, Any]):
        self.id = node_id
        self.type = node_type  # person, topic, note, meeting, reminder, organization, location, date
        self.properties = properties
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'properties': self.properties,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class Edge:
    """Graph edge representing relationships"""
    def __init__(self, source_id: str, target_id: str, edge_type: str, properties: Dict[str, Any] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.type = edge_type  # MENTIONS, DISCUSSES, COLLABORATES_WITH, BUILDS_ON, RELATED_TO, etc.
        self.properties = properties or {}
        self.weight = properties.get('weight', 1.0) if properties else 1.0
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.type,
            'properties': self.properties,
            'weight': self.weight,
            'created_at': self.created_at
        }


class KnowledgeGraph:
    """
    Central Knowledge Graph - The Brain of Rumee
    All data flows through this graph. It's the single source of truth.
    """
    
    def __init__(self):
        self.nodes: Dict[str, Node] = {}  # node_id -> Node
        self.edges: Dict[str, List[Edge]] = defaultdict(list)  # source_id -> [Edge]
        self.reverse_edges: Dict[str, List[Edge]] = defaultdict(list)  # target_id -> [Edge]
        self.type_index: Dict[str, Set[str]] = defaultdict(set)  # node_type -> {node_ids}
        
        logger.info("🕸️ Knowledge Graph initialized")
    
    # === CORE OPERATIONS ===
    
    def add_node(self, node_id: str, node_type: str, properties: Dict[str, Any]) -> Node:
        """Add or update a node in the graph"""
        if node_id in self.nodes:
            # Update existing node
            node = self.nodes[node_id]
            node.properties.update(properties)
            node.updated_at = datetime.now().isoformat()
        else:
            # Create new node
            node = Node(node_id, node_type, properties)
            self.nodes[node_id] = node
            self.type_index[node_type].add(node_id)
            logger.debug(f"Added node: {node_type}:{node_id}")
        
        return node
    
    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: Dict[str, Any] = None) -> Edge:
        """Add an edge between two nodes"""
        # Ensure both nodes exist
        if source_id not in self.nodes or target_id not in self.nodes:
            logger.warning(f"Cannot add edge: nodes don't exist ({source_id} -> {target_id})")
            return None
        
        # Check if edge already exists
        for edge in self.edges[source_id]:
            if edge.target_id == target_id and edge.type == edge_type:
                # Update weight/properties if it exists
                if properties:
                    edge.properties.update(properties)
                    edge.weight = properties.get('weight', edge.weight)
                return edge
        
        # Create new edge
        edge = Edge(source_id, target_id, edge_type, properties)
        self.edges[source_id].append(edge)
        self.reverse_edges[target_id].append(edge)
        
        logger.debug(f"Added edge: {source_id} --[{edge_type}]--> {target_id}")
        return edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """Get all nodes of a specific type"""
        node_ids = self.type_index.get(node_type, set())
        return [self.nodes[nid] for nid in node_ids]
    
    def get_edges_from(self, node_id: str, edge_type: Optional[str] = None) -> List[Edge]:
        """Get all outgoing edges from a node"""
        edges = self.edges.get(node_id, [])
        if edge_type:
            return [e for e in edges if e.type == edge_type]
        return edges
    
    def get_edges_to(self, node_id: str, edge_type: Optional[str] = None) -> List[Edge]:
        """Get all incoming edges to a node"""
        edges = self.reverse_edges.get(node_id, [])
        if edge_type:
            return [e for e in edges if e.type == edge_type]
        return edges
    
    def get_neighbors(self, node_id: str, edge_type: Optional[str] = None, direction: str = 'both') -> List[Node]:
        """Get neighboring nodes"""
        neighbors = []
        
        if direction in ['out', 'both']:
            edges = self.get_edges_from(node_id, edge_type)
            neighbors.extend([self.nodes[e.target_id] for e in edges if e.target_id in self.nodes])
        
        if direction in ['in', 'both']:
            edges = self.get_edges_to(node_id, edge_type)
            neighbors.extend([self.nodes[e.source_id] for e in edges if e.source_id in self.nodes])
        
        return neighbors
    
    # === DATA INGESTION ===
    
    def ingest_note(self, note: Dict[str, Any]):
        """Ingest a note into the graph"""
        note_id = f"note:{note['id']}"
        
        # Add note node
        self.add_node(note_id, 'note', {
            'title': note.get('title', ''),
            'content': note.get('content', ''),
            'tags': note.get('tags', []),
            'created_at': note.get('created_at', ''),
            'sentiment': note.get('ai_sentiment', {}),
            'priority': note.get('ai_priority', {}),
            'classification': note.get('ai_classification', {})
        })
        
        # Extract and link entities
        entities = note.get('ai_entities', {})
        
        # People
        for person in entities.get('people', []):
            person_id = f"person:{person}"
            self.add_node(person_id, 'person', {'name': person})
            self.add_edge(note_id, person_id, 'MENTIONS')
        
        # Topics
        for topic in entities.get('topics', []):
            topic_id = f"topic:{topic}"
            self.add_node(topic_id, 'topic', {'name': topic})
            self.add_edge(note_id, topic_id, 'DISCUSSES')
        
        # Organizations
        for org in entities.get('organizations', []):
            org_id = f"organization:{org}"
            self.add_node(org_id, 'organization', {'name': org})
            self.add_edge(note_id, org_id, 'REFERENCES')
        
        # Locations
        for location in entities.get('locations', []):
            loc_id = f"location:{location}"
            self.add_node(loc_id, 'location', {'name': location})
            self.add_edge(note_id, loc_id, 'AT_LOCATION')
        
        # Tasks extracted
        for task in entities.get('tasks', []):
            if isinstance(task, dict):
                task_id = f"task:{task.get('id', task.get('title', 'unknown'))}"
                self.add_node(task_id, 'task', task)
                self.add_edge(note_id, task_id, 'CONTAINS_TASK')
            elif isinstance(task, str):
                task_id = f"task:{task}"
                self.add_node(task_id, 'task', {'title': task})
                self.add_edge(note_id, task_id, 'CONTAINS_TASK')
    
    def ingest_person(self, person: Dict[str, Any]):
        """Ingest a person into the graph"""
        person_id = f"person:{person['id']}"
        self.add_node(person_id, 'person', {
            'name': person.get('name', ''),
            'email': person.get('email', ''),
            'phone': person.get('phone', ''),
            'company': person.get('company', ''),
            'notes': person.get('notes', ''),
            'created_at': person.get('created_at', '')
        })
    
    def ingest_meeting(self, meeting: Dict[str, Any]):
        """Ingest a meeting into the graph"""
        meeting_id = f"meeting:{meeting['id']}"
        
        self.add_node(meeting_id, 'meeting', {
            'title': meeting.get('title', ''),
            'description': meeting.get('description', ''),
            'scheduled_at': meeting.get('scheduled_at', ''),
            'location': meeting.get('location', ''),
            'created_at': meeting.get('created_at', '')
        })
        
        # Link attendees
        for attendee in meeting.get('attendees', []):
            person_id = f"person:{attendee}"
            if person_id not in self.nodes:
                self.add_node(person_id, 'person', {'name': attendee})
            self.add_edge(person_id, meeting_id, 'ATTENDS')
    
    def ingest_reminder(self, reminder: Dict[str, Any]):
        """Ingest a reminder/task into the graph"""
        reminder_id = f"reminder:{reminder['id']}"
        
        self.add_node(reminder_id, 'reminder', {
            'title': reminder.get('title', ''),
            'description': reminder.get('description', ''),
            'due_date': reminder.get('due_date', ''),
            'priority': reminder.get('priority', ''),
            'status': reminder.get('status', ''),
            'created_at': reminder.get('created_at', '')
        })
    
    def link_notes(self, source_note_id: str, target_note_id: str, connection_type: str, strength: float, reason: str):
        """Link two notes based on AI-discovered connection"""
        source_id = f"note:{source_note_id}"
        target_id = f"note:{target_note_id}"
        
        self.add_edge(source_id, target_id, connection_type.upper(), {
            'strength': strength,
            'reason': reason,
            'discovered_at': datetime.now().isoformat()
        })
    
    # === GRAPH QUERIES ===
    
    def find_context(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Find all context around a node (BFS to depth N)"""
        visited = set()
        queue = [(node_id, 0)]
        context = {
            'center': self.get_node(node_id).to_dict() if node_id in self.nodes else None,
            'nodes': [],
            'edges': []
        }
        
        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_id in visited or current_depth > depth:
                continue
            
            visited.add(current_id)
            
            if current_id != node_id:
                node = self.get_node(current_id)
                if node:
                    context['nodes'].append(node.to_dict())
            
            # Add neighbors to queue
            if current_depth < depth:
                for edge in self.get_edges_from(current_id):
                    context['edges'].append(edge.to_dict())
                    if edge.target_id not in visited:
                        queue.append((edge.target_id, current_depth + 1))
                
                for edge in self.get_edges_to(current_id):
                    context['edges'].append(edge.to_dict())
                    if edge.source_id not in visited:
                        queue.append((edge.source_id, current_depth + 1))
        
        return context
    
    def find_path(self, start_id: str, end_id: str, max_depth: int = 4) -> List[List[str]]:
        """Find paths between two nodes (BFS)"""
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        paths = []
        queue = [([start_id], set([start_id]))]
        
        while queue:
            path, visited = queue.pop(0)
            current_id = path[-1]
            
            if len(path) > max_depth:
                continue
            
            if current_id == end_id:
                paths.append(path)
                continue
            
            # Explore neighbors
            for edge in self.get_edges_from(current_id):
                if edge.target_id not in visited:
                    new_path = path + [edge.target_id]
                    new_visited = visited | {edge.target_id}
                    queue.append((new_path, new_visited))
        
        return paths
    
    def get_central_nodes(self, node_type: Optional[str] = None, limit: int = 10) -> List[Tuple[str, int]]:
        """Find most connected nodes (highest degree centrality)"""
        degree = {}
        
        nodes_to_check = self.nodes.keys()
        if node_type:
            nodes_to_check = self.type_index.get(node_type, set())
        
        for node_id in nodes_to_check:
            in_degree = len(self.get_edges_to(node_id))
            out_degree = len(self.get_edges_from(node_id))
            degree[node_id] = in_degree + out_degree
        
        sorted_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:limit]
    
    def get_clusters(self, node_type: str = 'topic') -> Dict[str, List[str]]:
        """Find clusters of related nodes"""
        clusters = defaultdict(list)
        visited = set()
        
        for node_id in self.type_index.get(node_type, set()):
            if node_id in visited:
                continue
            
            # BFS to find cluster
            cluster = []
            queue = [node_id]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                
                visited.add(current)
                cluster.append(current)
                
                # Add similar neighbors
                neighbors = self.get_neighbors(current)
                for neighbor in neighbors:
                    if neighbor.type == node_type and neighbor.id not in visited:
                        queue.append(neighbor.id)
            
            if cluster:
                clusters[f"cluster_{len(clusters)}"] = cluster
        
        return dict(clusters)
    
    def query_by_properties(self, node_type: str, filters: Dict[str, Any]) -> List[Node]:
        """Query nodes by properties"""
        results = []
        
        for node_id in self.type_index.get(node_type, set()):
            node = self.nodes[node_id]
            matches = True
            
            for key, value in filters.items():
                if key not in node.properties or node.properties[key] != value:
                    matches = False
                    break
            
            if matches:
                results.append(node)
        
        return results
    
    def get_timeline(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get timeline of all activities related to an entity"""
        timeline = []
        
        # Get all connected notes
        note_edges = self.get_edges_to(entity_id, direction='in')
        
        for edge in note_edges:
            if edge.source_id.startswith('note:'):
                node = self.get_node(edge.source_id)
                if node:
                    timeline.append({
                        'date': node.properties.get('created_at', ''),
                        'type': 'note',
                        'title': node.properties.get('title', ''),
                        'content': node.properties.get('content', '')[:200],
                        'relationship': edge.type
                    })
        
        # Sort by date
        timeline.sort(key=lambda x: x['date'], reverse=True)
        return timeline
    
    # === GRAPH ANALYTICS ===
    
    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics"""
        total_edges = sum(len(edges) for edges in self.edges.values())
        
        type_counts = {
            node_type: len(node_ids)
            for node_type, node_ids in self.type_index.items()
        }
        
        edge_types = defaultdict(int)
        for edges in self.edges.values():
            for edge in edges:
                edge_types[edge.type] += 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': total_edges,
            'node_types': type_counts,
            'edge_types': dict(edge_types),
            'density': total_edges / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0
        }
    
    def export_for_visualization(self, node_types: List[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Export graph in format suitable for D3.js or similar"""
        if node_types:
            node_ids = set()
            for nt in node_types:
                node_ids.update(self.type_index.get(nt, set()))
        else:
            node_ids = set(list(self.nodes.keys())[:limit])
        
        nodes = []
        edges = []
        
        for node_id in node_ids:
            node = self.nodes[node_id]
            nodes.append({
                'id': node.id,
                'label': node.properties.get('name') or node.properties.get('title', node.id.split(':')[1]),
                'type': node.type,
                'size': len(self.get_edges_from(node.id)) + len(self.get_edges_to(node.id))
            })
        
        for node_id in node_ids:
            for edge in self.get_edges_from(node_id):
                if edge.target_id in node_ids:
                    edges.append({
                        'source': edge.source_id,
                        'target': edge.target_id,
                        'type': edge.type,
                        'weight': edge.weight
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'stats': self.get_stats()
        }


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
