# WebRTC Socket.IO Server - Usage Guide

## 🎯 **Implementation Summary**

Your Socket.IO server now supports WebRTC peer discovery with all requested features:

✅ **Auto delete**: Peers automatically removed on disconnect  
✅ **Order on move**: Peer list broadcasted when someone joins/leaves  
✅ **Discovery only**: Simple peer discovery for WebRTC setup  
✅ **No auth**: No authentication required  
✅ **Max 100**: Room capacity limited to 100 peers  

## 🚀 **Quick Start**

### **1. Start the Server**
```bash
python socketio_server_python.py
```
Server runs on: `http://localhost:3001`

### **2. Connect via Socket.IO**
```javascript
const socket = io('http://localhost:3001');
```

### **3. Join a Room**
```javascript
socket.emit('join_room', {
    room_name: 'my-video-call',
    peer_id: 'unique-peer-id-123',
    username: 'Alice'
});
```

### **4. Listen for Peer Updates**
```javascript
socket.on('join_room_success', (data) => {
    console.log('Joined room:', data.room_name);
    console.log('Current peers:', data.peers);
    // Use data.peers for WebRTC peer discovery
});

socket.on('peer_list_updated', (data) => {
    console.log('Peer list updated:', data.peers);
    // Update your WebRTC connections
});
```

## 📡 **Socket.IO Events**

### **Client → Server**

#### **`join_room`**
Join a WebRTC room for peer discovery.

**Payload:**
```javascript
{
    room_name: "string",    // Room identifier
    peer_id: "string",      // Unique peer identifier  
    username: "string"      // Display name
}
```

**Response Events:**
- `join_room_success` - Successfully joined
- `join_room_error` - Failed to join (room full, etc.)

#### **`leave_room`**
Leave current room.

**Payload:** `{}` (empty object)

**Response Events:**
- `leave_room_success` - Successfully left
- `leave_room_error` - Error leaving room

### **Server → Client**

#### **`join_room_success`**
Confirmation of successful room join.

**Data:**
```javascript
{
    room_name: "my-video-call",
    peer_id: "unique-peer-id-123", 
    peers: [
        {
            peer_id: "peer-001",
            username: "Alice",
            joined_at: "2024-01-15T10:30:00Z"
        },
        {
            peer_id: "peer-002", 
            username: "Bob",
            joined_at: "2024-01-15T10:31:00Z"
        }
    ],
    total_peers: 2
}
```

#### **`peer_list_updated`**
Broadcasted when peer list changes (someone joins/leaves).

**Data:**
```javascript
{
    room_name: "my-video-call",
    peers: [...],           // Updated peer list
    total_peers: 3
}
```

## 🌐 **REST API Endpoints**

### **GET `/api/webrtc/rooms`**
List all active rooms.

**Response:**
```json
{
    "my-video-call": {
        "name": "my-video-call",
        "peer_count": 2,
        "max_peers": 100,
        "created_at": "2024-01-15T10:30:00Z",
        "peers": [...]
    }
}
```

### **GET `/api/webrtc/rooms/{room_name}`**
Get specific room information.

### **POST `/api/webrtc/rooms/{room_name}/join`**
HTTP endpoint for external services to join rooms.

**Body:**
```json
{
    "room_name": "my-video-call",
    "peer_id": "unique-peer-id",
    "username": "Alice"
}
```

## 💻 **JavaScript Client Example**

