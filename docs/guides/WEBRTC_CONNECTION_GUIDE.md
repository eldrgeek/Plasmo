# WebRTC Connection Guide - Enhanced Socket.IO Server

## Overview

This enhanced Socket.IO server provides WebRTC signaling with advanced features:
- **Inactive User Management**: Users are marked as inactive instead of being removed
- **User Data Structures**: Each user can store arbitrary application-specific information
- **File Upload Support**: Users can upload images and documents associated with their profile
- **Real-time Updates**: All changes broadcast to active peers in real-time

## Key Features

### 1. Enhanced User Management
- Users are marked as **inactive** when they disconnect (not removed)
- User data persists across sessions
- Reactivation when users rejoin
- Support for arbitrary application-specific data

### 2. File Upload System
- Upload images (JPEG, PNG, GIF, WebP)
- Upload documents (PDF, DOC, DOCX, TXT)
- Files are associated with specific users
- Automatic cleanup if user/room not found

### 3. Real-time Broadcasting
- Peer list updates include both active and inactive users
- File upload notifications
- User data change notifications

## Server Configuration

### Base URL
- **Local**: `http://localhost:3001`
- **Tunneled**: `https://monad-socketio.loca.lt`

### WebSocket Connection
```javascript
const socket = io('https://monad-socketio.loca.lt');
```

## Enhanced API Endpoints

### WebRTC Room Management

#### Get All Rooms (Enhanced)
```http
GET /api/webrtc/rooms
```

**Response:**
```json
{
  "room-name": {
    "name": "room-name",
    "active_peer_count": 3,
    "total_peer_count": 5,
    "max_peers": 100,
    "created_at": "2024-01-15T10:30:00Z",
    "peers": [
      {
        "peer_id": "user123",
        "username": "Alice",
        "joined_at": "2024-01-15T10:30:00Z",
        "is_active": true,
        "last_seen": "2024-01-15T10:35:00Z",
        "user_data": {
          "avatar": "https://example.com/avatar.jpg",
          "role": "moderator",
          "preferences": {"theme": "dark"}
        },
        "uploaded_files": [
          "uploads/abc123.jpg",
          "uploads/def456.pdf"
        ]
      },
      {
        "peer_id": "user456",
        "username": "Bob",
        "joined_at": "2024-01-15T10:25:00Z",
        "is_active": false,
        "last_seen": "2024-01-15T10:33:00Z",
        "user_data": {
          "role": "participant"
        },
        "uploaded_files": []
      }
    ]
  }
}
```

#### Join Room with User Data
```http
POST /api/webrtc/rooms/{room_name}/join
```

**Request Body:**
```json
{
  "room_name": "my-room",
  "peer_id": "user123",
  "username": "Alice",
  "user_data": {
    "avatar": "https://example.com/avatar.jpg",
    "role": "moderator",
    "preferences": {
      "theme": "dark",
      "notifications": true
    },
    "custom_field": "any value"
  }
}
```

#### Update User Data
```http
POST /api/webrtc/rooms/{room_name}/update-data?peer_id={peer_id}
```

**Request Body:**
```json
{
  "user_data": {
    "status": "presenting",
    "screen_sharing": true,
    "new_field": "updated value"
  }
}
```

#### File Upload
```http
POST /api/webrtc/upload
```

**Form Data:**
- `file`: File to upload (image or document)
- `room_name`: Target room name
- `peer_id`: User's peer ID

**Response:**
```json
{
  "success": true,
  "filename": "abc123-def456.jpg",
  "original_filename": "my-image.jpg",
  "file_path": "uploads/abc123-def456.jpg",
  "file_url": "/uploads/abc123-def456.jpg",
  "file_size": 245760,
  "content_type": "image/jpeg",
  "room_name": "my-room",
  "peer_id": "user123"
}
```

## Enhanced Socket.IO Events

### Client → Server Events

