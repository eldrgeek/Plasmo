#!/bin/bash
###############################################################################
# Chrome Debug Monitor - Installation Script
# ===========================================
# Installs Chrome Debug Monitor as a macOS LaunchAgent
#
# Usage:
#   ./install_chrome_monitor.sh
###############################################################################

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PLIST_FILE="com.plasmo.chromedebugmonitor.plist"
PLIST_PATH="$SCRIPT_DIR/$PLIST_FILE"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
LAUNCHD_PLIST="$LAUNCHD_DIR/$PLIST_FILE"
SERVICE_NAME="com.plasmo.chromedebugmonitor"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

echo ""
print_info "Installing Chrome Debug Monitor Service..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$LAUNCHD_DIR"

# Stop existing service if running
if launchctl list | grep -q "$SERVICE_NAME"; then
    print_warning "Stopping existing service..."
    launchctl unload "$LAUNCHD_PLIST" 2>/dev/null || true
fi

# Copy plist file
print_info "Installing service configuration..."
cp "$PLIST_PATH" "$LAUNCHD_PLIST"

# Load the service
print_info "Starting service..."
launchctl load "$LAUNCHD_PLIST"

# Give it a moment to start
sleep 2

# Check if service is running
if launchctl list | grep -q "$SERVICE_NAME"; then
    echo ""
    print_success "Chrome Debug Monitor installed and running!"
    echo ""
    print_info "The service will:"
    echo "  ✅ Start automatically when you log in"
    echo "  ✅ Monitor Chrome debug on port 9222"
    echo "  ✅ Auto-restart Chrome if it stops"
    echo ""
    print_info "Management:"
    echo "  Status:  ./manage_chrome_monitor.sh status"
    echo "  Restart: ./manage_chrome_monitor.sh restart"
    echo "  Logs:    ./manage_chrome_monitor.sh logs"
    echo "  Stop:    ./manage_chrome_monitor.sh stop"
    echo ""
else
    print_warning "Service loaded but not running. Check logs:"
    echo "  tail -f $SCRIPT_DIR/logs/chrome_monitor.log"
    exit 1
fi
