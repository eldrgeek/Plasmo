#!/usr/bin/env python3
"""
WebRTC Room State Management Test Suite
=======================================

Automated tests for Socket.IO WebRTC room functionality.
Runs on both local server and tunnel endpoint for comprehensive testing.
"""

import asyncio
import socketio
import json
import time
import aiohttp
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class WebRTCTestClient:
    """Enhanced test client for WebRTC room state management"""
    
    def __init__(self, server_url: str, username: str, room_name: str):
        self.server_url = server_url
        self.username = username
        self.room_name = room_name
        self.peer_id = f"{username}_{int(time.time())}"
        self.sio = socketio.AsyncClient(
            reconnection=False,  # Disable for testing
            logger=False,
            engineio_logger=False
        )
        self.connected = False
        self.in_room = False
        self.events_received = []
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.sio.event
        async def connect():
            self.connected = True
            self.events_received.append(('connect', {}))
            
        @self.sio.event
        async def disconnect():
            self.connected = False
            self.in_room = False
            self.events_received.append(('disconnect', {}))
            
        @self.sio.event
        async def join_room_success(data):
            self.in_room = True
            self.events_received.append(('join_room_success', data))
            
        @self.sio.event
        async def join_room_error(data):
            self.events_received.append(('join_room_error', data))
            
        @self.sio.event
        async def leave_room_success(data):
            self.in_room = False
            self.events_received.append(('leave_room_success', data))
            
        @self.sio.event
        async def peer_list_updated(data):
            self.events_received.append(('peer_list_updated', data))
            
        @self.sio.event
        async def peer_list_response(data):
            self.events_received.append(('peer_list_response', data))
            
        @self.sio.event
        async def heartbeat_ack(data):
            self.events_received.append(('heartbeat_ack', data))
    
    async def connect_to_server(self, timeout: int = 5) -> bool:
        try:
            await asyncio.wait_for(self.sio.connect(self.server_url), timeout=timeout)
            await asyncio.sleep(0.1)  # Small delay for connection establishment
            return self.connected
        except Exception as e:
            logger.debug(f"{self.username} connection failed: {e}")
            return False
    
    async def join_room(self) -> bool:
        if not self.connected:
            return False
        try:
            await self.sio.emit('join_room', {
                'room_name': self.room_name,
                'peer_id': self.peer_id,
                'username': self.username,
                'user_data': {'test_client': True, 'version': '1.0'}
            })
            await asyncio.sleep(0.1)  # Wait for response
            return True
        except Exception:
            return False
    
    async def leave_room(self) -> bool:
        if not self.in_room:
            return False
        try:
            await self.sio.emit('leave_room', {})
            await asyncio.sleep(0.1)  # Wait for response
            return True
        except Exception:
            return False
    
    async def request_peer_list(self) -> bool:
        try:
            await self.sio.emit('request_peer_list', {
                'room_name': self.room_name,
                'include_inactive': True
            })
            await asyncio.sleep(0.1)  # Wait for response
            return True
        except Exception:
            return False
    
    async def send_heartbeat(self) -> bool:
        try:
            await self.sio.emit('heartbeat', {'timestamp': datetime.now().isoformat()})
            await asyncio.sleep(0.1)  # Wait for response
            return True
        except Exception:
            return False
    
    async def disconnect_from_server(self):
        if self.connected:
            await self.sio.disconnect()
    
    def get_events_by_type(self, event_type: str) -> List[Dict]:
        return [data for event, data in self.events_received if event == event_type]
    
    def clear_events(self):
        self.events_received.clear()

