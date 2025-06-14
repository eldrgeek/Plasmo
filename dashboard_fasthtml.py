#!/usr/bin/env python3
"""
Modern FastHTML SPA Dashboard for Plasmo Extension Services
===========================================================

A Google Cloud Console-inspired Single Page Application for managing:
- Service Management (MCP, SocketIO, Plasmo, Tests, Dashboard, Chrome Debug)
- Real-time monitoring and logs
- Extension management
- Test execution
- Tunnel management

Features:
- Modern, responsive design inspired by Google Cloud Console
- Real-time status updates via WebSocket
- Single Page Application with smooth transitions
- Dark/Light theme support
- Mobile-responsive layout
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
from fasthtml.common import *

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

# FastHTML app with modern styling
app, rt = fast_app(
    live=True,
    hdrs=[
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap"),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/icon?family=Material+Icons"),
        Style("""
            :root {
                --primary: #1a73e8;
                --primary-hover: #1557b0;
                --secondary: #5f6368;
                --success: #137333;
                --warning: #ea8600;
                --error: #d93025;
                --surface: #ffffff;
                --surface-variant: #f8f9fa;
                --surface-container: #f1f3f4;
                --on-surface: #202124;
                --on-surface-variant: #5f6368;
                --outline: #dadce0;
                --outline-variant: #e8eaed;
                --shadow: rgba(60, 64, 67, 0.3);
                --shadow-light: rgba(60, 64, 67, 0.15);
                --border-radius: 8px;
                --border-radius-large: 12px;
                --spacing-xs: 4px;
                --spacing-sm: 8px;
                --spacing-md: 16px;
                --spacing-lg: 24px;
                --spacing-xl: 32px;
            }
            
            [data-theme="dark"] {
                --surface: #202124;
                --surface-variant: #303134;
                --surface-container: #292a2d;
                --on-surface: #e8eaed;
                --on-surface-variant: #9aa0a6;
                --outline: #5f6368;
                --outline-variant: #3c4043;
                --shadow: rgba(0, 0, 0, 0.3);
                --shadow-light: rgba(0, 0, 0, 0.15);
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--surface-variant);
                color: var(--on-surface);
                line-height: 1.5;
                overflow-x: hidden;
            }
            
            .app-container {
                display: flex;
                min-height: 100vh;
            }
            
            /* Header */
            .header {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                height: 64px;
                background: var(--surface);
                border-bottom: 1px solid var(--outline-variant);
                display: flex;
                align-items: center;
                padding: 0 var(--spacing-lg);
                z-index: 1000;
                box-shadow: 0 1px 3px var(--shadow-light);
            }
            
            .header-title {
                font-size: 22px;
                font-weight: 500;
                color: var(--on-surface);
                margin-left: var(--spacing-md);
            }
            
            .header-actions {
                margin-left: auto;
                display: flex;
                align-items: center;
                gap: var(--spacing-md);
            }
            
            /* Sidebar */
            .sidebar {
                position: fixed;
                top: 64px;
                left: 0;
                width: 280px;
                height: calc(100vh - 64px);
                background: var(--surface);
                border-right: 1px solid var(--outline-variant);
                padding: var(--spacing-lg);
                overflow-y: auto;
                z-index: 900;
            }
            
            .nav-section {
                margin-bottom: var(--spacing-xl);
            }
            
            .nav-section-title {
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                color: var(--on-surface-variant);
                margin-bottom: var(--spacing-md);
                padding: 0 var(--spacing-md);
            }
            
            .nav-item {
                display: flex;
                align-items: center;
                padding: var(--spacing-md);
                margin: var(--spacing-xs) 0;
                border-radius: var(--border-radius);
                text-decoration: none;
                color: var(--on-surface);
                transition: all 0.2s ease;
                cursor: pointer;
                border: none;
                background: none;
                width: 100%;
                text-align: left;
            }
            
            .nav-item:hover {
                background: var(--surface-container);
            }
            
            .nav-item.active {
                background: var(--primary);
                color: white;
            }
            
            .nav-item .material-icons {
                margin-right: var(--spacing-md);
                font-size: 20px;
            }
            
            /* Main Content */
            .main-content {
                margin-left: 280px;
                margin-top: 64px;
                padding: var(--spacing-xl);
                width: calc(100% - 280px);
                min-height: calc(100vh - 64px);
            }
            
            .page-section {
                display: none;
                animation: fadeIn 0.3s ease;
            }
            
            .page-section.active {
                display: block;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .page-header {
                margin-bottom: var(--spacing-xl);
            }
            
            .page-title {
                font-size: 28px;
                font-weight: 400;
                color: var(--on-surface);
                margin-bottom: var(--spacing-sm);
            }
            
            .page-subtitle {
                color: var(--on-surface-variant);
                font-size: 14px;
            }
            
            /* Cards */
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: var(--spacing-lg);
                margin: var(--spacing-lg) 0;
            }
            
            .card {
                background: var(--surface);
                border: 1px solid var(--outline-variant);
                border-radius: var(--border-radius-large);
                padding: var(--spacing-lg);
                box-shadow: 0 1px 3px var(--shadow-light);
                transition: all 0.2s ease;
            }
            
            .card:hover {
                box-shadow: 0 4px 8px var(--shadow-light);
                transform: translateY(-1px);
            }
            
            .card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--spacing-md);
            }
            
            .card-title {
                font-size: 16px;
                font-weight: 500;
                color: var(--on-surface);
                display: flex;
                align-items: center;
                gap: var(--spacing-sm);
            }
            
            .card-content {
                color: var(--on-surface-variant);
                font-size: 14px;
                line-height: 1.6;
            }
            
            /* Status Badges */
            .status-badge {
                display: inline-flex;
                align-items: center;
                padding: var(--spacing-xs) var(--spacing-md);
                border-radius: 16px;
                font-size: 12px;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                gap: var(--spacing-xs);
            }
            
            .status-running {
                background: rgba(19, 115, 51, 0.1);
                color: var(--success);
            }
            
            .status-stopped {
                background: rgba(217, 48, 37, 0.1);
                color: var(--error);
            }
            
            .status-warning {
                background: rgba(234, 134, 0, 0.1);
                color: var(--warning);
            }
            
            /* Buttons */
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: var(--spacing-sm) var(--spacing-md);
                border: 1px solid var(--outline);
                border-radius: var(--border-radius);
                background: var(--surface);
                color: var(--on-surface);
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                gap: var(--spacing-xs);
            }
            
            .btn:hover {
                background: var(--surface-container);
                border-color: var(--outline-variant);
            }
            
            .btn-primary {
                background: var(--primary);
                color: white;
                border-color: var(--primary);
            }
            
            .btn-primary:hover {
                background: var(--primary-hover);
                border-color: var(--primary-hover);
            }
            
            .btn-success {
                background: var(--success);
                color: white;
                border-color: var(--success);
            }
            
            .btn-warning {
                background: var(--warning);
                color: white;
                border-color: var(--warning);
            }
            
            .btn-error {
                background: var(--error);
                color: white;
                border-color: var(--error);
            }
            
            .btn-group {
                display: flex;
                gap: var(--spacing-sm);
                margin-top: var(--spacing-md);
            }
            
            /* Service Info */
            .service-info {
                display: flex;
                flex-direction: column;
                gap: var(--spacing-sm);
                margin: var(--spacing-md) 0;
            }
            
            .service-detail {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 13px;
            }
            
            .service-detail-label {
                color: var(--on-surface-variant);
                font-weight: 500;
            }
            
            .service-detail-value {
                color: var(--on-surface);
                font-family: 'Monaco', 'Menlo', monospace;
            }
            
            /* Logs */
            .log-container {
                background: #1a1a1a;
                color: #e8eaed;
                padding: var(--spacing-md);
                border-radius: var(--border-radius);
                font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                font-size: 13px;
                max-height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
                border: 1px solid var(--outline-variant);
            }
            
            /* Theme Toggle */
            .theme-toggle {
                background: none;
                border: 1px solid var(--outline);
                border-radius: var(--border-radius);
                padding: var(--spacing-sm);
                color: var(--on-surface);
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .theme-toggle:hover {
                background: var(--surface-container);
            }
            
            /* Status Indicator */
            .status-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                display: inline-block;
            }
            
            .status-dot.running {
                background: var(--success);
                box-shadow: 0 0 0 2px rgba(19, 115, 51, 0.2);
            }
            
            .status-dot.stopped {
                background: var(--error);
                box-shadow: 0 0 0 2px rgba(217, 48, 37, 0.2);
            }
            
            /* Responsive */
            @media (max-width: 768px) {
                .sidebar {
                    transform: translateX(-100%);
                    transition: transform 0.3s ease;
                }
                
                .sidebar.open {
                    transform: translateX(0);
                }
                
                .main-content {
                    margin-left: 0;
                    width: 100%;
                }
                
                .card-grid {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Loading States */
            .loading {
                opacity: 0.6;
                pointer-events: none;
            }
            
            .spinner {
                width: 16px;
                height: 16px;
                border: 2px solid var(--outline-variant);
                border-top: 2px solid var(--primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        """)
    ]
)

# Global service manager instance
service_manager = ServiceManager()

def AppHeader():
    """Modern header with title and controls"""
    return Header(
        Div(
            Span("🚀", style="font-size: 24px;"),
            H1("Plasmo Extension Dashboard", cls="header-title"),
            Div(
                Button(
                    I("light_mode", cls="material-icons"),
                    cls="theme-toggle",
                    onclick="toggleTheme()"
                ),
                Button(
                    I("refresh", cls="material-icons"),
                    cls="btn",
                    onclick="refreshAll()"
                ),
                cls="header-actions"
            ),
            cls="header"
        )
    )

def Sidebar():
    """Modern sidebar navigation"""
    return Nav(
        Div(
            H3("Overview", cls="nav-section-title"),
            Button(
                I("dashboard", cls="material-icons"),
                "Dashboard",
                cls="nav-item active",
                onclick="showSection('dashboard')",
                id="nav-dashboard"
            ),
            Button(
                I("settings", cls="material-icons"),
                "Services",
                cls="nav-item",
                onclick="showSection('services')",
                id="nav-services"
            ),
            cls="nav-section"
        ),
        Div(
            H3("Management", cls="nav-section-title"),
            Button(
                I("extension", cls="material-icons"),
                "Extensions",
                cls="nav-item",
                onclick="showSection('extensions')",
                id="nav-extensions"
            ),
            Button(
                I("bug_report", cls="material-icons"),
                "Testing",
                cls="nav-item",
                onclick="showSection('testing')",
                id="nav-testing"
            ),
            Button(
                I("cloud", cls="material-icons"),
                "Tunnels",
                cls="nav-item",
                onclick="showSection('tunnels')",
                id="nav-tunnels"
            ),
            cls="nav-section"
        ),
        Div(
            H3("Monitoring", cls="nav-section-title"),
            Button(
                I("article", cls="material-icons"),
                "Logs",
                cls="nav-item",
                onclick="showSection('logs')",
                id="nav-logs"
            ),
            Button(
                I("analytics", cls="material-icons"),
                "Metrics",
                cls="nav-item",
                onclick="showSection('metrics')",
                id="nav-metrics"
            ),
            cls="nav-section"
        ),
        cls="sidebar",
        id="sidebar"
    )

def ServiceCard(name: str, info: Dict):
    """Modern service card component"""
    is_running = info.get('running', False)
    status_class = "running" if is_running else "stopped"
    status_text = "Running" if is_running else "Stopped"
    
    # Service icons
    icons = {
        'socketio': 'electrical_services',
        'mcp': 'api',
        'plasmo': 'extension',
        'tests': 'bug_report',
        'dashboard': 'dashboard',
        'chrome_debug': 'web'
    }
    
    icon = icons.get(name, 'settings')
    
    return Div(
        Div(
            Div(
                I(icon, cls="material-icons"),
                name.replace('_', ' ').title(),
                cls="card-title"
            ),
            Div(
                Span(cls=f"status-dot {status_class}"),
                Span(status_text, cls=f"status-badge status-{status_class}"),
                style="display: flex; align-items: center; gap: 8px;"
            ),
            cls="card-header"
        ),
        Div(
            Div(
                Span("Implementation:", cls="service-detail-label"),
                Span(info.get('implementation', 'Unknown'), cls="service-detail-value"),
                cls="service-detail"
            ),
            Div(
                Span("Port:", cls="service-detail-label"),
                Span(str(info.get('port', 'N/A')), cls="service-detail-value"),
                cls="service-detail"
            ) if info.get('port') else None,
            Div(
                Span("PID:", cls="service-detail-label"),
                Span(str(info.get('pid', 'N/A')), cls="service-detail-value"),
                cls="service-detail"
            ) if info.get('pid') else None,
            cls="service-info"
        ),
        Div(
            Button(
                I("play_arrow", cls="material-icons"),
                "Start",
                cls="btn btn-success",
                onclick=f"controlService('{name}', 'start')",
                disabled=is_running
            ),
            Button(
                I("stop", cls="material-icons"),
                "Stop",
                cls="btn btn-error",
                onclick=f"controlService('{name}', 'stop')",
                disabled=not is_running
            ),
            Button(
                I("refresh", cls="material-icons"),
                "Restart",
                cls="btn btn-warning",
                onclick=f"controlService('${name}', 'restart')"
            ),
            cls="btn-group"
        ),
        cls="card",
        id=f"service-{name}"
    )

def DashboardSection():
    """Dashboard overview section"""
    return Div(
        Div(
            H1("Service Overview", cls="page-title"),
            P("Monitor and control all Plasmo extension services", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Button(
                I("play_arrow", cls="material-icons"),
                "Start All Services",
                cls="btn btn-primary",
                onclick="controlAllServices('start')"
            ),
            Button(
                I("stop", cls="material-icons"),
                "Stop All Services",
                cls="btn btn-error",
                onclick="controlAllServices('stop')"
            ),
            Button(
                I("refresh", cls="material-icons"),
                "Restart All Services",
                cls="btn btn-warning",
                onclick="controlAllServices('restart')"
            ),
            style="margin-bottom: 24px; display: flex; gap: 12px;"
        ),
        Div(id="services-grid", cls="card-grid"),
        cls="page-section active",
        id="dashboard-section"
    )

def ServicesSection():
    """Detailed services management section"""
    return Div(
        Div(
            H1("Service Management", cls="page-title"),
            P("Detailed control and monitoring of individual services", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(id="detailed-services", cls="card-grid"),
        cls="page-section",
        id="services-section"
    )

def ExtensionsSection():
    """Chrome extensions management section"""
    return Div(
        Div(
            H1("Extension Management", cls="page-title"),
            P("Manage Chrome extensions and development tools", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Div(
                Div(
                    I("extension", cls="material-icons"),
                    "Extension Tools",
                    cls="card-title"
                ),
                Div(
                    Button(
                        I("search", cls="material-icons"),
                        "Find Extension ID",
                        cls="btn btn-primary",
                        onclick="findExtensionId()"
                    ),
                    Button(
                        I("list", cls="material-icons"),
                        "List Extensions",
                        cls="btn",
                        onclick="listExtensions()"
                    ),
                    Button(
                        I("folder", cls="material-icons"),
                        "Show Paths",
                        cls="btn",
                        onclick="showExtensionPaths()"
                    ),
                    cls="btn-group"
                ),
                cls="card"
            ),
            cls="card-grid"
        ),
        Div(id="extension-results"),
        cls="page-section",
        id="extensions-section"
    )

def TestingSection():
    """Testing management section"""
    return Div(
        Div(
            H1("Test Management", cls="page-title"),
            P("Run and monitor test suites", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Div(
                Div(
                    I("bug_report", cls="material-icons"),
                    "Test Runner",
                    cls="card-title"
                ),
                Div(
                    Button(
                        I("play_arrow", cls="material-icons"),
                        "Run All Tests",
                        cls="btn btn-primary",
                        onclick="runTests('all')"
                    ),
                    Button(
                        I("list", cls="material-icons"),
                        "List Tests",
                        cls="btn",
                        onclick="listTests()"
                    ),
                    Button(
                        I("visibility", cls="material-icons"),
                        "Verbose Mode",
                        cls="btn",
                        onclick="runTests('verbose')"
                    ),
                    cls="btn-group"
                ),
                cls="card"
            ),
            cls="card-grid"
        ),
        Div(id="test-results"),
        cls="page-section",
        id="testing-section"
    )

def TunnelsSection():
    """Tunnel management section"""
    return Div(
        Div(
            H1("Tunnel Management", cls="page-title"),
            P("Manage external access tunnels", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Div(
                Div(
                    I("cloud", cls="material-icons"),
                    "LocalTunnel",
                    cls="card-title"
                ),
                Div(
                    Button(
                        I("play_arrow", cls="material-icons"),
                        "Start Tunnel",
                        cls="btn btn-primary",
                        onclick="controlTunnel('start')"
                    ),
                    Button(
                        I("stop", cls="material-icons"),
                        "Stop Tunnel",
                        cls="btn btn-error",
                        onclick="controlTunnel('stop')"
                    ),
                    Button(
                        I("info", cls="material-icons"),
                        "Status",
                        cls="btn",
                        onclick="controlTunnel('status')"
                    ),
                    cls="btn-group"
                ),
                cls="card"
            ),
            cls="card-grid"
        ),
        Div(id="tunnel-results"),
        cls="page-section",
        id="tunnels-section"
    )

def LogsSection():
    """Logs viewing section"""
    return Div(
        Div(
            H1("Service Logs", cls="page-title"),
            P("View real-time logs from all services", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Select(
                Option("Select a service...", value=""),
                Option("MCP Server", value="mcp"),
                Option("SocketIO Server", value="socketio"),
                Option("Plasmo Dev", value="plasmo"),
                Option("Dashboard", value="dashboard"),
                Option("Chrome Debug", value="chrome_debug"),
                Option("Tests", value="tests"),
                id="log-service-select",
                onchange="loadLogs(this.value)",
                style="margin-bottom: 16px; padding: 8px; border-radius: 4px; border: 1px solid var(--outline);"
            ),
            Button(
                I("refresh", cls="material-icons"),
                "Refresh",
                cls="btn",
                onclick="refreshLogs()",
                style="margin-left: 8px;"
            )
        ),
        Div(id="log-content", cls="log-container", style="min-height: 300px;"),
        cls="page-section",
        id="logs-section"
    )

def MetricsSection():
    """System metrics section"""
    return Div(
        Div(
            H1("System Metrics", cls="page-title"),
            P("Monitor system performance and resource usage", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(id="metrics-content"),
        cls="page-section",
        id="metrics-section"
    )

@rt("/")
def get():
    """Main SPA page"""
    return Html(
        Head(
            Title("Plasmo Extension Dashboard"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
        ),
        Body(
            AppHeader(),
            Div(
                Sidebar(),
                Main(
                    DashboardSection(),
                    ServicesSection(),
                    ExtensionsSection(),
                    TestingSection(),
                    TunnelsSection(),
                    LogsSection(),
                    MetricsSection(),
                    cls="main-content"
                ),
                cls="app-container"
            ),
            Script("""
                // Theme management
                function toggleTheme() {
                    const body = document.body;
                    const currentTheme = body.getAttribute('data-theme');
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    body.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                }
                
                // Load saved theme
                const savedTheme = localStorage.getItem('theme') || 'light';
                document.body.setAttribute('data-theme', savedTheme);
                
                // Navigation
                function showSection(sectionName) {
                    // Hide all sections
                    document.querySelectorAll('.page-section').forEach(section => {
                        section.classList.remove('active');
                    });
                    
                    // Remove active from all nav items
                    document.querySelectorAll('.nav-item').forEach(item => {
                        item.classList.remove('active');
                    });
                    
                    // Show selected section
                    document.getElementById(sectionName + '-section').classList.add('active');
                    document.getElementById('nav-' + sectionName).classList.add('active');
                    
                    // Load section-specific data
                    if (sectionName === 'dashboard' || sectionName === 'services') {
                        loadServices();
                    }
                }
                
                // Service management
                async function loadServices() {
                    try {
                        const response = await fetch('/api/services/status');
                        const services = await response.json();
                        
                        const dashboardGrid = document.getElementById('services-grid');
                        const servicesGrid = document.getElementById('detailed-services');
                        
                        if (dashboardGrid) {
                            dashboardGrid.innerHTML = '';
                            Object.entries(services).forEach(([name, info]) => {
                                dashboardGrid.innerHTML += createServiceCard(name, info);
                            });
                        }
                        
                        if (servicesGrid) {
                            servicesGrid.innerHTML = '';
                            Object.entries(services).forEach(([name, info]) => {
                                servicesGrid.innerHTML += createServiceCard(name, info);
                            });
                        }
                    } catch (error) {
                        console.error('Failed to load services:', error);
                    }
                }
                
                function createServiceCard(name, info) {
                    const isRunning = info.running;
                    const statusClass = isRunning ? 'running' : 'stopped';
                    const statusText = isRunning ? 'Running' : 'Stopped';
                    
                    const icons = {
                        'socketio': 'electrical_services',
                        'mcp': 'api',
                        'plasmo': 'extension',
                        'tests': 'bug_report',
                        'dashboard': 'dashboard',
                        'chrome_debug': 'web'
                    };
                    
                    const icon = icons[name] || 'settings';
                    
                    return `
                        <div class="card" id="service-${name}">
                            <div class="card-header">
                                <div class="card-title">
                                    <i class="material-icons">${icon}</i>
                                    ${name.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="status-dot ${statusClass}"></span>
                                    <span class="status-badge status-${statusClass}">${statusText}</span>
                                </div>
                            </div>
                            <div class="service-info">
                                <div class="service-detail">
                                    <span class="service-detail-label">Implementation:</span>
                                    <span class="service-detail-value">${info.implementation || 'Unknown'}</span>
                                </div>
                                ${info.port ? `
                                <div class="service-detail">
                                    <span class="service-detail-label">Port:</span>
                                    <span class="service-detail-value">${info.port}</span>
                                </div>
                                ` : ''}
                                ${info.pid ? `
                                <div class="service-detail">
                                    <span class="service-detail-label">PID:</span>
                                    <span class="service-detail-value">${info.pid}</span>
                                </div>
                                ` : ''}
                            </div>
                            <div class="btn-group">
                                <button class="btn btn-success" onclick="controlService('${name}', 'start')" ${isRunning ? 'disabled' : ''}>
                                    <i class="material-icons">play_arrow</i>
                                    Start
                                </button>
                                <button class="btn btn-error" onclick="controlService('${name}', 'stop')" ${!isRunning ? 'disabled' : ''}>
                                    <i class="material-icons">stop</i>
                                    Stop
                                </button>
                                <button class="btn btn-warning" onclick="controlService('${name}', 'restart')">
                                    <i class="material-icons">refresh</i>
                                    Restart
                                </button>
                            </div>
                        </div>
                    `;
                }
                
                async function controlService(serviceName, action) {
                    const card = document.getElementById(`service-${serviceName}`);
                    card.classList.add('loading');
                    
                    try {
                        const response = await fetch(`/api/services/${serviceName}/${action}`, {
                            method: 'POST'
                        });
                        
                        if (response.ok) {
                            setTimeout(loadServices, 1000); // Refresh after action
                        } else {
                            console.error(`Failed to ${action} ${serviceName}`);
                        }
                    } catch (error) {
                        console.error(`Error ${action}ing ${serviceName}:`, error);
                    } finally {
                        card.classList.remove('loading');
                    }
                }
                
                async function controlAllServices(action) {
                    try {
                        const response = await fetch(`/api/services/all/${action}`, {
                            method: 'POST'
                        });
                        
                        if (response.ok) {
                            setTimeout(loadServices, 2000); // Refresh after action
                        }
                    } catch (error) {
                        console.error(`Error ${action}ing all services:`, error);
                    }
                }
                
                function refreshAll() {
                    loadServices();
                    // Add other refresh actions as needed
                }
                
                // Extension management
                async function findExtensionId() {
                    const results = document.getElementById('extension-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch('/api/extensions/id');
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                async function listExtensions() {
                    const results = document.getElementById('extension-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch('/api/extensions/list');
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                async function showExtensionPaths() {
                    const results = document.getElementById('extension-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch('/api/extensions/paths');
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                // Test management
                async function runTests(mode) {
                    const results = document.getElementById('test-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch(`/api/tests/${mode}`, { method: 'POST' });
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                async function listTests() {
                    const results = document.getElementById('test-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch('/api/tests/list');
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                // Tunnel management
                async function controlTunnel(action) {
                    const results = document.getElementById('tunnel-results');
                    results.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch(`/api/tunnel/${action}`, { method: 'POST' });
                        const data = await response.text();
                        results.innerHTML = `<div class="card"><pre class="log-container">${data}</pre></div>`;
                    } catch (error) {
                        results.innerHTML = `<div class="card"><p class="error">Error: ${error.message}</p></div>`;
                    }
                }
                
                // Log management
                async function loadLogs(serviceName) {
                    if (!serviceName) return;
                    
                    const logContent = document.getElementById('log-content');
                    logContent.innerHTML = '<div class="spinner"></div>';
                    
                    try {
                        const response = await fetch(`/api/logs/${serviceName}`);
                        const data = await response.text();
                        logContent.textContent = data;
                        logContent.scrollTop = logContent.scrollHeight;
                    } catch (error) {
                        logContent.textContent = `Error loading logs: ${error.message}`;
                    }
                }
                
                function refreshLogs() {
                    const select = document.getElementById('log-service-select');
                    if (select.value) {
                        loadLogs(select.value);
                    }
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    loadServices();
                    
                    // Auto-refresh services every 30 seconds
                    setInterval(loadServices, 30000);
                });
            """)
        )
    )

# API Routes
@rt("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@rt("/api/services/status")
def get_services_status():
    """Get status of all services"""
    return service_manager.get_service_status()

@rt("/api/services/{service_name}/start", methods=["POST"])
async def start_service(service_name: str):
    """Start a specific service"""
    success = service_manager.start_service(service_name)
    return {"success": success, "service": service_name, "action": "start"}

@rt("/api/services/{service_name}/stop", methods=["POST"])
def stop_service(service_name: str):
    """Stop a specific service"""
    success = service_manager.stop_service(service_name)
    return {"success": success, "service": service_name, "action": "stop"}

@rt("/api/services/{service_name}/restart", methods=["POST"])
def restart_service(service_name: str):
    """Restart a specific service"""
    success = service_manager.restart_service(service_name)
    return {"success": success, "service": service_name, "action": "restart"}

@rt("/api/services/all/{action}", methods=["POST"])
async def control_all_services(action: str):
    """Control all services"""
    if action == "start":
        results = await service_manager.start_all_services_async()
    elif action == "stop":
        results = {}
        for service_name in service_manager.service_configs.keys():
            results[service_name] = service_manager.stop_service(service_name)
    elif action == "restart":
        # Stop all first, then start all
        for service_name in service_manager.service_configs.keys():
            service_manager.stop_service(service_name)
        await asyncio.sleep(2)
        results = await service_manager.start_all_services_async()
    else:
        return {"error": "Invalid action"}
    
    return {"success": all(results.values()), "results": results, "action": action}

@rt("/api/logs/{service_name}")
async def get_service_logs(service_name: str, lines: int = 50):
    """Get logs for a specific service"""
    log_file = Path("logs") / f"{service_name}.log"
    
    if not log_file.exists():
        return f"No log file found for {service_name}"
    
    try:
        async with aiofiles.open(log_file, 'r') as f:
            content = await f.read()
            log_lines = content.split('\n')
            return '\n'.join(log_lines[-lines:])
    except Exception as e:
        return f"Error reading logs: {str(e)}"

@rt("/api/extensions/id")
async def get_extension_id():
    """Get Chrome extension ID"""
    try:
        result = subprocess.run(
            ["python3", "extension_manager.py", "get-id"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@rt("/api/extensions/list")
async def list_extensions():
    """List Chrome extensions"""
    try:
        result = subprocess.run(
            ["python3", "extension_manager.py", "list-extensions"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@rt("/api/extensions/paths")
async def extension_paths():
    """Show Chrome extension paths"""
    try:
        result = subprocess.run(
            ["python3", "extension_manager.py", "paths"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@rt("/api/tests/{mode}", methods=["POST"])
async def run_tests(mode: str):
    """Run tests"""
    try:
        if mode == "all":
            cmd = ["python3", "test_runner.py", "all"]
        elif mode == "verbose":
            cmd = ["python3", "test_runner.py", "all", "--verbose"]
        else:
            return f"Invalid test mode: {mode}"
            
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@rt("/api/tests/list")
async def list_tests():
    """List available tests"""
    try:
        result = subprocess.run(
            ["python3", "test_runner.py", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

@rt("/api/tunnel/{action}", methods=["POST"])
async def control_tunnel(action: str):
    """Control LocalTunnel"""
    try:
        result = subprocess.run(
            ["python3", "localtunnel_manager.py", action],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    
    # Ensure logs directory exists
    Path("logs").mkdir(exist_ok=True)
    
    logger.info("Starting FastHTML Dashboard Server on port 8080")
    uvicorn.run(app, host="0.0.0.0", port=8080) 