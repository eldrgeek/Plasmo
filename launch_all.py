#!/usr/bin/env python3
"""
Unified Service Launcher
========================
Launch all services with proper orchestration, health monitoring, and dashboard aggregation.
Phase 1.1 Implementation
"""

import os
import sys
import asyncio
import signal
import time
import click
import logging
from pathlib import Path
from typing import Dict, List, Optional
from colorama import Fore, Style, init

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "shared" / "python-common"))

from services import (
    ServiceBase, ServiceStatus, ServiceConfig, ServiceType,
    SocketIOService, MCPService, PlasmoService, 
    TestingService, ChromeService, TunnelingService
)

# Initialize colorama
init()

class ServiceOrchestrator:
    """Central service orchestration and management"""
    
    def __init__(self):
        self.services: Dict[str, ServiceBase] = {}
        self.startup_order: List[str] = []
        self.shutdown_order: List[str] = []
        self.running = False
        self.logger = self._setup_logging()
        
        # Create service configurations
        self._create_service_configs()
        
        # Setup signal handlers
        self._setup_signal_handlers()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup centralized logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service_orchestrator.log"),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger("orchestrator")
    
    def _setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        asyncio.create_task(self.stop_all())
    
    def _create_service_configs(self):
        """Create service configurations based on current setup"""
        base_dir = str(project_root)
        
        # Service configurations
        configs = [
            ServiceConfig(
                name="socketio",
                service_type=ServiceType.SOCKETIO,
                command=[sys.executable, "socketio_server_python.py"],
                working_dir=base_dir,
                port=3001,
                log_file="socketio.log",
                health_check_url="http://localhost:3001/health",
                file_watchers=["socketio_server_python.py"]
            ),
            ServiceConfig(
                name="mcp",
                service_type=ServiceType.MCP_SERVER,
                command=[sys.executable, "mcp_server.py"],
                working_dir=base_dir,
                port=8001,
                log_file="mcp_server.log",
                health_check_url="http://localhost:8001/health",
                file_watchers=["mcp_server.py"],
                env_vars={"PYTHONPATH": base_dir}
            ),
            ServiceConfig(
                name="plasmo",
                service_type=ServiceType.PLASMO_DEV,
                command=["pnpm", "dev"],
                working_dir=base_dir,
                port=1012,
                log_file="plasmo_dev.log",
                health_check_url="http://localhost:1012",
                file_watchers=["popup.tsx", "background.ts", "options.tsx", "contents/"]
            ),
            ServiceConfig(
                name="testing",
                service_type=ServiceType.TESTING,
                command=[sys.executable, "continuous_test_runner.py"],
                working_dir=base_dir,
                port=8082,
                log_file="testing.log",
                health_check_url="http://localhost:8082/health",
                file_watchers=["test_*.py", "services/", "dashboards/"],
                env_vars={"PYTHONPATH": base_dir}
            ),
            ServiceConfig(
                name="chrome_debug",
                service_type=ServiceType.CHROME_DEBUG,
                command=[sys.executable, "chrome_debug_launcher.py"],
                working_dir=base_dir,
                port=9222,
                log_file="chrome_debug.log",
                health_check_url="http://localhost:9222/json",
                auto_restart=True
            ),
            ServiceConfig(
                name="tunneling",
                service_type=ServiceType.TUNNELING,
                command=[sys.executable, "localtunnel_manager.py"],
                working_dir=base_dir,
                log_file="tunneling.log",
                file_watchers=["localtunnel_manager.py"],
                env_vars={"PYTHONPATH": base_dir}
            )
        ]
        
        # Create service instances
        for config in configs:
            if config.service_type == ServiceType.SOCKETIO:
                service = SocketIOService(config)
            elif config.service_type == ServiceType.MCP_SERVER:
                service = MCPService(config)
            elif config.service_type == ServiceType.PLASMO_DEV:
                service = PlasmoService(config)
            elif config.service_type == ServiceType.TESTING:
                service = TestingService(config)
            elif config.service_type == ServiceType.CHROME_DEBUG:
                service = ChromeService(config)
            elif config.service_type == ServiceType.TUNNELING:
                service = TunnelingService(config)
            else:
                continue
                
            self.services[config.name] = service
        
        # Define startup order (respecting dependencies)
        self.startup_order = [
            "chrome_debug",    # Chrome needs to be available first
            "socketio",        # Core communication hub
            "mcp",            # MCP server depends on chrome being available
            "plasmo",         # Plasmo dev server
            "testing",        # Testing service
            "tunneling"       # Tunneling for external access
        ]
        
        # Shutdown order (reverse of startup)
        self.shutdown_order = list(reversed(self.startup_order))
    
    def print_status(self, message: str, status_type: str = "info"):
        """Print colored status message"""
        colors = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "header": Fore.MAGENTA
        }
        color = colors.get(status_type, "")
        print(f"{color}{message}{Style.RESET_ALL}")
    
    async def start_service(self, service_name: str) -> bool:
        """Start a specific service"""
        if service_name not in self.services:
            self.logger.error(f"Service {service_name} not found")
            return False
        
        service = self.services[service_name]
        self.print_status(f"🚀 Starting {service_name}...")
        
        success = await service.start()
        if success:
            self.print_status(f"✅ Service '{service_name}' started successfully", "success")
        else:
            self.print_status(f"❌ Service '{service_name}' failed to start", "error")
        
        return success
    
    async def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        if service_name not in self.services:
            self.logger.error(f"Service {service_name} not found")
            return False
        
        service = self.services[service_name]
        self.print_status(f"🛑 Stopping {service_name}...")
        
        success = await service.stop()
        if success:
            self.print_status(f"✅ Service '{service_name}' stopped successfully", "success")
        else:
            self.print_status(f"❌ Service '{service_name}' failed to stop", "error")
        
        return success
    
    async def start_all(self) -> bool:
        """Start all services in proper order"""
        self.print_status("🚀 Starting all services in orchestrated order...", "header")
        self.running = True
        
        started_services = 0
        total_services = len(self.startup_order)
        
        for service_name in self.startup_order:
            if not self.running:  # Check if shutdown was requested
                break
                
            success = await self.start_service(service_name)
            if success:
                started_services += 1
            else:
                self.print_status(f"⚠️  Continuing with remaining services...", "warning")
        
        # Summary
        if started_services == total_services:
            self.print_status(f"🎉 All {total_services} services started successfully!", "success")
        else:
            self.print_status(f"⚠️  {started_services}/{total_services} services started", "warning")
        
        return started_services > 0
    
    async def stop_all(self) -> bool:
        """Stop all services in proper order"""
        self.print_status("🛑 Stopping all services...", "header")
        self.running = False
        
        stopped_services = 0
        
        for service_name in self.shutdown_order:
            if service_name in self.services:
                success = await self.stop_service(service_name)
                if success:
                    stopped_services += 1
        
        self.print_status(f"✅ Stopped {stopped_services} services", "success")
        return True
    
    async def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        if service_name not in self.services:
            self.logger.error(f"Service {service_name} not found")
            return False
        
        service = self.services[service_name]
        self.print_status(f"🔄 Restarting {service_name}...")
        
        return await service.restart()
    
    def get_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        status = {}
        for name, service in self.services.items():
            status[name] = service.get_status()
        return status
    
    def print_service_status(self):
        """Print formatted service status"""
        self.print_status("=== Service Status ===", "header")
        
        for name, service in self.services.items():
            status = service.get_status()
            status_icon = "✅" if status["status"] == "running" else "❌"
            port_info = f"Port {status['port']}" if status['port'] else "No port"
            pid_info = f"PID {status['pid']}" if status['pid'] else "Not running"
            
            self.print_status(f"{status_icon} {name.upper()}: {port_info} - {pid_info}")
    
    async def health_monitor(self):
        """Continuous health monitoring of all services"""
        while self.running:
            for name, service in self.services.items():
                try:
                    await service.health_check()
                except Exception as e:
                    self.logger.error(f"Health check failed for {name}: {e}")
            
            await asyncio.sleep(30)  # Check every 30 seconds


@click.group()
def cli():
    """Unified Service Management System"""
    pass

@cli.command()
async def start():
    """Start all services"""
    orchestrator = ServiceOrchestrator()
    await orchestrator.start_all()
    
    # Keep running and monitor services
    try:
        await orchestrator.health_monitor()
    except KeyboardInterrupt:
        await orchestrator.stop_all()

@cli.command()
async def stop():
    """Stop all services"""
    orchestrator = ServiceOrchestrator()
    await orchestrator.stop_all()

@cli.command()
def status():
    """Show service status"""
    orchestrator = ServiceOrchestrator()
    orchestrator.print_service_status()

@cli.command()
@click.argument('service_name')
async def restart(service_name: str):
    """Restart a specific service"""
    orchestrator = ServiceOrchestrator()
    await orchestrator.restart_service(service_name)


def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        # Default to start command
        asyncio.run(cli.main(['start']))
    else:
        cli()


if __name__ == "__main__":
    main() 