class WebRTCTestSuite:
    """Comprehensive WebRTC test suite"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.results = []
    
    async def check_server_health(self) -> bool:
        """Check if server is healthy before running tests"""
        try:
            async with aiohttp.ClientSession() as session:
                health_url = f"{self.server_url}/health"
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=3)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('status') == 'healthy'
            return False
        except Exception:
            return False
    
    def add_result(self, test_name: str, passed: bool, details: str = "", duration: float = 0):
        """Add test result"""
        self.results.append({
            'name': test_name,
            'status': 'PASS' if passed else 'FAIL',
            'details': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        })
    
    async def test_basic_connection(self) -> bool:
        """Test basic Socket.IO connection"""
        start_time = time.time()
        client = WebRTCTestClient(self.server_url, "TestUser", "test-room")
        
        try:
            connected = await client.connect_to_server(timeout=3)
            await client.disconnect_from_server()
            
            duration = time.time() - start_time
            self.add_result(
                "Basic Connection",
                connected,
                f"Connection to {self.server_url}" + ("" if connected else " failed"),
                duration
            )
            return connected
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("Basic Connection", False, f"Exception: {str(e)}", duration)
            return False
    
    async def test_room_join_leave_cycle(self) -> bool:
        """Test room join/leave state management"""
        start_time = time.time()
        client = WebRTCTestClient(self.server_url, "TestUser", "test-room")
        
        try:
            # Connect and join
            await client.connect_to_server()
            await client.join_room()
            await asyncio.sleep(0.2)
            
            join_events = client.get_events_by_type('join_room_success')
            if not join_events:
                duration = time.time() - start_time
                self.add_result("Room Join/Leave Cycle", False, "No join_room_success event", duration)
                await client.disconnect_from_server()
                return False
            
            # Check join status
            join_data = join_events[0]
            initial_status = join_data.get('status')
            
            # Leave room
            await client.leave_room()
            await asyncio.sleep(0.2)
            
            leave_events = client.get_events_by_type('leave_room_success')
            if not leave_events:
                duration = time.time() - start_time
                self.add_result("Room Join/Leave Cycle", False, "No leave_room_success event", duration)
                await client.disconnect_from_server()
                return False
            
            # Rejoin (should be reactivated)
            client.clear_events()
            await client.join_room()
            await asyncio.sleep(0.2)
            
            rejoin_events = client.get_events_by_type('join_room_success')
            if not rejoin_events:
                duration = time.time() - start_time
                self.add_result("Room Join/Leave Cycle", False, "No rejoin_room_success event", duration)
                await client.disconnect_from_server()
                return False
            
            rejoin_status = rejoin_events[0].get('status')
            
            await client.disconnect_from_server()
            
            # Validate status progression
            success = (initial_status == 'joined' and rejoin_status == 'reactivated')
            duration = time.time() - start_time
            
            details = f"Initial: {initial_status}, Rejoin: {rejoin_status}"
            self.add_result("Room Join/Leave Cycle", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("Room Join/Leave Cycle", False, f"Exception: {str(e)}", duration)
            await client.disconnect_from_server()
            return False
    
    async def test_multi_client_state_sync(self) -> bool:
        """Test state synchronization between multiple clients"""
        start_time = time.time()
        client1 = WebRTCTestClient(self.server_url, "Alice", "sync-room")
        client2 = WebRTCTestClient(self.server_url, "Bob", "sync-room")
        
        try:
            # Connect both clients
            await client1.connect_to_server()
            await client2.connect_to_server()
            
            # Client1 joins
            await client1.join_room()
            await asyncio.sleep(0.2)
            
            # Client2 joins (should trigger peer list updates)
            client1.clear_events()
            await client2.join_room()
            await asyncio.sleep(0.3)
            
            # Check if client1 received peer list update
            updates1 = client1.get_events_by_type('peer_list_updated')
            updates2 = client2.get_events_by_type('peer_list_updated')
            
            # Verify peer counts
            peer_list_valid = False
            if updates1:
                update_data = updates1[0]
                active_count = update_data.get('active_peers', 0)
                total_count = update_data.get('total_peers', 0)
                peer_list_valid = (active_count == 2 and total_count == 2)
            
            await client1.disconnect_from_server()
            await client2.disconnect_from_server()
            
            duration = time.time() - start_time
            details = f"Updates received: C1={len(updates1)}, C2={len(updates2)}, Valid counts: {peer_list_valid}"
            success = len(updates1) > 0 and peer_list_valid
            
            self.add_result("Multi-Client State Sync", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("Multi-Client State Sync", False, f"Exception: {str(e)}", duration)
            await client1.disconnect_from_server()
            await client2.disconnect_from_server()
            return False
    
    async def test_heartbeat_functionality(self) -> bool:
        """Test heartbeat system"""
        start_time = time.time()
        client = WebRTCTestClient(self.server_url, "HeartbeatTest", "heartbeat-room")
        
        try:
            await client.connect_to_server()
            await client.join_room()
            await asyncio.sleep(0.1)
            
            # Send heartbeat
            await client.send_heartbeat()
            await asyncio.sleep(0.2)
            
            # Check for heartbeat acknowledgment
            heartbeat_acks = client.get_events_by_type('heartbeat_ack')
            
            await client.disconnect_from_server()
            
            duration = time.time() - start_time
            success = len(heartbeat_acks) > 0
            details = f"Heartbeat acks received: {len(heartbeat_acks)}"
            
            self.add_result("Heartbeat Functionality", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("Heartbeat Functionality", False, f"Exception: {str(e)}", duration)
            await client.disconnect_from_server()
            return False
    
    async def test_peer_list_request(self) -> bool:
        """Test manual peer list requests"""
        start_time = time.time()
        client = WebRTCTestClient(self.server_url, "PeerListTest", "list-room")
        
        try:
            await client.connect_to_server()
            await client.join_room()
            await asyncio.sleep(0.1)
            
            # Request peer list
            await client.request_peer_list()
            await asyncio.sleep(0.2)
            
            # Check for response
            responses = client.get_events_by_type('peer_list_response')
            
            await client.disconnect_from_server()
            
            duration = time.time() - start_time
            success = len(responses) > 0
            details = f"Peer list responses: {len(responses)}"
            
            if responses:
                response_data = responses[0]
                room_name = response_data.get('room_name')
                active_peers = response_data.get('active_peers', 0)
                details += f", Room: {room_name}, Active: {active_peers}"
            
            self.add_result("Peer List Request", success, details, duration)
            return success
            
        except Exception as e:
            duration = time.time() - start_time
            self.add_result("Peer List Request", False, f"Exception: {str(e)}", duration)
            await client.disconnect_from_server()
            return False
    
    async def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        suite_start = time.time()
        self.results.clear()
        
        # Check server health first
        if not await self.check_server_health():
            self.add_result("Server Health Check", False, f"Server {self.server_url} not healthy")
            return self.compile_results(suite_start)
        
        self.add_result("Server Health Check", True, f"Server {self.server_url} is healthy")
        
        # Run all tests
        tests = [
            self.test_basic_connection,
            self.test_room_join_leave_cycle,
            self.test_multi_client_state_sync,
            self.test_heartbeat_functionality,
            self.test_peer_list_request
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.1)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test {test.__name__} failed with exception: {e}")
        
        return self.compile_results(suite_start)
    
    def compile_results(self, start_time: float) -> Dict:
        """Compile final test results"""
        total_duration = time.time() - start_time
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        
        return {
            'success': failed == 0,
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'duration': round(total_duration, 2),
            'details': self.results,
            'test_type': 'webrtc_room_state',
            'server_url': self.server_url,
            'timestamp': datetime.now().isoformat()
        }

async def run_webrtc_tests(server_urls: List[str]) -> List[Dict]:
    """Run WebRTC tests on multiple server endpoints"""
    all_results = []
    
    for server_url in server_urls:
        logger.info(f"🧪 Running WebRTC tests on {server_url}")
        
        test_suite = WebRTCTestSuite(server_url)
        results = await test_suite.run_all_tests()
        
        # Add endpoint info
        endpoint_type = "tunnel" if "loca.lt" in server_url else "local"
        results['endpoint_type'] = endpoint_type
        
        all_results.append(results)
        
        # Log summary
        status = "✅" if results['success'] else "❌"
        logger.info(f"{status} {endpoint_type.title()} tests: {results['passed']}/{results['total']} passed")
    
    return all_results

if __name__ == "__main__":
    # For standalone testing
    import logging
    logging.basicConfig(level=logging.INFO)
    
    async def main():
        endpoints = [
            "http://localhost:3001",
            "https://monad-socketio.loca.lt"  # Add tunnel endpoint
        ]
        
        results = await run_webrtc_tests(endpoints)
        
        for result in results:
            print(f"\n{'='*50}")
            print(f"Results for {result['endpoint_type']} endpoint:")
            print(f"Success: {result['success']}")
            print(f"Tests: {result['passed']}/{result['total']} passed")
            print(f"Duration: {result['duration']}s")
            
            if not result['success']:
                for test in result['details']:
                    if test['status'] == 'FAIL':
                        print(f"❌ {test['name']}: {test['details']}")
    
    asyncio.run(main()) 