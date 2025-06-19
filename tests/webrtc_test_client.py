#!/usr/bin/env python3
"""
WebRTC Test Client - Demonstrates Socket.IO WebRTC room functionality
"""

import asyncio
import socketio
import json
from datetime import datetime

class WebRTCTestClient:
    def __init__(self, server_url="http://localhost:3001"):
        self.sio = socketio.AsyncClient()
        self.server_url = server_url
        self.peer_id = None
        self.username = None
        self.current_room = None
        
        # Set up event handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up Socket.IO event handlers"""
        
        @self.sio.event
        async def connect():
            print(f"✅ Connected to server: {self.server_url}")
        
        @self.sio.event
        async def disconnect():
            print("❌ Disconnected from server")
        
        @self.sio.event
        async def join_room_success(data):
            print(f"🎉 Successfully joined room: {data['room_name']}")
            print(f"📊 Total peers in room: {data['total_peers']}")
            print("👥 Current peers:")
            for peer in data['peers']:
                status = "👤 (you)" if peer['peer_id'] == self.peer_id else "👤"
                print(f"   {status} {peer['username']} ({peer['peer_id']})")
            self.current_room = data['room_name']
        
        @self.sio.event
        async def join_room_error(data):
            print(f"❌ Failed to join room: {data['error']}")
        
        @self.sio.event
        async def leave_room_success(data):
            print(f"👋 Successfully left room: {data['room_name']}")
            self.current_room = None
        
        @self.sio.event
        async def leave_room_error(data):
            print(f"❌ Failed to leave room: {data['error']}")
        
        @self.sio.event
        async def peer_list_updated(data):
            print(f"📡 Peer list updated in room: {data['room_name']}")
            print(f"📊 Total peers: {data['total_peers']}")
            print("👥 Updated peer list:")
            for peer in data['peers']:
                status = "👤 (you)" if peer['peer_id'] == self.peer_id else "👤"
                print(f"   {status} {peer['username']} ({peer['peer_id']})")
    
    async def connect(self):
        """Connect to the server"""
        await self.sio.connect(self.server_url)
    
    async def disconnect(self):
        """Disconnect from the server"""
        await self.sio.disconnect()
    
    async def join_room(self, room_name: str, peer_id: str, username: str):
        """Join a WebRTC room"""
        self.peer_id = peer_id
        self.username = username
        
        print(f"🚪 Attempting to join room: {room_name}")
        print(f"👤 Peer ID: {peer_id}")
        print(f"📝 Username: {username}")
        
        await self.sio.emit('join_room', {
            'room_name': room_name,
            'peer_id': peer_id,
            'username': username
        })
    
    async def leave_room(self):
        """Leave current room"""
        if not self.current_room:
            print("❌ Not in any room")
            return
        
        print(f"🚪 Leaving room: {self.current_room}")
        await self.sio.emit('leave_room', {})
    
    async def wait_for_events(self, duration=30):
        """Wait for events for a specified duration"""
        print(f"⏳ Waiting for events for {duration} seconds...")
        await asyncio.sleep(duration)

async def demo_scenario():
    """Demonstrate WebRTC room functionality"""
    print("🎬 Starting WebRTC Demo Scenario")
    print("=" * 50)
    
    # Create multiple clients
    client1 = WebRTCTestClient()
    client2 = WebRTCTestClient()
    client3 = WebRTCTestClient()
    
    try:
        # Connect all clients
        print("\n📡 Connecting clients...")
        await asyncio.gather(
            client1.connect(),
            client2.connect(),
            client3.connect()
        )
        
        await asyncio.sleep(1)
        
        # Client 1 joins room
        print("\n🎯 Scenario 1: First peer joins room")
        await client1.join_room("demo-room", "peer-001", "Alice")
        await asyncio.sleep(2)
        
        # Client 2 joins same room
        print("\n🎯 Scenario 2: Second peer joins room")
        await client2.join_room("demo-room", "peer-002", "Bob")
        await asyncio.sleep(2)
        
        # Client 3 joins same room
        print("\n🎯 Scenario 3: Third peer joins room")
        await client3.join_room("demo-room", "peer-003", "Charlie")
        await asyncio.sleep(2)
        
        # Client 2 leaves room
        print("\n🎯 Scenario 4: Peer leaves room (auto peer list update)")
        await client2.leave_room()
        await asyncio.sleep(2)
        
        # Client 1 joins different room
        print("\n🎯 Scenario 5: Peer switches rooms")
        await client1.join_room("another-room", "peer-001", "Alice")
        await asyncio.sleep(2)
        
        # Test room capacity (try to join with many peers)
        print("\n🎯 Scenario 6: Testing room limits")
        test_clients = []
        for i in range(5):
            client = WebRTCTestClient()
            await client.connect()
            await client.join_room("capacity-test", f"peer-{i:03d}", f"User{i}")
            test_clients.append(client)
            await asyncio.sleep(0.5)
        
        print("\n⏳ Waiting for final events...")
        await asyncio.sleep(3)
        
        # Cleanup test clients
        for client in test_clients:
            await client.disconnect()
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
    
    finally:
        # Disconnect all clients
        print("\n🧹 Cleaning up...")
        await asyncio.gather(
            client1.disconnect(),
            client2.disconnect(),
            client3.disconnect(),
            return_exceptions=True
        )
    
    print("\n✅ Demo completed!")

async def interactive_mode():
    """Interactive mode for manual testing"""
    print("🎮 Interactive WebRTC Test Mode")
    print("=" * 40)
    
    client = WebRTCTestClient()
    
    try:
        await client.connect()
        
        while True:
            print("\n📋 Available commands:")
            print("1. join <room_name> <peer_id> <username> - Join a room")
            print("2. leave - Leave current room")
            print("3. status - Show current status")
            print("4. quit - Exit")
            
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            if command[0] == "join" and len(command) == 4:
                room_name, peer_id, username = command[1], command[2], command[3]
                await client.join_room(room_name, peer_id, username)
            
            elif command[0] == "leave":
                await client.leave_room()
            
            elif command[0] == "status":
                print(f"Current room: {client.current_room or 'None'}")
                print(f"Peer ID: {client.peer_id or 'None'}")
                print(f"Username: {client.username or 'None'}")
            
            elif command[0] == "quit":
                break
            
            else:
                print("❌ Invalid command")
            
            await asyncio.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n👋 Interrupted by user")
    
    finally:
        await client.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(demo_scenario()) 