#!/bin/bash
# ─────────────────────────────────────────────────
# DataMind Pro — Setup & Run Script
# Run this ONCE to set up, then use ./run.sh to start
# ─────────────────────────────────────────────────

set -e

echo ""
echo "⚡ DataMind Pro — Setup"
echo "══════════════════════════════════"

# Check Python
python3 --version || { echo "❌ Python 3 not found. Install Python 3.9+"; exit 1; }

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Create .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env file. Add your ANTHROPIC_API_KEY to .env"
fi

# Create directories
mkdir -p data/uploads data/samples reports/output

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Add your API key: edit .env and set ANTHROPIC_API_KEY"
echo "  2. Run the server: ./run.sh"
echo "  3. Open browser: http://localhost:5000"
echo ""
