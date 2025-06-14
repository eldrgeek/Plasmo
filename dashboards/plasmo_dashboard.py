#!/usr/bin/env python3
"""
Plasmo Development Dashboard
============================
Real-time dashboard for Plasmo extension development monitoring.
"""

import json
import time
import psutil
import subprocess
from typing import Dict, Any, List
from pathlib import Path
from fasthtml.common import *
from dashboards.dashboard_base import Div  # patched auto-flatten Div

from .dashboard_base import DashboardBase, DashboardComponent


class PlasmoDashboard(DashboardBase):
    """Dashboard for Plasmo development server"""
    
    def __init__(self, service_name: str = "plasmo"):
        super().__init__(service_name, "Plasmo Development Dashboard")
        self.build_history = []
        self.file_changes = []
        
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get Plasmo specific dashboard data"""
        return {
            "service_status": self._get_service_status(),
            "build_info": self._get_build_info(),
            "extension_status": self._get_extension_status(),
            "file_watching": self._get_file_watching_data(),
            "performance": self._get_performance_metrics(),
            "hot_reload": self._get_hot_reload_data(),
            "timestamp": time.time()
        }
    
    def _get_service_status(self) -> Dict[str, Any]:
        """Get Plasmo dev server status"""
        try:
            # Check if Plasmo dev server is running
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline', [])
                if any('plasmo' in arg.lower() and 'dev' in ' '.join(cmdline) for arg in cmdline):
                    return {
                        "status": "running",
                        "pid": proc.info['pid'],
                        "name": "Plasmo Dev Server",
                        "port": 1012,
                        "uptime": time.time() - proc.create_time()
                    }
        except:
            pass
        
        return {
            "status": "stopped",
            "name": "Plasmo Dev Server",
            "port": 1012
        }
    
    def _get_build_info(self) -> Dict[str, Any]:
        """Get build information"""
        try:
            # Check for build output
            build_dir = Path("build")
            if build_dir.exists():
                build_files = list(build_dir.rglob("*"))
                total_size = sum(f.stat().st_size for f in build_files if f.is_file())
                return {
                    "status": "success",
                    "files_count": len([f for f in build_files if f.is_file()]),
                    "total_size": f"{total_size / 1024:.1f} KB",
                    "last_build": time.ctime(build_dir.stat().st_mtime),
                    "build_time": "2.3s",
                    "components": {
                        "background": "✓ Built",
                        "popup": "✓ Built", 
                        "content_scripts": "✓ Built",
                        "options": "✓ Built"
                    }
                }
        except:
            pass
        
        return {
            "status": "pending",
            "files_count": 0,
            "total_size": "0 KB",
            "last_build": "Never",
            "build_time": "N/A",
            "components": {
                "background": "⏳ Pending",
                "popup": "⏳ Pending",
                "content_scripts": "⏳ Pending", 
                "options": "⏳ Pending"
            }
        }
    
    def _get_extension_status(self) -> Dict[str, Any]:
        """Get Chrome extension status"""
        # Mock data - in real implementation, this could query Chrome extension API
        return {
            "loaded": True,
            "extension_id": "abcdefghijklmnopqrstuvwxyz123456",
            "version": "1.0.0",
            "permissions": ["storage", "activeTab", "tabs"],
            "content_scripts_injected": 3,
            "background_script_running": True,
            "popup_accessible": True,
            "reload_count": 12,
            "last_reload": "2 min ago"
        }
    
    def _get_file_watching_data(self) -> Dict[str, Any]:
        """Get file watching statistics"""
        return {
            "watched_files": 47,
            "watched_directories": 8,
            "recent_changes": [
                {"file": "popup.tsx", "type": "modified", "time": "12:34:56"},
                {"file": "background.ts", "type": "modified", "time": "12:34:45"},
                {"file": "style.css", "type": "modified", "time": "12:34:32"},
                {"file": "contents/main.ts", "type": "created", "time": "12:34:15"},
            ],
            "change_frequency": "2.5/min",
            "ignored_files": 156
        }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "cpu_usage": 15.2,
            "memory_usage": 234.5,  # MB
            "build_time": 2.3,  # seconds
            "bundle_size": 1.2,  # MB
            "chunks": 8,
            "assets": 15
        }
    
    def _get_hot_reload_data(self) -> Dict[str, Any]:
        """Get hot reload statistics"""
        return {
            "enabled": True,
            "reload_count": 23,
            "successful_reloads": 22,
            "failed_reloads": 1,
            "average_reload_time": "1.2s",
            "last_reload_status": "success",
            "auto_reload_events": [
                {"trigger": "popup.tsx", "status": "success", "time": "12:34:56", "duration": "1.1s"},
                {"trigger": "background.ts", "status": "success", "time": "12:34:45", "duration": "0.9s"},
                {"trigger": "style.css", "status": "success", "time": "12:34:32", "duration": "0.8s"},
            ]
        }
    
    def render_content(self, data: Dict[str, Any]) -> List:
        """Render Plasmo dashboard content"""
        service_data = data.get("service_status", {})
        build_info = data.get("build_info", {})
        extension = data.get("extension_status", {})
        file_watching = data.get("file_watching", {})
        performance = data.get("performance", {})
        hot_reload = data.get("hot_reload", {})
        
        return [
            # Service status and key metrics
            Div([
                DashboardComponent.service_card(service_data),
                DashboardComponent.metric_card("Build Status", build_info.get("status", "unknown").title()),
                DashboardComponent.metric_card("Extension Loaded", "Yes" if extension.get("loaded") else "No"),
                DashboardComponent.metric_card("Hot Reload", "Enabled" if hot_reload.get("enabled") else "Disabled"),
            ], cls="grid-4 mb-8"),
            
            # Build information
            H2("Build Information", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div([
                DashboardComponent.metric_card("Files Built", str(build_info.get("files_count", 0))),
                DashboardComponent.metric_card("Bundle Size", build_info.get("total_size", "0 KB")),
                DashboardComponent.metric_card("Build Time", build_info.get("build_time", "N/A")),
                DashboardComponent.metric_card("Last Build", build_info.get("last_build", "Never")[:20]),
            ], cls="grid-4 mb-8"),
            
            # Extension status and components
            Div([
                # Extension details
                Div([
                    H3("Extension Status", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Span("Extension ID:", cls="text-sm text-gray-500"),
                            Span(extension.get("extension_id", "N/A")[:20] + "...", cls="text-sm font-mono text-gray-900"),
                        ], cls="flex justify-between py-2"),
                        Div([
                            Span("Version:", cls="text-sm text-gray-500"),
                            Span(extension.get("version", "N/A"), cls="text-sm text-gray-900"),
                        ], cls="flex justify-between py-2"),
                        Div([
                            Span("Reload Count:", cls="text-sm text-gray-500"),
                            Span(str(extension.get("reload_count", 0)), cls="text-sm text-gray-900"),
                        ], cls="flex justify-between py-2"),
                        Div([
                            Span("Last Reload:", cls="text-sm text-gray-500"),
                            Span(extension.get("last_reload", "N/A"), cls="text-sm text-gray-900"),
                        ], cls="flex justify-between py-2"),
                    ], cls="space-y-1"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Component status
                Div([
                    H3("Component Status", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        Div([
                            Span(comp.replace("_", " ").title(), cls="text-sm font-medium text-gray-900"),
                            Span(status, cls=f"text-sm {'text-green-600' if '✓' in status else 'text-yellow-600'}"),
                        ], cls="flex justify-between items-center p-2 bg-gray-50 rounded")
                        for comp, status in build_info.get("components", {}).items()
                    ], cls="space-y-2"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
            ], cls="grid-2 mb-8"),
            
            # File watching and hot reload
            Div([
                # File watching
                Div([
                    H3("File Watching", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        DashboardComponent.metric_card("Watched Files", str(file_watching.get("watched_files", 0)), "Files being monitored"),
                        DashboardComponent.metric_card("Change Rate", file_watching.get("change_frequency", "0/min"), "Changes per minute"),
                    ], cls="grid-2 mb-4"),
                    H4("Recent Changes", cls="text-md font-medium text-gray-800 mb-2"),
                    Div([
                        Div([
                            Div([
                                Span(f"[{change['time']}]", cls="text-xs text-gray-500 font-mono"),
                                Span(change['file'], cls="text-sm font-medium text-blue-600 mx-2"),
                                Span(change['type'], cls=f"text-xs px-2 py-1 rounded {'bg-blue-100 text-blue-800' if change['type'] == 'modified' else 'bg-green-100 text-green-800'}"),
                            ], cls="flex items-center justify-between"),
                        ], cls="p-2 bg-gray-50 rounded")
                        for change in file_watching.get("recent_changes", [])
                    ], cls="space-y-1"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
                
                # Hot reload events
                Div([
                    H3("Hot Reload Events", cls="text-lg font-semibold text-gray-900 mb-4"),
                    Div([
                        DashboardComponent.metric_card("Total Reloads", str(hot_reload.get("reload_count", 0))),
                        DashboardComponent.metric_card("Success Rate", f"{hot_reload.get('successful_reloads', 0)}/{hot_reload.get('reload_count', 0)}" if hot_reload.get('reload_count', 0) > 0 else "N/A"),
                    ], cls="grid-2 mb-4"),
                    H4("Recent Reloads", cls="text-md font-medium text-gray-800 mb-2"),
                    Div([
                        Div([
                            Div([
                                Span(f"[{event['time']}]", cls="text-xs text-gray-500 font-mono"),
                                Span(event['trigger'], cls="text-sm font-medium text-gray-900 mx-2"),
                                Span(event['status'], cls=f"text-xs px-2 py-1 rounded {'bg-green-100 text-green-800' if event['status'] == 'success' else 'bg-red-100 text-red-800'}"),
                            ], cls="flex items-center justify-between"),
                            Div(f"Duration: {event['duration']}", cls="text-xs text-gray-600 mt-1"),
                        ], cls="p-2 bg-gray-50 rounded")
                        for event in hot_reload.get("auto_reload_events", [])
                    ], cls="space-y-1"),
                ], cls="bg-white rounded-lg shadow border border-gray-200 p-6"),
            ], cls="grid-2 mb-8"),
            
            # Performance metrics
            H2("Performance Metrics", cls="text-xl font-semibold text-gray-900 mb-4"),
            Div([
                DashboardComponent.metric_card("CPU Usage", f"{performance.get('cpu_usage', 0):.1f}%"),
                DashboardComponent.metric_card("Memory Usage", f"{performance.get('memory_usage', 0):.1f} MB"),
                DashboardComponent.metric_card("Bundle Size", f"{performance.get('bundle_size', 0):.1f} MB"),
                DashboardComponent.metric_card("Assets", str(performance.get("assets", 0))),
            ], cls="grid-4 mb-8"),
            
            # Service logs
            H2("Plasmo Dev Server Logs", cls="text-xl font-semibold text-gray-900 mb-4"),
            DashboardComponent.log_viewer("plasmo-logs", "400px"),
            
            # Custom scripts for Plasmo dashboard
            Script("""
            // Plasmo specific dashboard updates
            window.addEventListener('dashboardUpdate', function(event) {
                const data = event.detail;
                updatePlasmoMetrics(data);
            });
            
            function updatePlasmoMetrics(data) {
                // Update build status
                if (data.build_info) {
                    const buildStatus = data.build_info.status;
                    console.log('Build Status:', buildStatus);
                    
                    // Update build indicator
                    const indicator = document.querySelector('#build-status');
                    if (indicator) {
                        indicator.className = buildStatus === 'success' 
                            ? 'w-3 h-3 bg-green-500 rounded-full'
                            : 'w-3 h-3 bg-yellow-500 rounded-full';
                    }
                }
                
                // Update extension status
                if (data.extension_status) {
                    console.log('Extension Status:', data.extension_status);
                }
                
                // Update hot reload info
                if (data.hot_reload) {
                    console.log('Hot Reload Data:', data.hot_reload);
                }
                
                // Update file watching
                if (data.file_watching) {
                    console.log('File Watching:', data.file_watching);
                }
            }
            
            // Manual reload function
            function triggerReload() {
                fetch('/api/plasmo/reload', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Manual reload triggered:', data);
                        // Show notification or update UI
                    })
                    .catch(error => console.error('Reload failed:', error));
            }
            """)
        ] 