#### Join Room with User Data
```javascript
socket.emit('join_room', {
  room_name: 'my-room',
  peer_id: 'user123',
  username: 'Alice',
  user_data: {
    avatar: 'https://example.com/avatar.jpg',
    role: 'moderator',
    preferences: {
      theme: 'dark',
      notifications: true
    }
  }
});
```

#### Update User Data
```javascript
socket.emit('update_user_data', {
  user_data: {
    status: 'presenting',
    screen_sharing: true,
    mood: 'excited'
  }
});
```

#### Leave Room (Marks as Inactive)
```javascript
socket.emit('leave_room', {});
```

### Server → Client Events

#### Enhanced Join Success
```javascript
socket.on('join_room_success', (data) => {
  console.log('Joined room:', data.room_name);
  console.log('Active peers:', data.active_peers);
  console.log('Total peers:', data.total_peers);
  console.log('All peers:', data.peers);
});
```

#### Enhanced Peer List Updates
```javascript
socket.on('peer_list_updated', (data) => {
  console.log('Room:', data.room_name);
  console.log('Active peers:', data.active_peers);
  console.log('Total peers:', data.total_peers);
  
  data.peers.forEach(peer => {
    console.log(`${peer.username} (${peer.peer_id}):`, {
      active: peer.is_active,
      lastSeen: peer.last_seen,
      userData: peer.user_data,
      files: peer.uploaded_files
    });
  });
});
```

#### User Data Update Success
```javascript
socket.on('update_user_data_success', (data) => {
  console.log('Updated user data for:', data.peer_id);
  console.log('In room:', data.room_name);
  console.log('New data:', data.user_data);
});
```

## JavaScript Client Example

### Complete Enhanced Client
```javascript
class EnhancedWebRTCClient {
  constructor(serverUrl = 'https://monad-socketio.loca.lt') {
    this.socket = io(serverUrl);
    this.currentRoom = null;
    this.peerId = `peer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.userData = {};
    
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('✅ Connected to enhanced server');
    });
    
    this.socket.on('join_room_success', (data) => {
      this.currentRoom = data.room_name;
      console.log(`✅ Joined room: ${data.room_name}`);
      console.log(`Active: ${data.active_peers}, Total: ${data.total_peers}`);
      this.updatePeerList(data.peers);
    });
    
    this.socket.on('peer_list_updated', (data) => {
      console.log(`📡 Peer list updated: ${data.active_peers} active, ${data.total_peers} total`);
      this.updatePeerList(data.peers);
    });
    
    this.socket.on('update_user_data_success', (data) => {
      console.log('✅ User data updated successfully');
    });
  }
  
  joinRoom(roomName, username, userData = {}) {
    this.socket.emit('join_room', {
      room_name: roomName,
      peer_id: this.peerId,
      username: username,
      user_data: userData
    });
  }
  
  updateUserData(newData) {
    this.userData = { ...this.userData, ...newData };
    this.socket.emit('update_user_data', {
      user_data: newData
    });
  }
  
  async uploadFile(file, roomName = this.currentRoom) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('room_name', roomName);
    formData.append('peer_id', this.peerId);
    
    try {
      const response = await fetch(`${this.socket.io.uri}/api/webrtc/upload`, {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (response.ok) {
        console.log('✅ File uploaded:', result.file_url);
        return result;
      } else {
        throw new Error(result.detail);
      }
    } catch (error) {
      console.error('❌ Upload failed:', error);
      throw error;
    }
  }
  
  leaveRoom() {
    this.socket.emit('leave_room', {});
    this.currentRoom = null;
  }
  
  updatePeerList(peers) {
    const activePeers = peers.filter(p => p.is_active);
    const inactivePeers = peers.filter(p => !p.is_active);
    
    console.log('👥 Active Peers:', activePeers.map(p => ({
      id: p.peer_id,
      name: p.username,
      data: p.user_data,
      files: p.uploaded_files
    })));
    
    console.log('😴 Inactive Peers:', inactivePeers.map(p => ({
      id: p.peer_id,
      name: p.username,
      lastSeen: p.last_seen
    })));
  }
}

