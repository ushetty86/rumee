# Quick Start - Get Running in 5 Minutes! 🚀

## Prerequisites

- Python 3.9 or higher
- macOS, Linux, or Windows with WSL

## Step 1: Install Ollama

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Or visit https://ollama.com for other platforms
```

## Step 2: Pull AI Models

```bash
ollama pull llama3.2:latest
ollama pull embeddinggemma:latest
```

## Step 3: Setup Rumee

```bash
# Clone the repo (or if you already have it)
cd rumee

# Run setup (creates venv, installs dependencies)
chmod +x setup.sh
./setup.sh
```

## Step 4: Start the App

```bash
chmod +x start.sh
./start.sh
```

## Step 5: Open in Browser

- **UI**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## First Steps

1. **Create a note** in the Notes page:
   ```
   Met with John Smith about the new project. 
   Need to follow up on budget approval by next Friday.
   ```

2. **Watch the magic happen**:
   - Person "John Smith" automatically created
   - Reminder automatically created for budget follow-up
   - Topics extracted and linked

3. **Ask AI questions** in the "Ask AI" page:
   ```
   "What tasks do I need to complete?"
   "Who have I met recently?"
   "What projects am I working on?"
   ```

4. **Explore the Knowledge Graph** to see connections between:
   - Your notes
   - People you've mentioned
   - Topics you've discussed

## Troubleshooting

### "Connection refused to localhost:11434"
→ Ollama isn't running. Start it with: `ollama serve`

### Port already in use
```bash
# Change backend port
# Edit backend/.env and set: PORT=8001

# Change frontend port
streamlit run app.py --server.port 8502
```

### Need to stop the app?
Press `Ctrl+C` in the terminal - it will stop both servers.

## What's Next?

- Read the full [README.md](README.md) for detailed features
- Check [ROADMAP.md](ROADMAP.md) for upcoming features
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

That's it! You now have an AI-powered personal assistant running locally. 🎉
