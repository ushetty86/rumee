#!/bin/bash

# Rumee Start Script - Starts both FastAPI backend and Streamlit frontend

echo "🚀 Starting Rumee with Ollama AI..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Warning: Ollama not found. Install with: curl -fsSL https://ollama.com/install.sh | sh"
fi

# Start backend in background
echo "🔧 Starting FastAPI backend on port 8000..."
python backend/test_server.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend started successfully
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🎨 Starting Streamlit UI on port 8501..."
echo ""
echo "✅ Access the app at: http://localhost:8501"
echo "📚 API docs at: http://localhost:8000/docs"
echo ""
streamlit run app.py --server.headless=true

# When Streamlit exits, kill backend
echo "🛑 Stopping backend..."
kill $BACKEND_PID 2>/dev/null
echo "✅ Rumee stopped"
