#!/usr/bin/env python3
"""
Dashboard Server Framework
==========================
FastHTML server that hosts all service dashboards with unified routing.
Provides centralized dashboard management and real-time updates.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Type
from pathlib import Path

from fasthtml import *
from fasthtml.common import *
from fasthtml.core import to_xml
from fasthtml.fastapp import fast_app
import uvicorn

from .dashboard_base import DashboardBase, DashboardComponent, COMMON_HEAD
from services.service_base import ServiceOrchestrator


class DashboardServer:
    """Central server for all service dashboards"""
    
    def __init__(self, port: int = 8000):
        self.port = port
        self.dashboards: Dict[str, DashboardBase] = {}
        self.orchestrator = ServiceOrchestrator()
        self.logger = logging.getLogger(__name__)
        
        # Capture error log entries (4xx/5xx) for display
        self.error_messages: List[str] = []

        class _ErrHandler(logging.Handler):
            def __init__(self, outer):
                super().__init__(); self.outer = outer
            def emit(self, record):
                msg = record.getMessage()
                if any(code in msg for code in [" 4", " 5"]):
                    self.outer.error_messages.append(msg)
                    if len(self.outer.error_messages) > 200:
                        self.outer.error_messages = self.outer.error_messages[-200:]

        logging.getLogger("uvicorn.access").addHandler(_ErrHandler(self))
        
        # Create FastHTML app with live reload
        self.app = self._create_app()
        
    def register_dashboard(self, service_name: str, dashboard_class: Type[DashboardBase], **kwargs):
        """Register a dashboard for a service"""
        dashboard = dashboard_class(service_name, **kwargs)
        self.dashboards[service_name] = dashboard
        self.logger.info(f"Registered dashboard for service: {service_name}")
    
    def _create_app(self):
        """Create FastHTML application with modern layout"""

        app, rt = fast_app(live=False, default_hdrs=False)

        # --------------------------------------------------
        # UI Components
        # --------------------------------------------------
        def AppHeader():
            return Div(
                H2("Plasmo Dashboard"),
                Button(
                    Span("brightness_4", cls="material-icons-round"),
                    onclick="toggleTheme()",
                    cls="btn btn-primary",
                    title="Toggle theme"
                ),
                cls="header"
            )

        def NavItem(path: str, icon: str, label: str):
            return Button(
                Span(icon, cls="material-icons-round"),
                Span(label),
                onclick=f"location.href='{path}'",
                cls="nav-item"
            )

        def Sidebar():
            return Div(
                NavItem("/master", "dashboard", "Master"),
                NavItem("/socketio", "bolt", "Socket.IO"),
                NavItem("/mcp", "smart_toy", "MCP"),
                NavItem("/plasmo", "extension", "Plasmo"),
                cls="sidebar"
            )

        # Build master content cards using DashboardComponent
        async def _service_cards():
            services = await self.orchestrator.get_all_service_status()
            return [DashboardComponent.service_card(svc) for svc in services.values()]

        # ROOT ROUTE (alias master)
        @rt("/")
        async def root(request=None):  # request param for compatibility
            cards = await _service_cards()
            const_error_count = len(self.error_messages)
            error_banner = Div(
                Span("error", cls="material-icons-round mr-2"),
                Span(f"{const_error_count} recent error(s) – click to view"),
                onclick="location.href='/errors'",
                cls="card bg-red-600 text-white mb-4"
            ) if const_error_count else ""
            global_controls = Div(
                Button(Span("play_arrow", cls="material-icons-round"), Span("Start All"),
                       onclick="fetch('/api/services/all/start',{method:'POST'}).then(()=>location.reload())", cls="btn btn-success mr-2"),
                Button(Span("stop", cls="material-icons-round"), Span("Stop All"),
                       onclick="fetch('/api/services/all/stop',{method:'POST'}).then(()=>location.reload())", cls="btn btn-error mr-2"),
                Button(Span("refresh", cls="material-icons-round"), Span("Restart All"),
                       onclick="fetch('/api/services/all/restart',{method:'POST'}).then(()=>location.reload())", cls="btn btn-warning"),
                cls="flex flex-wrap gap-2 mb-4"
            )
            return to_xml(Html(
                Head(*COMMON_HEAD),
                Body(
                    AppHeader(),
                    Div(
                        Sidebar(),
                        Main(
                            Div(
                                global_controls,
                                error_banner,
                                Div(*cards, cls="card-grid"),
                            ),
                            cls="main-content"
                        ),
                        cls="app-container"
                    ),
                    # Theme script (already included in DashboardBase, but add for root page)
                    Script("""
const saved = localStorage.getItem('theme') || 'dark';
document.body.dataset.theme = saved;

function toggleTheme() {
  const next = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  document.body.dataset.theme = next;
  localStorage.setItem('theme', next);
}

