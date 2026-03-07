#!/bin/bash
# DataMind Pro — Start Server

source venv/bin/activate 2>/dev/null || true

# Load .env
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""
echo "⚡ Starting DataMind Pro..."
echo "🌐 Open: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

python app.py
