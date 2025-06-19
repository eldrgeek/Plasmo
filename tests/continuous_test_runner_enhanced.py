#!/usr/bin/env python3
"""
Enhanced Continuous Test Runner for Plasmo Extension
===================================================

Automatically runs tests via CDP and WebRTC when files change, providing immediate feedback.
Includes dual endpoint testing (local + tunnel) with smart file watching.
"""

import asyncio
import websockets
import json
import time
import requests
import sys
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
from aiohttp import web, ClientSession, ClientTimeout
import threading
from typing import Dict, List, Set

# Import WebRTC test suite
from webrtc_test_suite import run_webrtc_tests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/continuous_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedTestRunner:
    def __init__(self):
        self.chrome_debug_port = 9222
        self.socketio_server = "http://localhost:3001"
        self.tunnel_server = "https://monad-socketio.loca.lt"
        self.test_results_history = []
        self.last_test_time = None
        self.test_debounce_seconds = 2  # Wait 2 seconds after file change
        
        # File-to-test mapping for intelligent testing
        self.file_test_mappings = {
            # WebRTC/Socket.IO related files
            'socketio_server_python.py': ['webrtc'],
            'socketio_server.js': ['webrtc'],
            'service_manager.py': ['webrtc'],
            'webrtc_test_suite.py': ['webrtc'],
            'test_room_client.py': ['webrtc'],
            'dashboard_perfect.py': ['webrtc'],
            
            # Chrome extension files
            'popup.tsx': ['extension', 'basic'],
            'background.ts': ['extension', 'basic'],
            'options.tsx': ['extension', 'basic'],
            'contents/': ['extension', 'basic'],
            
            # Python backend files
            'mcp_server.py': ['basic'],
            'chrome_debug_launcher.py': ['basic'],
            
            # Test files
            'continuous_test_runner.py': ['basic'],
            'test_*.py': ['webrtc', 'basic'],
        }
        
    def should_run_webrtc_tests(self, file_path: str) -> bool:
        """Determine if file change should trigger WebRTC tests"""
        path = Path(file_path)
        
        # Check exact filename matches
        if path.name in self.file_test_mappings:
            return 'webrtc' in self.file_test_mappings[path.name]
        
        # Check pattern matches
        for pattern, test_types in self.file_test_mappings.items():
            if pattern.endswith('/') and pattern[:-1] in str(path):
                return 'webrtc' in test_types
            elif '*' in pattern and path.name.startswith(pattern.split('*')[0]):
                return 'webrtc' in test_types
        
        return False
    
    def should_run_basic_tests(self, file_path: str) -> bool:
        """Determine if file change should trigger basic CDP tests"""
        path = Path(file_path)
        
        # Always run basic tests for extension files
        extension_patterns = ['.ts', '.tsx', '.js', '.jsx', '.html', '.css']
        if path.suffix in extension_patterns:
            return True
        
        # Check mappings
        if path.name in self.file_test_mappings:
            return 'basic' in self.file_test_mappings[path.name]
        
        for pattern, test_types in self.file_test_mappings.items():
            if pattern.endswith('/') and pattern[:-1] in str(path):
                return 'basic' in test_types
            elif '*' in pattern and path.name.startswith(pattern.split('*')[0]):
                return 'basic' in test_types
        
        return False
        
    async def get_active_test_tab(self):
        """Find the active test page tab"""
        try:
            response = requests.get(f"http://localhost:{self.chrome_debug_port}/json", timeout=5)
            tabs = response.json()
            
            # Look for test page first
            for tab in tabs:
                if "test_page.html" in tab.get('url', '') and tab.get('type') == 'page':
                    return tab
            
            # Fallback to any page tab
            for tab in tabs:
                if tab.get('type') == 'page' and not tab.get('url', '').startswith('chrome://'):
                    return tab
                    
            return None
        except Exception as e:
            logger.error(f"Failed to get Chrome tabs: {e}")
            return None
    
    async def send_command_and_wait(self, ws, command_id, method, params=None):
        """Send CDP command and wait for specific response"""
        message = {'id': command_id, 'method': method}
        if params:
            message['params'] = params
            
        await ws.send(json.dumps(message))
        
        # Wait for our specific response, filtering out extension noise
        while True:
            response = await ws.recv()
            data = json.loads(response)
            
            if data.get('id') == command_id:
                return data
            elif data.get('method') in ['Runtime.executionContextCreated', 'Runtime.consoleAPICalled']:
                continue  # Skip extension events
    
    async def run_cdp_tests(self, tab_id):
        """Run tests using Chrome Debug Protocol"""
        ws_url = f"ws://localhost:{self.chrome_debug_port}/devtools/page/{tab_id}"
        
        try:
            async with websockets.connect(ws_url) as ws:
                # Enable Runtime
                await self.send_command_and_wait(ws, 1, 'Runtime.enable')
                
                # Check for test framework
                framework_check = await self.send_command_and_wait(ws, 2, 'Runtime.evaluate', {
                    'expression': 'typeof window.testRunner !== "undefined" ? "available" : "missing"',
                    'returnByValue': True
                })
                
                framework_status = framework_check.get('result', {}).get('result', {}).get('value', 'error')
                
                if framework_status == 'available':
                    # Run existing test suite
                    test_result = await self.send_command_and_wait(ws, 3, 'Runtime.evaluate', {
                        'expression': '''
                        (async () => {
                            try {
                                const results = await window.testRunner.run();
                                return {
                                    success: true,
                                    total: results.length,
                                    passed: results.filter(r => r.status === 'PASS').length,
                                    failed: results.filter(r => r.status === 'FAIL').length,
                                    details: results.map(r => ({
                                        name: r.name, 
                                        status: r.status, 
                                        error: r.error || null
                                    }))
                                };
                            } catch(e) {
                                return {
                                    success: false,
                                    error: e.message
                                };
                            }
                        })()
                        ''',
                        'awaitPromise': True,
                        'returnByValue': True
                    })
                    
                    return test_result.get('result', {}).get('result', {}).get('value', {})
                else:
                    # Run basic validation tests
                    basic_tests = await self.send_command_and_wait(ws, 4, 'Runtime.evaluate', {
                        'expression': '''
                        (() => {
                            const tests = [
                                {name: 'JavaScript Engine', test: () => typeof window === 'object'},
                                {name: 'DOM Ready', test: () => document.readyState === 'complete'},
                                {name: 'Basic Math', test: () => 2 + 2 === 4},
                                {name: 'Extension Context', test: () => typeof chrome !== 'undefined'}
                            ];
                            
                            const results = tests.map(t => {
                                try {
                                    const passed = t.test();
                                    return {name: t.name, status: passed ? 'PASS' : 'FAIL'};
                                } catch(e) {
                                    return {name: t.name, status: 'FAIL', error: e.message};
                                }
                            });
                            
                            return {
                                success: true,
                                total: results.length,
                                passed: results.filter(r => r.status === 'PASS').length,
                                failed: results.filter(r => r.status === 'FAIL').length,
                                details: results,
                                framework: 'basic'
                            };
                        })()
                        ''',
                        'returnByValue': True
                    })
                    
                    return basic_tests.get('result', {}).get('result', {}).get('value', {})
                    
        except Exception as e:
            logger.error(f"CDP test execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'total': 0,
                'passed': 0,
                'failed': 1
            }
    
    async def run_webrtc_tests(self) -> List[Dict]:
        """Run WebRTC tests on both endpoints"""
        endpoints = [self.socketio_server, self.tunnel_server]
        return await run_webrtc_tests(endpoints)
    
    async def run_test_cycle(self, trigger_reason="manual", test_types: Set[str] = None):
        """Run a complete test cycle with selective test execution"""
        start_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if test_types is None:
            test_types = {'basic', 'webrtc'}
        
        logger.info(f"🧪 Starting test cycle at {timestamp} (trigger: {trigger_reason}, types: {', '.join(test_types)})")
        
        all_results = []
        
        # Run CDP tests if requested
        if 'basic' in test_types:
            logger.info("🔍 Running CDP tests...")
            tab = await self.get_active_test_tab()
            if tab:
                logger.info(f"📄 Using tab: {tab['title'][:50]}...")
                cdp_results = await self.run_cdp_tests(tab['id'])
                cdp_results['test_type'] = 'cdp'
                cdp_results['trigger'] = trigger_reason
                cdp_results['timestamp'] = timestamp
                all_results.append(cdp_results)
            else:
                all_results.append({
                    'success': False,
                    'error': 'No suitable test tab found',
                    'test_type': 'cdp',
                    'trigger': trigger_reason,
                    'timestamp': timestamp,
                    'duration': 0
                })
        
        # Run WebRTC tests if requested
        if 'webrtc' in test_types:
            logger.info("🌐 Running WebRTC tests...")
            try:
                webrtc_results = await self.run_webrtc_tests()
                for result in webrtc_results:
                    result['trigger'] = trigger_reason
                    result['timestamp'] = timestamp
                all_results.extend(webrtc_results)
            except Exception as e:
                logger.error(f"WebRTC tests failed: {e}")
                all_results.append({
                    'success': False,
                    'error': f'WebRTC tests failed: {str(e)}',
                    'test_type': 'webrtc',
                    'trigger': trigger_reason,
                    'timestamp': timestamp,
                    'duration': 0
                })
        
        # Calculate total duration
        total_duration = time.time() - start_time
        
        # Report results
        await self.report_results(all_results, total_duration)
        
        self.last_test_time = time.time()
        return all_results
    
    async def report_results(self, results: List[Dict], total_duration: float):
        """Report test results to various outputs"""
        # Calculate totals
        total_passed = sum(r.get('passed', 0) for r in results)
        total_failed = sum(r.get('failed', 0) for r in results)
        total_tests = sum(r.get('total', 0) for r in results)
        all_successful = all(r.get('success', False) for r in results)
        
        # Console output
        status_icon = "✅" if all_successful else "❌"
        logger.info(f"{status_icon} All Tests: {total_passed}/{total_tests} passed in {total_duration:.1f}s")
        
        # Detailed results by type
        for result in results:
            test_type = result.get('test_type', 'unknown')
            endpoint = result.get('endpoint_type', '')
            server_url = result.get('server_url', '')
            
            if result.get('success', False):
                passed = result.get('passed', 0)
                total = result.get('total', 0)
                duration = result.get('duration', 0)
                
                type_label = f"{test_type}" + (f" ({endpoint})" if endpoint else "")
                logger.info(f"  ✅ {type_label}: {passed}/{total} passed in {duration}s")
                
                # Show individual test failures
                if result.get('details'):
                    for test in result['details']:
                        if test.get('status') == 'FAIL':
                            error_info = f" - {test.get('details', test.get('error', ''))}"
                            logger.info(f"    ❌ {test['name']}{error_info}")
            else:
                error = result.get('error', 'Unknown error')
                type_label = f"{test_type}" + (f" ({endpoint})" if endpoint else "")
                logger.error(f"  ❌ {type_label}: {error}")
        
        # Send to SocketIO server
        await self.send_to_socketio(results)
        
        # Write to file for other processes
        await self.write_results_file(results, total_duration)
    
    async def send_to_socketio(self, results: List[Dict]):
        """Send results to SocketIO server for web interface"""
        try:
            # Send each result separately to maintain structure
            async with ClientSession() as session:
                for result in results:
                    try:
                        async with session.post(
                            f"{self.socketio_server}/api/test-results",
                            json=result,
                            timeout=ClientTimeout(total=2)
                        ) as response:
                            if response.status == 200:
                                logger.debug(f"✅ {result.get('test_type', 'unknown')} results sent to SocketIO server")
                            else:
                                logger.debug(f"⚠️ SocketIO server returned {response.status} for {result.get('test_type', 'unknown')}")
                    except Exception as e:
                        logger.debug(f"Failed to send {result.get('test_type', 'unknown')} results: {e}")
        except Exception as e:
            logger.debug(f"Failed to create session for SocketIO: {e}")
    
    async def write_results_file(self, results: List[Dict], total_duration: float):
        """Write results to file for monitoring"""
        try:
            results_file = Path('logs/latest_test_results.json')
            results_file.parent.mkdir(exist_ok=True)
            
            summary = {
                'timestamp': datetime.now().isoformat(),
                'total_duration': total_duration,
                'summary': {
                    'total_passed': sum(r.get('passed', 0) for r in results),
                    'total_failed': sum(r.get('failed', 0) for r in results),
                    'total_tests': sum(r.get('total', 0) for r in results),
                    'all_successful': all(r.get('success', False) for r in results)
                },
                'results': results
            }
            
            with open(results_file, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to write results file: {e}")

class SmartFileChangeHandler(FileSystemEventHandler):
    def __init__(self, test_runner):
        self.test_runner = test_runner
        self.pending_test = None
        
    def should_trigger_test(self, file_path):
        """Determine if file change should trigger tests"""
        path = Path(file_path)
        
        # Ignore certain files/directories
        ignore_patterns = [
            'node_modules', '.git', '__pycache__', 'logs',
            '.log', '.pyc', '.tmp', 'chrome-debug-profile',
            'venv', '.pytest_cache', '__pycache__'
        ]
        
        if any(pattern in str(path) for pattern in ignore_patterns):
            return False
            
        # Test relevant extensions
        relevant_extensions = ['.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.py']
        return path.suffix in relevant_extensions
    
    def determine_test_types(self, file_path):
        """Determine which test types to run based on file change"""
        test_types = set()
        
        if self.test_runner.should_run_basic_tests(file_path):
            test_types.add('basic')
        
        if self.test_runner.should_run_webrtc_tests(file_path):
            test_types.add('webrtc')
        
        # Default to basic tests if no specific mapping
        if not test_types:
            test_types.add('basic')
            
        return test_types
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if not self.should_trigger_test(event.src_path):
            return
        
        test_types = self.determine_test_types(event.src_path)
        test_types_str = ', '.join(test_types)
        
        logger.info(f"📝 File changed: {Path(event.src_path).name} -> {test_types_str} tests")
        
        # Use threading instead of asyncio for file events
        import threading
        thread = threading.Thread(
            target=self.schedule_test_sync,
            args=(event.src_path, test_types)
        )
        thread.daemon = True
        thread.start()
    
    def schedule_test_sync(self, file_path, test_types):
        """Synchronous wrapper for test scheduling"""
        import time
        time.sleep(self.test_runner.test_debounce_seconds)
        
        # Don't run if last test was very recent
        if (self.test_runner.last_test_time and 
            time.time() - self.test_runner.last_test_time < 5):
            logger.debug("Skipping test - too recent")
            return
            
        # Create new event loop for this thread
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                self.test_runner.run_test_cycle(
                    f"file_change:{Path(file_path).name}",
                    test_types
                )
            )
        finally:
            loop.close()

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'service': 'enhanced_continuous_test_runner',
        'timestamp': datetime.now().isoformat(),
        'watching': str(Path.cwd()),
        'capabilities': ['cdp_tests', 'webrtc_tests', 'dual_endpoint', 'smart_file_watching']
    })