// Control single service
function controlService(name, action) {
  fetch(`/api/services/${name}/${action}`, {method:'POST'})
    .then(()=> location.reload())
    .catch(console.error);
}
""")
                )
            ))

        # Alias /master -> root (define first to avoid capture by wildcard route)
        @rt("/master")
        async def master_alias(request=None):
            return await root()

        # Individual dashboards reuse existing DashboardBase rendering
        @rt("/{service_name}")
        async def svc_dash(request, service_name: str):
            if service_name not in self.dashboards:
                return P("Dashboard not found: " + service_name)
            dashboard = self.dashboards[service_name]
            return dashboard.render_full_dashboard()

        @rt("/api/services")
        async def svc_api(request=None):
            return await self.orchestrator.get_all_service_status()

        @rt("/api/errors")
        async def errors_api(request=None):
            return {"errors": self.error_messages[-100:]}

        @rt("/errors")
        async def errors_page(request=None):
            msgs = [Div(msg, cls="mb-2") for msg in self.error_messages[-100:]] or [P("No errors captured.")]
            return to_xml(Html(
                Head(*COMMON_HEAD),
                Body(
                    AppHeader(),
                    Div(
                        Sidebar(),
                        Main(
                            H1("Captured Errors", cls="text-lg font-semibold mb-4"),
                            Div(*msgs, cls="card p-4"),
                            cls="main-content"
                        ),
                        cls="app-container"
                    ),
                    Script("""