// Usage Example
const client = new EnhancedWebRTCClient();

// Join with user data
client.joinRoom('my-room', 'Alice', {
  avatar: 'https://example.com/avatar.jpg',
  role: 'moderator',
  preferences: { theme: 'dark' }
});

// Update user data
client.updateUserData({
  status: 'presenting',
  screen_sharing: true
});

// Upload file
document.getElementById('fileInput').addEventListener('change', async (e) => {
  if (e.target.files[0]) {
    try {
      const result = await client.uploadFile(e.target.files[0]);
      console.log('File uploaded:', result.file_url);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }
});
```

## Python Client Example

### Enhanced Python Client
```python
import socketio
import requests
import json
from typing import Dict, Any, List

class EnhancedWebRTCClient:
    def __init__(self, server_url: str = 'https://monad-socketio.loca.lt'):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.current_room = None
        self.peer_id = f"peer_{int(time.time())}_{random.randint(1000, 9999)}"
        self.user_data = {}
        
        self.setup_event_handlers()
    
    def setup_event_handlers(self):
        @self.sio.event
        def connect():
            print("✅ Connected to enhanced server")
        
        @self.sio.event
        def join_room_success(data):
            self.current_room = data['room_name']
            print(f"✅ Joined room: {data['room_name']}")
            print(f"Active: {data['active_peers']}, Total: {data['total_peers']}")
            self.update_peer_list(data['peers'])
        
        @self.sio.event
        def peer_list_updated(data):
            print(f"📡 Peer list updated: {data['active_peers']} active, {data['total_peers']} total")
            self.update_peer_list(data['peers'])
        
        @self.sio.event
        def update_user_data_success(data):
            print("✅ User data updated successfully")
    
    def connect(self):
        self.sio.connect(self.server_url)
    
    def join_room(self, room_name: str, username: str, user_data: Dict[str, Any] = None):
        self.sio.emit('join_room', {
            'room_name': room_name,
            'peer_id': self.peer_id,
            'username': username,
            'user_data': user_data or {}
        })
    
    def update_user_data(self, new_data: Dict[str, Any]):
        self.user_data.update(new_data)
        self.sio.emit('update_user_data', {
            'user_data': new_data
        })
    
    def upload_file(self, file_path: str, room_name: str = None):
        room_name = room_name or self.current_room
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'room_name': room_name,
                'peer_id': self.peer_id
            }
            
            response = requests.post(
                f"{self.server_url}/api/webrtc/upload",
                files=files,
                data=data
            )
            
            if response.ok:
                result = response.json()
                print(f"✅ File uploaded: {result['file_url']}")
                return result
            else:
                raise Exception(f"Upload failed: {response.text}")
    
    def leave_room(self):
        self.sio.emit('leave_room', {})
        self.current_room = None
    
    def update_peer_list(self, peers: List[Dict]):
        active_peers = [p for p in peers if p['is_active']]
        inactive_peers = [p for p in peers if not p['is_active']]
        
        print("👥 Active Peers:")
        for peer in active_peers:
            print(f"  {peer['username']} ({peer['peer_id']})")
            print(f"    Data: {peer['user_data']}")
            print(f"    Files: {peer['uploaded_files']}")
        
        print("😴 Inactive Peers:")
        for peer in inactive_peers:
            print(f"  {peer['username']} (last seen: {peer['last_seen']})")

# Usage Example
client = EnhancedWebRTCClient()
client.connect()

# Join with user data
client.join_room('my-room', 'Alice', {
    'avatar': 'https://example.com/avatar.jpg',
    'role': 'moderator',
    'preferences': {'theme': 'dark'}
})

# Update user data
client.update_user_data({
    'status': 'presenting',
    'screen_sharing': True
})

