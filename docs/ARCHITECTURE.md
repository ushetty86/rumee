# ARCHITECTURE & IMPLEMENTATION GUIDE

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - Note Editor, People Directory, Meeting Scheduler          │
│  - Daily/Weekly Summary Views, Reminder Dashboard            │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS/REST
┌────────────────▼────────────────────────────────────────────┐
│                    API Gateway (Express)                     │
│  - Route Management, Authentication, Error Handling         │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┼────────────┬──────────────┬────────────┐
    │            │            │              │            │
┌───▼───┐    ┌──▼──┐    ┌────▼────┐    ┌──▼────┐   ┌───▼──┐
│Notes  │    │People│   │ Meetings│    │Reminders  │  │Users │
│Service│    │Service   │ Service │    │Service    │  │Service
└───┬───┘    └──┬──┘    └────┬────┘    └──┬────┘   └───┬──┘
    │           │            │              │           │
    └───────────┼────────────┼──────────────┼───────────┘
                │
    ┌───────────▼────────────────────────┐
    │   AI Service                       │
    │ - Entity Extraction                │
    │ - Embeddings Generation            │
    │ - Summary Generation               │
    │ - Action Item Extraction           │
    └───────────┬────────────────────────┘
                │
    ┌───────────▼────────────────────────┐
    │   Data Linking Service             │
    │ - Semantic Similarity              │
    │ - Entity Linking                   │
    │ - Cross-Reference Management       │
    └────────────────────────────────────┘
                │
    ┌───────────▼────────────────────────┐
    │        Database Layer              │
    │ - MongoDB (Main storage)           │
    │ - Vector Store (Embeddings)        │
    └────────────────────────────────────┘
```

## Core Services Deep Dive

### 1. AIService
**Purpose**: Interface with OpenAI for all AI-powered features

**Key Methods**:
- `generateEmbeddings(text)`: Creates vector representations for semantic search
- `extractEntities(text)`: Identifies people, dates, topics, locations, organizations
- `generateDailySummary(content)`: Creates concise summaries of daily activity
- `findConnections(source, targets)`: Identifies semantic relationships
- `generateActionItems(notes)`: Extracts tasks from meeting notes

**Example Flow**:
```
User creates note
    ↓
Extract entities (people, topics)
    ↓
Generate embeddings for semantic search
    ↓
Find related notes and people
    ↓
Store with links
```

### 2. DataLinkingService
**Purpose**: Automatically connect related information

**Key Methods**:
- `linkNoteToEntities()`: Links notes to mentioned people and similar notes
- `linkPersonToRelevantData()`: Finds all notes/meetings mentioning a person
- `linkMeetingToData()`: Connects meetings to related notes and extracts actions
- `createRemindersFromActionItems()`: Auto-generates reminders from meetings

**Linking Algorithm**:
```
1. Extract entities from new content
2. Direct matching: Find exact name/date matches
3. Semantic matching: Use embeddings (score > 0.6)
4. Bidirectional linking: Create links in both directions
5. Notification: Alert user of new connections
```

### 3. SummaryService
**Purpose**: Generate periodic summaries of user activity

**Key Methods**:
- `generateDailySummary(userId, date)`: Compiles notes, meetings, tasks for a day
- `generateWeeklySummary(userId)`: Creates weekly insights

**Summary Components**:
- Key topics from notes
- Meeting summaries with attendees
- Completed and pending action items
- Important dates and follow-ups

## Data Models

### Note Schema
```typescript
{
  userId: ObjectId,           // Reference to user
  title: String,              // Note title
  content: String,            // Full content
  tags: [String],            // User-assigned tags
  linkedEntities: [ObjectId],// Links to people/notes
  embeddings: [Number],      // Vector representation
  createdAt: Date,
  updatedAt: Date
}
```

**Indexes**:
- `{ userId: 1, createdAt: -1 }` - User's recent notes
- `{ tags: 1 }` - Tag-based filtering

### Person Schema
```typescript
{
  userId: ObjectId,
  name: String,
  email: String,
  phone: String,
  company: String,
  notes: String,             // Personal notes about them
  tags: [String],
  linkedNotes: [ObjectId],   // Notes mentioning them
  meetings: [ObjectId],      // Meetings they attended
  reminders: [ObjectId],     // Reminders to follow up
  createdAt: Date,
  updatedAt: Date
}
```

### Meeting Schema
```typescript
{
  userId: ObjectId,
  title: String,
  description: String,
  attendees: [ObjectId],     // References to Person docs
  date: Date,
  duration: Number,          // Minutes
  location: String,
  notes: String,
  actionItems: [String],     // AI-extracted tasks
  linkedNotes: [ObjectId],
  createdAt: Date,
  updatedAt: Date
}
```

### Reminder Schema
```typescript
{
  userId: ObjectId,
  title: String,
  description: String,
  dueDate: Date,
  type: 'task' | 'followup' | 'meeting_prep' | 'custom',
  priority: 'low' | 'medium' | 'high',
  linkedEntity: ObjectId,    // Note/Person/Meeting
  linkedEntityType: String,
  completed: Boolean,
  createdAt: Date,
  updatedAt: Date
}
```

## API Flow Examples

### Creating a Note with Auto-Linking

```
POST /api/notes
{
  "title": "Lunch with John from Acme",
  "content": "Discussed Q1 goals and roadmap. John agreed to send proposal by Friday.",
  "tags": ["meeting", "acme"]
}

