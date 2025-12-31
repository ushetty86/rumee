"""
Comprehensive Multi-Agent AI Engine
Acts like multiple assistants working in parallel to analyze, connect, and provide insights
All agents use the Knowledge Graph as the central data structure
"""

import ollama
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

# Import knowledge graph
from services.knowledge_graph import knowledge_graph


class AgentOrchestrator:
    """Orchestrates multiple AI agents working in parallel"""
    
    def __init__(self):
        self.is_running = False
        self.agents = {
            'signal_sorter': SignalSorterAgent(),
            'mind_weaver': MindWeaverAgent(),
            'context_builder': ContextBuilderAgent(),
            'pattern_detector': PatternDetectorAgent(),
            'insight_generator': InsightGeneratorAgent(),
            'relationship_mapper': RelationshipMapperAgent()
        }
        
        # Shared memory for agents
        self.shared_memory = {
            'user_context': {},
            'recent_patterns': [],
            'active_topics': [],
            'entity_graph': defaultdict(list),
            'insights_queue': [],
            'cross_references': defaultdict(list)
        }
        
    async def start(self, notes_db, people_db, reminders_db, meetings_db):
        """Start all agents"""
        self.is_running = True
        self.notes_db = notes_db
        self.people_db = people_db
        self.reminders_db = reminders_db
        self.meetings_db = meetings_db
        
        logger.info("🧠 Starting AI Agent Orchestrator")
        
        # Start all agents
        tasks = []
        for name, agent in self.agents.items():
            task = asyncio.create_task(
                self._run_agent_loop(name, agent)
            )
            tasks.append(task)
        
        logger.info(f"✅ Started {len(self.agents)} AI agents")
        
    async def _run_agent_loop(self, name: str, agent):
        """Run individual agent in loop"""
        while self.is_running:
            try:
                # Each agent processes data at its own interval
                await agent.process(
                    notes_db=self.notes_db,
                    people_db=self.people_db,
                    reminders_db=self.reminders_db,
                    meetings_db=self.meetings_db,
                    shared_memory=self.shared_memory
                )
                
                # Different agents run at different frequencies
                interval = agent.get_interval()
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in agent {name}: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop all agents"""
        self.is_running = False
        logger.info("🛑 Stopping AI Agent Orchestrator")


class SignalSorterAgent:
    """Classifies and prioritizes incoming data"""
    
    def get_interval(self):
        return 10  # Run every 10 seconds
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Sort and classify new data"""
        try:
            # Find unprocessed or recently modified notes
            recent_notes = [
                note for note in notes_db.values()
                if not note.get('fully_processed', False)
            ]
            
            if not recent_notes:
                return
            
            for note in recent_notes[:5]:  # Process 5 at a time
                # Deep classification
                loop = asyncio.get_event_loop()
                classification = await loop.run_in_executor(
                    None,
                    lambda n=note: self._classify_content(n)
                )
                
                # Update note with classification
                note['ai_classification'] = classification
                note['processing_level'] = 'deep'
                
                # Add to shared memory for other agents
                if classification.get('topics'):
                    for topic in classification['topics']:
                        shared_memory['active_topics'].append({
                            'topic': topic,
                            'note_id': note['id'],
                            'timestamp': datetime.now().isoformat()
                        })
                
                logger.info(f"🔍 Signal Sorter: Classified '{note.get('title', 'Untitled')}'")
                
        except Exception as e:
            logger.error(f"Signal Sorter error: {e}")
    
    def _classify_content(self, note):
        """Classify content using Ollama"""
        try:
            content = f"{note.get('title', '')} {note.get('content', '')}"
            
            response = ollama.chat(
                model='llama3.2:latest',
                messages=[{
                    'role': 'system',
                    'content': '''Classify this content deeply. Return JSON with:
                    - content_type: (idea, task, meeting_notes, reference, decision, question, reflection)
                    - topics: array of specific topics (be specific, not generic)
                    - importance: 1-10 score
                    - time_sensitivity: (immediate, soon, later, timeless)
                    - related_domains: array of knowledge domains this relates to
                    - actionable: boolean
                    - key_concepts: array of key concepts mentioned
                    '''
                }, {
                    'role': 'user',
                    'content': content[:1000]
                }],
                options={'temperature': 0.2, 'num_predict': 300}
            )
            
            result = response['message']['content']
            if '```json' in result:
                result = result.split('```json')[1].split('```')[0].strip()
            elif '```' in result:
                result = result.split('```')[1].split('```')[0].strip()
            
            return json.loads(result)
            
        except Exception as e:
            logger.error(f"Classification error: {e}")
            return {}


