#!/bin/bash

# Rumee Setup Script - Installs dependencies and configures environment

echo "🚀 Setting up Rumee with Ollama AI..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "📚 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "⚙️  Creating .env file..."
    if [ -f backend/.env.example ]; then
        cp backend/.env.example backend/.env
    else
        # Create basic .env if example doesn't exist
        cat > backend/.env << 'EOF'
# AI Models (using Ollama - local)
OLLAMA_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=embeddinggemma:latest
OLLAMA_BASE_URL=http://localhost:11434

# Neo4j (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123

# Server Config
PORT=8000
JWT_SECRET=your-secret-key-change-this

# MongoDB (optional - for persistence)
# MONGODB_URI=mongodb://localhost:27017/rumee
EOF
    fi
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "2. Pull AI models: ollama pull llama3.2:latest && ollama pull embeddinggemma:latest"
echo "3. (Optional) Install Neo4j: brew install --cask neo4j"
echo "4. Run ./start.sh to start the application"
echo ""
echo "The app will work with just Ollama - Neo4j and MongoDB are optional!"
echo ""