const saved = localStorage.getItem('theme') || 'dark';
document.body.dataset.theme = saved;
function toggleTheme(){const next=document.body.dataset.theme==='dark'?'light':'dark';document.body.dataset.theme=next;localStorage.setItem('theme',next);} 
""")
                )
            ))

        # --- Service control endpoints ---
        @rt("/api/services/{svc_name}/{action}", methods=["POST"])
        async def svc_control(request, svc_name: str, action: str):
            if action == "start":
                ok = await self.orchestrator.start_service(svc_name)
            elif action == "stop":
                ok = await self.orchestrator.stop_service(svc_name)
            elif action == "restart":
                ok = await self.orchestrator.restart_service(svc_name)
            else:
                ok = False
            return {"service": svc_name, "action": action, "success": ok}

        @rt("/api/services/all/{action}", methods=["POST"])
        async def all_control(request, action: str):
            statuses = await self.orchestrator.get_all_service_status()
            results = {}
            for svc in statuses.keys():
                if action == "start":
                    results[svc] = await self.orchestrator.start_service(svc)
                elif action == "stop":
                    results[svc] = await self.orchestrator.stop_service(svc)
                elif action == "restart":
                    results[svc] = await self.orchestrator.restart_service(svc)
            return {"action": action, "results": results}

        return app
    
    async def _render_master_dashboard(self) -> Html:
        """Render the master control dashboard"""
        # Get all service status
        services = await self.orchestrator.get_all_service_status()
        
        # Create service grid
        service_cards = []
        for service_name, service_data in services.items():
            card = DashboardComponent.service_card(service_data)
            service_cards.append(card)
        
        # Calculate summary metrics
        total_services = len(services)
        running_services = sum(1 for s in services.values() if s.get("status") == "running")
        
        content = [
            # Summary metrics
            Div(
                DashboardComponent.metric_card("Total Services", str(total_services)),
                DashboardComponent.metric_card("Running", str(running_services)),
                DashboardComponent.metric_card("Stopped", str(total_services - running_services)),
                DashboardComponent.metric_card("Uptime", self._get_system_uptime()),
                cls="grid-4 mb-8"),
            
            # Service grid
            H2("Service Status", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(*service_cards, cls="grid-3 mb-8"),
            
            # Quick actions
            H2("Quick Actions", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(
                Button("Start All", cls="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700", 
                       onclick="startAllServices()"),
                Button("Stop All", cls="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 ml-2", 
                       onclick="stopAllServices()"),
                Button("Restart All", cls="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 ml-2", 
                       onclick="restartAllServices()"),
                cls="mb-8"),
            
            # System logs
            H2("System Logs", cls="text-xl font-semibold text-gray-900 mb-4"),
            DashboardComponent.log_viewer("system-logs", "400px"),
        ]
        
        # Add master-specific JavaScript
        master_script = Script("""
        // Master dashboard specific functionality
        function startAllServices() {
            fetch('/api/services/all/start', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Started all services:', data))
                .catch(error => console.error('Error:', error));
        }
        
        function stopAllServices() {
            if (confirm('Are you sure you want to stop all services?')) {
                fetch('/api/services/all/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => console.log('Stopped all services:', data))
                    .catch(error => console.error('Error:', error));
            }
        }
        
        function restartAllServices() {
            fetch('/api/services/all/restart', { method: 'POST' })
                .then(response => response.json())
                .then(data => console.log('Restarted all services:', data))
                .catch(error => console.error('Error:', error));
        }
        
        // Listen for dashboard updates
        window.addEventListener('dashboardUpdate', function(event) {
            const data = event.detail;
            // Update service cards based on new data
            updateServiceCards(data);
        });
        
        function updateServiceCards(data) {
            // Implementation for updating service cards in real-time
            console.log('Updating service cards:', data);
        }
        """)
        
        return Html(
            Head(
                Meta(charset="utf-8"),
                Meta(name="viewport", content="width=device-width, initial-scale=1"),
                Title("Service Dashboard - Master Control"),
                Link(rel="stylesheet", href="https://cdn.tailwindcss.com"),
                Style("""
                /* Master dashboard specific styles */
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
                    min-height: calc(100vh - 120px);
                    border-radius: 20px 20px 0 0;
                    margin-top: 1rem;
                }
                
                /* Enhanced card styling */
                .bg-white {
                    background: rgba(255, 255, 255, 0.95) !important;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: all 0.3s ease;
                }
                
                .bg-white:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                    background: rgba(255, 255, 255, 0.98) !important;
                }
                
                /* Grid layouts with better spacing */
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
                
                /* Enhanced buttons */
                button {
                    transition: all 0.3s ease;
                    font-weight: 600;
                    letter-spacing: 0.5px;
                }
                
                button:hover {
                    transform: translateY(-1px);
                    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
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
                
                /* Connection status indicator */
                #connection-status {
                    animation: pulse 2s infinite;
                }
                
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }
                
                /* Responsive design */
                @media (max-width: 1024px) {
                    .grid-3, .grid-4 { grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
                    .content { padding: 1.5rem; }
                }
                
                @media (max-width: 768px) {
                    .grid-3, .grid-4 { grid-template-columns: 1fr; gap: 1rem; }
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
                """)
            ),
            Body(
                Div(
                    # Header
                    Div(
                        Div(
                            Div(
                                H1("Service Dashboard", cls="text-2xl font-bold mb-2"),
                                # Navigation menu
                                Div(
                                    A("🏠 Master", href="/master", cls="px-3 py-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 text-sm mr-2 transition-all duration-200"),
                                    A("🔌 Socket.IO", href="/socketio", cls="px-3 py-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 text-sm mr-2 transition-all duration-200"),
                                    A("🤖 MCP", href="/mcp", cls="px-3 py-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 text-sm mr-2 transition-all duration-200"),
                                    A("⚡ Plasmo", href="/plasmo", cls="px-3 py-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 text-sm mr-2 transition-all duration-200"),
                                    cls="flex flex-wrap items-center gap-1"),
                                cls="mb-4"),
                            Div(
                                Div(
                                    Div(id="connection-status", cls="w-3 h-3 bg-green-500 rounded-full"),
                                    Span("Live", cls="text-sm ml-2"),
                                    cls="flex items-center mr-4"),
                                Div(
                                    Span("Last update: ", cls="text-sm"),
                                    Span(id="last-update", cls="text-sm font-medium"),
                                    cls="mr-4"),
                                Button("🌙", onclick="toggleTheme()", 
                                       cls="px-3 py-1 rounded-full bg-white bg-opacity-20 hover:bg-opacity-30 transition-all duration-200",
                                       title="Toggle dark mode"),
                                cls="flex items-center"),
                            cls="flex items-center justify-between"),
                        cls="header"
                    ),
                    
                    # Content
                    Div(*content, cls="content"),
                    cls="dashboard-container"),
                
                # Base scripts
                Script("""
                // Dashboard functionality without WebSocket
                function updateConnectionStatus(connected) {
                    const indicator = document.getElementById('connection-status');
                    if (indicator) {
                        indicator.className = connected 
                            ? 'w-3 h-3 bg-green-500 rounded-full'
                            : 'w-3 h-3 bg-red-500 rounded-full';
                    }
                }
                
                function updateLastUpdate() {
                    const timestamp = document.getElementById('last-update');
                    if (timestamp) {
                        timestamp.textContent = new Date().toLocaleTimeString();
                    }
                }
                
                function toggleTheme() {
                    document.body.classList.toggle('dark');
                    localStorage.setItem('darkMode', document.body.classList.contains('dark'));
                }
                
                function refreshPage() {
                    window.location.reload();
                }
                
                // Auto-refresh every 30 seconds
                setInterval(function() {
                    updateLastUpdate();
                }, 1000);
                
                setInterval(refreshPage, 30000);
                
                document.addEventListener('DOMContentLoaded', function() {
                    if (localStorage.getItem('darkMode') === 'true') {
                        document.body.classList.add('dark');
                    }
                    updateConnectionStatus(true);
                    updateLastUpdate();
                });
                """),
                master_script
            )
        )
    

    
    def _get_system_uptime(self) -> str:
        """Get system uptime"""
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            return "N/A"
    
    async def start(self):
        """Start the dashboard server"""
        self.logger.info(f"Starting dashboard server on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)
    
    def run(self):
        """Run the dashboard server (blocking)"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


# Global dashboard server instance
dashboard_server = DashboardServer()


def register_dashboard(service_name: str, dashboard_class: Type[DashboardBase], **kwargs):
    """Convenience function to register a dashboard"""
    dashboard_server.register_dashboard(service_name, dashboard_class, **kwargs)


if __name__ == "__main__":
    # Run dashboard server
    dashboard_server.run() 