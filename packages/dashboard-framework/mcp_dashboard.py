#!/usr/bin/env python3
"""
🔧 MCP SERVER DASHBOARD - Model Context Protocol Management
=========================================================

A clean, modern dashboard for MCP server monitoring:
✨ MCP server status and health
🛠️ Available MCP tools
🔗 Connection monitoring
📊 Usage statistics
📝 Real-time logs
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiofiles
from fasthtml.common import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared head elements with clean styling
COMMON_HEAD = [
    Title("🔧 MCP Server Dashboard"),
    Meta(charset="utf-8"),
    Meta(name="viewport", content="width=device-width, initial-scale=1"),
    Link(rel="preconnect", href="https://fonts.googleapis.com"),
    Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"),
    Link(rel="stylesheet", href="https://fonts.googleapis.com/icon?family=Material+Icons+Round"),
    Style("""
        :root {
            /* Colors */
            --bg-dark: #0d1117;
            --bg-light: #ffffff;
            --fg-dark: #f0f6fc;
            --fg-light: #111827;
            --muted-dark: #8b949e;
            --muted-light: #6b7280;
            --card-dark: #161b22;
            --card-light: #f9fafb;
            --border-dark: #21262d;
            --border-light: #e5e7eb;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --mcp: #9333ea;
            
            /* Layout */
            --gap: 1.25rem;
            --gap-sm: 0.75rem;
            --gap-lg: 2rem;
            --radius: 0.75rem;
            --radius-sm: 0.5rem;
            --header-height: 3.5rem;
            --sidebar-width: 14rem;
            --transition: 0.2s ease;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: var(--fg-dark);
            line-height: 1.6;
            min-height: 100vh;
        }

        body[data-theme="light"] {
            background: var(--bg-light);
            color: var(--fg-light);
        }

        .material-icons-round {
            font-size: 1.2rem;
            vertical-align: middle;
        }

        /* Header */
        .header {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            background: var(--card-dark);
            border-bottom: 1px solid var(--border-dark);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 var(--gap);
            z-index: 1000;
        }

        body[data-theme="light"] .header {
            background: var(--card-light);
            border-bottom-color: var(--border-light);
        }

        .header-brand {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--mcp);
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
        }

        /* Main Content */
        .main-content {
            margin-top: var(--header-height);
            padding: var(--gap-lg);
            max-width: 1400px;
            margin-left: auto;
            margin-right: auto;
        }

        .page-header {
            text-align: center;
            margin-bottom: var(--gap-lg);
        }

        .page-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--fg-dark);
            margin-bottom: var(--gap-sm);
        }

        body[data-theme="light"] .page-title {
            color: var(--fg-light);
        }

        .page-subtitle {
            font-size: 1.1rem;
            color: var(--muted-dark);
            max-width: 600px;
            margin: 0 auto;
        }

        body[data-theme="light"] .page-subtitle {
            color: var(--muted-light);
        }

        /* Cards */
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--gap);
            margin: var(--gap-lg) 0;
        }

        .card {
            background: var(--card-dark);
            border: 1px solid var(--border-dark);
            border-radius: var(--radius);
            padding: var(--gap);
            transition: all var(--transition);
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
        }

        body[data-theme="light"] .card {
            background: var(--card-light);
            border-color: var(--border-light);
        }

        .card-header {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
            margin-bottom: var(--gap);
        }

        .card-icon {
            width: 2rem;
            height: 2rem;
            border-radius: var(--radius-sm);
            background: var(--mcp);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
        }

        /* Status indicators */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }

        .status-running {
            background: var(--success);
            color: white;
        }

        .status-stopped {
            background: var(--error);
            color: white;
        }

        .status-mcp {
            background: var(--mcp);
            color: white;
        }

        /* Logs */
        .log-container {
            background: #0d1117;
            border: 1px solid var(--border-dark);
            border-radius: var(--radius);
            padding: var(--gap);
            font-family: 'JetBrains Mono', Monaco, monospace;
            font-size: 0.85rem;
            max-height: 400px;
            overflow-y: auto;
            color: #f0f6fc;
        }

        .log-line {
            margin: 0.25rem 0;
            white-space: pre-wrap;
        }

        .log-error {
            color: #ff7b72;
        }

        .log-warning {
            color: #f1e05a;
        }

        .log-info {
            color: #79c0ff;
        }

        /* Theme Toggle */
        .theme-toggle {
            width: 2.5rem;
            height: 2.5rem;
            border-radius: 50%;
            background: var(--card-dark);
            border: 1px solid var(--border-dark);
            color: var(--fg-dark);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all var(--transition);
        }

        .theme-toggle:hover {
            transform: scale(1.05);
        }

        body[data-theme="light"] .theme-toggle {
            background: var(--card-light);
            border-color: var(--border-light);
            color: var(--fg-light);
        }

        body[data-theme="light"] .log-container {
            background: #f6f8fa;
            color: #24292f;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .main-content {
                padding: var(--gap);
            }

            .card-grid {
                grid-template-columns: 1fr;
            }

            .page-title {
                font-size: 2rem;
            }
        }
    """)
]

# FastHTML app
app, rt = fast_app(live=True)

def AppHeader():
    """Clean MCP dashboard header"""
    return Header(
        Div(
            I("api", cls="material-icons-round"),
            "MCP Server Dashboard",
            cls="header-brand"
        ),
        Div(
            Button(
                I("light_mode", cls="material-icons-round"),
                cls="theme-toggle",
                onclick="toggleTheme()",
                title="Toggle theme"
            ),
            cls="header-actions"
        ),
        cls="header"
    )

def MCPStatusCard():
    """MCP server status card"""
    return Div(
        Div(
            Div(
                I("api", cls="material-icons-round"),
                cls="card-icon"
            ),
            "MCP Server Status",
            cls="card-header"
        ),
        Div(id="mcp-status", cls="card-content"),
        cls="card"
    )

def MCPToolsCard():
    """Available MCP tools card"""
    return Div(
        Div(
            Div(
                I("build", cls="material-icons-round"),
                cls="card-icon"
            ),
            "Available Tools",
            cls="card-header"
        ),
        Div(id="mcp-tools", cls="card-content"),
        cls="card"
    )

def MCPConnectionsCard():
    """MCP connections card"""
    return Div(
        Div(
            Div(
                I("link", cls="material-icons-round"),
                cls="card-icon"
            ),
            "Connections",
            cls="card-header"
        ),
        Div(id="mcp-connections", cls="card-content"),
        cls="card"
    )

def MCPLogsCard():
    """MCP server logs card"""
    return Div(
        Div(
            Div(
                I("article", cls="material-icons-round"),
                cls="card-icon"
            ),
            "Server Logs",
            cls="card-header"
        ),
        Div(
            Div(id="mcp-logs", cls="log-container"),
            cls="card-content"
        ),
        cls="card",
        style="grid-column: 1 / -1;"
    )

@rt("/api/mcp/status")
async def get_mcp_status():
    """Get MCP server status"""
    try:
        # Check if MCP server is running
        import psutil
        mcp_running = False
        mcp_pid = None
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and 'mcp_server.py' in ' '.join(cmdline):
                    mcp_running = True
                    mcp_pid = proc.info['pid']
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "running": mcp_running,
            "pid": mcp_pid,
            "uptime": "Unknown",
            "memory_usage": "Unknown",
            "connections": 0
        }
    except Exception as e:
        return {"error": str(e)}

@rt("/api/mcp/tools")
async def get_mcp_tools():
    """Get available MCP tools"""
    try:
        # This would ideally connect to the MCP server to get available tools
        # For now, return some mock data based on known MCP tools
        tools = [
            {
                "name": "read_file",
                "description": "Read file contents with enhanced error handling",
                "category": "file_operations"
            },
            {
                "name": "write_file", 
                "description": "Write content to file with backup and validation",
                "category": "file_operations"
            },
            {
                "name": "list_files",
                "description": "List files in directory with pattern matching",
                "category": "file_operations"
            },
            {
                "name": "analyze_code",
                "description": "Analyze code file for comprehensive metrics",
                "category": "analysis"
            },
            {
                "name": "search_in_files",
                "description": "Search for patterns across files",
                "category": "search"
            },
            {
                "name": "connect_to_chrome",
                "description": "Connect to Chrome Debug Protocol",
                "category": "chrome_debug"
            },
            {
                "name": "execute_javascript",
                "description": "Execute JavaScript in Chrome tab",
                "category": "chrome_debug"
            }
        ]
        return {"tools": tools, "count": len(tools)}
    except Exception as e:
        return {"error": str(e)}

@rt("/api/mcp/logs")
async def get_mcp_logs():
    """Get recent MCP server logs"""
    try:
        log_file = Path("mcp_server.log")
        if log_file.exists():
            async with aiofiles.open(log_file, 'r') as f:
                content = await f.read()
                lines = content.split('\n')[-50:]  # Last 50 lines
                return {"logs": lines}
        return {"logs": ["No log file found"]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {e}"]}

@rt("/")
def get():
    """Main MCP dashboard page"""
    return Html(
        Head(*COMMON_HEAD),
        Body(
            AppHeader(),
            Main(
                Div(
                    H1("MCP Server Dashboard", cls="page-title"),
                    P("Monitor and manage your Model Context Protocol server", cls="page-subtitle"),
                    cls="page-header"
                ),
                Div(
                    MCPStatusCard(),
                    MCPToolsCard(),
                    MCPConnectionsCard(),
                    MCPLogsCard(),
                    cls="card-grid"
                ),
                cls="main-content"
            ),
            Script("""
                // Theme management
                const savedTheme = localStorage.getItem('theme') || 'dark';
                document.body.dataset.theme = savedTheme;

                function toggleTheme() {
                    const currentTheme = document.body.dataset.theme;
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    document.body.dataset.theme = newTheme;
                    localStorage.setItem('theme', newTheme);
                }

                // Load MCP data
                async function loadMCPStatus() {
                    try {
                        const response = await fetch('/api/mcp/status');
                        const data = await response.json();
                        
                        const statusEl = document.getElementById('mcp-status');
                        if (data.error) {
                            statusEl.innerHTML = `<p style="color: var(--error);">Error: ${data.error}</p>`;
                            return;
                        }
                        
                        const statusBadge = data.running ? 
                            '<span class="status-badge status-running">Running</span>' :
                            '<span class="status-badge status-stopped">Stopped</span>';
                            
                        statusEl.innerHTML = `
                            <div style="margin-bottom: 1rem;">${statusBadge}</div>
                            <div style="font-size: 0.9rem; color: var(--muted-dark);">
                                ${data.pid ? `<div>PID: ${data.pid}</div>` : ''}
                                <div>Uptime: ${data.uptime}</div>
                                <div>Memory: ${data.memory_usage}</div>
                                <div>Connections: ${data.connections}</div>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Failed to load MCP status:', error);
                    }
                }

                async function loadMCPTools() {
                    try {
                        const response = await fetch('/api/mcp/tools');
                        const data = await response.json();
                        
                        const toolsEl = document.getElementById('mcp-tools');
                        if (data.error) {
                            toolsEl.innerHTML = `<p style="color: var(--error);">Error: ${data.error}</p>`;
                            return;
                        }
                        
                        const categories = {};
                        data.tools.forEach(tool => {
                            if (!categories[tool.category]) {
                                categories[tool.category] = [];
                            }
                            categories[tool.category].push(tool);
                        });
                        
                        let html = `<div style="margin-bottom: 1rem;"><span class="status-badge status-mcp">${data.count} Tools</span></div>`;
                        
                        Object.entries(categories).forEach(([category, tools]) => {
                            html += `
                                <div style="margin-bottom: 1rem;">
                                    <h4 style="font-size: 0.9rem; color: var(--mcp); margin-bottom: 0.5rem; text-transform: capitalize;">
                                        ${category.replace('_', ' ')}
                                    </h4>
                                    ${tools.map(tool => `
                                        <div style="font-size: 0.85rem; margin: 0.25rem 0; padding: 0.25rem 0;">
                                            <strong>${tool.name}</strong><br>
                                            <span style="color: var(--muted-dark);">${tool.description}</span>
                                        </div>
                                    `).join('')}
                                </div>
                            `;
                        });
                        
                        toolsEl.innerHTML = html;
                    } catch (error) {
                        console.error('Failed to load MCP tools:', error);
                    }
                }

                async function loadMCPLogs() {
                    try {
                        const response = await fetch('/api/mcp/logs');
                        const data = await response.json();
                        
                        const logsEl = document.getElementById('mcp-logs');
                        const logs = data.logs.filter(line => line.trim()).map(line => {
                            let className = 'log-line';
                            if (line.includes('ERROR')) className += ' log-error';
                            else if (line.includes('WARNING')) className += ' log-warning';
                            else if (line.includes('INFO')) className += ' log-info';
                            
                            return `<div class="${className}">${line}</div>`;
                        }).join('');
                        
                        logsEl.innerHTML = logs || '<div class="log-line">No logs available</div>';
                        logsEl.scrollTop = logsEl.scrollHeight;
                    } catch (error) {
                        console.error('Failed to load MCP logs:', error);
                    }
                }

                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    loadMCPStatus();
                    loadMCPTools();
                    loadMCPLogs();
                    
                    // Auto-refresh every 10 seconds
                    setInterval(() => {
                        loadMCPStatus();
                        loadMCPLogs();
                    }, 10000);
                });
            """)
        )
    )

if __name__ == "__main__":
    import uvicorn
    print("🔧 Starting MCP Server Dashboard...")
    print("✨ Features: MCP Monitoring, Tool Discovery, Real-time Logs")
    print("🚀 Access at: http://localhost:8081")
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info") 