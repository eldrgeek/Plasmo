#!/usr/bin/env python3
"""
MCP Testing Proxy - FastMCP Proxy Edition
=========================================

A lightweight development proxy using FastMCP's built-in proxy capabilities.
This proxy provides a stable connection endpoint for Claude Desktop while your
actual development server can restart behind it without breaking the connection.

Features:
- Uses FastMCP's native proxy functionality 
- Automatic reconnection to development server
- Zero-downtime development workflow
- Built-in health monitoring and error handling
- Simple, clean implementation

Usage:
1. Configure Claude Desktop to connect to this proxy (port 8001)
2. Start your development server on port 8000
3. This proxy forwards all requests to your dev server
4. Restart your dev server anytime - Claude Desktop stays connected

Author: Claude AI Assistant
Version: 2.0.0 (FastMCP Proxy Edition)
"""

import asyncio
import json
import time
import logging
import signal
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import traceback
import aiohttp
from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_proxy.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
PROXY_PORT = 8001  # Port for Claude Desktop to connect to
DEV_SERVER_PORT = 8000  # Port of your development server
DEV_SERVER_HOST = "127.0.0.1"
HEALTH_CHECK_INTERVAL = 5.0  # Seconds between health checks

@dataclass
class ProxyStats:
    """Statistics about the proxy's operation."""
    uptime_start: float
    dev_server_connections: int = 0
    dev_server_disconnections: int = 0
    last_dev_server_contact: Optional[float] = None
    proxy_restarts: int = 0

