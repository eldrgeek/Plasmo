#!/usr/bin/env python3
"""
Python Socket.IO Server for Plasmo Extension with FastAPI.
Enhanced with user data structures, inactive user management, and file uploads.
"""

import os
import sys
import json
import asyncio
import logging
import subprocess
import uuid
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import uvicorn
import socketio
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

# Create uploads directory
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

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

# Enhanced WebRTC Models with user data support
class JoinRoomRequest(BaseModel):
    room_name: str
    peer_id: str
    username: str
    user_data: Optional[Dict[str, Any]] = {}  # Arbitrary application-specific data

class UpdateUserDataRequest(BaseModel):
    user_data: Dict[str, Any]  # New user data to merge

class PeerInfo(BaseModel):
    peer_id: str
    username: str
    socket_id: str
    joined_at: str
    is_active: bool = True
    last_seen: str
    user_data: Dict[str, Any] = {}  # Arbitrary application-specific information
    uploaded_files: List[str] = []  # Paths to uploaded files

# Global state management
connected_extensions: Dict[str, Dict] = {}
completion_signals: Dict[str, Dict] = {}
test_results: Dict[str, Dict] = {}

# Enhanced WebRTC Room Management with user data
webrtc_rooms: Dict[str, Dict] = {}  # room_name -> room_data
peer_to_room: Dict[str, str] = {}   # peer_id -> room_name
socket_to_peer: Dict[str, str] = {} # socket_id -> peer_id

# Room configuration
MAX_PEERS_PER_ROOM = 100

# Initialize FastAPI app
app = FastAPI(
    title="Plasmo Extension Socket.IO Server",
    description="Enhanced Python-based Socket.IO server with user data and file uploads",
    version="2.0.0"
)

# Mount uploads directory for static file serving
app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Initialize Socket.IO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    async_mode='asgi',
    ping_timeout=60,          # 60 seconds before timing out inactive connections
    ping_interval=25,         # Send ping every 25 seconds
    max_http_buffer_size=1000000  # 1MB buffer for large messages
)

# Combine FastAPI and Socket.IO
socket_app = socketio.ASGIApp(sio, app)

# Startup event to initialize background tasks
@app.on_event("startup")
async def startup_event():
    """Initialize background tasks when server starts"""
    logger.info("🔄 Server startup complete - background tasks will be managed by event loop")

# Enhanced WebRTC Room Management Functions
def create_room_if_not_exists(room_name: str) -> Dict:
    """Create a room if it doesn't exist"""
    if room_name not in webrtc_rooms:
        webrtc_rooms[room_name] = {
            "name": room_name,
            "peers": {},  # peer_id -> enhanced peer info with user_data
            "created_at": datetime.now().isoformat(),
            "max_peers": MAX_PEERS_PER_ROOM
        }
        logger.info(f"🏠 Created new WebRTC room: {room_name}")
    return webrtc_rooms[room_name]

def add_peer_to_room(room_name: str, peer_id: str, username: str, socket_id: str, user_data: Dict[str, Any] = None) -> bool:
    """Add a peer to a room with enhanced user data. Returns True if successful, False if room is full"""
    room = create_room_if_not_exists(room_name)
    
    # Check if peer already exists (reactivating)
    if peer_id in room["peers"]:
        # Reactivate existing peer
        room["peers"][peer_id].update({
            "socket_id": socket_id,
            "is_active": True,
            "last_seen": datetime.now().isoformat(),
            "username": username  # Allow username updates
        })
        # Merge new user_data if provided
        if user_data:
            room["peers"][peer_id]["user_data"].update(user_data)
        logger.info(f"🔄 Reactivated peer {peer_id} ({username}) in room {room_name}")
    else:
        # Check room capacity for new peers only
        active_peers = sum(1 for peer in room["peers"].values() if peer["is_active"])
        if active_peers >= MAX_PEERS_PER_ROOM:
            logger.warning(f"🚫 Room {room_name} is full ({MAX_PEERS_PER_ROOM} active peers)")
            return False
        
        # Add new peer
        room["peers"][peer_id] = {
            "username": username,
            "socket_id": socket_id,
            "joined_at": datetime.now().isoformat(),
            "is_active": True,
            "last_seen": datetime.now().isoformat(),
            "user_data": user_data or {},
            "uploaded_files": []
        }
        logger.info(f"👤 Added new peer {peer_id} ({username}) to room {room_name}")
    
    # Remove peer from previous room if exists
    if peer_id in peer_to_room and peer_to_room[peer_id] != room_name:
        old_room = peer_to_room[peer_id]
        deactivate_peer_in_room(old_room, peer_id)
    
    # Update mappings
    peer_to_room[peer_id] = room_name
    socket_to_peer[socket_id] = peer_id
    
    return True

