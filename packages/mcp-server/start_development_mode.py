#!/usr/bin/env python3
"""
Development Mode Startup Script
===============================

This script provides a zero-downtime development environment for the MCP server
using the FastMCP proxy. It handles:

1. Starting the main MCP server on port 8000
2. Starting the proxy server on port 8001
3. Monitoring both servers for changes
4. Automatic restart of the MCP server without affecting clients
5. Health monitoring and error reporting

Usage:
    python start_development_mode.py
    python start_development_mode.py --verbose
    python start_development_mode.py --proxy-only
"""

import asyncio
import argparse
import logging
import signal
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, List
import psutil
import aiohttp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MCPServerMonitor(FileSystemEventHandler):
    """Monitor MCP server files for changes and trigger restarts."""
    
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.restart_delay = 2.0  # Minimum seconds between restarts
        
    def on_modified(self, event):
        if not event.is_directory:
            # Only restart for Python files
            if event.src_path.endswith('.py'):
                current_time = time.time()
                if current_time - self.last_restart > self.restart_delay:
                    logger.info(f"📝 File changed: {event.src_path}")
                    self.last_restart = current_time
                    asyncio.create_task(self.restart_callback())

class DevelopmentEnvironment:
    """Main development environment manager."""
    
    def __init__(self, verbose: bool = False, proxy_only: bool = False):
        self.verbose = verbose
        self.proxy_only = proxy_only
        self.mcp_server_process: Optional[subprocess.Popen] = None
        self.proxy_process: Optional[subprocess.Popen] = None
        self.observer: Optional[Observer] = None
        self.shutdown_event = asyncio.Event()
        
        # Configuration
        self.mcp_server_script = Path(__file__).parent / "mcp_server.py"
        self.proxy_script = Path(__file__).parent / "mcp_testing_proxy.py"
        self.watch_paths = [
            str(Path(__file__).parent),
            str(Path(__file__).parent / "core"),
            str(Path(__file__).parent / "agents"),
            str(Path(__file__).parent / "files"),
            str(Path(__file__).parent / "chrome"),
            str(Path(__file__).parent / "automation"),
            str(Path(__file__).parent / "services"),
            str(Path(__file__).parent / "firebase"),
            str(Path(__file__).parent / "system"),
        ]
        
        if verbose:
            logger.setLevel(logging.DEBUG)
    
    async def start_mcp_server(self):
        """Start the main MCP server."""
        if self.proxy_only:
            return
            
        logger.info("🚀 Starting MCP server...")
        
        # Kill existing MCP server if running
        await self.stop_mcp_server()
        
        # Start new MCP server
        self.mcp_server_process = subprocess.Popen([
            sys.executable, str(self.mcp_server_script)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        await asyncio.sleep(2)
        
        # Check if server is healthy
        if await self.check_mcp_server_health():
            logger.info("✅ MCP server started successfully")
        else:
            logger.error("❌ MCP server failed to start")
            await self.stop_mcp_server()
    
    async def stop_mcp_server(self):
        """Stop the MCP server."""
        if self.mcp_server_process:
            try:
                self.mcp_server_process.terminate()
                await asyncio.sleep(1)
                if self.mcp_server_process.poll() is None:
                    self.mcp_server_process.kill()
                logger.info("🛑 MCP server stopped")
            except Exception as e:
                logger.error(f"Error stopping MCP server: {e}")
            finally:
                self.mcp_server_process = None
    
    async def start_proxy_server(self):
        """Start the proxy server."""
        logger.info("🔄 Starting proxy server...")
        
        # Kill existing proxy if running
        await self.stop_proxy_server()
        
        # Start new proxy server
        self.proxy_process = subprocess.Popen([
            sys.executable, str(self.proxy_script), 
            "--port", "8001"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for proxy to start
        await asyncio.sleep(2)
        
        # Check if proxy is healthy
        if await self.check_proxy_health():
            logger.info("✅ Proxy server started successfully")
        else:
            logger.error("❌ Proxy server failed to start")
            await self.stop_proxy_server()
    
    async def stop_proxy_server(self):
        """Stop the proxy server."""
        if self.proxy_process:
            try:
                self.proxy_process.terminate()
                await asyncio.sleep(1)
                if self.proxy_process.poll() is None:
                    self.proxy_process.kill()
                logger.info("🛑 Proxy server stopped")
            except Exception as e:
                logger.error(f"Error stopping proxy server: {e}")
            finally:
                self.proxy_process = None
    
    async def check_mcp_server_health(self) -> bool:
        """Check if the MCP server is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://127.0.0.1:8000/health",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    return response.status == 200
        except Exception as e:
            if self.verbose:
                logger.debug(f"MCP server health check failed: {e}")
            return False
    
    async def check_proxy_health(self) -> bool:
        """Check if the proxy server is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "http://127.0.0.1:8001/health",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    return response.status == 200
        except Exception as e:
            if self.verbose:
                logger.debug(f"Proxy health check failed: {e}")
            return False
    
    async def restart_mcp_server(self):
        """Restart the MCP server without affecting clients."""
        logger.info("🔄 Restarting MCP server...")
        await self.start_mcp_server()
    
    def start_file_watcher(self):
        """Start monitoring files for changes."""
        if self.proxy_only:
            return
            
        logger.info("👁️  Starting file watcher...")
        
        self.observer = Observer()
        handler = MCPServerMonitor(self.restart_mcp_server)
        
        for watch_path in self.watch_paths:
            if Path(watch_path).exists():
                self.observer.schedule(handler, watch_path, recursive=True)
                logger.info(f"📂 Watching: {watch_path}")
        
        self.observer.start()
    
    def stop_file_watcher(self):
        """Stop the file watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("👁️  File watcher stopped")
    
    async def health_monitor_loop(self):
        """Continuously monitor server health."""
        while not self.shutdown_event.is_set():
            try:
                # Check MCP server health
                if not self.proxy_only:
                    mcp_healthy = await self.check_mcp_server_health()
                    if not mcp_healthy and self.mcp_server_process:
                        logger.warning("⚠️  MCP server unhealthy, restarting...")
                        await self.restart_mcp_server()
                
                # Check proxy health
                proxy_healthy = await self.check_proxy_health()
                if not proxy_healthy and self.proxy_process:
                    logger.warning("⚠️  Proxy server unhealthy, restarting...")
                    await self.start_proxy_server()
                
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitor: {e}")
                await asyncio.sleep(10)
    
    async def start(self):
        """Start the development environment."""
        logger.info("🎯 Starting development environment...")
        
        # Start servers
        if not self.proxy_only:
            await self.start_mcp_server()
        await self.start_proxy_server()
        
        # Start file watcher
        self.start_file_watcher()
        
        # Start health monitor
        health_task = asyncio.create_task(self.health_monitor_loop())
        
        # Wait for shutdown
        try:
            await self.shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("⏸️  Interrupted by user")
        finally:
            # Cleanup
            health_task.cancel()
            try:
                await health_task
            except asyncio.CancelledError:
                pass
            
            await self.shutdown()
    
    async def shutdown(self):
        """Shutdown the development environment."""
        logger.info("🛑 Shutting down development environment...")
        
        self.shutdown_event.set()
        self.stop_file_watcher()
        await self.stop_mcp_server()
        await self.stop_proxy_server()
        
        logger.info("✅ Development environment shut down")

def setup_signal_handlers(dev_env: DevelopmentEnvironment):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(sig, frame):
        logger.info(f"📨 Received signal {sig}")
        asyncio.create_task(dev_env.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Development Mode Startup Script")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--proxy-only", action="store_true", help="Start only the proxy server")
    
    args = parser.parse_args()
    
    # Create development environment
    dev_env = DevelopmentEnvironment(verbose=args.verbose, proxy_only=args.proxy_only)
    
    # Setup signal handlers
    setup_signal_handlers(dev_env)
    
    # Print startup information
    logger.info("=" * 60)
    logger.info("🚀 MCP Server Development Mode")
    logger.info("=" * 60)
    logger.info("📋 Configuration:")
    logger.info(f"   • MCP Server: http://127.0.0.1:8000")
    logger.info(f"   • Proxy Server: http://127.0.0.1:8001")
    logger.info(f"   • Verbose Mode: {args.verbose}")
    logger.info(f"   • Proxy Only: {args.proxy_only}")
    logger.info("=" * 60)
    
    if not args.proxy_only:
        logger.info("🔧 Features:")
        logger.info("   • Zero-downtime server restarts")
        logger.info("   • Automatic file change detection")
        logger.info("   • Health monitoring and recovery")
        logger.info("   • Client connection stability")
        logger.info("=" * 60)
    
    logger.info("🎯 Client Connection Instructions:")
    logger.info("   • Claude Desktop: Use proxy via STDIO")
    logger.info("   • Claude CLI: http://127.0.0.1:8001/mcp")
    logger.info("   • Cursor IDE: http://127.0.0.1:8001/mcp")
    logger.info("=" * 60)
    
    # Start development environment
    try:
        await dev_env.start()
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        await dev_env.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    # Install required dependencies
    try:
        import watchdog
        import psutil
    except ImportError:
        logger.error("❌ Missing required dependencies. Install with:")
        logger.error("   pip install watchdog psutil")
        sys.exit(1)
    
    asyncio.run(main())