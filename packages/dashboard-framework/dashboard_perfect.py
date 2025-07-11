#!/usr/bin/env python3
"""
🎨 PERFECT SELF-CONTAINED DASHBOARD - Plasmo Extension Services
==============================================================

A completely self-contained beautiful dashboard with:
✨ No external dependencies (all CSS/fonts embedded)
🎨 Stunning glassmorphism design
🌈 Smooth animations and transitions
📱 Perfect responsive design
🌙 Dark/light theme support
⚡ Real-time service monitoring
"""

import asyncio
import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import psutil
from fasthtml.common import *

# Import our service manager
from service_manager import ServiceManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastHTML app with embedded styles
app, rt = fast_app(
    live=True,
    hdrs=[
        Style("""
            /* 🎨 PERFECT SELF-CONTAINED DASHBOARD STYLES */
            
            /* CSS Variables for theming */
            :root {
                /* Brand Colors */
                --primary: #667eea;
                --primary-light: rgba(102, 126, 234, 0.1);
                --secondary: #f093fb;
                --accent: #4facfe;
                
                /* Status Colors */
                --success: #11998e;
                --warning: #f093fb;
                --error: #fc466b;
                
                /* Dark Theme (default) */
                --bg-primary: #0a0a0f;
                --bg-secondary: #111118;
                --bg-tertiary: #1a1a24;
                --surface: rgba(255, 255, 255, 0.05);
                --surface-hover: rgba(255, 255, 255, 0.08);
                --glass: rgba(255, 255, 255, 0.03);
                --glass-border: rgba(255, 255, 255, 0.1);
                --text-primary: #ffffff;
                --text-secondary: rgba(255, 255, 255, 0.7);
                --text-muted: rgba(255, 255, 255, 0.3);
                --shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
                --glow: 0 0 32px rgba(102, 126, 234, 0.3);
            }
            
            /* Light Theme */
            [data-theme="light"] {
                --bg-primary: #fafafa;
                --bg-secondary: #ffffff;
                --bg-tertiary: #f5f5f5;
                --surface: rgba(0, 0, 0, 0.03);
                --surface-hover: rgba(0, 0, 0, 0.05);
                --glass: rgba(255, 255, 255, 0.8);
                --glass-border: rgba(0, 0, 0, 0.1);
                --text-primary: #1a1a1a;
                --text-secondary: rgba(0, 0, 0, 0.7);
                --text-muted: rgba(0, 0, 0, 0.3);
                --shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            }
            
            /* Reset and base styles */
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            html {
                scroll-behavior: smooth;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: var(--bg-primary);
                color: var(--text-primary);
                line-height: 1.6;
                overflow-x: hidden;
                min-height: 100vh;
                background-image: 
                    radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.1) 0%, transparent 50%);
                background-attachment: fixed;
            }
            
            /* Layout */
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
                height: 4rem;
                z-index: 1000;
                padding: 0 2rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-bottom: 1px solid var(--glass-border);
                transition: all 0.3s ease;
            }
            
            .header-brand {
                display: flex;
                align-items: center;
                gap: 1rem;
                font-weight: 700;
                font-size: 1.25rem;
                color: var(--primary);
            }
            
            .logo {
                width: 2rem;
                height: 2rem;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                border-radius: 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
                animation: float 3s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-5px); }
            }
            
            .header-actions {
                display: flex;
                align-items: center;
                gap: 1rem;
            }
            
            /* Sidebar */
            .sidebar {
                position: fixed;
                top: 4rem;
                left: 0;
                width: 16rem;
                height: calc(100vh - 4rem);
                background: var(--glass);
                backdrop-filter: blur(20px);
                border-right: 1px solid var(--glass-border);
                padding: 2rem;
                overflow-y: auto;
                z-index: 900;
            }
            
            .nav-section {
                margin-bottom: 2rem;
            }
            
            .nav-section-title {
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.1em;
                color: var(--text-muted);
                margin-bottom: 1rem;
                padding: 0 1rem;
            }
            
            .nav-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                margin: 0.25rem 0;
                border-radius: 0.75rem;
                color: var(--text-secondary);
                text-decoration: none;
                font-weight: 500;
                transition: all 0.3s ease;
                cursor: pointer;
                border: none;
                background: none;
                width: 100%;
                text-align: left;
            }
            
            .nav-item:hover {
                color: var(--text-primary);
                background: var(--surface-hover);
                transform: translateX(4px);
            }
            
            .nav-item.active {
                color: var(--text-primary);
                background: var(--primary-light);
                box-shadow: var(--glow);
            }
            
            .nav-icon {
                font-size: 1.25rem;
                width: 1.25rem;
                height: 1.25rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Main content */
            .main-content {
                margin-left: 16rem;
                margin-top: 4rem;
                padding: 2rem;
                width: calc(100% - 16rem);
                min-height: calc(100vh - 4rem);
            }
            
            .page-section {
                display: none;
                animation: slideInUp 0.5s ease;
            }
            
            .page-section.active {
                display: block;
            }
            
            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            
            .page-header {
                margin-bottom: 2rem;
                text-align: center;
            }
            
            .page-title {
                font-size: 3rem;
                font-weight: 800;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.5rem;
                line-height: 1.2;
            }
            
            .page-subtitle {
                font-size: 1.125rem;
                color: var(--text-secondary);
                max-width: 600px;
                margin: 0 auto;
            }
            
            /* Cards */
            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 1.5rem;
                margin: 2rem 0;
            }
            
            .card {
                background: var(--glass);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 1.5rem;
                padding: 1.5rem;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            
            .card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 2px;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                transform: scaleX(0);
                transition: transform 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-8px);
                box-shadow: var(--shadow);
                border-color: rgba(255, 255, 255, 0.2);
            }
            
            .card:hover::before {
                transform: scaleX(1);
            }
            
            .card-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 1.5rem;
            }
            
            .card-title {
                display: flex;
                align-items: center;
                gap: 1rem;
                font-size: 1.25rem;
                font-weight: 600;
                color: var(--text-primary);
            }
            
            .card-icon {
                width: 2.5rem;
                height: 2.5rem;
                border-radius: 0.75rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 1.25rem;
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: var(--glow);
            }
            
            /* Status components */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.25rem 1rem;
                border-radius: 1rem;
                font-size: 0.75rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            
            .status-running {
                background: linear-gradient(135deg, var(--success), #38ef7d);
                color: white;
                box-shadow: 0 4px 16px rgba(17, 153, 142, 0.3);
            }
            
            .status-stopped {
                background: linear-gradient(135deg, var(--error), #3f5efb);
                color: white;
                box-shadow: 0 4px 16px rgba(252, 70, 107, 0.3);
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
                50% { opacity: 0.5; }
            }
            
            /* Buttons */
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                padding: 1rem 1.5rem;
                border: none;
                border-radius: 0.75rem;
                font-size: 0.875rem;
                font-weight: 600;
                text-decoration: none;
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                background: var(--surface);
                color: var(--text-primary);
                backdrop-filter: blur(10px);
            }
            
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: var(--shadow);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: var(--glow);
            }
            
            .btn-success {
                background: linear-gradient(135deg, var(--success), #38ef7d);
                color: white;
            }
            
            .btn-warning {
                background: linear-gradient(135deg, var(--warning), #f5576c);
                color: white;
            }
            
            .btn-error {
                background: linear-gradient(135deg, var(--error), #3f5efb);
                color: white;
            }
            
            .btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: none;
            }
            
            .btn-group {
                display: flex;
                gap: 0.5rem;
                margin-top: 1.5rem;
                flex-wrap: wrap;
            }
            
            /* Service info */
            .service-info {
                display: flex;
                flex-direction: column;
                gap: 1rem;
                margin: 1.5rem 0;
            }
            
            .service-detail {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 0;
                border-bottom: 1px solid var(--glass-border);
            }
            
            .service-detail:last-child {
                border-bottom: none;
            }
            
            .service-detail-label {
                color: var(--text-secondary);
                font-weight: 500;
                font-size: 0.875rem;
            }
            
            .service-detail-value {
                color: var(--text-primary);
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 0.875rem;
                font-weight: 500;
                background: var(--surface);
                padding: 0.25rem 0.5rem;
                border-radius: 0.5rem;
            }
            
            /* Theme toggle */
            .theme-toggle {
                width: 2.5rem;
                height: 2.5rem;
                border-radius: 50%;
                background: var(--surface);
                border: 1px solid var(--glass-border);
                color: var(--text-primary);
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                backdrop-filter: blur(10px);
            }
            
            .theme-toggle:hover {
                transform: scale(1.1) rotate(180deg);
                box-shadow: var(--glow);
            }
            
            /* Loading states */
            .loading {
                opacity: 0.6;
                pointer-events: none;
                position: relative;
            }
            
            .loading::after {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 1rem;
                height: 1rem;
                margin: -0.5rem 0 0 -0.5rem;
                border: 2px solid transparent;
                border-top: 2px solid var(--primary);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .skeleton {
                background: linear-gradient(90deg, var(--surface) 25%, var(--surface-hover) 50%, var(--surface) 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: 0.5rem;
            }
            
            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }
            
            /* Control buttons */
            .control-buttons {
                display: flex;
                justify-content: center;
                gap: 1rem;
                margin-bottom: 2rem;
                flex-wrap: wrap;
            }
            
            /* Responsive design */
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
                    padding: 1rem;
                }
                
                .card-grid {
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                
                .page-title {
                    font-size: 2rem;
                }
                
                .btn-group {
                    flex-direction: column;
                }
                
                .control-buttons {
                    flex-direction: column;
                }
            }
            
            /* Scrollbar styling */
            ::-webkit-scrollbar {
                width: 6px;
            }
            
            ::-webkit-scrollbar-track {
                background: transparent;
            }
            
            ::-webkit-scrollbar-thumb {
                background: var(--glass-border);
                border-radius: 3px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: var(--primary);
            }
        """)
    ]
)

