#!/bin/bash

# Change to the Plasmo project directory
cd "$(dirname "$0")"

# Activate the virtual environment (handle nested venv)
PLASMO_VENV_PATH="$(pwd)/.venv"

if [ -d ".venv" ]; then
    # Only activate if not already in this specific venv
    if [ "$VIRTUAL_ENV" != "$PLASMO_VENV_PATH" ]; then
        # Deactivate any existing virtual environment first
        if [ -n "$VIRTUAL_ENV" ]; then
            deactivate 2>/dev/null || true
        fi
        source .venv/bin/activate
        echo "🐍 Activated virtual environment"
    fi
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "📦 Installing requirements..."
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed"
fi

# Run the service manager with all arguments passed through
python service_manager.py "$@" 