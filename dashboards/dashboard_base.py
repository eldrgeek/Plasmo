#!/usr/bin/env python3
"""
Dashboard Base Framework
========================
FastHTML-based dashboard framework with real-time WebSocket updates.
Provides base classes and components for all service dashboards.
"""

import json
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod

from fasthtml import *
from fasthtml.common import *
from fasthtml.core import to_xml
from fasthtml.core import to_xml
from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.responses import HTMLResponse
from fasthtml.fastapp import fast_app
from fasthtml.common import Div as _Div, Span as _Span, H1 as _H1, H2 as _H2, H3 as _H3, Button as _Button, P as _P

# (The global fasthtml.common monkey patch is inserted after tag definitions below)

@dataclass
class DashboardTheme:
    """Dashboard theme configuration"""
    primary_color: str = "#2563eb"      # Blue
    secondary_color: str = "#64748b"    # Slate
    success_color: str = "#10b981"      # Green
    warning_color: str = "#f59e0b"      # Amber
    error_color: str = "#ef4444"        # Red
    background_color: str = "#f8fafc"   # Light background
    card_background: str = "#ffffff"    # White cards
    text_primary: str = "#1e293b"       # Dark text
    text_secondary: str = "#475569"     # Muted text
    border_color: str = "#e2e8f0"       # Light border
    
    # Dark theme colors
    dark_background: str = "#0f172a"    # Dark background
    dark_card: str = "#1e293b"          # Dark cards
    dark_text_primary: str = "#f1f5f9"  # Light text
    dark_text_secondary: str = "#cbd5e1" # Muted light text
    dark_border: str = "#334155"        # Dark border


class DashboardComponent:
    """Base component for dashboard elements"""
    
    @staticmethod
    def status_badge(status: str, text: str = None) -> Div:
        """Create a status badge with appropriate color"""
        colors = {
            "running": "bg-green-100 text-green-800 border-green-200",
            "stopped": "bg-red-100 text-red-800 border-red-200", 
            "starting": "bg-yellow-100 text-yellow-800 border-yellow-200",
            "error": "bg-red-100 text-red-800 border-red-200",
            "unknown": "bg-gray-100 text-gray-800 border-gray-200"
        }
        
        color_class = colors.get(status, colors["unknown"])
        display_text = text or status.title()
        
        return Div(
            display_text,
            cls=f"inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {color_class}"
        )
    
    @staticmethod
    def metric_card(title: str, value: str, subtitle: str = None, trend: str = None) -> Div:
        """Create a metric card"""
        return Div(
            Div(
                Div(title, cls="text-sm font-medium text-gray-500"),
                Div(value, cls="mt-1 text-3xl font-semibold text-gray-900"),
                Div(subtitle, cls="mt-1 text-sm text-gray-600") if subtitle else "",
                cls="p-4"
            ),
            cls="card"
        )
    
    @staticmethod
    def service_card(service_data: Dict[str, Any]) -> Div:
        """Create a service status card including controls and link"""
        name = service_data.get("name", "Unknown")
        status = service_data.get("status", "unknown")
        port = service_data.get("port")
        pid = service_data.get("pid")
        uptime = service_data.get("uptime")
        
        # Format uptime
        uptime_text = ""
        if uptime:
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            uptime_text = f"{hours}h {minutes}m"
        
        # Determine which action button to show based on status
        if status == "running":
            action_btn = Button(
                Span("stop", cls="material-icons-round"),
                Span("Stop"),
                cls="btn btn-error",
                onclick=f"controlService('{name}','stop')",
                title="Stop this service"
            )
        else:
            action_btn = Button(
                Span("play_arrow", cls="material-icons-round"),
                Span("Start"),
                cls="btn btn-success",
                onclick=f"controlService('{name}','start')",
                title="Start this service"
            )
        # Link to dashboard
        link_btn = A(
            Span("open_in_new", cls="material-icons-round"),
            Span("Dashboard"),
            href=f"/{name}",
            cls="btn btn-primary",
            title="Open service dashboard"
        )
        # Header with controls
        header = Div(
            Div(
                H3(name.title(), cls="text-lg font-semibold text-gray-900"),
                DashboardComponent.status_badge(status),
                cls="flex items-center gap-2"
            ),
            Div(link_btn, action_btn, cls="flex items-center gap-2"),
            cls="flex items-center justify-between"
        )
        
        return Div(
            # Header
            Div(header, cls="p-4 border-b border-gray-200"),
            # Content
            Div(
                Div(
                    Div(
                        Span("Port:", cls="text-sm text-gray-500"),
                        Span(str(port) if port else "N/A", cls="text-sm font-medium text-gray-900 ml-2")
                    ) if port else "",
                    Div(
                        Span("PID:", cls="text-sm text-gray-500"),
                        Span(str(pid) if pid else "N/A", cls="text-sm font-medium text-gray-900 ml-2")
                    ),
                    Div(
                        Span("Uptime:", cls="text-sm text-gray-500"),
                        Span(uptime_text if uptime_text else "N/A", cls="text-sm font-medium text-gray-900 ml-2")
                    ),
                    cls="space-y-2"
                ),
                cls="p-4"
            ),
            cls="card"
        )
    
    @staticmethod
    def log_viewer(log_id: str, height: str = "300px") -> Div:
        """Create a log viewer component"""
        return Div(
            Div(
                Div("Service Logs", cls="text-lg font-semibold text-gray-900"),
                Button(
                    "Clear",
                    cls="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200",
                    onclick=f"clearLogs('{log_id}')"
                ),
                cls="flex items-center justify-between p-4 border-b border-gray-200"
            ),
            Div(
                id=log_id,
                cls="p-4 bg-gray-50 font-mono text-sm overflow-y-auto",
                style=f"height: {height};"
            ),
            cls="card"
        )


