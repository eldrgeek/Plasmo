#!/bin/bash
# CollaborAItion Dashboard Startup Script

echo "🚀 Starting CollaborAItion Dashboard..."
echo "📋 Installing dependencies..."

# Install Python dependencies
pip install -r requirements.txt

echo "🔧 Checking configuration..."
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found!"
    exit 1
fi

echo "📁 Ensuring data directory exists..."
mkdir -p data

echo "🌐 Starting FastHTML server with auto-reload..."
python dashboard.py