# Global service manager instance
service_manager = ServiceManager()

def AppHeader():
    """Modern header component"""
    return Header(
        Div(
            Div(
                Div("🚀", cls="logo"),
                "Plasmo Dashboard",
                cls="header-brand"
            ),
            Div(
                Button(
                    "☀️",
                    cls="theme-toggle",
                    onclick="toggleTheme()",
                    title="Toggle theme"
                ),
                Button(
                    "🔄",
                    cls="btn",
                    onclick="refreshAll()",
                    title="Refresh all"
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
                Span("📊", cls="nav-icon"),
                "Dashboard",
                cls="nav-item active",
                onclick="showSection('dashboard')",
                id="nav-dashboard"
            ),
            Button(
                Span("⚙️", cls="nav-icon"),
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
                Span("🧩", cls="nav-icon"),
                "Extensions",
                cls="nav-item",
                onclick="showSection('extensions')",
                id="nav-extensions"
            ),
            Button(
                Span("🧪", cls="nav-icon"),
                "Testing",
                cls="nav-item",
                onclick="showSection('testing')",
                id="nav-testing"
            ),
            Button(
                Span("☁️", cls="nav-icon"),
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
                Span("📄", cls="nav-icon"),
                "Logs",
                cls="nav-item",
                onclick="showSection('logs')",
                id="nav-logs"
            ),
            Button(
                Span("📈", cls="nav-icon"),
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
    """Beautiful service card component"""
    is_running = info.get('running', False)
    status_class = "running" if is_running else "stopped"
    status_text = "Running" if is_running else "Stopped"
    
    # Service icons mapping
    icons = {
        'socketio': '⚡',
        'mcp': '🔌',
        'plasmo': '🧩',
        'tests': '🧪',
        'dashboard': '📊',
        'chrome_debug': '🌐'
    }
    
    icon = icons.get(name, '⚙️')
    
    return Div(
        Div(
            Div(
                Div(icon, cls="card-icon"),
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
                Span("Implementation", cls="service-detail-label"),
                Span(info.get('implementation', 'Unknown'), cls="service-detail-value"),
                cls="service-detail"
            ),
            Div(
                Span("Port", cls="service-detail-label"),
                Span(str(info.get('port', 'N/A')), cls="service-detail-value"),
                cls="service-detail"
            ) if info.get('port') else None,
            Div(
                Span("PID", cls="service-detail-label"),
                Span(str(info.get('pid', 'N/A')), cls="service-detail-value"),
                cls="service-detail"
            ) if info.get('pid') else None,
            cls="service-info"
        ),
        Div(
            Button(
                "▶️ Start",
                cls="btn btn-success",
                onclick=f"controlService('{name}', 'start')",
                disabled=is_running
            ),
            Button(
                "⏹️ Stop",
                cls="btn btn-error",
                onclick=f"controlService('{name}', 'stop')",
                disabled=not is_running
            ),
            Button(
                "🔄 Restart",
                cls="btn btn-warning",
                onclick=f"controlService('{name}', 'restart')"
            ),
            cls="btn-group"
        ),
        cls="card",
        id=f"service-{name}"
    )

def DashboardSection():
    """Main dashboard section"""
    return Div(
        Div(
            H1("Service Overview", cls="page-title"),
            P("Monitor and control all Plasmo extension services with real-time updates", cls="page-subtitle"),
            cls="page-header"
        ),
        Div(
            Button(
                "▶️ Start All Services",
                cls="btn btn-primary",
                onclick="controlAllServices('start')"
            ),
            Button(
                "⏹️ Stop All Services",
                cls="btn btn-error",
                onclick="controlAllServices('stop')"
            ),
            Button(
                "🔄 Restart All Services",
                cls="btn btn-warning",
                onclick="controlAllServices('restart')"
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
        Head(
            Title("🚀 Plasmo Extension Dashboard"),
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1"),
            Meta(name="description", content="Beautiful modern dashboard for Plasmo extension services"),
        ),
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
                // 🎨 PERFECT DASHBOARD INTERACTIONS
                
                // Theme management
                function toggleTheme() {
                    const body = document.body;
                    const currentTheme = body.getAttribute('data-theme') || 'dark';
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    
                    body.style.transition = 'all 0.3s ease';
                    body.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                    
                    setTimeout(() => {
                        body.style.transition = '';
                    }, 300);
                }
                
                // Load saved theme
                const savedTheme = localStorage.getItem('theme') || 'dark';
                document.body.setAttribute('data-theme', savedTheme);
                
                // Service loading with error handling
                async function loadServices() {
                    const dashboardGrid = document.getElementById('services-grid');
                    
                    if (!dashboardGrid) {
                        console.error('Dashboard grid not found');
                        return;
                    }
                    
                    // Show loading skeletons
                    dashboardGrid.innerHTML = Array(6).fill(0).map(() => createSkeletonCard()).join('');
                    
                    try {
                        const response = await fetch('/api/services/status');
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const services = await response.json();
                        
                        if (services.error) {
                            throw new Error(services.error);
                        }
                        
                        // Clear and populate with real data
                        dashboardGrid.innerHTML = '';
                        
                        Object.entries(services).forEach(([name, info], index) => {
                            setTimeout(() => {
                                const cardElement = document.createElement('div');
                                cardElement.innerHTML = createServiceCard(name, info);
                                const card = cardElement.firstElementChild;
                                
                                if (card) {
                                    card.style.opacity = '0';
                                    card.style.transform = 'translateY(20px)';
                                    dashboardGrid.appendChild(card);
                                    
                                    // Animate in
                                    setTimeout(() => {
                                        card.style.transition = 'all 0.5s ease';
                                        card.style.opacity = '1';
                                        card.style.transform = 'translateY(0)';
                                    }, 50);
                                }
                            }, index * 100);
                        });
                        
                    } catch (error) {
                        console.error('Failed to load services:', error);
                        dashboardGrid.innerHTML = `
                            <div class="card" style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                                <h3 style="color: var(--error); margin-bottom: 1rem;">❌ Failed to Load Services</h3>
                                <p style="color: var(--text-secondary); margin-bottom: 1rem;">${error.message}</p>
                                <button class="btn btn-primary" onclick="loadServices()">🔄 Retry</button>
                            </div>
                        `;
                        showNotification('Failed to load services: ' + error.message, 'error');
                    }
                }
                
                function createSkeletonCard() {
                    return `
                        <div class="card">
                            <div class="card-header">
                                <div style="display: flex; align-items: center; gap: 1rem;">
                                    <div class="skeleton" style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem;"></div>
                                    <div class="skeleton" style="width: 120px; height: 1.5rem;"></div>
                                </div>
                                <div class="skeleton" style="width: 80px; height: 1.5rem; border-radius: 1rem;"></div>
                            </div>
                            <div class="service-info">
                                <div class="service-detail">
                                    <div class="skeleton" style="width: 100px; height: 1rem;"></div>
                                    <div class="skeleton" style="width: 80px; height: 1rem;"></div>
                                </div>
                                <div class="service-detail">
                                    <div class="skeleton" style="width: 60px; height: 1rem;"></div>
                                    <div class="skeleton" style="width: 40px; height: 1rem;"></div>
                                </div>
                            </div>
                            <div class="btn-group">
                                <div class="skeleton" style="width: 80px; height: 2.5rem; border-radius: 0.75rem;"></div>
                                <div class="skeleton" style="width: 80px; height: 2.5rem; border-radius: 0.75rem;"></div>
                                <div class="skeleton" style="width: 80px; height: 2.5rem; border-radius: 0.75rem;"></div>
                            </div>
                        </div>
                    `;
                }
                
                function createServiceCard(name, info) {
                    const isRunning = info.running;
                    const statusClass = isRunning ? 'running' : 'stopped';
                    const statusText = isRunning ? 'Running' : 'Stopped';
                    
                    const icons = {
                        'socketio': '⚡',
                        'mcp': '🔌',
                        'plasmo': '🧩',
                        'tests': '🧪',
                        'dashboard': '📊',
                        'chrome_debug': '🌐'
                    };
                    
                    const icon = icons[name] || '⚙️';
                    
                    return `
                        <div class="card" id="service-${name}">
                            <div class="card-header">
                                <div class="card-title">
                                    <div class="card-icon">${icon}</div>
                                    ${name.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase())}
                                </div>
                                <div style="display: flex; align-items: center; gap: 8px;">
                                    <span class="status-dot ${statusClass}"></span>
                                    <span class="status-badge status-${statusClass}">${statusText}</span>
                                </div>
                            </div>
                            <div class="service-info">
                                <div class="service-detail">
                                    <span class="service-detail-label">Implementation</span>
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
                                <button class="btn btn-success" onclick="controlService('${name}', 'start')" ${isRunning ? 'disabled' : ''}>
                                    ▶️ Start
                                </button>
                                <button class="btn btn-error" onclick="controlService('${name}', 'stop')" ${!isRunning ? 'disabled' : ''}>
                                    ⏹️ Stop
                                </button>
                                <button class="btn btn-warning" onclick="controlService('${name}', 'restart')">
                                    🔄 Restart
                                </button>
                            </div>
                        </div>
                    `;
                }
                
                // Service control with proper error handling
                async function controlService(serviceName, action) {
                    const card = document.getElementById(`service-${serviceName}`);
                    if (!card) {
                        console.error(`Card not found for service: ${serviceName}`);
                        return;
                    }
                    
                    card.classList.add('loading');
                    
                    try {
                        const response = await fetch(`/api/services/${serviceName}/${action}`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            }
                        });
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const result = await response.json();
                        
                        if (result.error) {
                            throw new Error(result.error);
                        }
                        
                        showNotification(`${action.charAt(0).toUpperCase() + action.slice(1)}ed ${serviceName}`, 'success');
                        
                        // Refresh services after a short delay
                        setTimeout(loadServices, 1000);
                        
                    } catch (error) {
                        console.error(`Error ${action}ing ${serviceName}:`, error);
                        showNotification(`Failed to ${action} ${serviceName}: ${error.message}`, 'error');
                    } finally {
                        card.classList.remove('loading');
                    }
                }
                
                // Notification system
                function showNotification(message, type = 'info') {
                    const notification = document.createElement('div');
                    notification.style.cssText = `
                        position: fixed;
                        top: 5rem;
                        right: 1.5rem;
                        background: var(--glass);
                        backdrop-filter: blur(20px);
                        border: 1px solid var(--glass-border);
                        border-radius: 0.75rem;
                        padding: 1rem 1.5rem;
                        color: var(--text-primary);
                        font-weight: 500;
                        z-index: 10000;
                        transform: translateX(100%);
                        transition: all 0.3s ease;
                        box-shadow: var(--shadow);
                        max-width: 300px;
                        word-wrap: break-word;
                    `;
                    
                    if (type === 'success') {
                        notification.style.borderLeft = '4px solid var(--success)';
                    } else if (type === 'error') {
                        notification.style.borderLeft = '4px solid var(--error)';
                    }
                    
                    notification.textContent = message;
                    document.body.appendChild(notification);
                    
                    // Animate in
                    setTimeout(() => {
                        notification.style.transform = 'translateX(0)';
                    }, 100);
                    
                    // Animate out and remove
                    setTimeout(() => {
                        notification.style.transform = 'translateX(100%)';
                        setTimeout(() => {
                            if (document.body.contains(notification)) {
                                document.body.removeChild(notification);
                            }
                        }, 300);
                    }, 4000);
                }
                
                // Global refresh function
                function refreshAll() {
                    loadServices();
                    showNotification('Refreshing all services...', 'info');
                }
                
                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('🚀 Perfect Dashboard Initialized');
                    
                    // Load services immediately
                    loadServices();
                    
                    // Auto-refresh every 30 seconds
                    setInterval(loadServices, 30000);
                    
                    // Add scroll effects
                    window.addEventListener('scroll', () => {
                        const header = document.querySelector('.header');
                        if (header) {
                            if (window.scrollY > 50) {
                                header.style.background = 'rgba(255, 255, 255, 0.08)';
                            } else {
                                header.style.background = 'var(--glass)';
                            }
                        }
                    });
                });
                
                // Error handling for uncaught errors
                window.addEventListener('error', function(e) {
                    console.error('Global error:', e.error);
                    showNotification('An unexpected error occurred', 'error');
                });
                
                window.addEventListener('unhandledrejection', function(e) {
                    console.error('Unhandled promise rejection:', e.reason);
                    showNotification('An unexpected error occurred', 'error');
                });
            """)
        )
    )

if __name__ == "__main__":
    import uvicorn
    print("🎨 Starting Perfect Self-Contained Dashboard...")
    print("✨ Features: No External Dependencies, Beautiful Design, Real-time Updates")
    print("🚀 Access at: http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8081, log_level="info")