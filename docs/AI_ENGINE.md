# Comprehensive Multi-Agent AI Engine

## Overview

Rumee's AI engine consists of **6 specialized agents** working in parallel, constantly analyzing your data like multiple assistants working behind the scenes.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Agent Orchestrator                      │
│            Coordinates all AI agents                     │
└──────────────────┬──────────────────────────────────────┘
                   │
       ┌───────────┴────────────┐
       │   Shared Memory        │
       │  - Context             │
       │  - Patterns            │
       │  - Connections         │
       │  - Insights            │
       └───────────┬────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌─────▼──┐  ┌───────▼────┐
│Signal  │  │Mind    │  │Context     │
│Sorter  │  │Weaver  │  │Builder     │
└────────┘  └────────┘  └────────────┘
    │              │              │
┌───▼────────┐  ┌─▼──────────┐  ┌▼────────────┐
│Pattern     │  │Insight     │  │Relationship │
│Detector    │  │Generator   │  │Mapper       │
└────────────┘  └────────────┘  └─────────────┘
```

## The 6 AI Agents

### 1. Signal Sorter Agent
**Run Interval:** Every 10 seconds  
**Purpose:** Deep classification and prioritization of incoming data

**What it does:**
- Classifies each note into types: idea, task, meeting_notes, reference, decision, question, reflection
- Extracts specific topics (not generic categories)
- Assigns importance scores (1-10)
- Determines time sensitivity: immediate, soon, later, timeless
- Identifies related knowledge domains
- Marks content as actionable or not
- Extracts key concepts

**Output:**
```json
{
  "content_type": "meeting_notes",
  "topics": ["product roadmap", "Q1 priorities", "AI features"],
  "importance": 8,
  "time_sensitivity": "soon",
  "related_domains": ["product management", "software development"],
  "actionable": true,
  "key_concepts": ["user feedback", "technical debt", "launch timeline"]
}
```

### 2. Mind Weaver Agent
**Run Interval:** Every 30 seconds  
**Purpose:** Discovers hidden connections between pieces of information

**What it does:**
- Compares recent notes with older ones
- Finds notes that share people, topics, or themes
- Uses AI to detect relationship types:
  - `builds_on`: New idea builds on previous thinking
  - `contradicts`: New info conflicts with old
  - `supports`: Reinforces previous ideas
  - `related_to`: Related but not dependent
  - `same_theme`: Part of the same theme
- Assigns connection strength (0.0-1.0)
- Provides reasoning for each connection

**Example Connections:**
```
Note A (Dec 20): "Need to improve onboarding flow"
Note B (Dec 28): "Users dropping off at signup"
→ Connection: builds_on (strength: 0.85)
→ Reason: "New data supports earlier concern about onboarding"
```

### 3. Context Builder Agent
**Run Interval:** Every 20 seconds  
**Purpose:** Maintains real-time understanding of user's current focus

**What it does:**
- Analyzes last 5 notes to understand current focus
- Identifies primary focus area
- Tracks active topics across recent activity
- Monitors active people/collaborators
- Measures recent activity level
- Updates continuously as new data arrives

**Output:**
```json
{
  "primary_focus": "product launch planning",
  "active_topics": ["launch strategy", "marketing", "pricing", "team coordination"],
  "active_people": ["Sarah", "Mike", "Alex"],
  "recent_activity_level": 8,
  "updated_at": "2025-12-31T11:15:00"
}
```

### 4. Pattern Detector Agent
**Run Interval:** Every 60 seconds  
**Purpose:** Identifies patterns and trends over time

**What it does:**
- **Temporal Patterns:**
  - Discovers when you're most productive (peak hours)
  - Identifies most active days of the week
  
- **Topic Evolution:**
  - Tracks how topics change week over week
  - Shows emerging vs declining topics
  - Analyzes last 4 weeks of data
  
- **Collaboration Patterns:**
  - Identifies frequent collaborators
  - Shows who you work with most
  - Tracks collaboration frequency

**Example Output:**
```json
{
  "time_patterns": {
    "peak_hours": [[9, 12], [14, 8], [16, 5]],
    "active_days": [["Monday", 15], ["Wednesday", 12], ["Friday", 10]]
  },
  "topic_evolution": {
    "0": {"AI features": 8, "user research": 5},
    "1": {"product design": 6, "AI features": 4},
    "2": {"market analysis": 7, "competitive research": 3}
  },
  "collaboration_patterns": [
    ["Sarah", 12], ["Mike", 8], ["Alex", 6]
  ]
}
```

### 5. Insight Generator Agent
**Run Interval:** Every 45 seconds  
**Purpose:** Generates proactive insights and suggestions

**What it does:**
- **Unfinished Business Detection:**
  - Finds tasks pending for over 3 days
  - Alerts about stale reminders
  
- **Neglected Contacts:**
  - Identifies people not mentioned in 14+ days
  - Suggests reaching out
  
- **Topic Convergence:**
  - Detects when your ideas are connecting
  - Highlights emerging themes
  
- **Priority-based Alerts:**
  - High: Immediate action needed
  - Medium: Should address soon
  - Low: FYI/informational

**Example Insights:**
```json
[
  {
    "type": "unfinished_business",
    "title": "Unfinished Items Need Attention",
    "description": "5 tasks pending for over 3 days",
    "priority": "high",
    "generated_at": "2025-12-31T11:20:00"
  },
  {
    "type": "neglected_contacts",
    "title": "People You Haven't Connected With",
    "description": "You haven't mentioned Sarah in a while. Consider reaching out.",
    "priority": "medium",
    "generated_at": "2025-12-31T11:20:00"
  },
  {
    "type": "topic_convergence",
    "title": "Your Ideas Are Connecting",
    "description": "I found 15 connections between your notes. Your thinking is converging around key themes.",
    "priority": "low",
    "generated_at": "2025-12-31T11:20:00"
  }
]
```

### 6. Relationship Mapper Agent
**Run Interval:** Every 40 seconds  
**Purpose:** Maps relationships between all entities

**What it does:**
- Builds comprehensive entity graph
- Creates relationships:
  - Person → discusses → Topic
  - Person → collaborates_with → Person
  - Topic → relates_to → Topic
- Tracks source notes for each relationship
- Enables network visualization

**Graph Structure:**
```json
{
  "person:Sarah": [
    {"type": "discusses", "target": "topic:AI features", "source_note": "note_123"},
    {"type": "collaborates_with", "target": "person:Mike", "source_note": "note_124"}
  ],
  "topic:product launch": [
    {"type": "relates_to", "target": "topic:marketing", "source_note": "note_125"}
  ]
}
```

## Shared Memory

All agents read from and write to shared memory, enabling collaboration:

```javascript
shared_memory = {
  'user_context': {
    primary_focus: "current focus area",
    active_topics: [...],
    active_people: [...]
  },
  'recent_patterns': [{
    time_patterns: {...},
    topic_evolution: {...},
    collaboration_patterns: [...]
  }],
  'active_topics': [
    {topic: "AI features", note_id: "123", timestamp: "..."}
  ],
  'entity_graph': {
    "person:Sarah": [relationships...],
    "topic:AI": [relationships...]
  },
  'insights_queue': [
    {type: "...", title: "...", description: "...", priority: "..."}
  ],
  'cross_references': {
    "note_123": [
      {target_id: "note_456", connection_type: "builds_on", strength: 0.85, reason: "..."}
    ]
  }
}
```

## API Endpoints

### Get Comprehensive Insights
```bash
GET /api/ai/insights
```
Returns top 10 insights sorted by priority (high → medium → low).

**Response:**
```json
{
  "insights": [
    {
      "type": "unfinished_business",
      "title": "...",
      "description": "...",
      "priority": "high",
      "generated_at": "..."
    }
  ],
  "status": "success"
}
```

### Get Current Context
```bash
GET /api/ai/context
```
Returns what AI understands about your current focus.

### Get Note Connections
```bash
GET /api/ai/connections/{note_id}
```
Returns all AI-discovered connections for a specific note.

**Response:**
```json
{
  "note_id": "123",
  "connections": [
    {
      "connection_type": "builds_on",
      "strength": 0.85,
      "reason": "...",
      "target_id": "456",
      "target_title": "...",
      "target_preview": "...",
      "target_created": "..."
    }
  ],
  "count": 5,
  "status": "success"
}
```

### Get Detected Patterns
```bash
GET /api/ai/patterns
```
Returns latest pattern analysis from Pattern Detector.

### Get Entity Graph
```bash
GET /api/ai/entity-graph
```
Returns full entity relationship graph for visualization.

**Response:**
```json
{
  "graph": {
    "nodes": [
      {"id": "person:Sarah", "label": "Sarah", "type": "person"},
      {"id": "topic:AI", "label": "AI", "type": "topic"}
    ],
    "edges": [
      {"source": "person:Sarah", "target": "topic:AI", "type": "discusses"}
    ],
    "stats": {
      "total_nodes": 25,
      "total_edges": 48
    }
  },
  "status": "success"
}
```

### Get Brain Status
```bash
GET /api/ai/brain-status
```
Returns status of all agents and shared memory stats.

**Response:**
```json
{
  "status": "active",
  "agents": {
    "signal_sorter": "Classifying and prioritizing data",
    "mind_weaver": "Finding hidden connections",
    "context_builder": "Building current context",
    "pattern_detector": "Detecting patterns and trends",
    "insight_generator": "Generating proactive insights",
    "relationship_mapper": "Mapping entity relationships"
  },
  "memory": {
    "insights_queued": 8,
    "connections_found": 23,
    "active_topics": 12,
    "patterns_detected": 4
  }
}
```

## How the Agents Work Together

### Example Flow: New Note Created

1. **User creates note:** "Met with Sarah about AI product launch. Need to finalize pricing by Jan 15th."

2. **Signal Sorter (10s):**
   - Classifies as: meeting_notes, actionable
   - Topics: AI product, pricing strategy, launch planning
   - Importance: 8/10
   - Time sensitive: soon

3. **Mind Weaver (30s):**
   - Finds older note: "Discussed pricing models in October"
   - Creates connection: builds_on (strength: 0.82)
   - Reason: "New deadline for previous pricing discussion"

4. **Context Builder (20s):**
   - Updates primary_focus: "product launch planning"
   - Adds "Sarah" to active_people
   - Adds topics to active_topics

5. **Pattern Detector (60s):**
   - Notes: Sarah mentioned frequently (collaboration pattern)
   - Topic: "product launch" trending upward

6. **Insight Generator (45s):**
   - Creates insight: "Unfinished Business - Pricing decision needed by Jan 15"
   - Priority: high

7. **Relationship Mapper (40s):**
   - Creates: person:Sarah → discusses → topic:pricing
   - Creates: person:Sarah → discusses → topic:AI product

### Result
The note is now deeply analyzed, connected to related information, and has generated actionable insights — all automatically in the background.

## Performance Characteristics

- **Memory Usage:** Lightweight (shared memory dict)
- **CPU Usage:** Low (agents run at staggered intervals)
- **Scalability:** Handles 1000+ notes efficiently
- **Real-time:** Context updates within 20 seconds
- **Background:** Non-blocking, runs independently

## Configuration

Agents are configured in `backend/services/agent_orchestrator.py`:

```python
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            'signal_sorter': SignalSorterAgent(),      # 10s interval
            'mind_weaver': MindWeaverAgent(),          # 30s interval
            'context_builder': ContextBuilderAgent(),  # 20s interval
            'pattern_detector': PatternDetectorAgent(), # 60s interval
            'insight_generator': InsightGeneratorAgent(), # 45s interval
            'relationship_mapper': RelationshipMapperAgent() # 40s interval
        }
