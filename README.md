# Rumee - AI-Powered Personal Assistant 🧠

**Intelligent note-taking and personal knowledge management with local AI**

Rumee is your AI-powered assistant that automatically organizes notes, tracks people and meetings, creates reminders, and discovers connections across all your data - running completely locally with Ollama.

## ✨ Key Features

### 🤖 **Intelligent Background Processing**
- **Automatic entity extraction** from notes (people, topics, organizations, locations, tasks)
- **Auto-creates people entries** when you mention someone
- **Auto-creates reminders** when you write about tasks
- **Zero manual effort** - just write naturally

### 🧠 **Knowledge Graph**
- **Visual mind map** of all your data connections
- **Neo4j graph database** for relationship tracking
- **Discover hidden patterns** across notes, people, and meetings
- **Brain-like correlation** of information

### 💬 **Ask AI**
- **Natural language queries** over all your data
- "Who have I met about project X?"
- "What tasks are pending?"
- "Summarize my week"

### 📝 **Smart Notes**
- Automatic topic extraction
- Semantic search and similarity
- Linked to people, meetings, and tasks
- AI-powered insights

### 👥 **People & Contacts**
- Auto-populated from note mentions
- Track interactions and meetings
- Relationship context and history

### 📅 **Meetings & Reminders**
- Schedule and document meetings
- Task tracking and follow-ups
- Priority management

### 📊 **Insights**
- Daily and weekly summaries
- Activity analytics
- Connection discovery

## 🏗️ Tech Stack

### Core Technologies
- **Backend**: FastAPI (Python) on port 8000
- **Frontend**: Streamlit (Python) on port 8501
- **AI Engine**: Ollama (100% local, privacy-first)
  - `llama3.2:latest` for chat and analysis
  - `embeddinggemma:latest` for semantic embeddings
- **Graph Database**: Neo4j (optional, graceful fallback)
- **Storage**: In-memory (test mode) or MongoDB (optional)

### Why This Stack?
- ✅ **No API keys required** - completely local AI
- ✅ **No cloud costs** - runs on your machine
- ✅ **Complete privacy** - your data stays local
- ✅ **Fast development** - pure Python, no separate frontend
- ✅ **Background intelligence** - AI works while you type

## 🚀 Quick Start

### Prerequisites

```bash
# 1. Install Python 3.9+
python3 --version

# 2. Install Ollama (macOS)
curl -fsSL https://ollama.com/install.sh | sh

# 3. Pull AI models
ollama pull llama3.2:latest
ollama pull embeddinggemma:latest

# 4. (Optional) Install Neo4j
brew install --cask neo4j
# Or use Docker: docker run -p 7474:7474 -p 7687:7687 neo4j
```

### Installation

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/rumee.git
cd rumee
chmod +x setup.sh
./setup.sh

# 2. Configure (optional - works with defaults)
# Edit backend/.env if you want to change ports or add MongoDB

# 3. Start the app
chmod +x start.sh
./start.sh
```

**Access the app:**
- 🌐 **UI**: http://localhost:8501
- 🔧 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

## 📖 Usage

### 1. Create Your First Note
```
Met with Sarah Johnson about the Q4 marketing campaign. 
Need to send her the budget proposal by Friday.
Also discussed partnership with Acme Corp.
```

**What happens automatically:**
- ✅ Creates person entry for "Sarah Johnson"
- ✅ Extracts topic "Q4 marketing campaign"
- ✅ Identifies organization "Acme Corp"
- ✅ Creates reminder "Send budget proposal to Sarah by Friday"
- ✅ Adds everything to knowledge graph
- ✅ Generates embeddings for semantic search

### 2. Ask AI Questions
```
"What did I discuss with Sarah?"
"What tasks are due this week?"
"Who have I met about marketing?"
```

The AI searches across all your notes, people, and reminders using semantic understanding.

### 3. Explore Knowledge Graph
See visual connections between:
- Notes ↔ People mentioned
- Notes ↔ Topics discussed
- Notes ↔ Organizations involved
- Notes ↔ Locations mentioned

## 🛠️ Manual Start

```bash
# Terminal 1 - Backend API
source venv/bin/activate
python backend/test_server.py

# Terminal 2 - Streamlit UI
source venv/bin/activate
streamlit run app.py
```

## 📂 Project Structure

```
rumee/
├── app.py                          # Streamlit frontend (7 pages)
├── backend/
│   ├── test_server.py             # FastAPI server with Ollama
│   ├── config/
│   │   ├── settings.py            # Configuration
│   │   └── database.py            # MongoDB setup (optional)
│   ├── services/
│   │   ├── ai_service.py          # Ollama integration
│   │   ├── background_processor.py # Automatic AI processing
│   │   ├── neo4j_service.py       # Graph database
│   │   ├── knowledge_graph_service.py
│   │   └── data_linking_service.py
│   ├── models/                    # Data models
│   └── routes/                    # API endpoints
├── requirements.txt               # Python dependencies
├── setup.sh                       # One-command setup
└── start.sh                       # Start both servers
```

## 🔧 Configuration

### Environment Variables (`backend/.env`)

```bash
# AI Models (using Ollama - local)
OLLAMA_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=embeddinggemma:latest
OLLAMA_BASE_URL=http://localhost:11434

# Neo4j (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123

# MongoDB (optional - for persistence)
MONGODB_URI=mongodb://localhost:27017/rumee

# Server Config
PORT=8000
JWT_SECRET=your-secret-key-here
```

## 🎯 How It Works

### Background Processing Pipeline

1. **User creates note** → Sent to FastAPI backend
2. **Queued for processing** → Async background processor
3. **AI extracts entities** → Ollama analyzes content
4. **Auto-creates related data**:
   - People entries from names
   - Reminders from tasks
   - Topics, organizations, locations
5. **Generates embeddings** → For semantic search
6. **Updates knowledge graph** → Neo4j or in-memory
7. **Returns to user** → With AI insights

### Graceful Fallbacks

- **No Neo4j?** → Uses in-memory graph
- **No MongoDB?** → Uses in-memory dictionaries
- **Ollama offline?** → Graceful error messages

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Check Ollama status
ollama list

# Restart Ollama
brew services restart ollama
```

### Neo4j Connection Issues
```bash
# The app works without Neo4j (uses fallback)
# To start Neo4j:
neo4j start
# Or use Docker:
docker run -p 7474:7474 -p 7687:7687 neo4j
```

### Port Conflicts
```bash
# Change backend port in backend/.env:
PORT=8001

# Change Streamlit port:
streamlit run app.py --server.port 8502
```

### AsyncIO Warnings
These are harmless warnings from the background processor. The app works perfectly despite them.

## 🚀 What Makes This Special?

1. **True Intelligence**: Not just storage - actual AI that understands and connects your information
2. **Zero Effort**: Write naturally, AI does the organization
3. **Privacy First**: All AI runs locally on your machine
4. **No Costs**: No API fees, no subscriptions
5. **Real Knowledge Graph**: See how everything connects like your brain does
6. **Background Processing**: AI works while you focus on writing

## 📚 Additional Documentation

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - System design and patterns
- [API.md](docs/API.md) - Complete API reference
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [DEPLOYMENT.md](DEPLOYMENT.md) - Production deployment guide
- [ROADMAP.md](ROADMAP.md) - Future features and plans

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🎉 Getting Help

- 📧 Issues: [GitHub Issues](https://github.com/yourusername/rumee/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/rumee/discussions)

---

**Built with ❤️ using Python, Ollama, and FastAPI**
