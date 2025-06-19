`#!/usr/bin/env python3
"""
Socket.IO Connection Diagnostic Tool
Test connection stability and timeout behavior
"""

import asyncio
import socketio
import time
import json
from datetime import datetime
import aiohttp
import sys

class SocketIOTester:
    def __init__(self, server_url="http://localhost:3001"):
        self.server_url = server_url
        self.sio = socketio.AsyncClient()
        self.connected = False
        self.ping_count = 0
        self.pong_count = 0
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect():
            print(f"✅ Connected to {self.server_url}")
            self.connected = True
            
        @self.sio.event
        async def disconnect():
            print("❌ Disconnected from server")
            self.connected = False
            
        @self.sio.event
        async def pong():
            self.pong_count += 1
            print(f"🏓 Pong received #{self.pong_count}")
            
        @self.sio.event
        async def connection_test(data):
            print(f"🧪 Connection test response: {data}")
    
    async def test_connection_stability(self, duration=60):
        """Test connection stability over time"""
        print(f"🔄 Testing connection stability for {duration} seconds...")
        
        try:
            await self.sio.connect(self.server_url)
            start_time = time.time()
            
            while time.time() - start_time < duration:
                if self.connected:
                    # Send ping
                    await self.sio.emit('ping')
                    self.ping_count += 1
                    print(f"🏓 Ping sent #{self.ping_count}")
                    
                    # Send connection test
                    await self.sio.emit('connection_test', {
                        'timestamp': datetime.now().isoformat(),
                        'test_id': f"test_{int(time.time())}"
                    })
                    
                    await asyncio.sleep(5)  # Test every 5 seconds
                else:
                    print("⚠️  Connection lost, attempting reconnect...")
                    await self.sio.connect(self.server_url)
                    await asyncio.sleep(1)
            
            print(f"📊 Test completed: {self.ping_count} pings sent, {self.pong_count} pongs received")
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
        finally:
            if self.connected:
                await self.sio.disconnect()
    
    async def test_server_health(self):
        """Test server health endpoint"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    health_data = await response.json()
                    print("🏥 Server Health:")
                    print(json.dumps(health_data, indent=2))
                    return health_data
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return None
    
    async def test_api_endpoints(self):
        """Test API endpoints"""
        endpoints = [
            "/api/extensions",
            "/api/webrtc/rooms",
            "/api/test-results/latest"
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f"{self.server_url}{endpoint}") as response:
                        print(f"✅ {endpoint}: {response.status}")
                except Exception as e:
                    print(f"❌ {endpoint}: {e}")

async def main():
    if len(sys.argv) > 1:
        server_url = sys.argv[1]
    else:
        server_url = "http://localhost:3001"
    
    tester = SocketIOTester(server_url)
    
    print("🚀 Starting Socket.IO Connection Diagnostics")
    print(f"📡 Server: {server_url}")
    print("-" * 50)
    
    # Test server health first
    health = await tester.test_server_health()
    if not health:
        print("❌ Server health check failed - server may be down")
        return
    
    print("\n" + "-" * 50)
    
    # Test API endpoints
    await tester.test_api_endpoints()
    
    print("\n" + "-" * 50)
    
    # Test connection stability
    await tester.test_connection_stability(30)  # 30 second test
    
    print("\n✅ Diagnostics completed")

if __name__ == "__main__":
    asyncio.run(main()) 