```

To adjust intervals, modify the `get_interval()` method in each agent class.

## Future Enhancements

- **Learning Agent:** Learns user preferences over time
- **Prediction Agent:** Predicts what you'll need next
- **Summarization Agent:** Creates daily/weekly summaries
- **Alert Agent:** Smart notifications based on patterns
- **Integration Agent:** Connects to external tools (calendar, email)
- **Search Agent:** Continuously indexes for instant search

## Monitoring

Check agent status in the UI:
- Dashboard → "Your AI Brain is Working" section
- Shows active connections, insights, patterns
- Real-time stats on agent activity

Or via API:
```bash
curl http://localhost:8000/api/ai/brain-status
```

## Troubleshooting

**Agents not running?**
- Check server logs for "🧠 Multi-agent AI orchestrator started (6 agents active)"

**No insights generated?**
- Agents need data to work with. Create 5+ notes first.
- Wait 1-2 minutes for all agents to complete first cycle.

**AsyncIO warnings?**
- Harmless. Legacy background processor interaction.
- Functionality not affected.

**Slow performance?**
- Check Ollama is running: `ollama list`
- Reduce agent frequency (increase intervals)
- Prune old data if 1000+ notes

---

**The AI engine runs automatically. No configuration needed. Just use Rumee normally and watch the AI work its magic! 🧠✨**