def deactivate_peer_in_room(room_name: str, peer_id: str) -> bool:
    """Mark a peer as inactive instead of removing them. Returns True if successful"""
    if room_name not in webrtc_rooms:
        return False
    
    room = webrtc_rooms[room_name]
    if peer_id not in room["peers"]:
        return False
    
    # Mark peer as inactive instead of removing
    room["peers"][peer_id]["is_active"] = False
    room["peers"][peer_id]["last_seen"] = datetime.now().isoformat()
    
    # Get socket_id before cleaning up mappings
    socket_id = room["peers"][peer_id]["socket_id"]
    
    # Clean up active mappings but keep peer data
    if peer_id in peer_to_room:
        del peer_to_room[peer_id]
    if socket_id in socket_to_peer:
        del socket_to_peer[socket_id]
    
    logger.info(f"😴 Marked peer {peer_id} as inactive in room {room_name}")
    return True

def get_peer_list(room_name: str, include_inactive: bool = True) -> List[Dict]:
    """Get list of peers in a room, optionally including inactive peers"""
    if room_name not in webrtc_rooms:
        return []
    
    room = webrtc_rooms[room_name]
    peer_list = []
    
    for peer_id, peer_info in room["peers"].items():
        if include_inactive or peer_info["is_active"]:
            peer_list.append({
                "peer_id": peer_id,
                "username": peer_info["username"],
                "joined_at": peer_info["joined_at"],
                "is_active": peer_info["is_active"],
                "last_seen": peer_info["last_seen"],
                "user_data": peer_info["user_data"],
                "uploaded_files": peer_info["uploaded_files"]
            })
    
    return peer_list

def update_peer_data(room_name: str, peer_id: str, user_data: Dict[str, Any]) -> bool:
    """Update arbitrary user data for a peer"""
    if room_name not in webrtc_rooms:
        return False
    
    room = webrtc_rooms[room_name]
    if peer_id not in room["peers"]:
        return False
    
    # Merge new data with existing data
    room["peers"][peer_id]["user_data"].update(user_data)
    room["peers"][peer_id]["last_seen"] = datetime.now().isoformat()
    
    logger.info(f"📝 Updated user data for peer {peer_id} in room {room_name}")
    return True

def add_file_to_peer(room_name: str, peer_id: str, file_path: str) -> bool:
    """Add an uploaded file path to a peer's data"""
    if room_name not in webrtc_rooms:
        return False
    
    room = webrtc_rooms[room_name]
    if peer_id not in room["peers"]:
        return False
    
    room["peers"][peer_id]["uploaded_files"].append(file_path)
    room["peers"][peer_id]["last_seen"] = datetime.now().isoformat()
    
    logger.info(f"📎 Added file {file_path} to peer {peer_id} in room {room_name}")
    return True

async def broadcast_peer_list_to_room(room_name: str, include_inactive: bool = True):
    """Broadcast updated peer list to all active peers in a room"""
    if room_name not in webrtc_rooms:
        return
    
    room = webrtc_rooms[room_name]
    peer_list = get_peer_list(room_name, include_inactive=include_inactive)
    active_peers = [p for p in peer_list if p["is_active"]]
    
    # Send to all active peers in the room
    for peer_id, peer_info in room["peers"].items():
        if peer_info["is_active"]:
            socket_id = peer_info["socket_id"]
            await sio.emit('peer_list_updated', {
                'room_name': room_name,
                'peers': peer_list,
                'active_peers': len(active_peers),
                'total_peers': len(peer_list)
            }, room=socket_id)
    
    logger.info(f"📡 Broadcasted peer list to room {room_name} ({len(active_peers)} active, {len(peer_list)} total)")

