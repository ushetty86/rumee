# Rumee - Project Structure

This document provides an overview of the cleaned-up repository structure.

## 📁 Root Directory

```
rumee/
├── .git/                       # Git repository
├── .github/                    # GitHub configuration
├── .gitignore                  # Git ignore rules
│
├── README.md                   # Main documentation (consolidated)
├── QUICKSTART.md              # 5-minute setup guide
├── CONTRIBUTING.md            # How to contribute
├── DEPLOYMENT.md              # Production deployment guide
├── DEVELOPMENT.md             # Development guidelines
├── ROADMAP.md                 # Future features and plans
│
├── app.py                     # Streamlit frontend (7 pages)
├── requirements.txt           # Frontend Python dependencies
│
├── setup.sh                   # One-command setup script
├── start.sh                   # Start both servers
│
├── venv/                      # Python virtual environment
│
├── backend/                   # FastAPI backend (see below)
└── docs/                      # Additional documentation
```

## 🔧 Backend Structure

```
backend/
├── test_server.py             # Main FastAPI server with Ollama
├── main.py                    # Alternative entry point
├── requirements.txt           # Backend Python dependencies
├── README_OLLAMA.md          # Ollama integration guide
├── .env                       # Environment configuration
│
├── config/
│   ├── settings.py           # App configuration
│   ├── settings_test.py      # Test configuration
│   └── database.py           # MongoDB setup (optional)
│
├── models/
│   ├── user.py               # User model
│   ├── note.py               # Note model
│   ├── person.py             # Person model
│   ├── meeting.py            # Meeting model
│   ├── reminder.py           # Reminder model
│   └── relationship.py       # Relationship model
│
├── routes/
│   ├── auth.py               # Authentication endpoints
│   ├── notes.py              # Note CRUD operations
│   ├── people.py             # People management
│   ├── meetings.py           # Meeting scheduling
│   ├── reminders.py          # Reminder management
│   ├── summary.py            # AI summaries
│   └── knowledge_graph.py    # Graph queries
│
└── services/
    ├── ai_service.py         # Ollama AI integration
    ├── background_processor.py # Automatic entity extraction
    ├── neo4j_service.py      # Neo4j graph database
    ├── knowledge_graph_service.py # Graph generation
    └── data_linking_service.py    # Auto-linking logic
```

## 📄 Documentation

```
docs/
├── API.md                     # Complete API reference
├── ARCHITECTURE.md            # System design and patterns
└── MOBILE.md                  # Mobile app integration guide
```

## 🎯 Key Files

### Startup Scripts

- **`setup.sh`**: Creates venv, installs dependencies, creates .env
- **`start.sh`**: Starts both FastAPI and Streamlit servers

### Frontend

- **`app.py`**: Complete Streamlit UI with 7 pages:
  - Dashboard: Overview and stats
  - Notes: Create and view notes with AI processing
  - People: Auto-populated contacts
  - Meetings: Schedule and track meetings
  - Reminders: Task management
  - Knowledge Graph: Visual connections
  - Ask AI: Natural language queries

### Backend Core

- **`test_server.py`**: Main API server
  - FastAPI with Ollama integration
  - In-memory storage (test mode)
  - Background AI processing
  - Neo4j integration with fallback

- **`services/background_processor.py`**: The AI brain
  - Automatic entity extraction
  - Auto-creates people and reminders
  - Generates embeddings
  - Populates knowledge graph

- **`services/ai_service.py`**: Ollama interface
  - Text generation
  - Entity extraction
  - Embedding generation
  - Relationship analysis

- **`services/neo4j_service.py`**: Graph database
  - Node creation
  - Relationship management
  - Graph queries
  - Graceful fallback

## 🗑️ What Was Removed

The following obsolete files from the Node.js/TypeScript version were removed:

- `frontend/` - React/TypeScript frontend (replaced by app.py)
- `shared/` - TypeScript type definitions (not needed in Python)
- `package.json` - Root Node.js dependencies
- `backend/src/` - TypeScript backend code
- `backend/package.json` - Node.js backend dependencies
- `backend/tsconfig.json` - TypeScript configuration
- `README_PYTHON.md` - Merged into README.md
- `PYTHON_QUICKSTART.md` - Replaced by QUICKSTART.md
- `SETUP_CHECKLIST.md` - Outdated checklist
- `START_HERE.txt` - Redundant
- `PROJECT_COMPLETE.sh` - Obsolete script
- `PROJECT_FILES.md` - Replaced by this file
- `test_setup.py` - Obsolete test

## 🏗️ Technology Stack

### Current Active Stack

- **Language**: Python 3.9+
- **Backend**: FastAPI 0.115.0
- **Frontend**: Streamlit 1.41.0
- **AI**: Ollama (local)
  - llama3.2:latest (chat, analysis)
  - embeddinggemma:latest (embeddings)
- **Graph DB**: Neo4j 5.28.2 (optional)
- **Storage**: In-memory / MongoDB (optional)

### Dependencies

See [requirements.txt](requirements.txt) and [backend/requirements.txt](backend/requirements.txt)

## 📝 Notes

- The app works **without** Neo4j or MongoDB (uses in-memory storage)
- All AI runs **locally** via Ollama - no API keys needed
- Frontend and backend are **pure Python** - no Node.js required
- Background processing is **fully automatic** - just create notes

## 🚀 Quick Commands

```bash
# Setup (first time only)
./setup.sh

# Start app
./start.sh

# Start backend only
source venv/bin/activate
python backend/test_server.py

# Start frontend only
source venv/bin/activate
streamlit run app.py
```

## 🔗 URLs

- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Neo4j Browser: http://localhost:7474 (if installed)

---

For more details, see [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md).
