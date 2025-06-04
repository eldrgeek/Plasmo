#!/bin/bash

echo "🚀 Setting up FastMCP Server for Cursor Integration"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete! To start the MCP server:"
echo "   python3 mcp_server.py"
echo "   or use: ./start_mcp.sh"
echo ""
echo "📝 Remember to configure Cursor settings:"
echo "   1. Open Cursor settings (Cmd+,)"
echo "   2. Search for 'mcp'"
echo "   3. Add the server configuration as shown in mcp_server.py"
echo "   4. Restart Cursor" 