# Socket.IO Event Handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    client_ip = environ.get('REMOTE_ADDR', 'unknown')
    user_agent = environ.get('HTTP_USER_AGENT', 'unknown')
    logger.info(f"🔌 Client connected: {sid} from {client_ip}")
    logger.debug(f"   User-Agent: {user_agent}")

@sio.event  
async def disconnect(sid):
    """Handle client disconnection with enhanced cleanup"""
    logger.info(f"❌ Client disconnected: {sid}")
    
    # Enhanced cleanup for WebRTC rooms
    if sid in socket_to_peer:
        peer_id = socket_to_peer[sid]
        if peer_id in peer_to_room:
            room_name = peer_to_room[peer_id]
            if deactivate_peer_in_room(room_name, peer_id):
                await broadcast_peer_list_to_room(room_name)
    
    # Clean up extension registration
    if sid in connected_extensions:
        del connected_extensions[sid]
        logger.info(f"🧩 Cleaned up extension registration for {sid}")

# Add connection health check
@sio.event
async def ping(sid):
    """Handle ping from client"""
    logger.debug(f"🏓 Ping received from {sid}")
    await sio.emit('pong', to=sid)

@sio.event
async def connection_test(sid, data):
    """Test connection stability"""
    logger.info(f"🧪 Connection test from {sid}: {data}")
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "sid": sid,
        "echo": data
    }

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

# Enhanced WebRTC Event Handlers
@sio.event
async def join_room(sid, data):
    """Handle WebRTC room join request with clean state management"""
    try:
        room_name = data.get('room_name')
        peer_id = data.get('peer_id')
        username = data.get('username')
        user_data = data.get('user_data', {})
        
        if not all([room_name, peer_id, username]):
            await sio.emit('join_room_error', {
                'error': 'Missing required fields: room_name, peer_id, username'
            }, room=sid)
            return

        # Check if peer already exists and is just reconnecting
        room = create_room_if_not_exists(room_name)
        was_existing = peer_id in room["peers"]
        was_active = was_existing and room["peers"][peer_id]["is_active"]
        
        # Add/reactivate peer
        success = add_peer_to_room(room_name, peer_id, username, sid, user_data)
        
        if not success:
            await sio.emit('join_room_error', {
                'error': f'Room {room_name} is full (max {MAX_PEERS_PER_ROOM} active peers)'
            }, room=sid)
            return

        # Get current peer list for the response
        peer_list = get_peer_list(room_name, include_inactive=True)
        active_peers = [p for p in peer_list if p["is_active"]]
        
        # Send simple success response to joining peer (no duplicate peer list)
        await sio.emit('join_room_success', {
            'room_name': room_name,
            'peer_id': peer_id,
            'status': 'reactivated' if was_existing else 'joined',
            'active_peers': len(active_peers),
            'total_peers': len(peer_list)
        }, room=sid)

        # Only broadcast peer list update if this was a state change
        if not was_active:  # Only if peer wasn't already active
            await broadcast_peer_list_to_room(room_name)
            action = "reactivated" if was_existing else "joined"
            logger.info(f"✅ Peer {peer_id} ({username}) {action} room {room_name}")
        
    except Exception as e:
        logger.error(f"Error in join_room: {e}")
        await sio.emit('join_room_error', {
            'error': str(e)
        }, room=sid)

