#!/usr/bin/env python3
"""
WebSocket Connection Test for LocalTunnel
Test Socket.IO WebSocket connections through tunnel endpoints
"""

import asyncio
import socketio
import time
import json
from datetime import datetime
import aiohttp
import sys
import ssl

class TunnelWebSocketTester:
    def __init__(self, tunnel_url="https://monad-socketio.loca.lt"):
        self.tunnel_url = tunnel_url
        self.sio = socketio.AsyncClient(
            # Configure for tunnel connections
            ssl_verify=False,  # LocalTunnel SSL handling
            reconnection=True,
            reconnection_attempts=3,
            reconnection_delay=1,
            logger=True,
            engineio_logger=True
        )
        self.connected = False
        self.ping_count = 0
        self.pong_count = 0
        self.connection_events = []
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect():
            self.connected = True
            event = {
                'type': 'connect',
                'timestamp': datetime.now().isoformat(),
                'tunnel_url': self.tunnel_url
            }
            self.connection_events.append(event)
            print(f"✅ Connected to tunnel: {self.tunnel_url}")
            
        @self.sio.event
        async def disconnect():
            self.connected = False
            event = {
                'type': 'disconnect',
                'timestamp': datetime.now().isoformat()
            }
            self.connection_events.append(event)
            print("❌ Disconnected from tunnel")
            
        @self.sio.event
        async def connect_error(data):
            event = {
                'type': 'connect_error',
                'timestamp': datetime.now().isoformat(),
                'error': str(data)
            }
            self.connection_events.append(event)
            print(f"🚨 Connection error: {data}")
            
        @self.sio.event
        async def pong():
            self.pong_count += 1
            print(f"🏓 Pong received #{self.pong_count} via tunnel")
            
        @self.sio.event
        async def connection_test(data):
            print(f"🧪 Tunnel connection test response: {data}")
            
        @self.sio.event
        async def join_room_success(data):
            print(f"🏠 Joined WebRTC room via tunnel: {data}")
            
        @self.sio.event
        async def peer_list_updated(data):
            print(f"👥 Peer list updated via tunnel: {len(data.get('peers', []))} peers")
    
    async def test_tunnel_websocket(self, duration=45):
        """Test WebSocket connection through tunnel"""
        print(f"🌐 Testing WebSocket through tunnel for {duration} seconds...")
        print(f"📡 Tunnel URL: {self.tunnel_url}")
        
        try:
            # Connect through tunnel
            print("🔗 Attempting tunnel connection...")
            await self.sio.connect(self.tunnel_url, transports=['websocket'])
            
            if not self.connected:
                print("❌ Failed to establish WebSocket connection through tunnel")
                return False
            
            start_time = time.time()
            test_cycle = 0
            
            while time.time() - start_time < duration and self.connected:
                test_cycle += 1
                print(f"\n--- Test Cycle #{test_cycle} ---")
                
                # Test basic ping/pong
                await self.sio.emit('ping')
                self.ping_count += 1
                print(f"🏓 Ping sent #{self.ping_count} via tunnel")
                
                # Test connection stability
                await self.sio.emit('connection_test', {
                    'timestamp': datetime.now().isoformat(),
                    'test_id': f"tunnel_test_{test_cycle}",
                    'tunnel_url': self.tunnel_url
                })
                
                # Test WebRTC room functionality
                if test_cycle == 1:
                    await self.sio.emit('join_room', {
                        'room_name': 'tunnel-test-room',
                        'peer_id': f'tunnel-tester-{int(time.time())}',
                        'username': 'TunnelTester',
                        'user_data': {
                            'test_mode': True,
                            'tunnel_connection': True
                        }
                    })
                
                await asyncio.sleep(10)  # Test every 10 seconds
            
            # Final statistics
            duration_actual = time.time() - start_time
            success_rate = (self.pong_count / self.ping_count * 100) if self.ping_count > 0 else 0
            
            print(f"\n📊 Tunnel WebSocket Test Results:")
            print(f"   Duration: {duration_actual:.1f} seconds")
            print(f"   Pings sent: {self.ping_count}")
            print(f"   Pongs received: {self.pong_count}")
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Connection events: {len(self.connection_events)}")
            
            # Show connection events
            print(f"\n📝 Connection Events:")
            for event in self.connection_events:
                print(f"   {event['timestamp']}: {event['type']}")
                if 'error' in event:
                    print(f"      Error: {event['error']}")
            
            return success_rate > 80  # Consider >80% success rate as good
            
        except Exception as e:
            print(f"❌ Tunnel WebSocket test failed: {e}")
            return False
        finally:
            if self.connected:
                await self.sio.disconnect()
    
    async def test_tunnel_http_endpoints(self):
        """Test HTTP endpoints through tunnel"""
        endpoints = [
            "/health",
            "/api/extensions", 
            "/api/webrtc/rooms",
            "/api/test-results/latest"
        ]
        
        print(f"🔍 Testing HTTP endpoints through tunnel...")
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False),
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            for endpoint in endpoints:
                try:
                    url = f"{self.tunnel_url}{endpoint}"
                    async with session.get(url) as response:
                        status = "✅" if response.status < 400 else "❌"
                        print(f"   {status} {endpoint}: {response.status}")
                        
                        if endpoint == "/health":
                            data = await response.json()
                            if 'server_config' in data:
                                config = data['server_config']
                                print(f"      Timeout config: ping={config['ping_timeout']}s, interval={config['ping_interval']}s")
                            
                except Exception as e:
                    print(f"   ❌ {endpoint}: {e}")

async def main():
    tunnel_url = "https://monad-socketio.loca.lt"
    if len(sys.argv) > 1:
        tunnel_url = sys.argv[1]
    
    tester = TunnelWebSocketTester(tunnel_url)
    
    print("🚀 Starting Tunnel WebSocket Diagnostics")
    print(f"🌐 Tunnel: {tunnel_url}")
    print("=" * 60)
    
    # Test HTTP endpoints first
    await tester.test_tunnel_http_endpoints()
    
    print("\n" + "=" * 60)
    
    # Test WebSocket connections
    success = await tester.test_tunnel_websocket(45)  # 45 second test
    
    print("\n" + "=" * 60)
    
    if success:
        print("✅ Tunnel WebSocket test PASSED - Connection stable through tunnel")
    else:
        print("❌ Tunnel WebSocket test FAILED - Connection issues detected")
    
    print("\n💡 This test verifies:")
    print("   • WebSocket connection establishment through LocalTunnel")
    print("   • Socket.IO ping/pong functionality via tunnel")
    print("   • Connection stability under tunnel networking conditions") 
    print("   • WebRTC room operations through tunneled WebSockets")

if __name__ == "__main__":
    asyncio.run(main()) 