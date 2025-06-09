#!/bin/bash

# Linux Setup Script for Plasmo Chrome Extension with MCP Server
# =============================================================

echo "🐧 Setting up Plasmo project for Linux..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $1"
}

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
    VERSION=$VERSION_ID
    print_info "🔍 Detected: $PRETTY_NAME"
else
    print_warning "⚠️  Could not detect Linux distribution"
    DISTRO="unknown"
fi

# Function to install packages based on distribution
install_packages() {
    print_info "📦 Installing required packages..."
    
    case $DISTRO in
        "ubuntu"|"debian")
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                python3 \
                python3-pip \
                python3-venv \
                nodejs \
                npm \
                google-chrome-stable \
                xdotool \
                build-essential
            ;;
        "fedora"|"rhel"|"centos")
            sudo dnf install -y \
                curl \
                wget \
                git \
                python3 \
                python3-pip \
                nodejs \
                npm \
                google-chrome-stable \
                xdotool \
                gcc \
                gcc-c++ \
                make
            ;;
        "arch"|"manjaro")
            sudo pacman -S --noconfirm \
                curl \
                wget \
                git \
                python \
                python-pip \
                nodejs \
                npm \
                google-chrome \
                xdotool \
                base-devel
            ;;
        *)
            print_warning "⚠️  Unknown distribution. Please install manually:"
            echo "   - curl, wget, git"
            echo "   - python3, python3-pip"
            echo "   - nodejs, npm"
            echo "   - google-chrome-stable"
            echo "   - xdotool"
            echo "   - build tools (gcc, make, etc.)"
            read -p "Continue anyway? (y/N): " CONTINUE
            if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
                exit 1
            fi
            ;;
    esac
}

# Check if Chrome is installed
check_chrome() {
    print_info "🔍 Checking for Google Chrome..."
    
    if command -v google-chrome &> /dev/null; then
        CHROME_VERSION=$(google-chrome --version)
        print_status "✅ Found: $CHROME_VERSION"
        return 0
    elif command -v chromium-browser &> /dev/null; then
        CHROME_VERSION=$(chromium-browser --version)
        print_status "✅ Found: $CHROME_VERSION"
        return 0
    elif command -v chromium &> /dev/null; then
        CHROME_VERSION=$(chromium --version)
        print_status "✅ Found: $CHROME_VERSION"
        return 0
    else
        print_error "❌ Chrome/Chromium not found"
        return 1
    fi
}

# Install Node.js dependencies
setup_nodejs() {
    print_info "📦 Setting up Node.js environment..."
    
    # Install pnpm if not present
    if ! command -v pnpm &> /dev/null; then
        print_info "Installing pnpm..."
        npm install -g pnpm
    fi
    
    print_status "✅ pnpm found: $(pnpm --version)"
    
    # Install project dependencies
    if [ -f "package.json" ]; then
        print_info "Installing project dependencies..."
        pnpm install
        print_status "✅ Node.js dependencies installed"
    else
        print_error "❌ package.json not found"
        return 1
    fi
}

# Setup Python environment
setup_python() {
    print_info "🐍 Setting up Python environment..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version)
        print_status "✅ Found: $PYTHON_VERSION"
    else
        print_error "❌ Python 3 not found"
        return 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        print_info "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        print_status "✅ Python dependencies installed"
    else
        print_error "❌ requirements.txt not found"
        return 1
    fi
    
    deactivate
}

# Update Chrome paths for Linux
update_chrome_paths() {
    print_info "🔧 Updating Chrome configuration paths for Linux..."
    
    # Chrome directories for Linux
    CHROME_CONFIG_DIR="$HOME/.config/google-chrome"
    CHROME_PREFS="$CHROME_CONFIG_DIR/Default/Preferences"
    NATIVE_MESSAGING_DIR="$CHROME_CONFIG_DIR/NativeMessagingHosts"
    
    # Create directories if they don't exist
    mkdir -p "$CHROME_CONFIG_DIR/Default"
    mkdir -p "$NATIVE_MESSAGING_DIR"
    
    print_status "✅ Chrome directories prepared"
    print_info "   Config: $CHROME_CONFIG_DIR"
    print_info "   Preferences: $CHROME_PREFS"
    print_info "   Native Messaging: $NATIVE_MESSAGING_DIR"
}

# Create Linux-specific launch script
create_linux_scripts() {
    print_info "📝 Creating Linux-specific scripts..."
    
    # Update get_extension_id.sh for Linux
    if [ -f "get_extension_id.sh" ]; then
        cp get_extension_id.sh get_extension_id.sh.bak
        sed -i 's|Library/Application Support/Google/Chrome|.config/google-chrome|g' get_extension_id.sh
        print_status "✅ Updated get_extension_id.sh for Linux"
    fi
    
    # Update configure_extension.sh for Linux
    if [ -f "configure_extension.sh" ]; then
        cp configure_extension.sh configure_extension.sh.bak
        sed -i 's|Library/Application Support/Google/Chrome|.config/google-chrome|g' configure_extension.sh
        print_status "✅ Updated configure_extension.sh for Linux"
    fi
}

# Test Chrome debugging capability
test_chrome_debug() {
    print_info "🧪 Testing Chrome debugging setup..."
    
    # Try to launch Chrome with debug flags
    if [ -f "launch-chrome-debug.sh" ]; then
        chmod +x launch-chrome-debug.sh
        print_info "Chrome debug script is ready to test"
        print_warning "⚠️  You can test it manually with: ./launch-chrome-debug.sh"
    fi
}

# Main execution
main() {
    print_info "🚀 Starting Linux setup process..."
    
    # Check if we're running on Linux
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_error "❌ This script is for Linux only"
        print_info "Current OS: $OSTYPE"
        exit 1
    fi
    
    # Install system packages
    install_packages
    
    # Check Chrome installation
    if ! check_chrome; then
        print_error "❌ Chrome installation failed or not found"
        print_info "Please install Google Chrome manually:"
        echo "   wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -"
        echo "   echo 'deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main' | sudo tee /etc/apt/sources.list.d/google-chrome.list"
        echo "   sudo apt-get update && sudo apt-get install google-chrome-stable"
        exit 1
    fi
    
    # Setup Node.js environment
    setup_nodejs
    
    # Setup Python environment
    setup_python
    
    # Update Chrome paths
    update_chrome_paths
    
    # Create Linux-specific scripts
    create_linux_scripts
    
    # Test Chrome debugging
    test_chrome_debug
    
    print_status "🎉 Linux setup complete!"
    echo ""
    print_info "📋 Next steps:"
    echo "   1. Test Chrome debugging: ./launch-chrome-debug.sh"
    echo "   2. Start the MCP server: ./start_mcp.sh"
    echo "   3. Start all services: ./start_all_services.sh"
    echo "   4. Configure extension: ./configure_extension.sh"
    echo ""
    print_info "🔧 Linux-specific notes:"
    echo "   • Chrome config: ~/.config/google-chrome/"
    echo "   • Native messaging: ~/.config/google-chrome/NativeMessagingHosts/"
    echo "   • Cursor automation uses xdotool (installed)"
    echo ""
    print_warning "⚠️  Remember to:"
    echo "   • Add your user to necessary groups if needed"
    echo "   • Check firewall settings for ports 8000, 3001, 9222"
    echo "   • Install Cursor IDE for full functionality"
}

# Run main function
main "$@" 