@sio.event
async def leave_room(sid, data):
    """Handle WebRTC room leave request (marks as inactive)"""
    try:
        if sid not in socket_to_peer:
            await sio.emit('leave_room_error', {
                'error': 'Not in any room'
            }, room=sid)
            return
        
        peer_id = socket_to_peer[sid]
        room_name = peer_to_room.get(peer_id)
        
        if not room_name:
            await sio.emit('leave_room_error', {
                'error': 'Room not found'
            }, room=sid)
            return

        # Check if peer was actually active before deactivating
        room = webrtc_rooms.get(room_name)
        was_active = room and peer_id in room["peers"] and room["peers"][peer_id]["is_active"]
        
        # Mark peer as inactive
        success = deactivate_peer_in_room(room_name, peer_id)
        
        if success:
            await sio.emit('leave_room_success', {
                'room_name': room_name,
                'peer_id': peer_id,
                'status': 'inactive'
            }, room=sid)
            
            # Only broadcast if peer was actually active
            if was_active:
                await broadcast_peer_list_to_room(room_name)
                logger.info(f"✅ Peer {peer_id} marked inactive in room {room_name}")
        else:
            await sio.emit('leave_room_error', {
                'error': 'Failed to leave room'
            }, room=sid)
            
    except Exception as e:
        logger.error(f"Error in leave_room: {e}")
        await sio.emit('leave_room_error', {
            'error': str(e)
        }, room=sid)

@sio.event
async def update_user_data(sid, data):
    """Handle user data update request"""
    try:
        if sid not in socket_to_peer:
            await sio.emit('update_user_data_error', {
                'error': 'Not in any room'
            }, room=sid)
            return
        
        peer_id = socket_to_peer[sid]
        room_name = peer_to_room.get(peer_id)
        user_data = data.get('user_data', {})
        
        if not room_name:
            await sio.emit('update_user_data_error', {
                'error': 'Room not found'
            }, room=sid)
            return
        
        # Update user data
        success = update_peer_data(room_name, peer_id, user_data)
        
        if success:
            await sio.emit('update_user_data_success', {
                'room_name': room_name,
                'peer_id': peer_id,
                'user_data': user_data
            }, room=sid)
            
            # Broadcast updated peer list to all active peers
            await broadcast_peer_list_to_room(room_name)
            
            logger.info(f"✅ Updated user data for peer {peer_id} in room {room_name}")
        else:
            await sio.emit('update_user_data_error', {
                'error': 'Failed to update user data'
            }, room=sid)
            
    except Exception as e:
        logger.error(f"Error in update_user_data: {e}")
        await sio.emit('update_user_data_error', {
            'error': str(e)
        }, room=sid)

@sio.event
async def request_peer_list(sid, data):
    """Handle client request for current peer list"""
    try:
        room_name = data.get('room_name')
        include_inactive = data.get('include_inactive', True)
        
        if not room_name:
            await sio.emit('peer_list_error', {
                'error': 'Missing room_name'
            }, room=sid)
            return
        
        # Get current peer list
        peer_list = get_peer_list(room_name, include_inactive=include_inactive)
        active_peers = [p for p in peer_list if p["is_active"]]
        
        await sio.emit('peer_list_response', {
            'room_name': room_name,
            'peers': peer_list,
            'active_peers': len(active_peers),
            'total_peers': len(peer_list),
            'timestamp': datetime.now().isoformat()
        }, room=sid)
        
    except Exception as e:
        logger.error(f"Error in request_peer_list: {e}")
        await sio.emit('peer_list_error', {
            'error': str(e)
        }, room=sid)

@sio.event
async def heartbeat(sid, data):
    """Handle client heartbeat to update last_seen timestamp"""
    try:
        if sid not in socket_to_peer:
            return
        
        peer_id = socket_to_peer[sid]
        room_name = peer_to_room.get(peer_id)
        
        if room_name and room_name in webrtc_rooms:
            room = webrtc_rooms[room_name]
            if peer_id in room["peers"] and room["peers"][peer_id]["is_active"]:
                room["peers"][peer_id]["last_seen"] = datetime.now().isoformat()
                
                # Send heartbeat response
                await sio.emit('heartbeat_ack', {
                    'timestamp': datetime.now().isoformat()
                }, room=sid)
        
    except Exception as e:
        logger.error(f"Error in heartbeat: {e}")

