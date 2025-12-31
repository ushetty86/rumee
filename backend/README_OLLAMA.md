# Rumee with Ollama - Local AI Integration

## Overview

Rumee now uses **Ollama** for local AI processing instead of OpenAI. This means:
- ✅ No API keys needed
- ✅ No usage costs
- ✅ Complete privacy - all processing happens locally
- ✅ Faster response times (no network latency)
- ✅ Works offline

## Features

### Automatic Background Processing

When you create notes or send messages, the AI automatically:
1. **Extracts entities** - People, dates, topics, organizations, locations
2. **Generates embeddings** - For semantic search and similarity matching
3. **Infers intent** - Understands what you want to do
4. **Organizes data** - Links related information automatically

### Models Used

- **llama3.2:latest** - For chat, entity extraction, and intent inference
- **embeddinggemma:latest** - For generating embeddings for semantic search

## Setup

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Or download from https://ollama.ai
```

### 2. Pull the Required Models

```bash
ollama pull llama3.2:latest
ollama pull embeddinggemma:latest
```

### 3. Start Ollama Service

```bash
ollama serve
```

(Ollama typically runs on http://localhost:11434 by default)

### 4. Start Rumee

```bash
cd /Users/umeshshetty/REPO/rumee
source venv/bin/activate
python backend/test_server.py
```

## API Endpoints

### Standard Endpoints
All existing endpoints work the same:
- `POST /api/notes` - Create a note (now with AI processing)
- `GET /api/notes` - Get all notes
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login

### New Endpoint
- `POST /api/infer` - Infer user intent from free-form message

Example:
```bash
curl -X POST http://localhost:8000/api/infer \
  -H "Content-Type: application/json" \
  -d '{"message": "Met with John today about the project"}'
```

Response:
```json
{
  "message": "Met with John today about the project",
  "intent": {
    "action": "create_note",
    "entities": {
      "person": "John",
      "topic": "project"
    },
    "confidence": 0.9
  },
  "status": "processed"
}
```

## How It Works

### 1. Note Creation with AI Processing

When you create a note:
```python
# User creates note
POST /api/notes
{
  "title": "Meeting with John",
  "content": "Discussed the new mobile app project"
}

# Backend automatically:
# 1. Stores the note
# 2. Queues it for AI processing
# 3. Returns immediately

# In background:
# - Extracts entities: ["John"], ["mobile app project"]
# - Generates embeddings for similarity search
# - Links to related notes/people
# - Updates note with AI-extracted data
```

### 2. Intent Inference

Send natural language messages:
```python
POST /api/infer
{
  "message": "Remind me to call Sarah tomorrow at 3pm"
}

# AI infers:
{
  "action": "set_reminder",
  "entities": {
    "person": "Sarah",
    "task": "call",
    "when": "tomorrow at 3pm"
  }
}
```

### 3. Semantic Search

Notes with embeddings can be searched semantically:
```python
# Find notes similar to a query
POST /api/notes/search
{
  "query": "mobile development"
}

# Returns notes even if they don't contain exact words
# Matches "app project", "iOS work", etc.
```

## Configuration

Edit `/backend/.env`:
```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=embeddinggemma:latest
```

## Performance

- **Embedding generation**: ~100-200ms per note
- **Entity extraction**: ~500ms-1s depending on text length
- **Intent inference**: ~300-800ms

All processing happens in background, so API responses are instant.

## Troubleshooting

### Ollama not running
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Model not found
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2:latest
ollama pull embeddinggemma:latest
```

### Slow processing
- First run downloads models (~4GB for llama3.2, ~275MB for embeddinggemma)
- Subsequent runs are fast
- Consider using GPU if available (Ollama auto-detects)

## Advantages over OpenAI

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| Cost | Free | $0.01-0.10 per 1K tokens |
| Privacy | Local | Cloud |
| Latency | 100-500ms | 500-2000ms |
| Internet | Not required | Required |
| Setup | Install locally | API key |
| Models | llama3.2, gemma | GPT-3.5, GPT-4 |

## Next Steps

1. Test note creation and see AI extraction
2. Try the `/api/infer` endpoint with natural messages
3. Create multiple notes and explore semantic search
4. View the knowledge graph to see automatic linking
