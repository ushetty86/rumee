"""
AI Service for Ollama integration
Handles embeddings, entity extraction, summarization, and relationship analysis
"""

import ollama
from config.settings import settings
from typing import List, Dict, Any
import logging
import asyncio

logger = logging.getLogger(__name__)

# Ollama client will use default local instance


class AIService:
    """AI service for various AI operations"""
    
    @staticmethod
    async def generate_embeddings(text: str) -> List[float]:
        """Generate embeddings for semantic search using Ollama"""
        try:
            # Run Ollama in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.embeddings(
                    model=settings.OLLAMA_EMBEDDING_MODEL,
                    prompt=text
                )
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return []
    
    @staticmethod
    async def extract_entities(text: str) -> Dict[str, Any]:
        """Extract entities (people, dates, topics) from text"""
        try:
            prompt = f"""Extract entities from the following text:
            
Text: {text}

Please identify:
1. People mentioned (names)
2. Dates/times mentioned
3. Topics/themes discussed
4. Organizations/companies mentioned
5. Locations mentioned

Return as JSON with keys: people, dates, topics, organizations, locations"""

            # Run Ollama in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an entity extraction assistant. Extract entities and return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.3}
                )
            )
            
            import json
            content = response.choices[0].message.content
            
            # Try to parse JSON from the response
            try:
                # Remove markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                entities = json.loads(content)
                return entities
            except json.JSONDecodeError:
                # If JSON parsing fails, return empty structure
                logger.warning("Could not parse JSON from entity extraction response")
                return {
                    "people": [],
                    "dates": [],
                    "topics": [],
                    "organizations": [],
                    "locations": []
                }
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {
                "people": [],
                "dates": [],
                "topics": [],
                "organizations": [],
                "locations": []
            }
    
    @staticmethod
    async def generate_summary(content: str, summary_type: str = "brief") -> str:
        """Generate summary of content"""
        try:
            prompts = {
                "brief": "Provide a brief 2-3 sentence summary of the following content:",
                "detailed": "Provide a detailed summary with key points of the following content:",
                "bullet": "Provide a bullet-point summary of the key points from the following content:"
            }
            
            prompt = prompts.get(summary_type, prompts["brief"])
            
            # Run Ollama in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarization assistant."},
                        {"role": "user", "content": f"{prompt}\n\n{content}"}
                    ],
                    options={"temperature": 0.5, "num_predict": 500}
                )
            )
            
            return response['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Error generating summary"
    
    @staticmethod
    async def analyze_relationship(source_content: str, target_content: str) -> Dict[str, Any]:
        """Analyze relationship between two pieces of content"""
        try:
            prompt = f"""Analyze the relationship between these two pieces of content:

Source: {source_content[:500]}

Target: {target_content[:500]}

Determine:
1. Relationship type (mentions, related_to, discusses, follows_up, similar_to, caused_by, derived_from)
2. Strength/confidence (0.0 to 1.0)
3. Reasoning for the relationship
4. Shared entities or themes

Return as JSON with keys: relationship_type, strength, reasoning, shared_themes"""

            # Run Ollama in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a relationship analysis assistant. Analyze relationships and return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.3}
                )
            )
            
            import json
            content = response['message']['content']
            
            # Try to parse JSON
            try:
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                analysis = json.loads(content)
                return analysis
            except json.JSONDecodeError:
                logger.warning("Could not parse JSON from relationship analysis")
                return {
                    "relationship_type": "related_to",
                    "strength": 0.5,
                    "reasoning": "Unable to analyze relationship",
                    "shared_themes": []
                }
                
        except Exception as e:
            logger.error(f"Error analyzing relationship: {e}")
            return {
                "relationship_type": "related_to",
                "strength": 0.0,
                "reasoning": f"Error: {str(e)}",
                "shared_themes": []
            }
    
    @staticmethod
    async def find_similar_content(query_embedding: List[float], 
                                   candidate_embeddings: List[tuple]) -> List[tuple]:
        """Find similar content using cosine similarity"""
        import numpy as np
        
        if not query_embedding or not candidate_embeddings:
            return []
        
        query_vec = np.array(query_embedding)
        
        similarities = []
        for item_id, embedding in candidate_embeddings:
            if not embedding:
                continue
            
            candidate_vec = np.array(embedding)
            
            # Cosine similarity
            similarity = np.dot(query_vec, candidate_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(candidate_vec)
            )
            
            similarities.append((item_id, float(similarity)))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities
    
    @staticmethod
    async def detect_sentiment(text: str) -> Dict[str, Any]:
        """
        Detect sentiment and emotional tone of text
        Returns: sentiment (positive/negative/neutral), confidence, emotions
        """
        try:
            prompt = f"""Analyze the sentiment and emotional tone of this text:

Text: {text}

Determine:
1. Overall sentiment (positive, negative, neutral, mixed)
2. Confidence level (0.0 to 1.0)
3. Primary emotions detected (e.g., excited, anxious, frustrated, hopeful, etc.)
4. Urgency level (low, medium, high)

Return as JSON: {{"sentiment": "positive", "confidence": 0.85, "emotions": ["excited", "hopeful"], "urgency": "medium"}}"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a sentiment analysis expert."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.3}
                )
            )
            
            import json
            content = response['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            sentiment = json.loads(content)
            return sentiment
            
        except Exception as e:
            logger.error(f"Error detecting sentiment: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "urgency": "medium"
            }
    
    @staticmethod
    async def detect_priority_and_urgency(text: str, 
                                           context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Intelligently detect priority and urgency of tasks/notes
        Returns: priority (low/medium/high), urgency (low/medium/high), reasoning
        """
        try:
            context_str = ""
            if context:
                context_str = f"\nContext: {json.dumps(context, indent=2)}"
            
            prompt = f"""Analyze this text to determine its priority and urgency:

Text: {text}
{context_str}

Determine:
1. Priority (low/medium/high) - How important is this?
2. Urgency (low/medium/high) - How time-sensitive is this?
3. Has explicit deadline? (yes/no)
4. Extracted deadline (if any, in natural language)
5. Action required (yes/no)
6. Reasoning for the assessment

Return as JSON: {{
    "priority": "high",
    "urgency": "medium",
    "has_deadline": true,
    "deadline": "next Friday",
    "action_required": true,
    "reasoning": "Contains specific deadline and actionable task"
}}"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a priority and urgency detection expert."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.3}
                )
            )
            
            import json
            content = response['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            priority_info = json.loads(content)
            return priority_info
            
        except Exception as e:
            logger.error(f"Error detecting priority: {e}")
            return {
                "priority": "medium",
                "urgency": "medium",
                "has_deadline": False,
                "deadline": None,
                "action_required": False,
                "reasoning": "Unable to determine"
            }
    
    @staticmethod
    async def extract_tasks_from_text(text: str) -> List[Dict[str, Any]]:
        """
        Extract actionable tasks from free-form text
        Returns list of tasks with title, description, priority, deadline
        """
        try:
            prompt = f"""Extract all actionable tasks from this text:

Text: {text}

For each task, identify:
1. Task title (brief, action-oriented)
2. Description (if more detail is available)
3. Priority (low/medium/high)
4. Deadline (if mentioned, in natural language)
5. Assigned to (if person is mentioned)

Return as JSON array: [{{
    "title": "Send budget proposal",
    "description": "Send quarterly budget proposal to Sarah",
    "priority": "high",
    "deadline": "next Friday",
    "assigned_to": "me"
}}]

If no tasks found, return empty array: []"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a task extraction expert."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.3}
                )
            )
            
            import json
            content = response['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            tasks = json.loads(content)
            return tasks if isinstance(tasks, list) else []
            
        except Exception as e:
            logger.error(f"Error extracting tasks: {e}")
            return []


ai_service = AIService()