class MindWeaverAgent:
    """Weaves connections between different pieces of information"""
    
    def get_interval(self):
        return 30  # Run every 30 seconds
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Find hidden connections"""
        try:
            notes = list(notes_db.values())
            if len(notes) < 2:
                return
            
            # Compare recent notes with older ones
            recent = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
            older = [n for n in notes if n not in recent][:20]
            
            connections_found = 0
            
            for recent_note in recent:
                for old_note in older:
                    # Check if we should compare these
                    if self._should_compare(recent_note, old_note):
                        connection = await self._find_connection(recent_note, old_note)
                        
                        if connection and connection.get('strength', 0) > 0.6:
                            # Store in shared memory
                            shared_memory['cross_references'][recent_note['id']].append({
                                'target_id': old_note['id'],
                                'connection_type': connection.get('type'),
                                'strength': connection.get('strength'),
                                'reason': connection.get('reason')
                            })
                            
                            # Store in Knowledge Graph (THE BRAIN)
                            knowledge_graph.link_notes(
                                recent_note['id'],
                                old_note['id'],
                                connection.get('type', 'related_to'),
                                connection.get('strength', 0.7),
                                connection.get('reason', 'AI discovered connection')
                            )
                            
                            connections_found += 1
            
            if connections_found > 0:
                logger.info(f"🕸️ Mind Weaver: Found {connections_found} new connections")
                
        except Exception as e:
            logger.error(f"Mind Weaver error: {e}")
    
    def _should_compare(self, note1, note2):
        """Decide if two notes should be compared"""
        # Compare if they share topics, people, or are close in time
        entities1 = note1.get('ai_entities', {})
        entities2 = note2.get('ai_entities', {})
        
        # Check for shared entities
        people1 = set(entities1.get('people', []))
        people2 = set(entities2.get('people', []))
        
        topics1 = set(entities1.get('topics', []))
        topics2 = set(entities2.get('topics', []))
        
        return bool(people1 & people2) or bool(topics1 & topics2)
    
    async def _find_connection(self, note1, note2):
        """Find connection between two notes using AI"""
        try:
            loop = asyncio.get_event_loop()
            
            content1 = f"{note1.get('title', '')} {note1.get('content', '')}"[:500]
            content2 = f"{note2.get('title', '')} {note2.get('content', '')}"[:500]
            
            result = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model='llama3.2:latest',
                    messages=[{
                        'role': 'system',
                        'content': '''Analyze if these two pieces of content are related. Return JSON:
                        {
                            "connected": true/false,
                            "strength": 0.0-1.0,
                            "type": "builds_on|contradicts|supports|related_to|same_theme",
                            "reason": "brief explanation"
                        }'''
                    }, {
                        'role': 'user',
                        'content': f"Content 1: {content1}\n\nContent 2: {content2}"
                    }],
                    options={'temperature': 0.3, 'num_predict': 150}
                )
            )
            
            response = result['message']['content']
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0].strip()
            elif '```' in response:
                response = response.split('```')[1].split('```')[0].strip()
            
            return json.loads(response)
            
        except Exception as e:
            logger.debug(f"Connection analysis error: {e}")
            return None


class ContextBuilderAgent:
    """Builds and maintains context about user's current focus"""
    
    def get_interval(self):
        return 20  # Run every 20 seconds
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Build current context"""
        try:
            # Analyze what user is currently focused on
            recent_notes = sorted(
                notes_db.values(),
                key=lambda x: x.get('created_at', ''),
                reverse=True
            )[:5]
            
            if not recent_notes:
                return
            
            # Extract current focus areas
            focus_areas = defaultdict(int)
            active_people = defaultdict(int)
            
            for note in recent_notes:
                entities = note.get('ai_entities', {})
                for topic in entities.get('topics', []):
                    focus_areas[topic] += 1
                for person in entities.get('people', []):
                    active_people[person] += 1
            
            # Build context summary
            context = {
                'primary_focus': max(focus_areas.items(), key=lambda x: x[1])[0] if focus_areas else None,
                'active_topics': [k for k, v in sorted(focus_areas.items(), key=lambda x: x[1], reverse=True)[:5]],
                'active_people': [k for k, v in sorted(active_people.items(), key=lambda x: x[1], reverse=True)[:5]],
                'recent_activity_level': len(recent_notes),
                'updated_at': datetime.now().isoformat()
            }
            
            shared_memory['user_context'] = context
            
            logger.info(f"🎯 Context Builder: Focus on '{context['primary_focus']}'")
            
        except Exception as e:
            logger.error(f"Context Builder error: {e}")


class PatternDetectorAgent:
    """Detects patterns and trends over time"""
    
    def get_interval(self):
        return 60  # Run every minute
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Detect patterns"""
        try:
            notes = list(notes_db.values())
            if len(notes) < 5:
                return
            
            # Temporal patterns
            time_patterns = self._detect_time_patterns(notes)
            
            # Topic evolution patterns
            topic_evolution = self._detect_topic_evolution(notes)
            
            # Collaboration patterns
            collab_patterns = self._detect_collaboration_patterns(notes, people_db)
            
            patterns = {
                'time_patterns': time_patterns,
                'topic_evolution': topic_evolution,
                'collaboration_patterns': collab_patterns,
                'detected_at': datetime.now().isoformat()
            }
            
            shared_memory['recent_patterns'].append(patterns)
            
            # Keep only last 10 pattern detections
            if len(shared_memory['recent_patterns']) > 10:
                shared_memory['recent_patterns'] = shared_memory['recent_patterns'][-10:]
            
            logger.info(f"📈 Pattern Detector: Found {len(time_patterns)} temporal patterns")
            
        except Exception as e:
            logger.error(f"Pattern Detector error: {e}")
    
    def _detect_time_patterns(self, notes):
        """Detect when user is most active"""
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        
        for note in notes:
            try:
                created = datetime.fromisoformat(note.get('created_at', ''))
                hour_counts[created.hour] += 1
                day_counts[created.strftime('%A')] += 1
            except:
                pass
        
        return {
            'peak_hours': sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3],
            'active_days': sorted(day_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        }
    
    def _detect_topic_evolution(self, notes):
        """Detect how topics are evolving"""
        # Group notes by week
        now = datetime.now()
        weeks = defaultdict(lambda: defaultdict(int))
        
        for note in notes:
            try:
                created = datetime.fromisoformat(note.get('created_at', ''))
                weeks_ago = (now - created).days // 7
                
                if weeks_ago <= 4:  # Last 4 weeks
                    entities = note.get('ai_entities', {})
                    for topic in entities.get('topics', []):
                        weeks[weeks_ago][topic] += 1
            except:
                pass
        
        return dict(weeks)
    
    def _detect_collaboration_patterns(self, notes, people_db):
        """Detect who user works with most"""
        person_mentions = defaultdict(int)
        
        for note in notes:
            entities = note.get('ai_entities', {})
            for person in entities.get('people', []):
                person_mentions[person] += 1
        
        return sorted(person_mentions.items(), key=lambda x: x[1], reverse=True)[:10]


