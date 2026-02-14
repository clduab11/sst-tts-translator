#!/bin/bash
# Quick start script for SST/TTS Translator

set -e

echo "🚀 SST/TTS Translator - Quick Start"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Python version: $python_version"

required_version="3.9"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9 or higher required"
    exit 1
fi
echo "   ✅ Python version OK"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "   ✅ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "   ⚠️  Please edit .env and add your API keys"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Install package in development mode
echo "📦 Installing package in development mode..."
pip install -e . -q
echo "   ✅ Package installed"
echo ""

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Edit .env and add your API keys:"
echo "      - OPENAI_API_KEY (for LLM)"
echo "      - DEEPGRAM_API_KEY (optional, for cloud STT)"
echo ""
echo "   2. Start the server:"
echo "      python -m sst_tts_translator serve"
echo ""
echo "   3. Or use the CLI:"
echo "      python -m sst_tts_translator --help"
echo ""
echo "   4. Access API docs:"
echo "      http://localhost:8000/docs"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Quick start guide"
echo "   - docs/architecture.md - System architecture"
echo "   - docs/api-specs.md - API documentation"
echo "   - docs/usage.md - Usage examples"
echo ""
