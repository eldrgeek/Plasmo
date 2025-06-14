#!/usr/bin/env python3
"""
🎨 CLEAN MODERN DASHBOARD - Plasmo Extension Services
==================================================

A clean, modern dashboard with:
✨ Simple, elegant design
🌙 Working dark/light themes
📱 Responsive grid layout
⚡ Real-time service updates
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared head elements including all CSS
COMMON_HEAD = [
    Title("🚀 Plasmo Dashboard"),
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
            
            /* Spacing & Layout */
            --gap: 1.25rem;
            --gap-sm: 0.75rem;
            --gap-lg: 2rem;
            --radius: 0.75rem;
            --radius-sm: 0.5rem;
            --header-height: 3.5rem;
            --sidebar-width: 14rem;
            
            /* Transitions */
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
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
        }

        /* Sidebar */
        .sidebar {
            position: fixed;
            top: var(--header-height);
            left: 0;
            width: var(--sidebar-width);
            height: calc(100vh - var(--header-height));
            background: var(--card-dark);
            border-right: 1px solid var(--border-dark);
            padding: var(--gap);
            overflow-y: auto;
            z-index: 900;
        }

        body[data-theme="light"] .sidebar {
            background: var(--card-light);
            border-right-color: var(--border-light);
        }

        .nav-section {
            margin-bottom: var(--gap-lg);
        }

        .nav-section-title {
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--muted-dark);
            margin-bottom: var(--gap-sm);
            padding: 0 var(--gap-sm);
        }

        body[data-theme="light"] .nav-section-title {
            color: var(--muted-light);
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
            padding: 0.6rem var(--gap-sm);
            border-radius: var(--radius-sm);
            color: var(--muted-dark);
            background: none;
            border: none;
            cursor: pointer;
            width: 100%;
            text-align: left;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all var(--transition);
        }

        .nav-item:hover {
            background: rgba(255, 255, 255, 0.05);
            color: var(--fg-dark);
        }

        .nav-item.active {
            background: rgba(59, 130, 246, 0.15);
            color: var(--accent);
        }

        body[data-theme="light"] .nav-item {
            color: var(--muted-light);
        }

        body[data-theme="light"] .nav-item:hover {
            background: rgba(0, 0, 0, 0.05);
            color: var(--fg-light);
        }

        body[data-theme="light"] .nav-item.active {
            background: rgba(59, 130, 246, 0.1);
            color: var(--accent);
        }

        /* Main Content */
        .main-content {
            margin-left: var(--sidebar-width);
            margin-top: var(--header-height);
            padding: var(--gap-lg);
            min-height: calc(100vh - var(--header-height));
        }

        .page-section {
            display: none;
        }

        .page-section.active {
            display: block;
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
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: var(--gap-sm);
            margin: var(--gap-lg) 0;
        }

        .card {
            background: var(--card-dark);
            border: 1px solid var(--border-dark);
            border-radius: var(--radius);
            padding: var(--gap-sm);
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

        body[data-theme="light"] .card:hover {
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }

        .card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--gap-sm);
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: var(--gap-sm);
            font-size: 1rem;
            font-weight: 600;
        }

        .card-icon {
            width: 1.75rem;
            height: 1.75rem;
            border-radius: var(--radius-sm);
            background: var(--accent);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }

        /* Status */
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            padding: 0.25rem 0.5rem;
            border-radius: var(--radius-sm);
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.025em;
        }

        .status-running {
            background: var(--success);
            color: white;
        }

        .status-stopped {
            background: var(--error);
            color: white;
        }

        .status-dot {
            width: 0.5rem;
            height: 0.5rem;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        .status-dot.running {
            background: var(--success);
        }

        .status-dot.stopped {
            background: var(--error);
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }

        /* Service Info */
        .service-info {
            margin: var(--gap-sm) 0;
        }

        .service-detail {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.25rem 0;
            border-bottom: 1px solid var(--border-dark);
        }

        .service-detail:last-child {
            border-bottom: none;
        }

        body[data-theme="light"] .service-detail {
            border-bottom-color: var(--border-light);
        }

        .service-detail-label {
            color: var(--muted-dark);
            font-size: 0.8rem;
            font-weight: 500;
        }

        body[data-theme="light"] .service-detail-label {
            color: var(--muted-light);
        }

        .service-detail-value {
            font-family: 'JetBrains Mono', Monaco, monospace;
            font-size: 0.8rem;
            color: var(--fg-dark);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.2rem 0.4rem;
            border-radius: var(--radius-sm);
        }

        body[data-theme="light"] .service-detail-value {
            color: var(--fg-light);
            background: rgba(0, 0, 0, 0.05);
        }

        /* Buttons */
        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            padding: 0.5rem 0.75rem;
            border: none;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all var(--transition);
            text-decoration: none;
            color: white;
        }

        .btn:hover {
            transform: translateY(-1px);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .btn-primary {
            background: var(--accent);
        }

        .btn-success {
            background: var(--success);
        }

        .btn-warning {
            background: var(--warning);
        }

        .btn-error {
            background: var(--error);
        }

        .btn-group {
            display: flex;
            gap: 0.5rem;
            margin-top: var(--gap-sm);
            flex-wrap: wrap;
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

        /* Control Buttons */
        .control-buttons {
            display: flex;
            justify-content: center;
            gap: var(--gap);
            margin-bottom: var(--gap-lg);
            flex-wrap: wrap;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .sidebar {
                transform: translateX(-100%);
                transition: transform var(--transition);
            }

            .sidebar.open {
                transform: translateX(0);
            }

            .main-content {
                margin-left: 0;
                padding: var(--gap);
            }

            .card-grid {
                grid-template-columns: 1fr;
            }

            .page-title {
                font-size: 2rem;
            }

            .control-buttons {
                flex-direction: column;
                align-items: center;
            }

            .btn-group {
                justify-content: center;
            }
        }

        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-track {
            background: transparent;
        }

        ::-webkit-scrollbar-thumb {
            background: var(--border-dark);
            border-radius: 3px;
        }

        body[data-theme="light"] ::-webkit-scrollbar-thumb {
            background: var(--border-light);
        }
    """)
]

