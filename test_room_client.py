#!/usr/bin/env python3
"""
WebRTC Room State Management Test Client
Demonstrates the new clean state management and room dashboard
"""

import asyncio
import socketio
import json
import time
from datetime import datetime

class RoomTestClient:
    def __init__(self, server_url="http://localhost:3001", username="TestUser", room_name="demo-room"):
        self.server_url = server_url
        self.username = username
        self.room_name = room_name
        self.peer_id = f"{username}_{int(time.time())}"
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.in_room = False
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect():
            print(f"✅ {self.username} connected to server")
            self.connected = True
            
        @self.sio.event
        async def disconnect():
            print(f"❌ {self.username} disconnected from server")
            self.connected = False
            self.in_room = False
            
        @self.sio.event
        async def join_room_success(data):
            print(f"🏠 {self.username} joined room '{data['room_name']}' - Status: {data['status']}")
            print(f"   📊 Stats: {data['active_peers']} active, {data['total_peers']} total")
            self.in_room = True
            
        @self.sio.event
        async def join_room_error(data):
            print(f"❌ {self.username} failed to join room: {data['error']}")
            
        @self.sio.event
        async def leave_room_success(data):
            print(f"🚪 {self.username} left room '{data['room_name']}' - Status: {data['status']}")
            self.in_room = False
            
        @self.sio.event
        async def peer_list_updated(data):
            active_count = data['active_peers']
            total_count = data['total_peers']
            print(f"📡 {self.username} received peer list update for '{data['room_name']}':")
            print(f"   📊 {active_count} active, {total_count} total peers")
            
            # Show active peers
            active_peers = [p for p in data['peers'] if p['is_active']]
            if active_peers:
                print("   ✅ Active peers:")
                for peer in active_peers:
                    print(f"      • {peer['username']} ({peer['peer_id'][:8]}...)")
            
            # Show inactive peers
            inactive_peers = [p for p in data['peers'] if not p['is_active']]
            if inactive_peers:
                print("   💤 Inactive peers:")
                for peer in inactive_peers:
                    print(f"      • {peer['username']} ({peer['peer_id'][:8]}...) - Last seen: {peer['last_seen']}")
                    
        @self.sio.event
        async def peer_list_response(data):
            print(f"📋 {self.username} received peer list response:")
            print(f"   Room: {data['room_name']} ({data['active_peers']} active, {data['total_peers']} total)")
            
        @self.sio.event
        async def heartbeat_ack(data):
            print(f"💓 {self.username} heartbeat acknowledged: {data['timestamp']}")
    
    async def connect_to_server(self):
        """Connect to the Socket.IO server"""
        try:
            await self.sio.connect(self.server_url)
            await asyncio.sleep(1)  # Give connection time to establish
            return True
        except Exception as e:
            print(f"❌ {self.username} failed to connect: {e}")
            return False
    
    async def join_room(self):
        """Join a WebRTC room"""
        if not self.connected:
            print(f"❌ {self.username} not connected to server")
            return False
            
        try:
            await self.sio.emit('join_room', {
                'room_name': self.room_name,
                'peer_id': self.peer_id,
                'username': self.username,
                'user_data': {
                    'client_type': 'test_client',
                    'version': '1.0',
                    'capabilities': ['video', 'audio', 'data']
                }
            })
            return True
        except Exception as e:
            print(f"❌ {self.username} failed to join room: {e}")
            return False
    
    async def leave_room(self):
        """Leave the WebRTC room (marks as inactive)"""
        if not self.in_room:
            print(f"❌ {self.username} not in any room")
            return False
            
        try:
            await self.sio.emit('leave_room', {})
            return True
        except Exception as e:
            print(f"❌ {self.username} failed to leave room: {e}")
            return False
    
    async def request_peer_list(self):
        """Request current peer list"""
        try:
            await self.sio.emit('request_peer_list', {
                'room_name': self.room_name,
                'include_inactive': True
            })
        except Exception as e:
            print(f"❌ {self.username} failed to request peer list: {e}")
    
    async def send_heartbeat(self):
        """Send heartbeat to keep connection alive"""
        try:
            await self.sio.emit('heartbeat', {
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            print(f"❌ {self.username} failed to send heartbeat: {e}")
    
    async def disconnect_from_server(self):
        """Disconnect from server"""
        if self.connected:
            await self.sio.disconnect()

async def test_room_state_management():
    """Test the clean room state management"""
    print("🧪 Testing WebRTC Room State Management")
    print("=" * 50)
    
    # Create test clients
    client1 = RoomTestClient(username="Alice", room_name="test-room")
    client2 = RoomTestClient(username="Bob", room_name="test-room")
    client3 = RoomTestClient(username="Charlie", room_name="test-room")
    
    try:
        # Phase 1: Connect clients
        print("\n📡 Phase 1: Connecting clients...")
        await client1.connect_to_server()
        await client2.connect_to_server()
        await client3.connect_to_server()
        
        await asyncio.sleep(1)
        
        # Phase 2: Join room sequentially
        print("\n🏠 Phase 2: Joining room...")
        await client1.join_room()
        await asyncio.sleep(2)
        
        await client2.join_room()
        await asyncio.sleep(2)
        
        await client3.join_room()
        await asyncio.sleep(2)
        
        # Phase 3: Request peer lists
        print("\n📋 Phase 3: Requesting peer lists...")
        await client1.request_peer_list()
        await asyncio.sleep(1)
        
        # Phase 4: One client leaves (becomes inactive)
        print("\n🚪 Phase 4: Bob leaves room...")
        await client2.leave_room()
        await asyncio.sleep(2)
        
        # Phase 5: Check peer list after leave
        print("\n📋 Phase 5: Checking peer list after leave...")
        await client1.request_peer_list()
        await asyncio.sleep(1)
        
        # Phase 6: Bob rejoins (should reactivate)
        print("\n🔄 Phase 6: Bob rejoins room...")
        await client2.join_room()
        await asyncio.sleep(2)
        
        # Phase 7: Send heartbeats
        print("\n💓 Phase 7: Sending heartbeats...")
        await client1.send_heartbeat()
        await client2.send_heartbeat()
        await client3.send_heartbeat()
        await asyncio.sleep(1)
        
        # Phase 8: Final peer list
        print("\n📊 Phase 8: Final peer list check...")
        await client1.request_peer_list()
        await asyncio.sleep(2)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    finally:
        # Cleanup
        print("\n🧹 Cleaning up...")
        await client1.disconnect_from_server()
        await client2.disconnect_from_server()
        await client3.disconnect_from_server()

if __name__ == "__main__":
    asyncio.run(test_room_state_management()) 