class MCPDevelopmentProxy:
    """
    MCP Development Proxy using FastMCP's native proxy capabilities.
    
    This proxy creates a FastMCP proxy server that forwards all requests to your
    development server, providing a stable endpoint for Claude Desktop.
    """
    
    def __init__(self, stdio_mode: bool = False):
        self.dev_server_url = f"http://{DEV_SERVER_HOST}:{DEV_SERVER_PORT}"
        self.dev_server_connected = False
        self.stats = ProxyStats(uptime_start=time.time())
        self._shutdown_event = asyncio.Event()
        self._health_check_task: Optional[asyncio.Task] = None
        self.stdio_mode = stdio_mode
        self.proxy_server: Optional[FastMCP] = None
        self.backend_client: Optional[Client] = None
        
        # Initialize the proxy
        self._setup_proxy()
    
    def _setup_proxy(self):
        """Set up the FastMCP proxy server."""
        try:
            # Create a client that connects to the development server
            transport = StreamableHttpTransport(f"{self.dev_server_url}/mcp")
            self.backend_client = Client(transport)
            
            # Create a proxy server using FastMCP's built-in proxy functionality
            self.proxy_server = FastMCP.as_proxy(
                self.backend_client,
                name="MCP Development Proxy v2.0",
                instructions="Development proxy for stable Claude Desktop connection during server restarts."
            )
            
            # Add proxy-specific monitoring tools
            self._add_proxy_tools()
            
            logger.info("✅ FastMCP proxy server initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup proxy: {e}")
            self.proxy_server = self._create_fallback_server()
    
    def _create_fallback_server(self) -> FastMCP:
        """Create a fallback server when the main dev server is not available."""
        fallback = FastMCP(
            name="MCP Development Proxy (Fallback Mode)",
            instructions="Development server proxy - backend currently unavailable."
        )
        
        @fallback.tool()
        def dev_server_status() -> Dict[str, Any]:
            """Check development server connection status."""
            return {
                "status": "disconnected",
                "dev_server_url": self.dev_server_url,
                "message": "Development server is not available. Start your dev server and restart the proxy.",
                "suggestion": f"Start your development server on {self.dev_server_url} and use force_reconnect()"
            }
        
        # Add the common proxy tools
        self._add_proxy_tools_to_server(fallback)
        
        return fallback
    
    def _add_proxy_tools(self):
        """Add proxy-specific tools to the proxy server."""
        if self.proxy_server:
            self._add_proxy_tools_to_server(self.proxy_server)
    
    def _add_proxy_tools_to_server(self, server: FastMCP):
        """Add proxy monitoring tools to a FastMCP server."""
        
        @server.tool()
        def proxy_status() -> Dict[str, Any]:
            """Get development proxy status and statistics."""
            current_time = time.time()
            uptime = current_time - self.stats.uptime_start
            
            return {
                "proxy_info": {
                    "version": "2.0.0 (FastMCP Proxy Edition)",
                    "uptime_seconds": round(uptime, 1),
                    "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
                    "mode": "stdio" if self.stdio_mode else "http",
                    "proxy_type": "FastMCP Native Proxy"
                },
                "dev_server": {
                    "connected": self.dev_server_connected,
                    "url": self.dev_server_url,
                    "last_contact": self.stats.last_dev_server_contact,
                    "last_contact_ago": round(current_time - self.stats.last_dev_server_contact, 1) if self.stats.last_dev_server_contact else None
                },
                "statistics": {
                    "dev_server_connections": self.stats.dev_server_connections,
                    "dev_server_disconnections": self.stats.dev_server_disconnections,
                    "proxy_restarts": self.stats.proxy_restarts
                }
            }
        
        @server.tool()
        def force_reconnect() -> Dict[str, Any]:
            """Force reconnection to the development server."""
            async def reconnect():
                try:
                    await self._recreate_proxy()
                    return {"success": True, "message": "Proxy reconnection initiated"}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            
            # Run the async reconnection
            try:
                loop = asyncio.get_event_loop()
                result = loop.create_task(reconnect())
                return {"status": "reconnection_started", "message": "Attempting to reconnect to development server..."}
            except Exception as e:
                return {"success": False, "error": f"Failed to start reconnection: {e}"}
    
    async def _recreate_proxy(self):
        """Recreate the proxy connection to the development server."""
        try:
            logger.info("🔄 Recreating proxy connection...")
            
            # Close old client if it exists
            if self.backend_client:
                try:
                    await self.backend_client.close()
                except:
                    pass
            
            # Create new client and proxy
            transport = StreamableHttpTransport(f"{self.dev_server_url}/mcp")
            self.backend_client = Client(transport)
            
            # Test the connection
            async with self.backend_client:
                await self.backend_client.ping()
                logger.info("✅ Development server connection verified")
            
            # Create new proxy server
            self.proxy_server = FastMCP.as_proxy(
                self.backend_client,
                name="MCP Development Proxy v2.0",
                instructions="Development proxy for stable Claude Desktop connection during server restarts."
            )
            
            # Add proxy tools
            self._add_proxy_tools()
            
            self.dev_server_connected = True
            self.stats.dev_server_connections += 1
            self.stats.proxy_restarts += 1
            self.stats.last_dev_server_contact = time.time()
            
            logger.info("✅ Proxy recreated successfully")
            
        except Exception as e:
            logger.error(f"Failed to recreate proxy: {e}")
            self.dev_server_connected = False
            self.stats.dev_server_disconnections += 1
            # Fall back to disconnected server
            self.proxy_server = self._create_fallback_server()
    
    async def start(self, host: str = "127.0.0.1", port: int = PROXY_PORT):
        """Start the proxy server."""
        if not self.stdio_mode:
            logger.info(f"🚀 Starting MCP Development Proxy v2.0 (FastMCP Proxy Edition)")
            logger.info(f"📡 Proxy listening on {host}:{port}")
            logger.info(f"🎯 Backend server: {self.dev_server_url}")
            logger.info(f"📋 Claude Desktop should connect to: http://{host}:{port}/mcp")
        
        # Start health check loop
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        try:
            if self.stdio_mode:
                # For stdio mode, run the proxy directly
                if self.proxy_server:
                    await self.proxy_server.run_async(transport="stdio")
                else:
                    logger.error("No proxy server available for stdio mode")
            else:
                # For HTTP mode, run the proxy server
                if self.proxy_server:
                    await self.proxy_server.run_async(
                        transport="streamable-http",
                        host=host,
                        port=port,
                        path="/mcp"
                    )
                else:
                    logger.error("No proxy server available for HTTP mode")
                    
        except Exception as e:
            logger.error(f"Error running proxy server: {e}")
            raise
    
    async def _check_dev_server_health(self):
        """Check if the development server is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.dev_server_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        if not self.dev_server_connected:
                            logger.info("✅ Development server reconnected!")
                            # Recreate proxy to ensure fresh connection
                            await self._recreate_proxy()
                        else:
                            self.stats.last_dev_server_contact = time.time()
                        return True
                    else:
                        if self.dev_server_connected:
                            logger.warning(f"Development server health check failed: HTTP {response.status}")
                            self.dev_server_connected = False
                            self.stats.dev_server_disconnections += 1
                        return False
                        
        except Exception as e:
            if self.dev_server_connected:
                logger.warning(f"Lost connection to development server: {e}")
                self.dev_server_connected = False
                self.stats.dev_server_disconnections += 1
                # Switch to fallback mode
                self.proxy_server = self._create_fallback_server()
            return False
    
    async def _health_check_loop(self):
        """Continuous health checking of the development server."""
        while not self._shutdown_event.is_set():
            try:
                await self._check_dev_server_health()
                await asyncio.sleep(HEALTH_CHECK_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(HEALTH_CHECK_INTERVAL)
    
    async def shutdown(self):
        """Shut down the proxy gracefully."""
        if not self.stdio_mode:
            logger.info("🛑 Shutting down MCP Development Proxy...")
        
        self._shutdown_event.set()
        
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        if self.backend_client:
            try:
                await self.backend_client.close()
            except:
                pass
        
        if not self.stdio_mode:
            logger.info("✅ MCP Development Proxy shut down gracefully")

async def main():
    """Main entry point for the MCP Development Proxy."""
    parser = argparse.ArgumentParser(description="MCP Development Proxy v2.0 (FastMCP Proxy Edition)")
    parser.add_argument("--stdio", action="store_true", help="Use STDIO transport for Claude Desktop")
    parser.add_argument("--port", type=int, default=PROXY_PORT, help="Server port (HTTP mode only)")
    parser.add_argument("--host", default="127.0.0.1", help="Server host (HTTP mode only)")
    
    args = parser.parse_args()
    
    proxy = MCPDevelopmentProxy(stdio_mode=args.stdio)
    
    # Set up signal handlers
    def signal_handler(sig, frame):
        if not args.stdio:
            logger.info("📨 Received shutdown signal")
        asyncio.create_task(proxy.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await proxy.start(host=args.host, port=args.port)
    except KeyboardInterrupt:
        if not args.stdio:
            logger.info("⏸️  Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        raise
    finally:
        await proxy.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
