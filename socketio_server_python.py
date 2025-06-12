#!/usr/bin/env python3
"""
Python Socket.IO Server for Plasmo Extension with FastAPI.
Replacement for socketio_server.js with enhanced features and cross-platform support.
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import uvicorn
import socketio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic Models
class CommandPayload(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class AICompletionSignal(BaseModel):
    completion_id: str
    status: str = "completed"
    timestamp: Optional[str] = None
    summary: Optional[str] = None

# Global state management
connected_extensions: Dict[str, Dict] = {}
completion_signals: Dict[str, Dict] = {}
test_results: Dict[str, Dict] = {}

# Initialize FastAPI app
app = FastAPI(
    title="Plasmo Extension Socket.IO Server",
    description="Python-based Socket.IO server for Chrome extension communication",
    version="1.0.0"
)

# Initialize Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi'
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"🔌 Client connected: {sid}")
    
@sio.event  
async def disconnect(sid):
    """Handle client disconnection"""
    logger.info(f"❌ Client disconnected: {sid}")
    if sid in connected_extensions:
        del connected_extensions[sid]

@sio.event
async def extension_register(sid, data):
    """Handle extension registration"""
    logger.info(f"📱 Extension registered: {data}")
    
    connected_extensions[sid] = {
        'extensionId': data.get('extensionId'),
        'timestamp': data.get('timestamp'),
        'socket_id': sid
    }
    
    await sio.emit('registration_confirmed', {
        'message': 'Extension successfully registered',
        'serverId': sid
    }, room=sid)

# REST API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the main web interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Plasmo Socket.IO Server (Python)</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            .header {
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            .status {
                padding: 15px;
                margin: 15px 0;
                border-radius: 5px;
                border-left: 4px solid #007bff;
                background: #f8f9fa;
            }
            .endpoint {
                background: #f1f1f1;
                padding: 10px;
                margin: 10px 0;
                border-radius: 5px;
                font-family: monospace;
            }
            .python-badge {
                background: #28a745;
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: bold;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
            }
            button:hover { background: #0056b3; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="header">
                🐍 Plasmo Socket.IO Server 
                <span class="python-badge">Python Implementation</span>
            </h1>
            
            <div class="status">
                <strong>🚀 Server Status:</strong> Running on Python with FastAPI + Socket.IO<br>
                <strong>🔗 WebSocket:</strong> ws://localhost:3001<br>
                <strong>🌐 HTTP API:</strong> http://localhost:3001<br>
                <strong>📊 Connected Extensions:</strong> <span id="ext-count">Loading...</span>
            </div>
            
            <h3>📡 Available Endpoints</h3>
            <div class="endpoint">GET /health - Health check and server info</div>
            <div class="endpoint">GET /api/extensions - List connected Chrome extensions</div>
            <div class="endpoint">POST /api/command/broadcast - Send commands to all extensions</div>
            <div class="endpoint">WebSocket /socket.io/ - Real-time communication</div>
            
            <h3>🧪 Quick Tests</h3>
            <button onclick="testHealth()">Test Health</button>
            <button onclick="testExtensions()">List Extensions</button>
            <button onclick="refreshStatus()">Refresh Status</button>
            
            <div id="test-results" style="margin-top: 20px;"></div>
        </div>
        
        <script src="/socket.io/socket.io.js"></script>
        <script>
            const socket = io();
            
            socket.on('connect', () => {
                showResult('✅ Connected to Python Socket.IO server', 'success');
                refreshStatus();
            });
            
            socket.on('disconnect', () => {
                showResult('❌ Disconnected from server', 'error');
            });
            
            async function testHealth() {
                try {
                    const response = await fetch('/health');
                    const data = await response.json();
                    showResult('Health Check: ' + JSON.stringify(data, null, 2), 'success');
                } catch (error) {
                    showResult('Health Check Error: ' + error.message, 'error');
                }
            }
            
            async function testExtensions() {
                try {
                    const response = await fetch('/api/extensions');
                    const data = await response.json();
                    showResult('Extensions: ' + JSON.stringify(data, null, 2), 'success');
                } catch (error) {
                    showResult('Extensions Error: ' + error.message, 'error');
                }
            }
            
            async function refreshStatus() {
                try {
                    const response = await fetch('/api/extensions');
                    const data = await response.json();
                    document.getElementById('ext-count').textContent = data.count;
                } catch (error) {
                    document.getElementById('ext-count').textContent = 'Error';
                }
            }
            
            function showResult(message, type) {
                const resultsDiv = document.getElementById('test-results');
                const resultElement = document.createElement('div');
                resultElement.style.padding = '10px';
                resultElement.style.margin = '5px 0';
                resultElement.style.borderRadius = '5px';
                resultElement.style.backgroundColor = type === 'success' ? '#d4edda' : '#f8d7da';
                resultElement.style.borderLeft = type === 'success' ? '4px solid #28a745' : '4px solid #dc3545';
                resultElement.innerHTML = '<pre>' + message + '</pre>';
                resultsDiv.appendChild(resultElement);
                
                // Auto-remove after 10 seconds
                setTimeout(() => {
                    resultElement.remove();
                }, 10000);
            }
            
            // Initial status load
            refreshStatus();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connected_extensions": len(connected_extensions),
        "implementation": "python"
    }

@app.post("/api/command/broadcast")
async def broadcast_command(command: CommandPayload):
    """Send command to all connected extensions"""
    command_data = {
        "action": command.action,
        "payload": command.payload,
        "timestamp": command.timestamp or datetime.now().isoformat()
    }
    
    sent_count = 0
    for sid in connected_extensions:
        await sio.emit('cursor_command', command_data, room=sid)
        sent_count += 1
        
    return {
        "success": True,
        "message": f"Command sent to {sent_count} extension(s)",
        "command": command_data
    }

@app.get("/api/extensions")
async def get_connected_extensions():
    """Get list of connected extensions"""
    extensions = []
    for sid, ext_data in connected_extensions.items():
        extensions.append({
            "socketId": sid,
            "extensionId": ext_data['extensionId'],
            "timestamp": ext_data['timestamp'],
            "connected": True
        })
        
    return {
        "success": True,
        "extensions": extensions,
        "count": len(extensions)
    }

def main():
    """Main entry point"""
    port = int(os.getenv('SOCKETIO_PORT', 3001))
    host = os.getenv('SOCKETIO_HOST', 'localhost')
    
    logger.info(f"🐍 Starting Python Socket.IO Server")
    logger.info(f"🚀 Server will run on http://{host}:{port}")
    
    uvicorn.run(
        socket_app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main() 