# Add periodic cleanup task
async def cleanup_inactive_peers():
    """Periodically remove very old inactive peers (24+ hours)"""
    while True:
        try:
            now = datetime.now()
            cleanup_threshold = now - timedelta(hours=24)
            
            for room_name, room in list(webrtc_rooms.items()):
                peers_to_remove = []
                
                for peer_id, peer_info in room["peers"].items():
                    if not peer_info["is_active"]:
                        last_seen = datetime.fromisoformat(peer_info["last_seen"])
                        if last_seen < cleanup_threshold:
                            peers_to_remove.append(peer_id)
                
                # Remove old inactive peers
                for peer_id in peers_to_remove:
                    del room["peers"][peer_id]
                    logger.info(f"🧹 Cleaned up old inactive peer {peer_id} from room {room_name}")
                
                # Remove empty rooms (no peers at all)
                if not room["peers"]:
                    del webrtc_rooms[room_name]
                    logger.info(f"🧹 Cleaned up empty room {room_name}")
            
            # Sleep for 1 hour before next cleanup
            await asyncio.sleep(3600)
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            await asyncio.sleep(3600)  # Still wait before retrying

# REST API Endpoints
@app.get("/", response_class=HTMLResponse)
async def get_web_interface():
    """Serve the enhanced web interface with room/client status dashboard"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Socket.IO WebRTC Room Dashboard</title>
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .dashboard {
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }
            
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
                border-left: 4px solid #4facfe;
            }
            
            .stat-number {
                font-size: 2.5em;
                font-weight: bold;
                color: #2d3748;
                margin-bottom: 5px;
            }
            
            .stat-label {
                color: #718096;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .rooms-container {
                padding: 30px;
            }
            
            .room-card {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                margin-bottom: 20px;
                overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .room-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .room-title {
                font-size: 1.4em;
                font-weight: bold;
            }
            
            .room-stats {
                display: flex;
                gap: 20px;
                font-size: 0.9em;
            }
            
            .room-stat {
                display: flex;
                align-items: center;
                gap: 5px;
            }
            
            .clients-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
                padding: 20px;
                background: #f7fafc;
            }
            
            .client-card {
                background: white;
                border-radius: 6px;
                padding: 15px;
                border-left: 4px solid #48bb78;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            
            .client-card:hover {
                transform: translateY(-2px);
            }
            
            .client-card.inactive {
                border-left-color: #ed8936;
                opacity: 0.7;
            }
            
            .client-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }
            
            .client-name {
                font-weight: bold;
                color: #2d3748;
            }
            
            .client-status {
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 0.8em;
                font-weight: bold;
                text-transform: uppercase;
            }
            
            .client-status.active {
                background: #c6f6d5;
                color: #276749;
            }
            
            .client-status.inactive {
                background: #fed7cc;
                color: #c05621;
            }
            
            .client-details {
                font-size: 0.9em;
                color: #718096;
                line-height: 1.4;
            }
            
            .client-id {
                font-family: monospace;
                background: #edf2f7;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 0.8em;
            }
            
            .no-rooms {
                text-align: center;
                padding: 60px 30px;
                color: #718096;
            }
            
            .no-rooms h3 {
                margin-bottom: 10px;
                font-size: 1.5em;
            }
            
            .refresh-button {
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 1em;
                cursor: pointer;
                transition: transform 0.2s;
                margin: 20px auto;
                display: block;
            }
            
            .refresh-button:hover {
                transform: translateY(-1px);
            }
            
            .last-updated {
                text-align: center;
                color: #718096;
                font-size: 0.9em;
                padding: 20px;
                border-top: 1px solid #e2e8f0;
            }
            
            .loading {
                text-align: center;
                padding: 40px;
                color: #718096;
            }
            
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            .loading::after {
                content: "●●●";
                animation: pulse 1.5s infinite;
                margin-left: 10px;
            }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🌐 WebRTC Room Dashboard</h1>
                <p>Real-time Socket.IO client and room monitoring</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="total-rooms">-</div>
                    <div class="stat-label">Total Rooms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="active-clients">-</div>
                    <div class="stat-label">Active Clients</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="total-clients">-</div>
                    <div class="stat-label">Total Clients</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="ping-timeout">60s</div>
                    <div class="stat-label">Ping Timeout</div>
                </div>
            </div>
            
            <div class="rooms-container">
                <button class="refresh-button" onclick="loadRooms()">🔄 Refresh Data</button>
                <div id="rooms-list" class="loading">Loading rooms...</div>
            </div>
            
            <div class="last-updated">
                Last updated: <span id="last-updated-time">-</span>
            </div>
        </div>

        <script>
            let autoRefreshInterval;
            
            async function loadRooms() {
                try {
                    const [healthResponse, roomsResponse] = await Promise.all([
                        fetch('/health'),
                        fetch('/api/webrtc/rooms')
                    ]);
                    
                    const health = await healthResponse.json();
                    const roomsData = await roomsResponse.json();
                    
                    // Update stats
                    document.getElementById('total-rooms').textContent = roomsData.rooms.length;
                    document.getElementById('ping-timeout').textContent = health.server_config?.ping_timeout + 's' || '60s';
                    
                    let totalActiveClients = 0;
                    let totalClients = 0;
                    
                    const roomsList = document.getElementById('rooms-list');
                    
                    if (roomsData.rooms.length === 0) {
                        roomsList.innerHTML = `
                            <div class="no-rooms">
                                <h3>No Active Rooms</h3>
                                <p>Rooms will appear here when clients connect</p>
                            </div>
                        `;
                    } else {
                        let roomsHtml = '';
                        
                        for (const room of roomsData.rooms) {
                            const roomDetails = await fetch(`/api/webrtc/rooms/${room.name}`);
                            const roomData = await roomDetails.json();
                            
                            const activeClients = roomData.peers.filter(p => p.is_active).length;
                            const totalRoomClients = roomData.peers.length;
                            
                            totalActiveClients += activeClients;
                            totalClients += totalRoomClients;
                            
                            roomsHtml += generateRoomHtml(roomData);
                        }
                        
                        roomsList.innerHTML = roomsHtml;
                    }
                    
                    // Update global stats
                    document.getElementById('active-clients').textContent = totalActiveClients;
                    document.getElementById('total-clients').textContent = totalClients;
                    document.getElementById('last-updated-time').textContent = new Date().toLocaleTimeString();
                    
                } catch (error) {
                    console.error('Error loading rooms:', error);
                    document.getElementById('rooms-list').innerHTML = `
                        <div class="no-rooms">
                            <h3>Error Loading Rooms</h3>
                            <p>Failed to fetch room data: ${error.message}</p>
                        </div>
                    `;
                }
            }
            
            function generateRoomHtml(roomData) {
                const activeClients = roomData.peers.filter(p => p.is_active);
                const inactiveClients = roomData.peers.filter(p => !p.is_active);
                
                let clientsHtml = '';
                
                // Active clients first
                activeClients.forEach(client => {
                    clientsHtml += generateClientHtml(client, true);
                });
                
                // Then inactive clients
                inactiveClients.forEach(client => {
                    clientsHtml += generateClientHtml(client, false);
                });
                
                return `
                    <div class="room-card">
                        <div class="room-header">
                            <div class="room-title">🏠 ${roomData.name}</div>
                            <div class="room-stats">
                                <div class="room-stat">
                                    <span>✅ Active:</span>
                                    <strong>${activeClients.length}</strong>
                                </div>
                                <div class="room-stat">
                                    <span>💤 Inactive:</span>
                                    <strong>${inactiveClients.length}</strong>
                                </div>
                                <div class="room-stat">
                                    <span>📊 Total:</span>
                                    <strong>${roomData.peers.length}</strong>
                                </div>
                            </div>
                        </div>
                        <div class="clients-grid">
                            ${clientsHtml || '<div style="padding: 20px; text-align: center; color: #718096;">No clients in this room</div>'}
                        </div>
                    </div>
                `;
            }
            
            function generateClientHtml(client, isActive) {
                const joinedDate = new Date(client.joined_at);
                const lastSeenDate = new Date(client.last_seen);
                
                return `
                    <div class="client-card ${isActive ? 'active' : 'inactive'}">
                        <div class="client-header">
                            <div class="client-name">👤 ${client.username}</div>
                            <div class="client-status ${isActive ? 'active' : 'inactive'}">
                                ${isActive ? 'Active' : 'Inactive'}
                            </div>
                        </div>
                        <div class="client-details">
                            <div>ID: <span class="client-id">${client.peer_id.substring(0, 8)}...</span></div>
                            <div>Joined: ${joinedDate.toLocaleString()}</div>
                            <div>Last seen: ${lastSeenDate.toLocaleString()}</div>
                            ${client.uploaded_files.length > 0 ? `<div>📎 Files: ${client.uploaded_files.length}</div>` : ''}
                            ${Object.keys(client.user_data).length > 0 ? `<div>📋 Has custom data</div>` : ''}
                        </div>
                    </div>
                `;
            }
            
            // Load rooms on page load
            loadRooms();
            
            // Auto-refresh every 10 seconds
            autoRefreshInterval = setInterval(loadRooms, 10000);
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', () => {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Enhanced health check with connection statistics"""
    active_connections = len(connected_extensions)
    active_peers = sum(
        sum(1 for peer in room["peers"].values() if peer["is_active"]) 
        for room in webrtc_rooms.values()
    )
    total_peers = sum(len(room["peers"]) for room in webrtc_rooms.values())
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "connections": {
            "extensions": active_connections,
            "webrtc_active_peers": active_peers,
            "webrtc_total_peers": total_peers,
            "rooms": len(webrtc_rooms)
        },
        "uptime": datetime.now().isoformat(),
        "server_config": {
            "ping_timeout": 60,
            "ping_interval": 25,
            "max_buffer_size": 1000000
        }
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