# Upload file
client.upload_file('/path/to/image.jpg')
```

## React Native Integration

### Enhanced React Native Client
```javascript
import io from 'socket.io-client';
import DocumentPicker from 'react-native-document-picker';

class EnhancedWebRTCClient {
  constructor(serverUrl = 'https://monad-socketio.loca.lt') {
    this.socket = io(serverUrl);
    this.currentRoom = null;
    this.peerId = `mobile_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.userData = {};
    
    this.setupEventListeners();
  }
  
  setupEventListeners() {
    this.socket.on('connect', () => {
      console.log('✅ Connected to enhanced server');
    });
    
    this.socket.on('peer_list_updated', (data) => {
      // Update UI with active/inactive peer status
      this.updatePeerList(data.peers);
    });
  }
  
  joinRoom(roomName, username, userData = {}) {
    this.socket.emit('join_room', {
      room_name: roomName,
      peer_id: this.peerId,
      username: username,
      user_data: {
        platform: 'mobile',
        device: Platform.OS,
        ...userData
      }
    });
  }
  
  async uploadDocument() {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.images, DocumentPicker.types.pdf],
      });
      
      const formData = new FormData();
      formData.append('file', {
        uri: result[0].uri,
        type: result[0].type,
        name: result[0].name,
      });
      formData.append('room_name', this.currentRoom);
      formData.append('peer_id', this.peerId);
      
      const response = await fetch(`${this.socket.io.uri}/api/webrtc/upload`, {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const uploadResult = await response.json();
      console.log('✅ File uploaded:', uploadResult.file_url);
      return uploadResult;
      
    } catch (error) {
      console.error('❌ Upload failed:', error);
    }
  }
  
  updateUserData(newData) {
    this.userData = { ...this.userData, ...newData };
    this.socket.emit('update_user_data', {
      user_data: newData
    });
  }
  
  updatePeerList(peers) {
    // Filter and display active vs inactive peers
    const activePeers = peers.filter(p => p.is_active);
    const inactivePeers = peers.filter(p => !p.is_active);
    
    // Update your React Native UI components
    this.onPeerListUpdate?.(activePeers, inactivePeers);
  }
}
```

## Testing and Debugging

### Test the Enhanced Features

1. **Join with User Data**:
```bash
curl -X POST https://monad-socketio.loca.lt/api/webrtc/rooms/test-room/join \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "test-room",
    "peer_id": "test-user",
    "username": "Test User",
    "user_data": {
      "role": "tester",
      "preferences": {"theme": "dark"}
    }
  }'
```

2. **Upload File**:
```bash
curl -X POST https://monad-socketio.loca.lt/api/webrtc/upload \
  -F "file=@test-image.jpg" \
  -F "room_name=test-room" \
  -F "peer_id=test-user"
```

3. **Check Room Status**:
```bash
curl https://monad-socketio.loca.lt/api/webrtc/rooms/test-room
```

### Web Interface Testing

Visit `https://monad-socketio.loca.lt` to access the enhanced web interface with:
- File upload testing
- Real-time peer monitoring
- Active/inactive user status
- User data visualization

## Key Differences from Basic Version

### Enhanced Features:
1. **Persistent User Data**: Users maintain data across sessions
2. **Inactive Status**: Users shown as inactive instead of removed
3. **File Associations**: Files linked to specific users
4. **Rich User Profiles**: Arbitrary application data support
5. **Enhanced Broadcasting**: More detailed peer information

### Migration from Basic Version:
- Peer lists now include `is_active`, `last_seen`, `user_data`, `uploaded_files`
- Room capacity counts only active users
- File upload endpoints added
- User data update events added

This enhanced system provides a robust foundation for applications requiring persistent user presence, file sharing, and rich user profiles while maintaining real-time WebRTC signaling capabilities.

---

**Server Status**: ✅ Live at `https://monad-socketio.loca.lt`  
**Documentation**: Complete and ready for integration  
**Support**: WebRTC peer discovery with automatic room management 