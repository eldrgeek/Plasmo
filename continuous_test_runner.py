#!/usr/bin/env python3
"""
Continuous Test Runner for Plasmo Extension
===========================================

Automatically runs tests via CDP when files change, providing immediate feedback.
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
from aiohttp import web, ClientSession
import threading

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

class TestRunner:
    def __init__(self):
        self.chrome_debug_port = 9222
        self.socketio_server = "http://localhost:3001"
        self.test_results_history = []
        self.last_test_time = None
        self.test_debounce_seconds = 2  # Wait 2 seconds after file change
        
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
    
    async def run_tests_via_cdp(self, tab_id):
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
    
    async def run_test_cycle(self, trigger_reason="manual"):
        """Run a complete test cycle"""
        start_time = time.time()
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        logger.info(f"🧪 Starting test cycle at {timestamp} (trigger: {trigger_reason})")
        
        # Get active tab
        tab = await self.get_active_test_tab()
        if not tab:
            result = {
                'success': False,
                'error': 'No suitable test tab found',
                'timestamp': timestamp,
                'trigger': trigger_reason,
                'duration': 0
            }
            await self.report_results(result)
            return result
        
        logger.info(f"📄 Using tab: {tab['title'][:50]}...")
        
        # Run tests
        test_results = await self.run_tests_via_cdp(tab['id'])
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Prepare final result
        result = {
            **test_results,
            'timestamp': timestamp,
            'trigger': trigger_reason,
            'duration': round(duration, 2),
            'tab_title': tab.get('title', 'Unknown'),
            'tab_url': tab.get('url', 'Unknown')
        }
        
        # Store in history
        self.test_results_history.append(result)
        if len(self.test_results_history) > 50:  # Keep last 50 results
            self.test_results_history.pop(0)
        
        # Report results
        await self.report_results(result)
        
        self.last_test_time = time.time()
        return result
    
    async def report_results(self, result):
        """Report test results to various outputs"""
        success = result.get('success', False)
        passed = result.get('passed', 0)
        total = result.get('total', 0)
        failed = result.get('failed', 0)
        duration = result.get('duration', 0)
        
        # Console output
        if success:
            status_icon = "✅" if failed == 0 else "⚠️"
            logger.info(f"{status_icon} Tests: {passed}/{total} passed in {duration}s")
            
            if result.get('details'):
                for test in result['details']:
                    icon = "✅" if test['status'] == 'PASS' else "❌"
                    error_info = f" - {test.get('error', '')}" if test.get('error') else ""
                    logger.info(f"  {icon} {test['name']}{error_info}")
        else:
            logger.error(f"❌ Test execution failed: {result.get('error', 'Unknown error')}")
        
        # Send to SocketIO server
        await self.send_to_socketio(result)
        
        # Write to file for other processes
        await self.write_results_file(result)
    
    async def send_to_socketio(self, result):
        """Send results to SocketIO server for web interface"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.socketio_server}/api/test-results",
                    json=result,
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    if response.status == 200:
                        logger.debug("✅ Test results sent to SocketIO server")
                    else:
                        logger.debug(f"⚠️ SocketIO server returned {response.status}")
        except Exception as e:
            logger.debug(f"Failed to send to SocketIO: {e}")
    
    async def write_results_file(self, result):
        """Write results to file for monitoring"""
        try:
            results_file = Path('logs/latest_test_results.json')
            results_file.parent.mkdir(exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(result, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to write results file: {e}")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, test_runner):
        self.test_runner = test_runner
        self.pending_test = None
        
    def should_trigger_test(self, file_path):
        """Determine if file change should trigger tests"""
        path = Path(file_path)
        
        # Ignore certain files/directories
        ignore_patterns = [
            'node_modules', '.git', '__pycache__', 'logs',
            '.log', '.pyc', '.tmp', 'chrome-debug-profile'
        ]
        
        if any(pattern in str(path) for pattern in ignore_patterns):
            return False
            
        # Test relevant extensions
        relevant_extensions = ['.ts', '.tsx', '.js', '.jsx', '.html', '.css', '.py']
        return path.suffix in relevant_extensions
    
    def on_modified(self, event):
        if event.is_directory:
            return
            
        if not self.should_trigger_test(event.src_path):
            return
            
        logger.info(f"📝 File changed: {Path(event.src_path).name}")
        
        # Use threading instead of asyncio for file events
        import threading
        thread = threading.Thread(
            target=self.schedule_test_sync,
            args=(event.src_path,)
        )
        thread.daemon = True
        thread.start()
    
    def schedule_test_sync(self, file_path):
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
                self.test_runner.run_test_cycle(f"file_change:{Path(file_path).name}")
            )
        finally:
            loop.close()
    
    async def schedule_test(self, file_path):
        """Schedule test after debounce period"""
        await asyncio.sleep(self.test_runner.test_debounce_seconds)
        
        # Don't run if last test was very recent
        if (self.test_runner.last_test_time and 
            time.time() - self.test_runner.last_test_time < 5):
            logger.debug("Skipping test - too recent")
            return
            
        await self.test_runner.run_test_cycle(f"file_change:{Path(file_path).name}")

async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        'status': 'healthy',
        'service': 'continuous_test_runner',
        'timestamp': datetime.now().isoformat(),
        'watching': str(Path.cwd())
    })

async def start_health_server():
    """Start health check server on port 8082"""
    app = web.Application()
    app.router.add_get('/health', health_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8082)
    await site.start()
    logger.info("🔍 Health server started on http://localhost:8082/health")

async def main():
    """Main continuous testing loop"""
    test_runner = TestRunner()
    
    # Ensure logs directory exists
    Path('logs').mkdir(exist_ok=True)
    
    logger.info("🚀 Starting Continuous Test Runner")
    
    # Start health server
    await start_health_server()
    
    logger.info(f"📁 Watching: {Path.cwd()}")
    logger.info(f"🌐 Chrome Debug: localhost:{test_runner.chrome_debug_port}")
    logger.info(f"📡 SocketIO Server: {test_runner.socketio_server}")
    
    # Run initial test
    logger.info("🧪 Running initial test cycle...")
    await test_runner.run_test_cycle("startup")
    
    # Set up file watching
    event_handler = FileChangeHandler(test_runner)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    
    logger.info("👀 File watching started - tests will run automatically on changes")
    logger.info("💡 Ctrl+C to stop")
    
    try:
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Stopping continuous test runner...")
        observer.stop()
        observer.join()

if __name__ == "__main__":
    asyncio.run(main())