# Enhanced WebRTC REST API Endpoints
@app.get("/api/webrtc/rooms")
async def get_webrtc_rooms():
    """Get all WebRTC rooms with enhanced peer info including inactive users"""
    rooms_info = {}
    for room_name, room_data in webrtc_rooms.items():
        all_peers = get_peer_list(room_name, include_inactive=True)
        active_peers = [p for p in all_peers if p["is_active"]]
        
        rooms_info[room_name] = {
            "name": room_name,
            "active_peer_count": len(active_peers),
            "total_peer_count": len(all_peers),
            "max_peers": room_data["max_peers"],
            "created_at": room_data["created_at"],
            "peers": all_peers
        }
    return rooms_info

@app.get("/api/webrtc/rooms/{room_name}")
async def get_webrtc_room(room_name: str):
    """Get specific WebRTC room information with enhanced peer data"""
    if room_name not in webrtc_rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    
    room_data = webrtc_rooms[room_name]
    all_peers = get_peer_list(room_name, include_inactive=True)
    active_peers = [p for p in all_peers if p["is_active"]]
    
    return {
        "name": room_name,
        "active_peer_count": len(active_peers),
        "total_peer_count": len(all_peers),
        "max_peers": room_data["max_peers"],
        "created_at": room_data["created_at"],
        "peers": all_peers
    }

