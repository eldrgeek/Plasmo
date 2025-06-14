#!/usr/bin/env python3
"""
MCP Server Dashboard
====================
Real-time dashboard for MCP (Model Context Protocol) server monitoring.
"""

import json
import time
import psutil
import requests
from typing import Dict, Any, List
from fasthtml.common import *
from dashboards.dashboard_base import Div  # patched auto-flatten Div

from .dashboard_base import DashboardBase, DashboardComponent


class MCPDashboard(DashboardBase):
    """Dashboard for MCP server"""
    
    def __init__(self, service_name: str = "mcp"):
        super().__init__(service_name, "MCP Server Dashboard")
        self.tool_usage_history = []
        self.request_history = []
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get MCP specific dashboard data"""
        return {
            "service_status": self._get_service_status(),
            "tools": self._get_tool_data(),
            "chrome_debug": self._get_chrome_debug_status(),
            "requests": self._get_request_data(),
            "performance": self._get_performance_metrics(),
            "errors": self._get_error_data(),
            "timestamp": time.time()
        }
    
    def _get_service_status(self) -> Dict[str, Any]:
        """Get MCP service status"""
        try:
            # Check if MCP server process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if any('mcp_server' in arg for arg in cmdline):
                    return {
                        "status": "running",
                        "pid": proc.info['pid'],
                        "name": "MCP Server",
                        "port": 8001,
                        "uptime": time.time() - proc.create_time()
                    }
        except:
            pass
        
        return {
            "status": "stopped",
            "name": "MCP Server",
            "port": 8001
        }
    
    def _get_tool_data(self) -> Dict[str, Any]:
        """Get MCP tool usage statistics"""
        return {
            "total_tools": 15,
            "active_tools": 12,
            "tool_calls": 234,
            "success_rate": 98.5,
            "most_used_tools": [
                {"name": "read_file", "calls": 45, "success": 44},
                {"name": "write_file", "calls": 32, "success": 32},
                {"name": "list_files", "calls": 28, "success": 28},
                {"name": "chrome_debug", "calls": 15, "success": 14},
                {"name": "execute_command", "calls": 12, "success": 11},
            ],
            "recent_calls": [
                {"tool": "read_file", "args": "services/service_base.py", "status": "success", "time": "12:34:56"},
                {"tool": "chrome_debug", "args": "get_tabs", "status": "success", "time": "12:34:55"},
                {"tool": "list_files", "args": "dashboards/", "status": "success", "time": "12:34:53"},
                {"tool": "write_file", "args": "test.py", "status": "success", "time": "12:34:51"},
            ]
        }
    
    def _get_chrome_debug_status(self) -> Dict[str, Any]:
        """Get Chrome Debug Protocol status"""
        try:
            # Try to connect to Chrome Debug Protocol
            response = requests.get("http://localhost:9222/json", timeout=2)
            if response.status_code == 200:
                tabs = response.json()
                return {
                    "status": "connected",
                    "tabs_count": len(tabs),
                    "active_tab": next((tab for tab in tabs if tab.get("type") == "page"), {}).get("title", "N/A"),
                    "websocket_url": tabs[0].get("webSocketDebuggerUrl", "") if tabs else "",
                    "last_command": "Runtime.evaluate",
                    "commands_sent": 156
                }
        except:
            pass
        
        return {
            "status": "disconnected",
            "tabs_count": 0,
            "active_tab": "N/A",
            "last_command": "N/A",
            "commands_sent": 0
        }
    
    def _get_request_data(self) -> Dict[str, Any]:
        """Get request/response statistics"""
        return {
            "total_requests": 1567,
            "requests_per_minute": 12.4,
            "average_response_time": 45.6,  # ms
            "active_connections": 3,
            "request_types": {
                "file_operations": 45,
                "chrome_debug": 30,
                "system_commands": 15,
                "other": 10
            },
            "status_codes": {
                "success": 95.2,
                "error": 3.8,
                "timeout": 1.0
            }
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "cpu_usage": 8.5,
            "memory_usage": 89.3,  # MB
            "response_time": 45.6,  # ms
            "concurrent_requests": 3,
            "queue_length": 0
        }
    
    def _get_error_data(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "total_errors": 23,
            "error_rate": 1.5,  # %
            "recent_errors": [
                {"time": "12:30:15", "type": "TimeoutError", "tool": "chrome_debug", "message": "Chrome connection timeout"},
                {"time": "12:25:42", "type": "FileNotFoundError", "tool": "read_file", "message": "File not found: test.txt"},
                {"time": "12:20:33", "type": "PermissionError", "tool": "write_file", "message": "Permission denied"},
            ],
            "error_types": {
                "TimeoutError": 8,
                "FileNotFoundError": 6,
                "PermissionError": 5,
                "ConnectionError": 4
            }
        }
    
    def render_content(self, data: Dict[str, Any]) -> List:
        """Render MCP dashboard content"""
        service_data = data.get("service_status", {})
        tools = data.get("tools", {})
        chrome_debug = data.get("chrome_debug", {})
        requests = data.get("requests", {})
        performance = data.get("performance", {})
        errors = data.get("errors", {})
        
        return [
            # Service status and key metrics
            Div([
                DashboardComponent.service_card(service_data),
                DashboardComponent.metric_card("Total Tools", str(tools.get("total_tools", 0))),
                DashboardComponent.metric_card("Tool Calls", str(tools.get("tool_calls", 0))),
                DashboardComponent.metric_card("Success Rate", f"{tools.get('success_rate', 0):.1f}%"),
            ], cls="grid-4 mb-8"),
            
            # Chrome Debug Protocol status
            H2("Chrome Debug Protocol", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div([
                DashboardComponent.metric_card("Status", chrome_debug.get("status", "unknown").title()),
                DashboardComponent.metric_card("Active Tabs", str(chrome_debug.get("tabs_count", 0))),
                DashboardComponent.metric_card("Commands Sent", str(chrome_debug.get("commands_sent", 0))),
                DashboardComponent.metric_card("Active Tab", chrome_debug.get("active_tab", "N/A")[:20] + "..." if len(chrome_debug.get("active_tab", "")) > 20 else chrome_debug.get("active_tab", "N/A")),
            ], cls="grid-4 mb-8"),
            
            # Performance metrics
            H2("Performance Metrics", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div([
                DashboardComponent.metric_card("CPU Usage", f"{performance.get('cpu_usage', 0):.1f}%"),
                DashboardComponent.metric_card("Memory", f"{performance.get('memory_usage', 0):.1f} MB"),
                DashboardComponent.metric_card("Response Time", f"{performance.get('response_time', 0):.1f} ms"),
                DashboardComponent.metric_card("Active Connections", str(performance.get('concurrent_requests', 0))),
            ], cls="grid-4 mb-8"),
            
            # Tool usage and recent activity
            Div([
                # Most used tools
                Div([
                    H3("Most Used Tools", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Div([
                                Span(tool['name'], cls="font-medium text-gray-900"),
                                Span(f"{tool['calls']} calls", cls="text-sm text-gray-600"),
                            ], cls="flex justify-between"),
                            Div([
                                Span(f"Success: {tool['success']}/{tool['calls']}", cls="text-xs text-green-600"),
                                Span(f"{tool['success']/tool['calls']*100:.1f}%" if tool['calls'] > 0 else "0%", cls="text-xs text-gray-500"),
                            ], cls="flex justify-between mt-1"),
                        ], cls="p-3 bg-gray-50 rounded")
                        for tool in tools.get("most_used_tools", [])
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Recent tool calls
                Div([
                    H3("Recent Tool Calls", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Div([
                                Span(f"[{call['time']}]", cls="text-xs text-gray-500 font-mono"),
                                Span(call['tool'], cls="text-sm font-medium text-blue-600 mx-2"),
                                Span(call['status'], cls=f"text-xs px-2 py-1 rounded {'bg-green-100 text-green-800' if call['status'] == 'success' else 'bg-red-100 text-red-800'}"),
                            ], cls="flex items-center justify-between"),
                            Div(call['args'], cls="text-sm text-gray-600 mt-1 truncate"),
                        ], cls="p-3 bg-gray-50 rounded")
                        for call in tools.get("recent_calls", [])
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
            ], cls="grid-2 mb-8"),
            
            # Request statistics and errors
            Div([
                # Request types
                Div([
                    H3("Request Types", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Span(req_type.replace("_", " ").title(), cls="text-sm font-medium text-gray-900"),
                            Span(f"{percentage}%", cls="text-sm text-gray-600"),
                        ], cls="flex justify-between items-center p-2 bg-gray-50 rounded")
                        for req_type, percentage in requests.get("request_types", {}).items()
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Recent errors
                Div([
                    H3("Recent Errors", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Div([
                                Span(f"[{error['time']}]", cls="text-xs text-gray-500 font-mono"),
                                Span(error['type'], cls="text-sm font-medium text-red-600 mx-2"),
                            ], cls="flex items-center"),
                            Div(error['message'], cls="text-sm text-gray-600 mt-1"),
                        ], cls="p-3 bg-red-50 rounded border border-red-200")
                        for error in errors.get("recent_errors", [])
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
            ], cls="grid-2 mb-8"),
            
            # Service logs
            H2("MCP Server Logs", cls="text-xl font-semibold text-gray-900 mb-4"),
            DashboardComponent.log_viewer("mcp-logs", "400px"),
            
            # Custom scripts for MCP dashboard
            Script("""
            // MCP specific dashboard updates
            window.addEventListener('dashboardUpdate', function(event) {
                const data = event.detail;
                updateMCPMetrics(data);
            });
            
            function updateMCPMetrics(data) {
                // Update tool usage
                if (data.tools) {
                    console.log('Updating MCP tool usage:', data.tools);
                }
                
                // Update Chrome debug status
                if (data.chrome_debug) {
                    const status = data.chrome_debug.status;
                    console.log('Chrome Debug Status:', status);
                    
                    // Update connection indicator
                    const indicator = document.querySelector('#chrome-debug-status');
                    if (indicator) {
                        indicator.className = status === 'connected' 
                            ? 'w-3 h-3 bg-green-500 rounded-full'
                            : 'w-3 h-3 bg-red-500 rounded-full';
                    }
                }
                
                // Update performance metrics
                if (data.performance) {
                    console.log('Updating MCP performance:', data.performance);
                }
                
                // Update error counts
                if (data.errors) {
                    console.log('Updating error data:', data.errors);
                }
            }
            """)
        ] 