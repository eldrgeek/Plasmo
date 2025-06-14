#!/bin/bash

echo "🌩️ Cloudflare Tunnel Setup for Plasmo MCP Server"
echo "=============================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
TUNNEL_NAME="plasmo-mcp-server"
MCP_PORT=8000
SOCKETIO_PORT=3001
CONFIG_FILE="$HOME/.cloudflared/config.yml"

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

# Check if cloudflared is installed
check_cloudflared() {
    print_status "Checking if cloudflared is installed..."
    if ! command -v cloudflared &> /dev/null; then
        print_warning "cloudflared not found. Installing..."
        
        # Detect OS and install accordingly
        if [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                brew install cloudflared
            else
                print_error "Homebrew not found. Please install homebrew first or download cloudflared manually"
                exit 1
            fi
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # For Ubuntu/Debian
            if command -v apt-get &> /dev/null; then
                curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
                sudo dpkg -i cloudflared.deb
                rm cloudflared.deb
            else
                print_error "Please install cloudflared manually for your Linux distribution"
                exit 1
            fi
        else
            print_error "Unsupported OS. Please install cloudflared manually"
            exit 1
        fi
    else
        print_success "cloudflared is already installed"
    fi
}

# Login to Cloudflare
login_cloudflare() {
    print_status "Checking Cloudflare authentication..."
    
    # Check if already logged in
    if cloudflared tunnel list > /dev/null 2>&1; then
        print_success "Already authenticated with Cloudflare"
        return 0
    fi
    
    print_status "Please authenticate with Cloudflare..."
    print_warning "A browser window will open. Please login to your Cloudflare account."
    read -p "Press Enter to continue..."
    
    cloudflared tunnel login
    
    if [ $? -eq 0 ]; then
        print_success "Successfully authenticated with Cloudflare"
    else
        print_error "Failed to authenticate with Cloudflare"
        exit 1
    fi
}

# Create tunnel
create_tunnel() {
    print_status "Creating tunnel: $TUNNEL_NAME"
    
    # Check if tunnel already exists
    if cloudflared tunnel list | grep -q "$TUNNEL_NAME"; then
        print_warning "Tunnel '$TUNNEL_NAME' already exists"
        
        # Get tunnel ID
        TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
        print_status "Using existing tunnel ID: $TUNNEL_ID"
    else
        # Create new tunnel
        print_status "Creating new tunnel..."
        cloudflared tunnel create "$TUNNEL_NAME"
        
        if [ $? -eq 0 ]; then
            TUNNEL_ID=$(cloudflared tunnel list | grep "$TUNNEL_NAME" | awk '{print $1}')
            print_success "Tunnel created successfully with ID: $TUNNEL_ID"
        else
            print_error "Failed to create tunnel"
            exit 1
        fi
    fi
}

# Create configuration file
create_config() {
    print_status "Creating configuration file..."
    
    # Create .cloudflared directory if it doesn't exist
    mkdir -p "$HOME/.cloudflared"
    
    # Create configuration
    cat > "$CONFIG_FILE" << EOF
tunnel: $TUNNEL_ID
credentials-file: $HOME/.cloudflared/$TUNNEL_ID.json

ingress:
  # MCP Server (Main service)
  - hostname: mcp.${TUNNEL_NAME}.your-domain.com
    service: http://localhost:$MCP_PORT
    originRequest:
      httpHostHeader: localhost:$MCP_PORT
  
  # Socket.IO Server (for orchestration)
  - hostname: socketio.${TUNNEL_NAME}.your-domain.com  
    service: http://localhost:$SOCKETIO_PORT
    originRequest:
      httpHostHeader: localhost:$SOCKETIO_PORT
  
  # Wildcard rule (catches all other traffic)
  - service: http_status:404

# Optional: Add authentication (uncomment to enable)
# Access:
#   - service: http://localhost:$MCP_PORT
#     policy:
#       - name: "MCP Access Policy"
#         decision: allow
#         rules:
#           - email: ["your-email@domain.com"]

EOF

    print_success "Configuration file created at: $CONFIG_FILE"
}

# Setup DNS (with instructions)
setup_dns_instructions() {
    print_status "DNS Setup Instructions"
    echo ""
    print_warning "You have two options for DNS setup:"
    echo ""
    echo "Option 1: Use Cloudflare's provided URLs (Easiest)"
    echo "  - Cloudflare will provide auto-generated URLs"
    echo "  - No domain required"
    echo "  - URLs will look like: https://tunnel-id.cfargotunnel.com"
    echo ""
    echo "Option 2: Use your own domain (Professional)"
    echo "  - Requires a domain managed by Cloudflare"
    echo "  - Custom subdomains like: mcp.yourdomain.com"
    echo ""
    
    read -p "Do you have a domain managed by Cloudflare? (y/N): " has_domain
    
    if [[ $has_domain =~ ^[Yy]$ ]]; then
        read -p "Enter your domain name: " domain_name
        
        print_status "Setting up DNS routes..."
        cloudflared tunnel route dns "$TUNNEL_NAME" "mcp.$domain_name"
        cloudflared tunnel route dns "$TUNNEL_NAME" "socketio.$domain_name"
        
        if [ $? -eq 0 ]; then
            print_success "DNS routes created successfully"
            print_success "Your MCP server will be available at: https://mcp.$domain_name"
            print_success "Your Socket.IO server will be available at: https://socketio.$domain_name"
        else
            print_error "Failed to create DNS routes"
        fi
    else
        print_status "No problem! Cloudflare will provide auto-generated URLs"
        print_success "Your services will be available at auto-generated Cloudflare URLs"
    fi
}

# Create management scripts
create_management_scripts() {
    print_status "Creating management scripts..."
    
    # Create start tunnel script
    cat > "start_tunnel.sh" << 'EOF'
#!/bin/bash

echo "🌩️ Starting Cloudflare Tunnel..."

# Check if MCP server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  MCP server not running. Starting services first..."
    ./start_all.sh &
    
    # Wait for MCP server to be ready
    echo "⏳ Waiting for MCP server to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ MCP server is ready"
            break
        fi
        sleep 1
    done
fi

echo "🚀 Starting Cloudflare tunnel..."
cloudflared tunnel run plasmo-mcp-server

EOF

    # Create stop tunnel script  
    cat > "stop_tunnel.sh" << 'EOF'
#!/bin/bash

echo "🛑 Stopping Cloudflare Tunnel..."

# Kill cloudflared processes
pkill -f "cloudflared tunnel run"

echo "✅ Tunnel stopped"

EOF

    # Create status script
    cat > "tunnel_status.sh" << 'EOF'
#!/bin/bash

echo "🔍 Cloudflare Tunnel Status"
echo "=========================="

# Check if tunnel process is running
if pgrep -f "cloudflared tunnel run" > /dev/null; then
    echo "✅ Tunnel process: Running"
else
    echo "❌ Tunnel process: Not running"
fi

# Check MCP server
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ MCP server: Running (port 8000)"
else
    echo "❌ MCP server: Not running"
fi

# Check Socket.IO server
if curl -s http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ Socket.IO server: Running (port 3001)"
else
    echo "❌ Socket.IO server: Not running"
fi

echo ""
echo "📋 Tunnel Information:"
cloudflared tunnel list | grep "plasmo-mcp-server" || echo "❌ Tunnel not found"

EOF

    # Make scripts executable
    chmod +x start_tunnel.sh stop_tunnel.sh tunnel_status.sh
    
    print_success "Management scripts created:"
    print_success "  - start_tunnel.sh: Start the tunnel"
    print_success "  - stop_tunnel.sh: Stop the tunnel"  
    print_success "  - tunnel_status.sh: Check tunnel status"
}

# Update VSCode tasks
update_vscode_tasks() {
    print_status "Updating VSCode tasks..."
    
    if [ -f ".vscode/tasks.json" ]; then
        # Create backup
        cp .vscode/tasks.json .vscode/tasks.json.backup
        
        # Add tunnel tasks (this would require more complex JSON manipulation)
        print_success "VSCode tasks backed up"
        print_warning "Please manually add tunnel tasks to .vscode/tasks.json"
        print_warning "Or use the provided management scripts directly"
    else
        print_warning ".vscode/tasks.json not found. Skipping VSCode integration"
    fi
}

# Main execution
main() {
    echo "Starting Cloudflare Tunnel setup..."
    echo ""
    
    check_cloudflared
    echo ""
    
    login_cloudflare  
    echo ""
    
    create_tunnel
    echo ""
    
    create_config
    echo ""
    
    setup_dns_instructions
    echo ""
    
    create_management_scripts
    echo ""
    
    update_vscode_tasks
    echo ""
    
    print_success "🎉 Cloudflare Tunnel setup complete!"
    echo ""
    print_status "Next steps:"
    echo "  1. Test your setup: ./tunnel_status.sh"
    echo "  2. Start the tunnel: ./start_tunnel.sh"
    echo "  3. Access your MCP server via the Cloudflare URL"
    echo ""
    print_warning "Remember to:"
    echo "  - Keep your tunnel credentials secure"
    echo "  - Consider adding authentication for production use"
    echo "  - Monitor tunnel usage in Cloudflare dashboard"
    echo ""
}

# Run main function
main 