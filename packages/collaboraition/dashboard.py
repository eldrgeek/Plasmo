#!/usr/bin/env python3
"""
CollaborAItion Dashboard - Single-file FastHTML server with auto-reload
Multi-Agent AI Collaboration Platform Dashboard

Author: CC-Alex (Technical Co-founder)
Date: 2024-12-20
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fasthtml.common import *
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
DATA_DIR = Path(__file__).parent / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
AGENTS_FILE = DATA_DIR / "agents.json"

def load_config() -> Dict:
    """Load configuration from config.json"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {"server": {"host": "127.0.0.1", "port": 8000}}

def load_json_file(file_path: Path) -> List[Dict]:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

def save_json_file(file_path: Path, data: List[Dict]):
    """Save JSON data to file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {file_path}: {e}")

def get_status_color(status: str) -> str:
    """Get CSS color class for status"""
    colors = {
        'active': 'bg-green-500',
        'busy': 'bg-orange-500', 
        'idle': 'bg-yellow-500',
        'offline': 'bg-gray-500',
        'completed': 'bg-green-500',
        'in_progress': 'bg-blue-500',
        'pending': 'bg-gray-400',
        'blocked': 'bg-red-500'
    }
    return colors.get(status, 'bg-gray-400')

def get_priority_color(priority: str) -> str:
    """Get CSS color class for priority"""
    colors = {
        'high': 'text-red-600 border-red-200 bg-red-50',
        'medium': 'text-yellow-600 border-yellow-200 bg-yellow-50', 
        'low': 'text-green-600 border-green-200 bg-green-50'
    }
    return colors.get(priority, 'text-gray-600 border-gray-200 bg-gray-50')

def format_time_ago(timestamp: str) -> str:
    """Format timestamp as 'X minutes ago'"""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        diff = now - dt
        
        if diff.seconds < 60:
            return "Just now"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60} minutes ago"
        elif diff.days == 0:
            return f"{diff.seconds // 3600} hours ago"
        else:
            return f"{diff.days} days ago"
    except:
        return "Unknown"

# Initialize FastHTML app
config = load_config()
app, rt = fast_app(
    hdrs=(
        Link(rel="stylesheet", href="https://cdn.tailwindcss.com/3.3.2"),
        Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        Title("CollaborAItion Dashboard")
    )
)

@rt("/")
def homepage():
    """Main dashboard homepage"""
    tasks = load_json_file(TASKS_FILE)
    agents = load_json_file(AGENTS_FILE)
    
    # Calculate stats
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    active_agents = len([a for a in agents if a.get('status') == 'active'])
    total_agents = len(agents)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    return Html(
        Head(
            Meta(charset="utf-8"),
            Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            Title("CollaborAItion Dashboard"),
            Link(rel="stylesheet", href="https://cdn.tailwindcss.com/3.3.2"),
            Script("""
                function switchTab(tab) {
                    // Hide all tab contents
                    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
                    document.querySelectorAll('.tab-button').forEach(el => {
                        el.classList.remove('bg-blue-50', 'text-blue-600', 'border-b-2', 'border-blue-600');
                        el.classList.add('text-gray-600', 'hover:bg-gray-50');
                    });
                    
                    // Show selected tab
                    document.getElementById(tab + '-content').classList.remove('hidden');
                    document.getElementById(tab + '-tab').classList.add('bg-blue-50', 'text-blue-600', 'border-b-2', 'border-blue-600');
                    document.getElementById(tab + '-tab').classList.remove('text-gray-600', 'hover:bg-gray-50');
                }
                
                // Auto-refresh every 30 seconds
                setTimeout(() => location.reload(), 30000); 
            """)
        ),
        Body(
            Div(
                # Header
                Div(
                    H1("CollaborAItion 0.1", cls="text-2xl font-bold text-white"),
                    P("Multi-Agent AI Coordination Platform", cls="text-sm opacity-90 text-white"),
                    cls="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6"
                ),
                
                # Navigation Tabs
                Div(
                    Button("Overview", onclick="switchTab('overview')", 
                           id="overview-tab", cls="tab-button flex-1 py-3 px-4 text-sm font-medium bg-blue-50 text-blue-600 border-b-2 border-blue-600"),
                    Button("Agents", onclick="switchTab('agents')", 
                           id="agents-tab", cls="tab-button flex-1 py-3 px-4 text-sm font-medium text-gray-600 hover:bg-gray-50"),
                    Button("Tasks", onclick="switchTab('tasks')", 
                           id="tasks-tab", cls="tab-button flex-1 py-3 px-4 text-sm font-medium text-gray-600 hover:bg-gray-50"),
                    cls="flex border-b"
                ),
                
                # Overview Tab Content
                Div(
                    # Stats Cards
                    Div(
                        Div(
                            Div(f"{completed_tasks}/{total_tasks}", cls="text-3xl font-bold text-blue-600"),
                            Div("Tasks Complete", cls="text-sm text-blue-700"),
                            cls="bg-blue-50 border border-blue-200 rounded-lg p-4"
                        ),
                        Div(
                            Div(f"{active_agents}/{total_agents}", cls="text-3xl font-bold text-green-600"),
                            Div("Agents Active", cls="text-sm text-green-700"),
                            cls="bg-green-50 border border-green-200 rounded-lg p-4"
                        ),
                        cls="grid grid-cols-2 gap-4 mb-6"
                    ),
                    
                    # Progress Bar
                    Div(
                        Div(
                            Div(style=f"width: {completion_rate}%", 
                                cls="bg-blue-500 h-3 rounded-full transition-all duration-300"),
                            cls="bg-gray-200 rounded-full h-3 mb-2"
                        ),
                        Div(f"{completion_rate:.0f}% Complete", cls="text-sm text-gray-600 text-center"),
                        cls="mb-6"
                    ),
                    
                    # Quick Actions
                    Div(
                        H3("Quick Actions", cls="font-semibold text-lg mb-4"),
                        Button("+ New Task", cls="w-full bg-blue-500 text-white py-3 px-4 rounded-lg mb-3 hover:bg-blue-600 font-medium"),
                        Button("🤝 Coordinate Agents", cls="w-full bg-green-500 text-white py-3 px-4 rounded-lg mb-3 hover:bg-green-600 font-medium"),
                        Button("📊 View Analytics", cls="w-full bg-purple-500 text-white py-3 px-4 rounded-lg hover:bg-purple-600 font-medium"),
                    ),
                    
                    id="overview-content", cls="tab-content p-6"
                ),
                
                # Agents Tab Content
                Div(
                    H3("Team Agents", cls="font-semibold text-lg mb-4"),
                    *[
                        Div(
                            Div(
                                Div(
                                    H4(agent['name'], cls="font-semibold text-base"),
                                    Div(
                                        Div(cls=f"w-3 h-3 rounded-full {get_status_color(agent.get('status', 'offline'))}"),
                                        Span(agent.get('status', 'offline').title(), cls="text-sm ml-2"),
                                        cls="flex items-center"
                                    ),
                                    cls="flex items-center justify-between mb-2"
                                ),
                                P(agent.get('role', 'Unknown Role'), cls="text-sm text-gray-600 mb-2"),
                                P(f"💼 {agent.get('currentTask', 'No current task')}" if agent.get('currentTask') else "💤 Idle", 
                                  cls="text-sm text-blue-600 mb-2"),
                                P(f"Last active: {format_time_ago(agent.get('lastActivity', ''))}", 
                                  cls="text-xs text-gray-500"),
                                cls="border rounded-lg p-4 mb-4 hover:shadow-md transition-shadow"
                            )
                        ) for agent in agents
                    ],
                    id="agents-content", cls="tab-content p-6 hidden"
                ),
                
                # Tasks Tab Content  
                Div(
                    H3("Project Tasks", cls="font-semibold text-lg mb-4"),
                    *[
                        Div(
                            Div(
                                H4(task['title'], cls="font-semibold text-base mb-2"),
                                Div(
                                    Div(cls=f"w-3 h-3 rounded-full {get_status_color(task.get('status', 'pending'))}"),
                                    Span(f"{task.get('priority', 'medium').upper()}", 
                                         cls=f"text-xs px-2 py-1 rounded border {get_priority_color(task.get('priority', 'medium'))}"),
                                    cls="flex items-center gap-2"
                                ),
                                cls="flex items-start justify-between mb-2"
                            ),
                            P(task.get('description', 'No description'), cls="text-sm text-gray-600 mb-3"),
                            Div(
                                P(f"👤 {task.get('assignedTo', 'Unassigned')}", cls="text-xs text-blue-600 mb-1") if task.get('assignedTo') else "",
                                P(f"Status: {task.get('status', 'pending').replace('_', ' ').title()}", cls="text-xs text-gray-500"),
                                cls="border-t pt-2"
                            ),
                            cls="border rounded-lg p-4 mb-4 hover:shadow-md transition-shadow"
                        ) for task in tasks
                    ],
                    id="tasks-content", cls="tab-content p-6 hidden"
                ),
                
                # Footer
                Div(
                    P("Built by CollaborAItion Team • Live Status • Auto-refresh: 30s", 
                      cls="text-xs text-gray-500 text-center"),
                    cls="border-t p-4 bg-gray-50"
                ),
                
                cls="max-w-4xl mx-auto bg-white shadow-lg"
            ),
            cls="min-h-screen bg-gray-100"
        )
    )

@rt("/api/tasks")
def get_tasks():
    """API endpoint to get tasks as JSON"""
    tasks = load_json_file(TASKS_FILE)
    return {"tasks": tasks}

@rt("/api/agents")  
def get_agents():
    """API endpoint to get agents as JSON"""
    agents = load_json_file(AGENTS_FILE) 
    return {"agents": agents}

@rt("/api/stats")
def get_stats():
    """API endpoint to get project statistics"""
    tasks = load_json_file(TASKS_FILE)
    agents = load_json_file(AGENTS_FILE)
    
    return {
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.get('status') == 'completed']),
        "active_agents": len([a for a in agents if a.get('status') == 'active']),
        "total_agents": len(agents),
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

# Auto-reload setup
class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for auto-reload"""
    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in ['.py', '.json']:
                print(f"File changed: {file_path.name} - Server will auto-reload...")
                # FastHTML handles the actual reload

def setup_auto_reload():
    """Set up file watching for auto-reload"""
    observer = Observer()
    handler = ConfigFileHandler()
    
    # Watch current directory and data directory
    observer.schedule(handler, str(Path(__file__).parent), recursive=False)
    observer.schedule(handler, str(DATA_DIR), recursive=False)
    
    observer.start()
    print("🔄 Auto-reload enabled - watching for file changes...")
    return observer

if __name__ == "__main__":
    print("🚀 Starting CollaborAItion Dashboard...")
    print(f"📁 Data directory: {DATA_DIR}")
    print(f"⚙️  Config file: {CONFIG_FILE}")
    
    # Setup auto-reload
    observer = setup_auto_reload()
    
    try:
        serve(
            host=config['server']['host'],
            port=config['server']['port'],
            reload=config['server'].get('auto_reload', True)
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down CollaborAItion Dashboard...")
        observer.stop()
    observer.join()