```javascript
class WebRTCPeerDiscovery {
    constructor(serverUrl = 'http://localhost:3001') {
        this.socket = io(serverUrl);
        this.currentRoom = null;
        this.peers = [];
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.socket.on('join_room_success', (data) => {
            this.currentRoom = data.room_name;
            this.peers = data.peers;
            this.onPeerListUpdate(data.peers);
        });
        
        this.socket.on('peer_list_updated', (data) => {
            this.peers = data.peers;
            this.onPeerListUpdate(data.peers);
        });
        
        this.socket.on('join_room_error', (data) => {
            console.error('Failed to join room:', data.error);
        });
    }
    
    joinRoom(roomName, peerId, username) {
        this.socket.emit('join_room', {
            room_name: roomName,
            peer_id: peerId,
            username: username
        });
    }
    
    leaveRoom() {
        this.socket.emit('leave_room', {});
    }
    
    onPeerListUpdate(peers) {
        // Implement your WebRTC peer connection logic here
        console.log('Available peers for WebRTC:', peers);
        
        // Example: Initialize WebRTC connections to new peers
        peers.forEach(peer => {
            if (peer.peer_id !== this.myPeerId) {
                this.initWebRTCConnection(peer);
            }
        });
    }
    
    initWebRTCConnection(peer) {
        // Your WebRTC connection setup logic
        console.log('Setting up WebRTC with:', peer.username);
    }
}

// Usage
const discovery = new WebRTCPeerDiscovery();
discovery.joinRoom('video-call-123', 'my-unique-id', 'Alice');
```

## 🐍 **Python Client Example**

```python
import asyncio
import socketio

class WebRTCClient:
    def __init__(self, server_url="http://localhost:3001"):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.current_room = None
        self.peers = []
        
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def join_room_success(data):
            self.current_room = data['room_name']
            self.peers = data['peers']
            await self.on_peer_list_update(data['peers'])
        
        @self.sio.event
        async def peer_list_updated(data):
            self.peers = data['peers']
            await self.on_peer_list_update(data['peers'])
    
    async def connect(self):
        await self.sio.connect(self.server_url)
    
    async def join_room(self, room_name, peer_id, username):
        await self.sio.emit('join_room', {
            'room_name': room_name,
            'peer_id': peer_id,
            'username': username
        })
    
    async def on_peer_list_update(self, peers):
        print(f"Peers available for WebRTC: {len(peers)}")
        for peer in peers:
            print(f"  - {peer['username']} ({peer['peer_id']})")

# Usage
async def main():
    client = WebRTCClient()
    await client.connect()
    await client.join_room('video-call-123', 'my-unique-id', 'Alice')
    await asyncio.sleep(30)  # Keep alive

asyncio.run(main())
```

## 🔧 **Configuration**

### **Room Limits**
```python
# In socketio_server_python.py
MAX_PEERS_PER_ROOM = 100  # Adjust as needed
```

### **Server Port**
```python
# In main() function
uvicorn.run(socket_app, host="0.0.0.0", port=3001)
```

## 🚨 **Error Handling**

### **Common Errors**
- **Room Full**: `Room {name} is full (max 100 peers)`
- **Missing Fields**: `Missing required fields: room_name, peer_id, username`
- **Not in Room**: `Not in any room` (when trying to leave)

### **Auto-Cleanup**
- Peers automatically removed on disconnect
- Empty rooms automatically deleted
- Peer mappings cleaned up

## 🎯 **WebRTC Integration Flow**

1. **Connect** to Socket.IO server
2. **Join room** with unique peer_id and username
3. **Receive peer list** of other users in room
4. **Set up WebRTC** connections to discovered peers
5. **Listen for updates** when peers join/leave
6. **Update WebRTC** connections accordingly
7. **Auto-cleanup** when disconnecting

## 🧪 **Testing**

### **Run Demo**
```bash
python webrtc_test_client.py
```

### **Interactive Mode**
```bash
python webrtc_test_client.py interactive
```

### **Check Room Status**
```bash
curl http://localhost:3001/api/webrtc/rooms
```

### **Web Interface**
Visit: `http://localhost:3001`

## 🔗 **Integration with External Services**

The server provides both Socket.IO and REST endpoints, making it easy to integrate with:

- **Web browsers** (Socket.IO JavaScript client)
- **Mobile apps** (Socket.IO native clients)
- **Backend services** (REST API)
- **Chrome extensions** (existing Socket.IO integration)

Your WebRTC signaling server is now ready for production use! 🚀 