# FastHTML app without hdrs
app, rt = fast_app(live=True)

# Global service manager instance
service_manager = ServiceManager()

def AppHeader():
    """Clean modern header"""
    return Header(
        Div(
            "🚀 Plasmo Dashboard",
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

def Sidebar():
    """Clean sidebar navigation"""
    return Nav(
        Div(
            H3("Overview", cls="nav-section-title"),
            Button(
                I("dashboard", cls="material-icons-round"),
                "Dashboard",
                cls="nav-item active",
                onclick="showSection('dashboard')",
                id="nav-dashboard"
            ),
            cls="nav-section"
        ),
        Div(
            H3("Services", cls="nav-section-title"),
            Button(
                I("settings", cls="material-icons-round"),
                "All Services",
                cls="nav-item",
                onclick="showSection('services')",
                id="nav-services"
            ),
            cls="nav-section"
        ),
        cls="sidebar",
        id="sidebar"
    )

def DashboardSection():
    """Main dashboard section"""
    return Div(
        Div(
            H1("Service Overview", cls="page-title"),
            P("Monitor and control all Plasmo extension services", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Button(
                I("play_arrow", cls="material-icons-round"),
                "Start All",
                cls="btn btn-success",
                onclick="controlAllServices('start')"
            ),
            Button(
                I("stop", cls="material-icons-round"),
                "Stop All",
                cls="btn btn-error",
                onclick="controlAllServices('stop')"
            ),
            Button(
                I("refresh", cls="material-icons-round"),
                "Restart All",
                cls="btn btn-warning",
                onclick="controlAllServices('restart')"
            ),
            Button(
                I("refresh", cls="material-icons-round"),
                "Refresh",
                cls="btn btn-primary",
                onclick="loadServices()"
            ),
            cls="control-buttons"
        ),
        Div(id="services-grid", cls="card-grid"),
        cls="page-section active",
        id="dashboard-section"
    )

# API Routes
@rt("/api/services/status")
def get_services_status():
    """Get status of all services"""
    try:
        status = service_manager.get_service_status()
        return status
    except Exception as e:
        logger.error(f"Error getting services status: {e}")
        return {"error": str(e)}

@rt("/api/services/{service_name}/{action}", methods=["POST"])
def control_service(service_name: str, action: str):
    """Control individual service"""
    try:
        if action == "start":
            result = service_manager.start_service(service_name)
        elif action == "stop":
            result = service_manager.stop_service(service_name)
        elif action == "restart":
            result = service_manager.restart_service(service_name)
        else:
            return {"error": f"Unknown action: {action}"}
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Error {action}ing {service_name}: {e}")
        return {"error": str(e)}

@rt("/")
def get():
    """Main dashboard page"""
    return Html(
        Head(*COMMON_HEAD),
        Body(
            AppHeader(),
            Div(
                Sidebar(),
                Main(
                    DashboardSection(),
                    cls="main-content"
                ),
                cls="app-container"
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

                // Service management
                async function loadServices() {
                    const grid = document.getElementById('services-grid');
                    if (!grid) return;

                    try {
                        const response = await fetch('/api/services/status');
                        const services = await response.json();
                        
                        grid.innerHTML = '';
                        Object.entries(services).forEach(([name, info]) => {
                            grid.appendChild(createServiceCard(name, info));
                        });
                    } catch (error) {
                        console.error('Failed to load services:', error);
                        showNotification('Failed to load services', 'error');
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
                        'continuous_tests': 'bug_report',
                        'dashboard': 'dashboard',
                        'mcp_dashboard': 'analytics',
                        'chrome_debug': 'web'
                    };
                    
                    const icon = icons[name] || 'settings';
                    const displayName = name.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                    
                    // Special handling for dashboard services
                    let viewButton = '';
                    if (name === 'mcp_dashboard' && isRunning && info.port) {
                        viewButton = `
                            <button class="btn btn-primary" onclick="window.open('http://localhost:${info.port}', '_blank')" title="Open MCP Dashboard">
                                <i class="material-icons-round">open_in_new</i>
                                View Dashboard
                            </button>
                        `;
                    } else if (name === 'dashboard' && isRunning && info.port) {
                        viewButton = `
                            <button class="btn btn-primary" onclick="window.open('http://localhost:${info.port}', '_blank')" title="Open Main Dashboard">
                                <i class="material-icons-round">open_in_new</i>
                                View Dashboard
                            </button>
                        `;
                    }
                    
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <div class="card-header">
                            <div class="card-title">
                                <div class="card-icon">
                                    <i class="material-icons-round">${icon}</i>
                                </div>
                                ${displayName}
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <span class="status-dot ${statusClass}"></span>
                                <span class="status-badge status-${statusClass}">${statusText}</span>
                            </div>
                        </div>
                        <div class="service-info">
                            <div class="service-detail">
                                <span class="service-detail-label">Type</span>
                                <span class="service-detail-value">${info.implementation || 'Unknown'}</span>
                            </div>
                            ${info.port ? `
                            <div class="service-detail">
                                <span class="service-detail-label">Port</span>
                                <span class="service-detail-value">${info.port}</span>
                            </div>
                            ` : ''}
                            ${info.pid ? `
                            <div class="service-detail">
                                <span class="service-detail-label">PID</span>
                                <span class="service-detail-value">${info.pid}</span>
                            </div>
                            ` : ''}
                        </div>
                        <div class="btn-group">
                            ${viewButton}
                            <button class="btn btn-success" onclick="controlService('${name}', 'start')" ${isRunning ? 'disabled' : ''}>
                                <i class="material-icons-round">play_arrow</i>
                                Start
                            </button>
                            <button class="btn btn-error" onclick="controlService('${name}', 'stop')" ${!isRunning ? 'disabled' : ''}>
                                <i class="material-icons-round">stop</i>
                                Stop
                            </button>
                            <button class="btn btn-warning" onclick="controlService('${name}', 'restart')">
                                <i class="material-icons-round">refresh</i>
                                Restart
                            </button>
                        </div>
                    `;
                    return card;
                }

                async function controlService(serviceName, action) {
                    try {
                        const response = await fetch(`/api/services/${serviceName}/${action}`, {
                            method: 'POST'
                        });
                        
                        if (response.ok) {
                            showNotification(`${action.charAt(0).toUpperCase() + action.slice(1)}ed ${serviceName}`, 'success');
                            setTimeout(loadServices, 1000);
                        } else {
                            throw new Error(`Failed to ${action} ${serviceName}`);
                        }
                    } catch (error) {
                        console.error(`Error ${action}ing ${serviceName}:`, error);
                        showNotification(`Failed to ${action} ${serviceName}`, 'error');
                    }
                }

                async function controlAllServices(action) {
                    try {
                        const response = await fetch('/api/services/status');
                        const services = await response.json();
                        
                        const promises = Object.keys(services).map(serviceName => 
                            fetch(`/api/services/${serviceName}/${action}`, { method: 'POST' })
                        );
                        
                        await Promise.all(promises);
                        showNotification(`${action.charAt(0).toUpperCase() + action.slice(1)}ed all services`, 'success');
                        setTimeout(loadServices, 2000);
                    } catch (error) {
                        console.error(`Error ${action}ing all services:`, error);
                        showNotification(`Failed to ${action} all services`, 'error');
                    }
                }

                function showNotification(message, type = 'info') {
                    const notification = document.createElement('div');
                    notification.style.cssText = `
                        position: fixed;
                        top: 4rem;
                        right: 1rem;
                        background: var(--card-dark);
                        border: 1px solid var(--border-dark);
                        border-radius: var(--radius);
                        padding: 1rem;
                        color: var(--fg-dark);
                        font-weight: 500;
                        z-index: 10000;
                        transform: translateX(100%);
                        transition: transform 0.3s ease;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                        max-width: 300px;
                    `;
                    
                    if (type === 'success') {
                        notification.style.borderLeftColor = 'var(--success)';
                        notification.style.borderLeftWidth = '4px';
                    } else if (type === 'error') {
                        notification.style.borderLeftColor = 'var(--error)';
                        notification.style.borderLeftWidth = '4px';
                    }
                    
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    setTimeout(() => {
                        notification.style.transform = 'translateX(0)';
                    }, 100);
                    
                    setTimeout(() => {
                        notification.style.transform = 'translateX(100%)';
                        setTimeout(() => {
                            document.body.removeChild(notification);
                        }, 300);
                    }, 3000);
                }

                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    loadServices();
                    setInterval(loadServices, 30000); // Auto-refresh every 30 seconds
                });
            """)
        )
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Clean Plasmo Dashboard...")
    print("✨ Features: Clean Design, Working Theme Toggle, Responsive Layout")
    print("🎨 Access at: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")