#!/bin/bash

echo "🚀 Starting FastMCP Server in STDIO Mode..."
echo "============================================"

# Check if the server file exists
if [ ! -f "mcp_server.py" ]; then
    echo "❌ mcp_server.py not found in current directory"
    echo "Please run this script from the directory containing mcp_server.py"
    exit 1
fi

# Check if dependencies are installed
python3 -c "import fastmcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Dependencies not installed. Please install first:"
    echo "   pip3 install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies verified"
echo "📡 Starting MCP server in STDIO mode..."
echo ""
echo "📝 This mode is perfect for:"
echo "   • Claude Desktop integration"
echo "   • Local MCP client testing"
echo "   • Command-line tools that manage server processes"
echo ""
echo "🔧 To use with Claude Desktop, add this configuration:"
echo "{"
echo "  \"mcpServers\": {"
echo "    \"cursor-dev-assistant\": {"
echo "      \"command\": \"python\","
echo "      \"args\": [\"$(pwd)/mcp_server.py\", \"--stdio\"]"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "🎯 Starting server..."

# Start the server in STDIO mode
python3 mcp_server.py --stdio 