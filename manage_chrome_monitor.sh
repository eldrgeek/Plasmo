#!/bin/bash
###############################################################################
# Chrome Debug Monitor - Management Script
# =========================================
# Simple wrapper around service-manager.sh for Chrome Debug Monitor
#
# Usage:
#   ./manage_chrome_monitor.sh {status|start|stop|restart|logs|test}
###############################################################################

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
SERVICE_NAME="com.plasmo.chromedebugmonitor"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }

# Check if service-manager.sh is available
SERVICE_MANAGER="$HOME/bin/service-manager.sh"

if [ ! -f "$SERVICE_MANAGER" ]; then
    echo "⚠️  Universal service-manager.sh not found at: $SERVICE_MANAGER"
    echo ""
    echo "Using direct launchctl commands instead..."
    USE_DIRECT=true
else
    USE_DIRECT=false
fi

# Function to run service commands
run_service_cmd() {
    if [ "$USE_DIRECT" = true ]; then
        # Direct launchctl commands
        case "$1" in
            start)
                launchctl start "$SERVICE_NAME"
                ;;
            stop)
                launchctl stop "$SERVICE_NAME"
                ;;
            restart)
                launchctl kickstart -k "gui/$(id -u)/$SERVICE_NAME"
                ;;
            status)
                launchctl list | grep "$SERVICE_NAME" || echo "Service not running"
                ;;
            *)
                echo "Unknown action: $1"
                exit 1
                ;;
        esac
    else
        # Use universal service manager
        "$SERVICE_MANAGER" launchd "$SERVICE_NAME" "$1"
    fi
}

case "${1:-}" in
    status)
        print_info "Chrome Debug Monitor Status"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""

        run_service_cmd status

        echo ""
        print_info "Chrome Debug Status:"
        python3 "$SCRIPT_DIR/chrome_debug_monitor.py" --status

        echo ""
        print_info "Recent Logs:"
        if [ -f "$SCRIPT_DIR/logs/chrome_monitor.log" ]; then
            tail -n 10 "$SCRIPT_DIR/logs/chrome_monitor.log"
        else
            echo "No logs found"
        fi
        ;;

    start)
        print_info "Starting Chrome Debug Monitor..."
        run_service_cmd start
        sleep 2
        print_success "Service started"
        "$0" status
        ;;

    stop)
        print_info "Stopping Chrome Debug Monitor..."
        run_service_cmd stop
        sleep 1
        print_success "Service stopped"
        ;;

    restart)
        print_info "Restarting Chrome Debug Monitor..."
        run_service_cmd restart
        sleep 2
        print_success "Service restarted"
        "$0" status
        ;;

    logs)
        print_info "Following Chrome Debug Monitor logs (Ctrl+C to exit)..."
        if [ -f "$SCRIPT_DIR/logs/chrome_monitor.log" ]; then
            tail -f "$SCRIPT_DIR/logs/chrome_monitor.log"
        else
            echo "No logs found at: $SCRIPT_DIR/logs/chrome_monitor.log"
            exit 1
        fi
        ;;

    test)
        print_info "Testing Chrome Debug Monitor (manual run)..."
        python3 "$SCRIPT_DIR/chrome_debug_monitor.py"
        ;;

    uninstall)
        if [ "$USE_DIRECT" = false ]; then
            "$SERVICE_MANAGER" launchd "$SERVICE_NAME" uninstall
        else
            print_info "Uninstalling Chrome Debug Monitor..."
            launchctl unload "$HOME/Library/LaunchAgents/$SERVICE_NAME.plist" 2>/dev/null || true
            print_success "Service unloaded"
            echo ""
            echo "To fully remove, delete the plist:"
            echo "  rm $HOME/Library/LaunchAgents/$SERVICE_NAME.plist"
        fi
        ;;

    *)
        echo "Chrome Debug Monitor Management"
        echo ""
        echo "Usage: $0 {status|start|stop|restart|logs|test|uninstall}"
        echo ""
        echo "Commands:"
        echo "  status    - Show service and Chrome debug status"
        echo "  start     - Start the monitor service"
        echo "  stop      - Stop the monitor service"
        echo "  restart   - Restart the monitor service"
        echo "  logs      - Follow monitor logs in real-time"
        echo "  test      - Run monitor manually for testing"
        echo "  uninstall - Uninstall the service"
        echo ""
        echo "What it does:"
        echo "  ✅ Monitors Chrome debug on port 9222"
        echo "  ✅ Auto-starts Chrome if not running"
        echo "  ✅ Runs automatically on login"
        echo ""
        exit 1
        ;;
esac