@app.post("/api/webrtc/rooms/{room_name}/join")
async def join_room_http(room_name: str, request: JoinRoomRequest):
    """HTTP endpoint to join a WebRTC room with user data support"""
    # Generate socket_id for HTTP clients
    socket_id = f"http_{request.peer_id}_{datetime.now().timestamp()}"
    
    success = add_peer_to_room(room_name, request.peer_id, request.username, socket_id, request.user_data)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"Room {room_name} is full (max {MAX_PEERS_PER_ROOM} active peers)"
        )
    
    peer_list = get_peer_list(room_name, include_inactive=True)
    active_peers = [p for p in peer_list if p["is_active"]]
    
    return {
        "success": True,
        "room_name": room_name,
        "peer_id": request.peer_id,
        "peers": peer_list,
        "active_peers": len(active_peers),
        "total_peers": len(peer_list)
    }

@app.post("/api/webrtc/rooms/{room_name}/update-data")
async def update_user_data_http(room_name: str, peer_id: str, request: UpdateUserDataRequest):
    """HTTP endpoint to update user data for a peer"""
    success = update_peer_data(room_name, peer_id, request.user_data)
    
    if not success:
        raise HTTPException(status_code=404, detail="Room or peer not found")
    
    return {
        "success": True,
        "room_name": room_name,
        "peer_id": peer_id,
        "updated_data": request.user_data
    }

