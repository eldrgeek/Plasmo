#!/usr/bin/env python3
"""
MCP Server Proxy Setup Script
=============================

This script configures and tests the FastMCP proxy for zero-downtime client connections.
It ensures that Claude Desktop, Claude Code, and other MCP clients can connect to a stable
proxy that forwards requests to the development server.

Usage:
    python setup_proxy.py --test    # Test proxy configuration
    python setup_proxy.py --start   # Start proxy server
    python setup_proxy.py --config  # Generate client configuration
"""

import asyncio
import json
import logging
import argparse
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import aiohttp
from fastmcp import FastMCP, Client
from fastmcp.client.transports import StreamableHttpTransport

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PROXY_CONFIG = {
    "proxy_port": 8001,
    "dev_server_port": 8000,
    "dev_server_host": "127.0.0.1",
    "health_check_interval": 5.0,
    "max_retries": 3,
    "retry_delay": 2.0
}

class ProxySetupManager:
    """Manager for setting up and testing the FastMCP proxy."""
    
    def __init__(self):
        self.config = PROXY_CONFIG
        self.dev_server_url = f"http://{self.config['dev_server_host']}:{self.config['dev_server_port']}"
        self.proxy_url = f"http://127.0.0.1:{self.config['proxy_port']}"
        
    async def test_dev_server_connection(self) -> bool:
        """Test if the development server is running and accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.dev_server_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5.0)
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Development server is running and accessible")
                        return True
                    else:
                        logger.error(f"❌ Development server returned status {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to development server: {e}")
            return False
    
    async def test_proxy_functionality(self) -> bool:
        """Test that the proxy can connect to and forward requests to the dev server."""
        try:
            # Create a client that connects to the development server through proxy
            transport = StreamableHttpTransport(f"{self.proxy_url}/mcp")
            client = Client(transport)
            
            async with client:
                # Test basic connectivity
                response = await client.ping()
                logger.info("✅ Proxy successfully forwards requests to development server")
                
                # Test tool enumeration
                tools = await client.list_tools()
                logger.info(f"✅ Proxy forwarded {len(tools)} tools from development server")
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Proxy functionality test failed: {e}")
            return False
    
    async def start_proxy_server(self) -> None:
        """Start the proxy server using the existing mcp_testing_proxy.py."""
        logger.info("🚀 Starting FastMCP proxy server...")
        
        # Import and run the existing proxy
        sys.path.insert(0, str(Path(__file__).parent))
        from mcp_testing_proxy import MCPDevelopmentProxy
        
        proxy = MCPDevelopmentProxy(stdio_mode=False)
        
        # Set up signal handlers for graceful shutdown
        def signal_handler(sig, frame):
            logger.info("📨 Received shutdown signal")
            asyncio.create_task(proxy.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await proxy.start(host="127.0.0.1", port=self.config["proxy_port"])
        except KeyboardInterrupt:
            logger.info("⏸️  Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Proxy server error: {e}")
            raise
        finally:
            await proxy.shutdown()
    
    def generate_client_config(self) -> Dict[str, Any]:
        """Generate MCP client configuration for various clients."""
        return {
            "claude_desktop": {
                "mcpServers": {
                    "plasmo-proxy": {
                        "command": "python",
                        "args": [
                            str(Path(__file__).parent / "mcp_testing_proxy.py"),
                            "--stdio"
                        ]
                    }
                }
            },
            "claude_cli": {
                "server_url": f"{self.proxy_url}/mcp",
                "transport": "streamable-http"
            },
            "cursor_ide": {
                "mcpServers": {
                    "plasmo-proxy": {
                        "url": f"{self.proxy_url}/mcp"
                    }
                }
            }
        }
    
    def save_client_configs(self):
        """Save client configurations to files."""
        configs = self.generate_client_config()
        
        # Save Claude Desktop config
        claude_desktop_path = Path.home() / ".claude" / "claude_desktop_config.json"
        if claude_desktop_path.exists():
            with open(claude_desktop_path, 'r') as f:
                existing_config = json.load(f)
            
            # Merge with existing config
            if "mcpServers" not in existing_config:
                existing_config["mcpServers"] = {}
            existing_config["mcpServers"]["plasmo-proxy"] = configs["claude_desktop"]["mcpServers"]["plasmo-proxy"]
            
            with open(claude_desktop_path, 'w') as f:
                json.dump(existing_config, f, indent=2)
            
            logger.info(f"✅ Updated Claude Desktop config: {claude_desktop_path}")
        
        # Save individual config files
        config_dir = Path(__file__).parent / "client_configs"
        config_dir.mkdir(exist_ok=True)
        
        for client_name, config in configs.items():
            config_path = config_dir / f"{client_name}_config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Saved {client_name} config: {config_path}")
    
    async def run_comprehensive_test(self) -> bool:
        """Run a comprehensive test of the proxy setup."""
        logger.info("🧪 Running comprehensive proxy setup test...")
        
        # Test 1: Development server connectivity
        logger.info("\n📋 Test 1: Development server connectivity")
        if not await self.test_dev_server_connection():
            logger.error("❌ Development server test failed")
            return False
        
        # Test 2: Start proxy in background for testing
        logger.info("\n📋 Test 2: Proxy server startup")
        try:
            # Start proxy server in background
            import subprocess
            proxy_process = subprocess.Popen([
                sys.executable, 
                str(Path(__file__).parent / "mcp_testing_proxy.py"),
                "--port", str(self.config["proxy_port"])
            ])
            
            # Wait for proxy to start
            await asyncio.sleep(3)
            
            # Test 3: Proxy functionality
            logger.info("\n📋 Test 3: Proxy functionality")
            if not await self.test_proxy_functionality():
                logger.error("❌ Proxy functionality test failed")
                proxy_process.terminate()
                return False
            
            # Test 4: Client configuration generation
            logger.info("\n📋 Test 4: Client configuration generation")
            self.save_client_configs()
            
            # Cleanup
            proxy_process.terminate()
            await asyncio.sleep(1)
            
            logger.info("\n✅ All proxy setup tests passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Proxy test failed: {e}")
            return False

async def main():
    """Main entry point for the proxy setup script."""
    parser = argparse.ArgumentParser(description="MCP Server Proxy Setup Script")
    parser.add_argument("--test", action="store_true", help="Run comprehensive proxy tests")
    parser.add_argument("--start", action="store_true", help="Start the proxy server")
    parser.add_argument("--config", action="store_true", help="Generate client configurations")
    parser.add_argument("--all", action="store_true", help="Run tests, generate configs, and start proxy")
    
    args = parser.parse_args()
    
    if not any([args.test, args.start, args.config, args.all]):
        parser.print_help()
        return
    
    manager = ProxySetupManager()
    
    if args.test or args.all:
        success = await manager.run_comprehensive_test()
        if not success:
            logger.error("❌ Proxy setup tests failed")
            sys.exit(1)
    
    if args.config or args.all:
        manager.save_client_configs()
        logger.info("✅ Client configurations generated")
    
    if args.start or args.all:
        await manager.start_proxy_server()

if __name__ == "__main__":
    asyncio.run(main())