async def start_health_server():
    """Start health check server on port 8083"""
    app = web.Application()
    app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8083)
    await site.start()
    logger.info("🔍 Enhanced health server started on http://localhost:8083/health")

async def main():
    """Main continuous testing loop"""
    test_runner = EnhancedTestRunner()
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    logger.info("🚀 Starting Enhanced Continuous Test Runner")
    logger.info("   📊 Features: CDP tests, WebRTC tests, dual endpoints, smart file watching")
    
    # Start health server
    await start_health_server()
    
    logger.info(f"📁 Watching: {Path.cwd()}")
    logger.info(f"🌐 Chrome Debug: localhost:{test_runner.chrome_debug_port}")
    logger.info(f"📡 Local Server: {test_runner.socketio_server}")
    logger.info(f"🌍 Tunnel Server: {test_runner.tunnel_server}")
    
    # Run initial test cycle
    logger.info("🧪 Running initial test cycle...")
    await test_runner.run_test_cycle("startup")
    
    # Set up file watching
    event_handler = SmartFileChangeHandler(test_runner)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    
    logger.info("👀 Smart file watching started - tests will run automatically on relevant changes")
    logger.info("💡 File patterns:")
    for pattern, types in test_runner.file_test_mappings.items():
        logger.info(f"   {pattern}: {', '.join(types)}")
    logger.info("💡 Ctrl+C to stop")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Stopping enhanced continuous test runner...")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    asyncio.run(main()) 