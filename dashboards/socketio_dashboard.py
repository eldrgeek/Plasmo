#!/usr/bin/env python3
"""
Socket.IO Service Dashboard
===========================
Real-time dashboard for Socket.IO service monitoring.
"""

import json
import time
import psutil
from typing import Dict, Any, List
from fasthtml.common import *

from .dashboard_base import DashboardBase, DashboardComponent


class SocketIODashboard(DashboardBase):
    """Dashboard for Socket.IO service"""
    
    def __init__(self, service_name: str = "socketio"):
        super().__init__(service_name, "Socket.IO Service Dashboard")
        self.connection_history = []
        self.message_history = []
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get Socket.IO specific dashboard data"""
        return {
            "service_status": self._get_service_status(),
            "connections": self._get_connection_data(),
            "messages": self._get_message_data(),
            "performance": self._get_performance_metrics(),
            "rooms": self._get_room_data(),
            "timestamp": time.time()
        }
    
    def _get_service_status(self) -> Dict[str, Any]:
        """Get Socket.IO service status"""
        try:
            # Check if Socket.IO process is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if any('socketio' in arg.lower() for arg in cmdline):
                    return {
                        "status": "running",
                        "pid": proc.info['pid'],
                        "name": "Socket.IO Server",
                        "port": 3001,
                        "uptime": time.time() - proc.create_time()
                    }
        except:
            pass
        
        return {
            "status": "stopped",
            "name": "Socket.IO Server",
            "port": 3001
        }
    
    def _get_connection_data(self) -> Dict[str, Any]:
        """Get connection statistics"""
        # Mock data - in real implementation, this would connect to Socket.IO metrics
        return {
            "active_connections": 12,
            "total_connections": 45,
            "peak_connections": 20,
            "connection_rate": "2.3/min",
            "recent_connections": [
                {"id": "conn_1", "joined": "2 min ago", "ip": "192.168.1.100"},
                {"id": "conn_2", "joined": "5 min ago", "ip": "192.168.1.101"},
                {"id": "conn_3", "joined": "8 min ago", "ip": "192.168.1.102"},
            ]
        }
    
    def _get_message_data(self) -> Dict[str, Any]:
        """Get message flow statistics"""
        return {
            "messages_per_second": 15.7,
            "total_messages": 1234,
            "message_types": {
                "chat": 45,
                "ping": 30,
                "status": 25
            },
            "recent_messages": [
                {"event": "chat", "room": "general", "timestamp": "12:34:56"},
                {"event": "ping", "room": "lobby", "timestamp": "12:34:55"},
                {"event": "status", "room": "admin", "timestamp": "12:34:53"},
            ]
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "cpu_usage": 12.5,
            "memory_usage": 145.2,  # MB
            "response_time": 23.4,  # ms
            "throughput": "1.2k req/s",
            "error_rate": 0.1  # %
        }
    
    def _get_room_data(self) -> Dict[str, Any]:
        """Get room statistics"""
        return {
            "total_rooms": 8,
            "active_rooms": 5,
            "rooms": [
                {"name": "general", "users": 15, "messages": 245},
                {"name": "tech", "users": 8, "messages": 89},
                {"name": "random", "users": 12, "messages": 156},
                {"name": "admin", "users": 2, "messages": 12},
                {"name": "lobby", "users": 25, "messages": 45},
            ]
        }
    
    def render_content(self, data: Dict[str, Any]) -> List:
        """Render Socket.IO dashboard content"""
        service_data = data.get("service_status", {})
        connections = data.get("connections", {})
        messages = data.get("messages", {})
        performance = data.get("performance", {})
        rooms = data.get("rooms", {})
        
        return [
            # Service status
            Div(*[
                DashboardComponent.service_card(service_data),
                DashboardComponent.metric_card("Active Connections", str(connections.get("active_connections", 0))),
                DashboardComponent.metric_card("Messages/sec", f"{messages.get('messages_per_second', 0):.1f}"),
                DashboardComponent.metric_card("Active Rooms", str(rooms.get("active_rooms", 0))),
            ], cls="grid-4 mb-8"),
            
            # Performance metrics
            H2("Performance Metrics", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div(*[
                DashboardComponent.metric_card("CPU Usage", f"{performance.get('cpu_usage', 0):.1f}%"),
                DashboardComponent.metric_card("Memory", f"{performance.get('memory_usage', 0):.1f} MB"),
                DashboardComponent.metric_card("Response Time", f"{performance.get('response_time', 0):.1f} ms"),
                DashboardComponent.metric_card("Throughput", performance.get("throughput", "0")),
            ], cls="grid-4 mb-8"),
            
                         # Connection details and rooms
            Div(*[
                # Active connections
                Div(*[
                    H3("Active Connections", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div(*[
                        Div(*[
                            Div(f"Connection {conn['id']}", cls="font-medium text-gray-900"),
                            Div(f"IP: {conn['ip']}", cls="text-sm text-gray-600"),
                            Div(f"Joined: {conn['joined']}", cls="text-sm text-gray-500"),
                        ], cls="p-3 bg-gray-50 rounded")
                        for conn in connections.get("recent_connections", [])
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Room statistics
                Div(*[
                    H3("Room Statistics", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div(*[
                        Div(*[
                            Div(*[
                                Div(f"#{room['name']}", cls="font-medium text-gray-900"),
                                Div(f"{room['users']} users", cls="text-sm text-gray-600"),
                                Div(f"{room['messages']} messages", cls="text-sm text-gray-500"),
                            ], cls="p-3 bg-gray-50 rounded flex justify-between items-center")
                            for room in rooms.get("rooms", [])
                        ], cls="space-y-2"),
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
            ], cls="grid-2 mb-8"),
            
            # Message flow and logs
            Div(*[
                # Message types
                Div(*[
                    H3("Message Types", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div(*[
                        Div(*[
                            Span(msg_type.title(), cls="text-sm font-medium text-gray-900"),
                            Span(f"{count}%", cls="text-sm text-gray-600"),
                        ], cls="flex justify-between items-center p-2 bg-gray-50 rounded")
                        for msg_type, count in messages.get("message_types", {}).items()
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Recent messages
                Div(*[
                    H3("Recent Messages", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div(*[
                        Div(*[
                            Span(*[
                                Span(f"[{msg['timestamp']}]", cls="text-xs text-gray-500 font-mono"),
                                Span(msg['event'], cls="text-sm font-medium text-blue-600 mx-2"),
                                Span(f"#{msg['room']}", cls="text-sm text-gray-600"),
                            ], cls="p-2 bg-gray-50 rounded")
                            for msg in messages.get("recent_messages", [])
                        ], cls="space-y-1"),
                    ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                ], cls="grid-2 mb-8"),
            ], cls="grid-2 mb-8"),
            
            # Service logs
            H2("Service Logs", cls="text-xl font-semibold text-gray-900 mb-4"),
            DashboardComponent.log_viewer("socketio-logs", "400px"),
            
            # Custom scripts for Socket.IO dashboard
            Script("""
            // Socket.IO specific dashboard updates
            window.addEventListener('dashboardUpdate', function(event) {
                const data = event.detail;
                updateSocketIOMetrics(data);
            });
            
            function updateSocketIOMetrics(data) {
                // Update connection count
                if (data.connections) {
                    // Update connection widgets
                    console.log('Updating Socket.IO connections:', data.connections);
                }
                
                // Update message flow
                if (data.messages) {
                    console.log('Updating message flow:', data.messages);
                }
                
                // Update performance metrics
                if (data.performance) {
                    console.log('Updating performance metrics:', data.performance);
                }
            }
            """)
        ] 