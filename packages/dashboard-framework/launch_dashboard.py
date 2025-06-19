#!/usr/bin/env python3
"""
Dashboard Launcher
==================
Launches the unified dashboard server with all service dashboards registered.
"""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboards.dashboard_server import dashboard_server
from dashboards.socketio_dashboard import SocketIODashboard
from dashboards.mcp_dashboard import MCPDashboard
from dashboards.plasmo_dashboard import PlasmoDashboard


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('logs/dashboard.log')
        ]
    )


def register_all_dashboards():
    """Register all service dashboards"""
    
    # Register Socket.IO dashboard
    dashboard_server.register_dashboard(
        "socketio", 
        SocketIODashboard
    )
    
    # Register MCP Server dashboard  
    dashboard_server.register_dashboard(
        "mcp",
        MCPDashboard
    )
    
    # Register Plasmo Development dashboard
    dashboard_server.register_dashboard(
        "plasmo",
        PlasmoDashboard
    )
    
    # TODO: Add more dashboards as they're implemented
    # dashboard_server.register_dashboard("testing", TestingDashboard)
    # dashboard_server.register_dashboard("chrome", ChromeDashboard)
    # dashboard_server.register_dashboard("tunneling", TunnelingDashboard)
    
    logging.info("All dashboards registered successfully")


def main():
    """Main dashboard launcher"""
    print("🚀 Starting Unified Dashboard Server...")
    
    # Setup logging
    setup_logging()
    
    # Ensure logs directory exists
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Register all dashboards
    register_all_dashboards()
    
    # Start the dashboard server
    print(f"📊 Dashboard server starting on http://localhost:8000")
    print(f"🎛️  Master Control: http://localhost:8000/master")
    print(f"🔌 Socket.IO Dashboard: http://localhost:8000/socketio")
    print(f"🤖 MCP Server Dashboard: http://localhost:8000/mcp")
    print(f"⚡ Plasmo Dev Dashboard: http://localhost:8000/plasmo")
    print(f"")
    print(f"Press Ctrl+C to stop the server")
    
    try:
        dashboard_server.run()
    except KeyboardInterrupt:
        print("\n👋 Dashboard server stopped")
    except Exception as e:
        logging.error(f"Dashboard server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 