Server Flow:
1. Create note in DB
2. Call AIService.extractEntities()
   → { people: ["John"], organizations: ["Acme"], dates: ["Friday"] }
3. Call AIService.generateEmbeddings()
   → Numeric vector [0.2, 0.5, -0.1, ...]
4. Find matching Person doc for "John"
5. Link note to John's record
6. Find similar notes using embeddings
7. Link to matching notes
8. Call DataLinkingService.createRemindersFromActionItems()
   → Create reminder: "Get proposal from John - Due Friday"
9. Return note with all links

Response:
{
  "_id": "...",
  "title": "Lunch with John from Acme",
  "linkedEntities": ["personId_john", "noteId_acme_discussion"],
  "linkedPeople": ["John (john@acme.com)"],
  "autoGeneratedReminder": {
    "title": "Get proposal from John",
    "dueDate": "2024-01-12T09:00:00Z"
  }
}
```

### Getting Daily Summary

```
GET /api/summaries/daily?date=2024-01-10

Server Flow:
1. Fetch all notes for 2024-01-10
   → 5 notes found
2. Fetch all meetings for 2024-01-10
   → 3 meetings found
3. Fetch all reminders due on 2024-01-10
   → 4 reminders found (2 completed)
4. Compile content:
   "Today's activities:
    - Client call with Acme
    - Follow-up on proposal
    - Team standup
    
    Action items:
    - Send report (pending)
    - Review budget (pending)
    - Schedule follow-up (pending)"
5. Call AIService.generateDailySummary()
6. Return formatted summary

Response:
{
  "date": "2024-01-10",
  "summary": "Productive day with 3 meetings and 5 notes. 
             Key actions: respond to Acme proposal, review budget, 
             and schedule follow-up with John. 2 of 4 action items completed.",
  "stats": {
    "notesCreated": 5,
    "meetingsAttended": 3,
    "remindersCompleted": 2,
    "remindersRemaining": 2
  },
  "keyTopics": ["Acme", "proposal", "budget"],
  "generatedAt": "2024-01-10T20:00:00Z"
}
```

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Database connection and models
- [ ] Express server with basic routes
- [ ] JWT authentication
- [ ] Error handling middleware
- [ ] Logging system

### Phase 2: AI Integration
- [ ] OpenAI API setup
- [ ] Embedding generation
- [ ] Entity extraction
- [ ] Semantic similarity calculation
- [ ] Summary generation

### Phase 3: Data Linking
- [ ] Note-to-entity linking
- [ ] Person-to-content linking
- [ ] Meeting-to-note linking
- [ ] Automatic reminder creation
- [ ] Bidirectional link management

### Phase 4: API Endpoints
- [ ] Note CRUD endpoints
- [ ] Person CRUD endpoints
- [ ] Meeting CRUD endpoints
- [ ] Reminder CRUD endpoints
- [ ] Summary endpoints

### Phase 5: Frontend Components
- [ ] Note editor with auto-save
- [ ] People directory
- [ ] Meeting scheduler
- [ ] Reminder dashboard
- [ ] Summary viewer
- [ ] Data relationship visualizer

### Phase 6: Enhancements
- [ ] Real-time notifications
- [ ] Search with filters
- [ ] Export capabilities
- [ ] Calendar integration
- [ ] Mobile app
- [ ] Voice input

## Performance Considerations

### Database Optimization
- Use indexes on frequently queried fields
- Implement pagination for large result sets
- Cache frequently accessed summaries (refresh daily)

### AI Service Optimization
- Batch entity extraction requests
- Cache embeddings for recent content
- Limit summary generation to recent data

### Frontend Optimization
- Lazy load components
- Implement virtual scrolling for large lists
- Cache API responses with React Query
- Debounce search queries

## Security Considerations

- Always validate user input
- Sanitize database queries
- Use environment variables for secrets
- Implement rate limiting
- Add CORS restrictions
- Validate JWT tokens on every request
- Hash sensitive data in logs

## Next Steps

1. Complete Phase 1 setup
2. Test database models
3. Implement basic CRUD endpoints
4. Add OpenAI integration
5. Build data linking service
6. Create frontend UI
7. Add advanced features
