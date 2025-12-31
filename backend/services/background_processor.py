"""
Background AI Processor - Automatically processes user messages and organizes data
Uses Ollama for local AI inference
"""

import ollama
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Global references to storage (will be set by test_server)
notes_db = None
people_db = None
reminders_db = None
meetings_db = None  # Will be set by test_server
neo4j_service = None  # Will be set by test_server
save_callback = None  # Callback to save data to disk


class BackgroundProcessor:
    """Processes messages in background and organizes data"""
    
    def __init__(self):
        self.processing_queue = asyncio.Queue()
        self.is_running = False
        
    async def start(self):
        """Start background processing"""
        if self.is_running:
            return
        self.is_running = True
        # Don't create task here, let the caller do it
        logger.info("Background processor started")
        
    async def stop(self):
        """Stop background processing"""
        self.is_running = False
        
    async def _process_loop(self):
        """Main processing loop"""
        while self.is_running:
            try:
                # Get item from queue
                item = await asyncio.wait_for(
                    self.processing_queue.get(),
                    timeout=1.0
                )
                
                # Process the item
                await self._process_item(item)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(1)
                
    async def _process_item(self, item: Dict[str, Any]):
        """Process a single item"""
        try:
            item_type = item.get("type")
            data = item.get("data")
            user_id = item.get("user_id")
            
            if item_type == "note":
                await self._process_note(data, user_id)
            elif item_type == "message":
                await self._process_message(data, user_id)
            elif item_type == "organize":
                await self._organize_user_data(user_id)
                
        except Exception as e:
            logger.error(f"Error processing item: {e}")
            
    async def _process_note(self, note: Dict[str, Any], user_id: str):
        """Process a note - extract entities, generate embeddings, link data"""
        try:
            content = f"{note.get('title', '')} {note.get('content', '')}"
            
            logger.info(f"🤖 Processing note: {note.get('title')}")
            
            # Run Ollama inference in executor
            loop = asyncio.get_event_loop()
            
            # Extract entities and topics
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model='llama3.2:latest',
                    messages=[{
                        'role': 'system',
                        'content': 'Extract key information from text. Return ONLY valid JSON with these keys: people (array of names), dates (array), topics (array), tasks (array), organizations (array), locations (array). Be concise.'
                    }, {
                        'role': 'user',
                        'content': f'Extract entities from: {content}'
                    }],
                    options={'temperature': 0.2, 'num_predict': 200}
                )
            )
            
            # Parse response
            ai_content = response['message']['content']
            if "```json" in ai_content:
                ai_content = ai_content.split("```json")[1].split("```")[0].strip()
            elif "```" in ai_content:
                ai_content = ai_content.split("```")[1].split("```")[0].strip()
            
            try:
                entities = json.loads(ai_content)
            except:
                entities = {"people": [], "dates": [], "topics": [], "tasks": [], "organizations": [], "locations": []}
            
            # Generate embeddings for similarity search
            embeddings = await loop.run_in_executor(
                None,
                lambda: ollama.embeddings(
                    model='embeddinggemma:latest',
                    prompt=content
                )
            )
            
            # Detect sentiment and priority
            sentiment_response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model='llama3.2:latest',
                    messages=[{
                        'role': 'system',
                        'content': 'Analyze sentiment and priority. Return JSON with keys: sentiment (positive/negative/neutral), urgency (low/medium/high), priority (low/medium/high), emotions (array)'
                    }, {
                        'role': 'user',
                        'content': f'Analyze: {content}'
                    }],
                    options={'temperature': 0.3, 'num_predict': 150}
                )
            )
            
            # Parse sentiment/priority
            sentiment_content = sentiment_response['message']['content']
            if "```json" in sentiment_content:
                sentiment_content = sentiment_content.split("```json")[1].split("```")[0].strip()
            elif "```" in sentiment_content:
                sentiment_content = sentiment_content.split("```")[1].split("```")[0].strip()
            
            try:
                sentiment_data = json.loads(sentiment_content)
            except:
                sentiment_data = {"sentiment": "neutral", "urgency": "medium", "priority": "medium", "emotions": []}
            
            # Update note with AI results
            if notes_db is not None and note['id'] in notes_db:
                notes_db[note['id']]['ai_entities'] = entities
                notes_db[note['id']]['embeddings'] = embeddings['embedding']
                notes_db[note['id']]['sentiment'] = sentiment_data
                notes_db[note['id']]['ai_processed'] = True
                notes_db[note['id']]['processed_at'] = datetime.now().isoformat()
                
                # Auto-create people entries
                if people_db is not None:
                    for person_name in entities.get('people', []):
                        person_id = f"person_{person_name.lower().replace(' ', '_')}"
                        if person_id not in people_db:
                            people_db[person_id] = {
                                'id': person_id,
                                'name': person_name,
                                'notes': [note['id']],
                                'created_at': datetime.now().isoformat(),
                                'auto_created': True
                            }
                        else:
                            if note['id'] not in people_db[person_id].get('notes', []):
                                people_db[person_id].setdefault('notes', []).append(note['id'])
                
                # Auto-create reminders from tasks with priority AND deadlines
                if reminders_db is not None:
                    for task in entities.get('tasks', []):
                        reminder_id = f"reminder_{len(reminders_db) + 1}"
                        # Use AI-detected priority for auto-created reminders
                        task_priority = sentiment_data.get('priority', 'medium')
                        
                        # Try to extract deadline for this task from dates
                        task_deadline = None
                        for date_str in entities.get('dates', []):
                            # Simple heuristic: use first future date as deadline
                            try:
                                # Parse common date formats
                                from dateutil import parser
                                parsed_date = parser.parse(date_str, fuzzy=True)
                                if parsed_date > datetime.now():
                                    task_deadline = parsed_date.isoformat()
                                    break
                            except:
                                pass
                        
                        reminders_db[reminder_id] = {
                            'id': reminder_id,
                            'title': task,
                            'description': f'Extracted from note: {note.get("title", "Untitled")}',
                            'source_note': note['id'],
                            'status': 'pending',
                            'priority': task_priority,
                            'urgency': sentiment_data.get('urgency', 'medium'),
                            'due_date': task_deadline,
                            'created_at': datetime.now().isoformat(),
                            'auto_created': True
                        }
                        
                        logger.info(f"📅 Auto-created reminder: {task}" + (f" (due: {task_deadline})" if task_deadline else ""))
                
                # Auto-create calendar/meeting entries from dates mentioned
                if meetings_db is not None and entities.get('dates'):
                    for date_str in entities.get('dates', []):
                        try:
                            from dateutil import parser
                            parsed_date = parser.parse(date_str, fuzzy=True)
                            
                            # Only create meetings for future dates
                            if parsed_date > datetime.now():
                                meeting_id = f"meeting_{len(meetings_db) + 1}"
                                
                                # Try to infer meeting title from context
                                meeting_title = f"Event on {parsed_date.strftime('%Y-%m-%d')}"
                                if entities.get('topics'):
                                    meeting_title = f"{entities['topics'][0]} - {parsed_date.strftime('%b %d')}"
                                
                                meetings_db[meeting_id] = {
                                    'id': meeting_id,
                                    'title': meeting_title,
                                    'description': f'Auto-created from note: {note.get("title", "Untitled")}',
                                    'scheduled_at': parsed_date.isoformat(),
                                    'status': 'scheduled',
                                    'source_note': note['id'],
                                    'attendees': entities.get('people', []),
                                    'location': entities.get('locations', [None])[0],
                                    'created_at': datetime.now().isoformat(),
                                    'auto_created': True
                                }
                                
                                logger.info(f"📆 Auto-created meeting: {meeting_title} on {parsed_date.strftime('%Y-%m-%d')}")
                        except Exception as e:
                            logger.debug(f"Could not parse date '{date_str}': {e}")
                            continue
                
                # Store in Neo4j if available
                if neo4j_service is not None:
                    try:
                        neo4j_service.create_note_node(
                            note_id=note['id'],
                            title=note.get('title', ''),
                            content=note.get('content', ''),
                            entities=entities
                        )
                        logger.info(f"📊 Stored note {note['id']} in Neo4j graph")
                    except Exception as e:
                        logger.error(f"Neo4j error: {e}")
                
                logger.info(f"✅ Processed note: {note.get('title')} - Found {len(entities.get('people', []))} people, {len(entities.get('topics', []))} topics, {len(entities.get('tasks', []))} tasks")
                
                # Save data to disk after processing
                if save_callback is not None:
                    try:
                        save_callback()
                    except Exception as e:
                        logger.error(f"Error saving data: {e}")
            
        except Exception as e:
            logger.error(f"❌ Error processing note: {e}")
            
    async def _process_message(self, message: str, user_id: str):
        """Process a free-form message and infer intent"""
        try:
            loop = asyncio.get_event_loop()
            
            # Infer what the user wants to do
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model='llama3.2:latest',
                    messages=[{
                        'role': 'system',
                        'content': '''You are an intelligent assistant. Analyze user messages and determine intent.
                        Return JSON with:
                        - action: (create_note, add_person, schedule_meeting, set_reminder, search, organize)
                        - entities: extracted information
                        - confidence: 0-1
                        
                        Examples:
                        "Met John today, discussed project" -> {action: "create_note", entities: {person: "John", topic: "project"}}
                        "Remind me to call Sarah tomorrow" -> {action: "set_reminder", entities: {person: "Sarah", task: "call", when: "tomorrow"}}
                        '''
                    }, {
                        'role': 'user',
                        'content': message
                    }],
                    options={'temperature': 0.4}
                )
            )
            
            intent = response['message']['content']
            logger.info(f"Inferred intent for user {user_id}: {intent}")
            
            # Return intent for further processing
            return intent
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return None
            
    async def _organize_user_data(self, user_id: str):
        """Organize all user data - find connections, suggest relationships"""
        try:
            # This would connect to the database and organize data
            # For now, just log
            logger.info(f"Organizing data for user {user_id}")
            
            # In full implementation:
            # 1. Get all user's notes, people, meetings
            # 2. Use embeddings to find similar items
            # 3. Suggest automatic links
            # 4. Create knowledge graph relationships
            
        except Exception as e:
            logger.error(f"Error organizing data: {e}")
            
    async def add_to_queue(self, item_type: str, data: Any, user_id: str):
        """Add item to processing queue"""
        await self.processing_queue.put({
            "type": item_type,
            "data": data,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })
        logger.debug(f"Added {item_type} to processing queue")


# Global instance
processor = BackgroundProcessor()
