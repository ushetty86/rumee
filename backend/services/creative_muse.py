"""
Creative Muse - Proactive AI Agent
Surfaces relevant old ideas, discovers patterns, and provides contextual inspiration
"""

import ollama
from config.settings import settings
from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CreativeMuse:
    """Proactive AI agent that surfaces relevant ideas and connections"""
    
    @staticmethod
    async def find_relevant_past_ideas(current_context: str, 
                                        all_notes: List[Dict], 
                                        days_lookback: int = 90) -> List[Dict]:
        """
        Find past notes/ideas that are relevant to current context
        Args:
            current_context: What the user is currently working on/thinking about
            all_notes: All user notes
            days_lookback: How far back to look (default 90 days)
        """
        try:
            # Filter notes by date
            cutoff_date = datetime.now() - timedelta(days=days_lookback)
            relevant_notes = [
                note for note in all_notes
                if datetime.fromisoformat(note.get('created_at', '1970-01-01')) >= cutoff_date
            ]
            
            if not relevant_notes:
                return []
            
            # Build prompt for relevance detection
            notes_summary = "\n".join([
                f"Note {i+1} (ID:{note['id']}): {note.get('title', 'Untitled')} - {note.get('content', '')[:200]}"
                for i, note in enumerate(relevant_notes[:20])  # Limit to 20 for token efficiency
            ])
            
            prompt = f"""Current Context: {current_context}

Past Notes from the last {days_lookback} days:
{notes_summary}

Which of these past notes are most relevant to the current context? 
Consider:
1. Similar themes or topics
2. Related people or projects
3. Building blocks for current ideas
4. Contrasting perspectives worth reconsidering

Return JSON array with format: [{{"id": "note_id", "relevance_score": 0.0-1.0, "reason": "why it's relevant"}}]
Only include notes with relevance_score > 0.6
"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a creative muse that helps users discover connections between their past and present thoughts."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.7}
                )
            )
            
            import json
            content = response['message']['content']
            
            # Parse JSON response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            relevant_ideas = json.loads(content)
            return relevant_ideas
            
        except Exception as e:
            logger.error(f"Error finding relevant past ideas: {e}")
            return []
    
    @staticmethod
    async def suggest_proactive_insights(notes: List[Dict], 
                                          people: List[Dict], 
                                          reminders: List[Dict]) -> Dict[str, Any]:
        """
        Generate proactive insights based on user's data
        Returns suggestions like:
        - Patterns you're noticing
        - People you haven't contacted recently
        - Ideas that might connect
        - Tasks that align with your themes
        """
        try:
            # Build context summary
            recent_notes = sorted(notes, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
            notes_summary = "\n".join([
                f"- {note.get('title', 'Untitled')}: {note.get('content', '')[:150]}"
                for note in recent_notes
            ])
            
            people_summary = "\n".join([
                f"- {person.get('name', 'Unknown')}: {person.get('company', '')} {person.get('role', '')}"
                for person in people[:10]
            ])
            
            reminders_summary = "\n".join([
                f"- {reminder.get('title', 'Untitled')} (Priority: {reminder.get('priority', 'medium')})"
                for reminder in reminders[:10]
            ])
            
            prompt = f"""Analyze this user's recent activity and provide proactive insights:

Recent Notes:
{notes_summary}

People in Network:
{people_summary}

Current Tasks:
{reminders_summary}

Generate insights in the following categories:
1. PATTERNS: What themes or patterns are emerging?
2. CONNECTIONS: What ideas or people might benefit from connection?
3. OPPORTUNITIES: What opportunities or next actions are suggested by the data?
4. WARNINGS: Are there forgotten commitments or stale projects?

Return as JSON:
{{
    "patterns": ["pattern1", "pattern2"],
    "connections": ["connection1", "connection2"],
    "opportunities": ["opportunity1", "opportunity2"],
    "warnings": ["warning1", "warning2"]
}}
"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: ollama.chat(
                    model=settings.OLLAMA_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a proactive AI assistant that identifies patterns and opportunities in user data."},
                        {"role": "user", "content": prompt}
                    ],
                    options={"temperature": 0.6}
                )
            )
            
            import json
            content = response['message']['content']
            
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            insights = json.loads(content)
            return insights
            
        except Exception as e:
            logger.error(f"Error generating proactive insights: {e}")
            return {
                "patterns": [],
                "connections": [],
                "opportunities": [],
                "warnings": []
            }
    
    @staticmethod
    async def detect_themes_over_time(notes: List[Dict], 
                                       time_window_days: int = 30) -> List[Dict[str, Any]]:
        """
        Detect evolving themes over time
        """
        try:
            # Group notes by time periods
            now = datetime.now()
            time_groups = {}
            
            for note in notes:
                created_at = datetime.fromisoformat(note.get('created_at', '1970-01-01'))
                days_ago = (now - created_at).days
                
                if days_ago <= time_window_days:
                    period = f"0-{time_window_days} days ago"
                elif days_ago <= time_window_days * 2:
                    period = f"{time_window_days}-{time_window_days*2} days ago"
                else:
                    period = f"Over {time_window_days*2} days ago"
                
                if period not in time_groups:
                    time_groups[period] = []
                time_groups[period].append(note)
            
            # Analyze themes per period
            themes = []
            for period, period_notes in time_groups.items():
                if not period_notes:
                    continue
                
                notes_text = "\n".join([
                    f"{note.get('title', '')}: {note.get('content', '')[:100]}"
                    for note in period_notes[:10]
                ])
                
                prompt = f"""Analyze these notes from {period} and identify the main themes:

{notes_text}

What are the 3-5 main themes or topics? Return as JSON: {{"themes": ["theme1", "theme2", ...]}}"""

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda p=prompt: ollama.chat(
                        model=settings.OLLAMA_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a theme detection assistant."},
                            {"role": "user", "content": p}
                        ],
                        options={"temperature": 0.5}
                    )
                )
                
                import json
                content = response['message']['content']
                
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                period_themes = json.loads(content).get('themes', [])
                themes.append({
                    "period": period,
                    "themes": period_themes,
                    "note_count": len(period_notes)
                })
            
            return themes
            
        except Exception as e:
            logger.error(f"Error detecting themes: {e}")
            return []


creative_muse = CreativeMuse()