class DashboardBase(ABC):
    """Base class for all dashboard implementations"""
    
    def __init__(self, service_name: str, title: str):
        self.service_name = service_name
        self.title = title
        self.theme = DashboardTheme()
        self.connected_clients: List[WebSocket] = []
        self.last_update = time.time()
        
    @abstractmethod
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard-specific data"""
        pass
    
    @abstractmethod
    def render_content(self, data: Dict[str, Any]) -> List:
        """Render dashboard-specific content"""
        pass
    
    def get_base_styles(self) -> Style:
        """Get base CSS styles for the dashboard"""
        return Style("""
        /* Modern Dashboard Styles */
        .dashboard-container {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a202c;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .content {
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
        
        /* Enhanced Grid layouts with better spacing */
        .grid-2 { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
            gap: 2rem; 
        }
        .grid-3 { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 2rem; 
        }
        .grid-4 { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
        }
        
        /* Enhanced cards */
        .bg-white {
            background: rgba(255, 255, 255, 0.9) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border-radius: 16px;
            transition: all 0.3s ease;
        }
        
        .bg-white:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        /* Enhanced buttons */
        button, .btn {
            transition: all 0.3s ease;
            font-weight: 600;
            letter-spacing: 0.5px;
            border-radius: 12px;
        }
        
        button:hover, .btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }
        
        /* Navigation links */
        a {
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        a:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Status badges with glow */
        .bg-green-100 {
            background: rgba(16, 185, 129, 0.2) !important;
            color: #059669 !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.3);
        }
        
        .bg-red-100 {
            background: rgba(239, 68, 68, 0.2) !important;
            color: #dc2626 !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
            box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
        }
        
        .bg-yellow-100 {
            background: rgba(245, 158, 11, 0.2) !important;
            color: #d97706 !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
        }
        
        /* Connection status indicator */
        #connection-status {
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Status animations */
        .status-running { animation: pulse-green 2s infinite; }
        .status-error { animation: pulse-red 2s infinite; }
        
        @keyframes pulse-green {
            0%, 100% { background-color: #10b981; }
            50% { background-color: #059669; }
        }
        
        @keyframes pulse-red {
            0%, 100% { background-color: #ef4444; }
            50% { background-color: #dc2626; }
        }
        
        /* Responsive design */
        @media (max-width: 1024px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
            .content { padding: 1.5rem; }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; gap: 1rem; }
            .content { padding: 1rem; }
            .header { padding: 1rem; }
        }
        
        /* Dark mode enhancements */
        .dark {
            background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        }
        
        .dark .content {
            background: rgba(0, 0, 0, 0.3);
        }
        
        .dark .bg-white {
            background: rgba(45, 55, 72, 0.9) !important;
            color: #f7fafc !important;
        }
        
        .dark .text-gray-900 {
            color: #f1f5f9 !important;
        }
        
        .dark .border-gray-200 {
            border-color: #334155 !important;
        }
        
        /* Typography enhancements */
        h1, h2, h3 {
            font-weight: 700;
            letter-spacing: -0.025em;
        }
        
        .text-3xl {
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Log viewer enhancements */
        .log-viewer {
            background: rgba(0, 0, 0, 0.8);
            color: #00ff00;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        body[data-theme="dark"] .text-gray-500,
        body[data-theme="dark"] .text-gray-600,
        body[data-theme="dark"] .text-gray-700 {
            color: var(--muted-dark) !important;
        }
        
        body[data-theme="dark"] .text-gray-900 {
            color: var(--fg-dark) !important;
        }
        """)
    
    def get_base_scripts(self) -> Script:
        """Get base JavaScript for dashboard functionality"""
        return Script("""
// Theme persistence
const saved = localStorage.getItem('theme') || 'dark';
document.body.dataset.theme = saved;

function toggleTheme() {
  const next = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  document.body.dataset.theme = next;
  localStorage.setItem('theme', next);
}

// Control individual service via API
function controlService(name, action) {
  fetch(`/api/services/${name}/${action}`, {method: 'POST'})
    .then(r => r.json())
    .then(data => {
      console.log(`Service ${name} ${action}:`, data);
      // Simple feedback reload
      setTimeout(() => location.reload(), 500);
    })
    .catch(err => console.error(err));
}
""")
    
    def render_header(self) -> Div:
        """Render dashboard header"""
        return Div(
            Div(
                A(
                    Span("arrow_back", cls="material-icons-round mr-2"),
                    Span("Services"),
                    href="/master",
                    cls="nav-item"
                ),
                cls="flex items-center gap-2"
            ),
            H1(self.title, cls="text-lg font-semibold"),
            Button(
                Span("brightness_4", cls="material-icons-round"),
                onclick="toggleTheme()",
                cls="btn btn-primary",
                title="Toggle dark/light"
            ),
            cls="header flex justify-between items-center"
        )
    
    def render_sidebar(self) -> Div:
        """Render left sidebar navigation"""
        return Div(
            A("Services", href="/master", cls="nav-item"),
            A("Socket.IO", href="/socketio", cls="nav-item"),
            A("MCP", href="/mcp", cls="nav-item"),
            A("Plasmo", href="/plasmo", cls="nav-item"),
            cls="sidebar flex flex-col gap-2"
        )
    
    def render_full_dashboard(self) -> str:
        """Render complete dashboard HTML"""
        data = self.get_dashboard_data()
        content = self.render_content(data)
        
        html = Html(
            Head(*COMMON_HEAD),
            Body(
                self.render_header(),
                self.render_sidebar(),
                Div(*content, cls="main-content card-grid"),
                self.get_base_scripts()
            )
        )
        
        return to_xml(html)
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connection for real-time updates"""
        await websocket.accept()
        self.connected_clients.append(websocket)
        
        try:
            while True:
                # Send updates every 2 seconds
                await asyncio.sleep(2)
                data = self.get_dashboard_data()
                await websocket.send_text(json.dumps(data))
                
        except WebSocketDisconnect:
            pass
        finally:
            if websocket in self.connected_clients:
                self.connected_clients.remove(websocket)
    
    async def broadcast_update(self, data: Dict[str, Any]):
        """Broadcast update to all connected clients"""
        if not self.connected_clients:
            return
            
        message = json.dumps(data)
        disconnected = []
        
        for client in self.connected_clients:
            try:
                await client.send_text(message)
            except:
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            if client in self.connected_clients:
                self.connected_clients.remove(client)

# --------------------
# Common HEAD Elements (fonts, icons, and modern flat CSS variables)
# --------------------
COMMON_HEAD = [
    Title("Plasmo Dashboard"),
    Meta(charset="utf-8"),
    Meta(name="viewport", content="width=device-width,initial-scale=1"),
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap"),
    Link(rel="stylesheet", href="https://fonts.googleapis.com/icon?family=Material+Icons+Round"),
    Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"),
    # Modern flat-design CSS – single dark/light theme with variables and one mobile breakpoint
    Style("""
:root {
  --bg-dark: #0d1117;
  --bg-light: #ffffff;
  --fg-dark: #f0f6fc;
  --fg-light: #111827;
  --muted-dark: #8b949e;
  --muted-light: #4b5563;
  --card-dark: #161b22;
  --card-light: #f3f4f6;
  --accent: #3b82f6;
  --ok: #10b981;
  --warn: #f59e0b;
  --error: #ef4444;
  --gap: 1.25rem;
  --radius: 0.75rem;
  --ts: 0.2s ease;
}
body {
  font-family: 'Inter', sans-serif;
  background: var(--bg-dark);
  color: var(--fg-dark);
  margin: 0;
  min-height: 100vh;
}
body[data-theme="light"] {
  background: var(--bg-light);
  color: var(--fg-light);
}
.material-icons-round { font-size: 1.2rem; }

.header {
  position: fixed; top: 0; left: 0; right: 0;
  height: 3.5rem;
  display: flex; justify-content: space-between; align-items: center;
  background: var(--card-dark);
  padding: 0 var(--gap);
  border-bottom: 1px solid #2c2f36;
}
body[data-theme="light"] .header {
  background: var(--card-light);
  border-color: #e5e7eb;
}

.sidebar {
  position: fixed;
  top: 3.5rem; bottom: 0; left: 0;
  width: 14rem;
  background: var(--card-dark);
  padding: var(--gap);
  overflow-y: auto;
  border-right: 1px solid #2c2f36;
}
body[data-theme="light"] .sidebar {
  background: var(--card-light);
  border-color: #e5e7eb;
}

.sidebar .nav-item {
  width: 100%;
}

.nav-item {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  color: var(--muted-dark);
  background: none; border: none;
  transition: background var(--ts), color var(--ts);
  cursor: pointer; width: 100%; text-align: left;
}
.nav-item.active,
.nav-item:hover {
  background: rgba(255,255,255,0.05);
  color: var(--fg-dark);
}
body[data-theme="light"] .nav-item { color: var(--muted-light); }
body[data-theme="light"] .nav-item.active,
body[data-theme="light"] .nav-item:hover {
  background: rgba(0,0,0,0.05);
  color: var(--fg-light);
}

.main-content {
  margin-left: 14rem;
  margin-top: 3.5rem;
  padding: var(--gap);
}
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--gap);
}
.card {
  background: var(--card-dark);
  padding: var(--gap);
  border-radius: var(--radius);
  border: 1px solid #2c2f36;
  transition: transform var(--ts), box-shadow var(--ts);
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.2);
}
body[data-theme="light"] .card {
  background: var(--card-light);
  border-color: #e5e7eb;
}
.btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.6rem 1rem;
  font-size: 0.85rem; font-weight: 600;
  border-radius: var(--radius); border: none; cursor: pointer;
  transition: transform var(--ts); color: white;
}
.btn:hover { transform: translateY(-2px); }
.btn-primary { background: var(--accent); }
.btn-success { background: var(--ok); }
.btn-warning { background: var(--warn); }
.btn-error   { background: var(--error); }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 768px) {
  .sidebar { display: none; }
  .main-content { margin-left: 0; }
}
""")
] 

# ---------------------------------------------------------------------------
# Helper: auto-flatten list children so we can safely write Div([a,b])
# without ending up with raw Python list/tuple in rendered HTML. This keeps
# older dashboard code working even if we forget to unpack with *.
# ---------------------------------------------------------------------------

def _auto_flatten(tag_cls):
    def _wrapper(*children, **attrs):
        # If a single positional argument is a list/tuple, flatten it.
        if len(children) == 1 and isinstance(children[0], (list, tuple)):
            children = children[0]
        return tag_cls(*children, **attrs)
    return _wrapper

# Patch commonly used elements
Div = _auto_flatten(_Div)  # type: ignore
Span = _auto_flatten(_Span)  # type: ignore
H1 = _auto_flatten(_H1)  # type: ignore
H2 = _auto_flatten(_H2)  # type: ignore
H3 = _auto_flatten(_H3)  # type: ignore
Button = _auto_flatten(_Button)  # type: ignore
P = _auto_flatten(_P)  # type: ignore

# Re-export patched symbols so `from dashboards.dashboard_base import *` works
__all__ = [
    # existing exports (if any) plus patched tags
    'Div', 'Span', 'H1', 'H2', 'H3', 'Button', 'P',
]

# --- propagate patched tags to fasthtml.common so that any module that
# imported directly from FastHTML still benefits from list-flattening.
import sys as _sys
_mod = _sys.modules.get('fasthtml.common')
if _mod is not None:
    _mod.Div = Div  # type: ignore
    _mod.Span = Span  # type: ignore
    _mod.H1 = H1  # type: ignore
    _mod.H2 = H2  # type: ignore
    _mod.H3 = H3  # type: ignore
    _mod.Button = Button  # type: ignore
    _mod.P = P  # type: ignore 