@app.post("/api/webrtc/upload")
async def upload_file(
    file: UploadFile = File(...),
    room_name: str = Form(...),
    peer_id: str = Form(...)
):
    """Upload images or documents and associate with a peer"""
    try:
        # Validate file type
        allowed_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'application/msword', 
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add file to peer's data
        relative_path = f"uploads/{unique_filename}"
        success = add_file_to_peer(room_name, peer_id, relative_path)
        
        if not success:
            # Clean up file if peer not found
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=404, detail="Room or peer not found")
        
        # Broadcast updated peer list
        await broadcast_peer_list_to_room(room_name)
        
        return {
            "success": True,
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": relative_path,
            "file_url": f"/uploads/{unique_filename}",
            "file_size": file_path.stat().st_size,
            "content_type": file.content_type,
            "room_name": room_name,
            "peer_id": peer_id
        }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/completion-signal")
async def completion_signal(signal: AICompletionSignal):
    """Store completion signal from AI tools"""
    try:
        completion_id = signal.completion_id
        completion_signals[completion_id] = {
            "status": signal.status,
            "timestamp": signal.timestamp or datetime.now().isoformat(),
            "summary": signal.summary
        }
        
        # Broadcast completion signal to all connected clients
        await sio.emit('ai_completion', {
            'completion_id': completion_id,
            'status': signal.status,
            'timestamp': completion_signals[completion_id]["timestamp"],
            'summary': signal.summary
        })
        
        logger.info(f"🎯 Received completion signal: {completion_id} - {signal.status}")
        return {"status": "success", "message": "Completion signal stored"}
    
    except Exception as e:
        logger.error(f"❌ Error storing completion signal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test Results API endpoints (for continuous test runner integration)
@app.post("/api/test-results")
async def store_test_results(request: Request):
    """Store test results from continuous test runner"""
    try:
        data = await request.json()
        test_id = data.get('test_id', str(uuid.uuid4()))
        
        test_results[test_id] = {
            **data,
            'timestamp': datetime.now().isoformat(),
            'test_id': test_id
        }
        
        # Broadcast test results to connected clients
        await sio.emit('test_results', test_results[test_id])
        
        logger.info(f"📊 Stored test results: {test_id}")
        return {"status": "success", "test_id": test_id}
    
    except Exception as e:
        logger.error(f"❌ Error storing test results: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-results/latest")
async def get_latest_test_results():
    """Get the most recent test results"""
    if not test_results:
        return {"status": "no_results", "message": "No test results available"}
    
    # Get the most recent test result
    latest_test = max(test_results.values(), key=lambda x: x['timestamp'])
    return latest_test

@app.get("/api/test-results")
async def get_all_test_results():
    """Get all test results"""
    return {
        "status": "success",
        "count": len(test_results),
        "results": list(test_results.values())
    }

def main():
    """Main entry point"""
    port = int(os.getenv('SOCKETIO_PORT', 3001))
    host = os.getenv('SOCKETIO_HOST', 'localhost')
    
    logger.info(f"🐍 Starting Enhanced Python Socket.IO Server v2.0")
    logger.info(f"🚀 Server will run on http://{host}:{port}")
    logger.info(f"📁 Uploads directory: {UPLOADS_DIR.absolute()}")
    
    uvicorn.run(
        socket_app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
