#!/bin/bash

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Load environment variables
if [ -f environment.env ]; then
    source environment.env
    print_status "Loaded environment configuration"
else
    print_error "environment.env file not found"
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate
print_status "Activated Python virtual environment"

# Install/upgrade dependencies
print_status "Installing/upgrading dependencies..."
pip install -r requirements.txt

# Check if cloudflared is installed and running
if ! command -v cloudflared &> /dev/null; then
    print_error "cloudflared is not installed. Please run setup_cloudflare_tunnel.sh first"
    exit 1
fi

# Start secure MCP server
print_status "Starting secure MCP server..."
python3 mcp_server_secure.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 2

# Check if MCP server is running
if ps -p $MCP_PID > /dev/null; then
    print_success "Secure MCP server started successfully (PID: $MCP_PID)"
    echo $MCP_PID > .mcp_secure.pid
else
    print_error "Failed to start secure MCP server"
    exit 1
fi

# Start Cloudflare tunnel
print_status "Starting Cloudflare tunnel..."
if [ -f ~/.cloudflared/config.yml ]; then
    cloudflared tunnel run plasmo-mcp-server &
    TUNNEL_PID=$!
    echo $TUNNEL_PID > .tunnel.pid
    print_success "Cloudflare tunnel started successfully"
else
    print_error "Cloudflare tunnel configuration not found. Please run setup_cloudflare_tunnel.sh first"
    exit 1
fi

print_success "🚀 Secure MCP server and Cloudflare tunnel are running!"
print_status "To stop the services, run: ./stop_secure_mcp.sh"

# Keep script running to maintain tunnel
wait 