class InsightGeneratorAgent:
    """Generates proactive insights and suggestions"""
    
    def get_interval(self):
        return 45  # Run every 45 seconds
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Generate insights"""
        try:
            context = shared_memory.get('user_context', {})
            patterns = shared_memory.get('recent_patterns', [])
            cross_refs = shared_memory.get('cross_references', {})
            
            if not context:
                return
            
            # Generate different types of insights
            insights = []
            
            # Insight 1: Unfinished business
            unfinished = self._find_unfinished_items(notes_db, reminders_db)
            if unfinished:
                insights.append({
                    'type': 'unfinished_business',
                    'title': 'Unfinished Items Need Attention',
                    'description': unfinished,
                    'priority': 'high'
                })
            
            # Insight 2: Neglected contacts
            neglected = self._find_neglected_people(notes_db, people_db)
            if neglected:
                insights.append({
                    'type': 'neglected_contacts',
                    'title': 'People You Haven\'t Connected With',
                    'description': f"You haven't mentioned {neglected[0]} in a while. Consider reaching out.",
                    'priority': 'medium'
                })
            
            # Insight 3: Topic convergence
            if len(cross_refs) > 3:
                insights.append({
                    'type': 'topic_convergence',
                    'title': 'Your Ideas Are Connecting',
                    'description': f"I found {sum(len(v) for v in cross_refs.values())} connections between your notes. Your thinking is converging around key themes.",
                    'priority': 'low'
                })
            
            # Add insights to queue
            for insight in insights:
                insight['generated_at'] = datetime.now().isoformat()
                shared_memory['insights_queue'].append(insight)
            
            # Keep only last 20 insights
            if len(shared_memory['insights_queue']) > 20:
                shared_memory['insights_queue'] = shared_memory['insights_queue'][-20:]
            
            if insights:
                logger.info(f"💡 Insight Generator: Generated {len(insights)} new insights")
            
        except Exception as e:
            logger.error(f"Insight Generator error: {e}")
    
    def _find_unfinished_items(self, notes_db, reminders_db):
        """Find unfinished items"""
        pending = [r for r in reminders_db.values() if r.get('status') == 'pending']
        
        # Find old pending items
        old_pending = []
        for reminder in pending:
            try:
                created = datetime.fromisoformat(reminder.get('created_at', ''))
                if (datetime.now() - created).days > 3:
                    old_pending.append(reminder.get('title'))
            except:
                pass
        
        if old_pending:
            return f"{len(old_pending)} tasks pending for over 3 days"
        return None
    
    def _find_neglected_people(self, notes_db, people_db):
        """Find people not mentioned recently"""
        # Find people mentioned more than 7 days ago
        now = datetime.now()
        people_last_seen = {}
        
        for note in notes_db.values():
            try:
                created = datetime.fromisoformat(note.get('created_at', ''))
                entities = note.get('ai_entities', {})
                
                for person in entities.get('people', []):
                    if person not in people_last_seen or created > datetime.fromisoformat(people_last_seen[person]):
                        people_last_seen[person] = created.isoformat()
            except:
                pass
        
        neglected = []
        for person, last_seen in people_last_seen.items():
            try:
                last_seen_dt = datetime.fromisoformat(last_seen)
                if (now - last_seen_dt).days > 14:
                    neglected.append(person)
            except:
                pass
        
        return neglected


class RelationshipMapperAgent:
    """Maps relationships between entities"""
    
    def get_interval(self):
        return 40  # Run every 40 seconds
    
    async def process(self, notes_db, people_db, reminders_db, meetings_db, shared_memory):
        """Map entity relationships using Knowledge Graph"""
        try:
            # The Knowledge Graph already maintains relationships
            # This agent enriches it with higher-level patterns
            
            # Get graph stats
            stats = knowledge_graph.get_stats()
            
            # Update shared memory with graph insights
            shared_memory['entity_graph'] = {
                'total_nodes': stats['total_nodes'],
                'total_edges': stats['total_edges'],
                'node_types': stats['node_types'],
                'edge_types': stats['edge_types']
            }
            
            # Find central nodes (most connected entities)
            central_people = knowledge_graph.get_central_nodes('person', limit=5)
            central_topics = knowledge_graph.get_central_nodes('topic', limit=5)
            
            shared_memory['central_entities'] = {
                'people': [{'id': nid, 'connections': degree} for nid, degree in central_people],
                'topics': [{'id': nid, 'connections': degree} for nid, degree in central_topics]
            }
            
            logger.debug(f"🗺️ Relationship Mapper: Graph has {stats['total_nodes']} nodes, {stats['total_edges']} edges")
            
        except Exception as e:
            logger.error(f"Relationship Mapper error: {e}")


# Global orchestrator instance
orchestrator = AgentOrchestrator()
