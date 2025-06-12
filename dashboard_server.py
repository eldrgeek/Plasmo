#!/usr/bin/env python3
"""
Dashboard Server for Plasmo Extension Services
==============================================

Provides web dashboards for:
1. Service Management - Control all services (MCP, Socket.IO, Plasmo, Tests)
2. MCP Server Monitoring - Detailed MCP server status and control

Features:
- Real-time status updates via WebSocket
- Service start/stop/restart controls
- Log viewing and monitoring
- Health check endpoints
- Responsive web interface
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
import psutil
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import our service manager
from service_manager import ServiceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DashboardServer:
    def __init__(self, port: int = 8080):
        self.app = FastAPI(title="Plasmo Services Dashboard", version="1.0.0")
        self.port = port
        self.service_manager = ServiceManager()
        self.websocket_connections: List[WebSocket] = []
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        # Health check
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "service": "dashboard_server",
                "timestamp": datetime.now().isoformat(),
                "port": self.port
            }
        
        # Main service dashboard
        @self.app.get("/", response_class=HTMLResponse)
        async def service_dashboard():
            return self.generate_service_dashboard()
            
        # MCP-specific dashboard
        @self.app.get("/mcp", response_class=HTMLResponse)
        async def mcp_dashboard():
            return self.generate_mcp_dashboard()
            
        # API endpoints for service control
        @self.app.get("/api/services/status")
        async def get_services_status():
            return self.service_manager.get_service_status()
            
        @self.app.post("/api/services/{service_name}/start")
        async def start_service(service_name: str):
            success = await self.service_manager.start_service_async(service_name)
            await self.broadcast_status_update()
            return {"success": success, "service": service_name, "action": "start"}
            
        @self.app.post("/api/services/{service_name}/stop")
        async def stop_service(service_name: str):
            success = self.service_manager.stop_service(service_name)
            await self.broadcast_status_update()
            return {"success": success, "service": service_name, "action": "stop"}
            
        @self.app.post("/api/services/{service_name}/restart")
        async def restart_service(service_name: str):
            success = self.service_manager.restart_service(service_name)
            await self.broadcast_status_update()
            return {"success": success, "service": service_name, "action": "restart"}
            
        @self.app.post("/api/services/start-all")
        async def start_all_services():
            results = await self.service_manager.start_all_services_async()
            await self.broadcast_status_update()
            return {"results": results, "action": "start_all"}
            
        @self.app.post("/api/services/stop-all")
        async def stop_all_services():
            services = ["tests", "dashboard", "plasmo", "socketio", "mcp"]
            results = {}
            for service in services:
                if service != "dashboard":  # Don't stop ourselves
                    results[service] = self.service_manager.stop_service(service)
            await self.broadcast_status_update()
            return {"results": results, "action": "stop_all"}
            
        # MCP server specific endpoints
        @self.app.get("/api/mcp/status")
        async def get_mcp_status():
            return await self.get_detailed_mcp_status()
            
        @self.app.get("/api/mcp/tools")
        async def get_mcp_tools():
            return await self.get_mcp_tools_list()
            
        @self.app.get("/api/logs/{service_name}")
        async def get_service_logs(service_name: str, lines: int = 50):
            return await self.get_service_logs(service_name, lines)
            
        # WebSocket endpoint for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_connections.append(websocket)
            logger.info(f"WebSocket connected. Total connections: {len(self.websocket_connections)}")
            
            try:
                # Send initial status
                status = self.service_manager.get_service_status()
                await websocket.send_json({
                    "type": "status_update",
                    "data": status,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Keep connection alive
                while True:
                    await websocket.receive_text()
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
                logger.info(f"WebSocket disconnected. Total connections: {len(self.websocket_connections)}")
                
    async def broadcast_status_update(self):
        """Broadcast status update to all connected WebSocket clients"""
        if not self.websocket_connections:
            return
            
        status = self.service_manager.get_service_status()
        message = {
            "type": "status_update",
            "data": status,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all connected clients
        disconnected = []
        for websocket in self.websocket_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send WebSocket message: {e}")
                disconnected.append(websocket)
                
        # Remove disconnected clients
        for ws in disconnected:
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)
                
    async def get_detailed_mcp_status(self) -> Dict:
        """Get detailed MCP server status"""
        basic_status = self.service_manager.get_service_status().get("mcp", {})
        
        detailed = {
            **basic_status,
            "tools_count": 0,
            "memory_usage": 0,
            "cpu_percent": 0,
            "uptime": "unknown",
            "version": "unknown",
            "transport": "stdio",
            "health_endpoints": []
        }
        
        # Get process details if running
        if basic_status.get("running") and basic_status.get("pid"):
            try:
                process = psutil.Process(basic_status["pid"])
                detailed.update({
                    "memory_usage": process.memory_info().rss / 1024 / 1024,  # MB
                    "cpu_percent": process.cpu_percent(),
                    "uptime": str(datetime.now() - datetime.fromtimestamp(process.create_time()))
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return detailed
        
    async def get_mcp_tools_list(self) -> List[Dict]:
        """Get list of available MCP tools"""
        # This would require introspecting the MCP server
        # For now, return a static list of known tools
        return [
            {"name": "read_file", "description": "Read file contents"},
            {"name": "write_file", "description": "Write content to file"},
            {"name": "list_files", "description": "List files in directory"},
            {"name": "search_in_files", "description": "Search for patterns in files"},
            {"name": "get_project_structure", "description": "Get project directory structure"},
            {"name": "analyze_code", "description": "Analyze code metrics"},
            {"name": "run_git_command", "description": "Execute git commands"},
            {"name": "create_sqlite_db", "description": "Create SQLite database"},
            {"name": "query_sqlite_db", "description": "Query SQLite database"},
            {"name": "connect_to_chrome", "description": "Connect to Chrome Debug Protocol"},
            {"name": "execute_javascript_fixed", "description": "Execute JavaScript in Chrome"},
            {"name": "tell_chatgpt_to_and_wait", "description": "Automate ChatGPT interactions"}
        ]
        
    async def get_service_logs(self, service_name: str, lines: int = 50) -> Dict:
        """Get recent logs for a service"""
        config = self.service_manager.service_configs.get(service_name)
        if not config or not config.log_file:
            return {"error": f"No log file configured for service: {service_name}"}
            
        log_path = self.logs_dir / config.log_file
        if not log_path.exists():
            return {"error": f"Log file not found: {log_path}"}
            
        try:
            # Read last N lines
            proc = await asyncio.create_subprocess_exec(
                "tail", "-n", str(lines), str(log_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return {
                    "service": service_name,
                    "lines": lines,
                    "content": stdout.decode('utf-8', errors='ignore'),
                    "log_file": str(log_path)
                }
            else:
                return {"error": f"Failed to read logs: {stderr.decode()}"}
                
        except Exception as e:
            return {"error": f"Exception reading logs: {str(e)}"}
            
    def generate_service_dashboard(self) -> str:
        """Generate HTML for the main service dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plasmo Services Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .nav { margin-bottom: 30px; }
        .nav a { background: #fff; padding: 12px 24px; margin-right: 10px; text-decoration: none; color: #333; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: all 0.3s; }
        .nav a:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .service-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .service-card:hover { transform: translateY(-5px); }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .service-name { font-size: 1.3em; font-weight: bold; }
        .status-indicator { width: 12px; height: 12px; border-radius: 50%; margin-left: 10px; }
        .status-running { background: #4CAF50; }
        .status-stopped { background: #f44336; }
        .service-info { margin-bottom: 15px; }
        .service-info div { margin-bottom: 5px; color: #666; }
        .service-controls button { background: #2196F3; color: white; border: none; padding: 8px 16px; margin-right: 10px; border-radius: 5px; cursor: pointer; transition: background 0.3s; }
        .service-controls button:hover { background: #1976D2; }
        .service-controls button.stop { background: #f44336; }
        .service-controls button.stop:hover { background: #d32f2f; }
        .service-controls button.restart { background: #FF9800; }
        .service-controls button.restart:hover { background: #F57C00; }
        .global-controls { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .global-controls h3 { margin-bottom: 15px; color: #333; }
        .global-controls button { background: #4CAF50; color: white; border: none; padding: 12px 24px; margin-right: 15px; border-radius: 5px; cursor: pointer; font-size: 1em; transition: all 0.3s; }
        .global-controls button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .global-controls button.stop-all { background: #f44336; }
        .logs-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .logs-section h3 { margin-bottom: 15px; color: #333; }
        .log-viewer { background: #1e1e1e; color: #d4d4d4; padding: 15px; border-radius: 5px; font-family: 'Courier New', monospace; font-size: 0.9em; max-height: 300px; overflow-y: auto; }
        .connection-status { position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white; padding: 10px 15px; border-radius: 5px; font-size: 0.9em; }
        .connection-status.disconnected { background: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Plasmo Services Dashboard</h1>
            <p>Monitor and control all your Plasmo extension services in real-time</p>
        </div>
        
        <div class="nav">
            <a href="/">📊 Services</a>
            <a href="/mcp">🔧 MCP Server</a>
        </div>
        
        <div class="connection-status" id="connectionStatus">🟢 Connected</div>
        
        <div class="global-controls">
            <h3>Global Controls</h3>
            <button onclick="startAllServices()">🚀 Start All Services</button>
            <button onclick="stopAllServices()" class="stop-all">🛑 Stop All Services</button>
            <button onclick="refreshStatus()">🔄 Refresh Status</button>
        </div>
        
        <div class="services-grid" id="servicesGrid">
            <!-- Services will be populated by JavaScript -->
        </div>
        
        <div class="logs-section">
            <h3>Service Logs</h3>
            <select id="logService" onchange="loadLogs()">
                <option value="">Select a service...</option>
                <option value="mcp">MCP Server</option>
                <option value="socketio">Socket.IO Server</option>
                <option value="dashboard">Dashboard Server</option>
                <option value="plasmo">Plasmo Dev Server</option>
                <option value="tests">Test Runner</option>
            </select>
            <div class="log-viewer" id="logViewer">Select a service to view logs...</div>
        </div>
    </div>

    <script>
        let ws = null;
        let servicesData = {};
        
        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws`;
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('connectionStatus').textContent = '🟢 Connected';
                document.getElementById('connectionStatus').className = 'connection-status';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'status_update') {
                    servicesData = data.data;
                    updateServicesDisplay();
                }
            };
            
            ws.onclose = function() {
                document.getElementById('connectionStatus').textContent = '🔴 Disconnected';
                document.getElementById('connectionStatus').className = 'connection-status disconnected';
                // Attempt to reconnect after 3 seconds
                setTimeout(connectWebSocket, 3000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateServicesDisplay() {
            const grid = document.getElementById('servicesGrid');
            grid.innerHTML = '';
            
            Object.entries(servicesData).forEach(([serviceName, info]) => {
                const card = document.createElement('div');
                card.className = 'service-card';
                
                const statusClass = info.running ? 'status-running' : 'status-stopped';
                const statusText = info.running ? 'Running' : 'Stopped';
                
                card.innerHTML = `
                    <div class="service-header">
                        <span class="service-name">${serviceName.toUpperCase()}</span>
                        <div class="status-indicator ${statusClass}" title="${statusText}"></div>
                    </div>
                    <div class="service-info">
                        <div><strong>Implementation:</strong> ${info.implementation}</div>
                        <div><strong>Port:</strong> ${info.port || 'N/A'}</div>
                        <div><strong>PID:</strong> ${info.pid || 'N/A'}</div>
                        <div><strong>Status:</strong> ${statusText}</div>
                    </div>
                    <div class="service-controls">
                        <button onclick="startService('${serviceName}')" ${info.running ? 'disabled' : ''}>▶️ Start</button>
                        <button onclick="stopService('${serviceName}')" class="stop" ${!info.running ? 'disabled' : ''}>⏹️ Stop</button>
                        <button onclick="restartService('${serviceName}')" class="restart" ${!info.running ? 'disabled' : ''}>🔄 Restart</button>
                    </div>
                `;
                
                grid.appendChild(card);
            });
        }
        
        async function apiCall(url, method = 'GET') {
            try {
                const response = await fetch(url, { method });
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                alert('Operation failed. Check console for details.');
            }
        }
        
        async function startService(serviceName) {
            await apiCall(`/api/services/${serviceName}/start`, 'POST');
        }
        
        async function stopService(serviceName) {
            await apiCall(`/api/services/${serviceName}/stop`, 'POST');
        }
        
        async function restartService(serviceName) {
            await apiCall(`/api/services/${serviceName}/restart`, 'POST');
        }
        
        async function startAllServices() {
            await apiCall('/api/services/start-all', 'POST');
        }
        
        async function stopAllServices() {
            await apiCall('/api/services/stop-all', 'POST');
        }
        
        async function refreshStatus() {
            const status = await apiCall('/api/services/status');
            servicesData = status;
            updateServicesDisplay();
        }
        
        async function loadLogs() {
            const serviceName = document.getElementById('logService').value;
            if (!serviceName) return;
            
            const logViewer = document.getElementById('logViewer');
            logViewer.textContent = 'Loading logs...';
            
            const logs = await apiCall(`/api/logs/${serviceName}`);
            if (logs.error) {
                logViewer.textContent = `Error: ${logs.error}`;
            } else {
                logViewer.textContent = logs.content || 'No logs available';
            }
        }
        
        // Initialize
        connectWebSocket();
        refreshStatus();
    </script>
</body>
</html>
        """
        
    def generate_mcp_dashboard(self) -> str:
        """Generate HTML for the MCP server dashboard"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Server Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .nav { margin-bottom: 30px; }
        .nav a { background: #fff; padding: 12px 24px; margin-right: 10px; text-decoration: none; color: #333; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); transition: all 0.3s; }
        .nav a:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; color: #333; margin-bottom: 10px; }
        .stat-label { color: #666; font-size: 0.9em; }
        .tools-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .tools-section h3 { margin-bottom: 15px; color: #333; }
        .tools-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }
        .tool-card { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 15px; }
        .tool-name { font-weight: bold; color: #495057; margin-bottom: 5px; }
        .tool-description { color: #6c757d; font-size: 0.9em; }
        .status-section { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status-section h3 { margin-bottom: 15px; color: #333; }
        .status-item { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }
        .status-item:last-child { border-bottom: none; }
        .status-label { font-weight: 500; color: #333; }
        .status-value { color: #666; }
        .controls { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px; }
        .controls button { background: #ff6b6b; color: white; border: none; padding: 12px 24px; margin-right: 15px; border-radius: 5px; cursor: pointer; font-size: 1em; transition: all 0.3s; }
        .controls button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        .controls button.stop { background: #dc3545; }
        .controls button.restart { background: #fd7e14; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 MCP Server Dashboard</h1>
            <p>Monitor and control your Model Context Protocol server</p>
        </div>
        
        <div class="nav">
            <a href="/">📊 Services</a>
            <a href="/mcp">🔧 MCP Server</a>
        </div>
        
        <div class="controls">
            <h3>MCP Server Controls</h3>
            <button onclick="startMCP()">🚀 Start MCP</button>
            <button onclick="stopMCP()" class="stop">🛑 Stop MCP</button>
            <button onclick="restartMCP()" class="restart">🔄 Restart MCP</button>
            <button onclick="refreshMCPStatus()">📊 Refresh Status</button>
        </div>
        
        <div class="stats-grid" id="statsGrid">
            <!-- Stats will be populated by JavaScript -->
        </div>
        
        <div class="tools-section">
            <h3>Available MCP Tools</h3>
            <div class="tools-grid" id="toolsGrid">
                <!-- Tools will be populated by JavaScript -->
            </div>
        </div>
        
        <div class="status-section">
            <h3>Detailed Status</h3>
            <div id="statusDetails">
                <!-- Status details will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        let mcpStatus = {};
        let mcpTools = [];
        
        async function apiCall(url, method = 'GET') {
            try {
                const response = await fetch(url, { method });
                return await response.json();
            } catch (error) {
                console.error('API call failed:', error);
                alert('Operation failed. Check console for details.');
            }
        }
        
        async function loadMCPStatus() {
            mcpStatus = await apiCall('/api/mcp/status');
            updateStatsDisplay();
            updateStatusDetails();
        }
        
        async function loadMCPTools() {
            mcpTools = await apiCall('/api/mcp/tools');
            updateToolsDisplay();
        }
        
        function updateStatsDisplay() {
            const grid = document.getElementById('statsGrid');
            grid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${mcpStatus.running ? '🟢' : '🔴'}</div>
                    <div class="stat-label">Server Status</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${mcpStatus.pid || 'N/A'}</div>
                    <div class="stat-label">Process ID</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Math.round(mcpStatus.memory_usage || 0)} MB</div>
                    <div class="stat-label">Memory Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${Math.round(mcpStatus.cpu_percent || 0)}%</div>
                    <div class="stat-label">CPU Usage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${mcpTools.length}</div>
                    <div class="stat-label">Available Tools</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${mcpStatus.uptime || 'N/A'}</div>
                    <div class="stat-label">Uptime</div>
                </div>
            `;
        }
        
        function updateToolsDisplay() {
            const grid = document.getElementById('toolsGrid');
            grid.innerHTML = mcpTools.map(tool => `
                <div class="tool-card">
                    <div class="tool-name">${tool.name}</div>
                    <div class="tool-description">${tool.description}</div>
                </div>
            `).join('');
        }
        
        function updateStatusDetails() {
            const details = document.getElementById('statusDetails');
            details.innerHTML = `
                <div class="status-item">
                    <span class="status-label">Implementation:</span>
                    <span class="status-value">${mcpStatus.implementation || 'python'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Transport:</span>
                    <span class="status-value">${mcpStatus.transport || 'stdio'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Version:</span>
                    <span class="status-value">${mcpStatus.version || 'Unknown'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Command:</span>
                    <span class="status-value">${mcpStatus.command || 'N/A'}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Log File:</span>
                    <span class="status-value">${mcpStatus.log_file || 'mcp_server.log'}</span>
                </div>
            `;
        }
        
        async function startMCP() {
            await apiCall('/api/services/mcp/start', 'POST');
            setTimeout(refreshMCPStatus, 1000);
        }
        
        async function stopMCP() {
            await apiCall('/api/services/mcp/stop', 'POST');
            setTimeout(refreshMCPStatus, 1000);
        }
        
        async function restartMCP() {
            await apiCall('/api/services/mcp/restart', 'POST');
            setTimeout(refreshMCPStatus, 1000);
        }
        
        async function refreshMCPStatus() {
            await loadMCPStatus();
        }
        
        // Initialize
        loadMCPStatus();
        loadMCPTools();
        
        // Auto-refresh every 30 seconds
        setInterval(loadMCPStatus, 30000);
    </script>
</body>
</html>
        """
    
    async def start_server(self):
        """Start the dashboard server"""
        logger.info(f"🚀 Starting Dashboard Server on http://localhost:{self.port}")
        config = uvicorn.Config(
            app=self.app,
            host="localhost",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

async def main():
    """Main entry point"""
    dashboard = DashboardServer(port=8080)
    
    try:
        await dashboard.start_server()
    except KeyboardInterrupt:
        logger.info("🛑 Dashboard Server stopped")

if __name__ == "__main__":
    asyncio.run(main()) 