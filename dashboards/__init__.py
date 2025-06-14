"""
Dashboards Module
=================
Unified dashboard system for service monitoring and management.
"""

from .dashboard_base import DashboardBase, DashboardComponent, DashboardTheme
from .dashboard_server import DashboardServer, dashboard_server, register_dashboard
from .socketio_dashboard import SocketIODashboard
from .mcp_dashboard import MCPDashboard
from .plasmo_dashboard import PlasmoDashboard

__all__ = [
    "DashboardBase",
    "DashboardComponent", 
    "DashboardTheme",
    "DashboardServer",
    "dashboard_server",
    "register_dashboard",
    "SocketIODashboard",
    "MCPDashboard",
    "PlasmoDashboard"
] 