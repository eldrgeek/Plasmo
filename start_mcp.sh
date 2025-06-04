#!/bin/bash

echo "🚀 Starting FastMCP Server for Cursor..."
echo "========================================"

# Check if the server file exists
if [ ! -f "mcp_server.py" ]; then
    echo "❌ mcp_server.py not found in current directory"
    echo "Please run this script from the directory containing mcp_server.py"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed. Running setup first..."
    ./setup_mcp.sh
    if [ $? -ne 0 ]; then
        echo "❌ Setup failed. Please install dependencies manually:"
        echo "   pip3 install fastmcp"
        exit 1
    fi
fi

echo "✅ Dependencies verified"
echo "🌐 Starting server on http://127.0.0.1:8000"
echo ""
echo "📝 Make sure to configure Cursor with the MCP server settings"
echo "   (see mcp_server.py for configuration details)"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Start the server
python3 mcp_server.py 