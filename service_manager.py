import os
import sys
import time
import signal
import subprocess
import psutil
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import click
from colorama import Fore, Style, init
from dotenv import load_dotenv

# Initialize colorama for Windows compatibility
init()

# Load environment variables
load_dotenv(Path.cwd() / "environment.env", override=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/service_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    SOCKETIO = "socketio"
    MCP_SERVER = "mcp_server"  
    PLASMO_DEV = "plasmo_dev"
    CONTINUOUS_TESTS = "continuous_tests"
    DASHBOARD = "dashboard"

class ImplementationType(Enum):
    JAVASCRIPT = "javascript"
    PYTHON = "python"

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    service_type: ServiceType
    implementation: ImplementationType
    command: List[str]
    working_dir: Optional[str] = None
    port: Optional[int] = None
    log_file: Optional[str] = None
    auto_restart: bool = True
    env_vars: Optional[Dict[str, str]] = None

class ServiceManager:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.logs_dir = self.base_dir / "logs"
        self.running_processes: Dict[str, subprocess.Popen] = {}
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging and load configurations
        self.setup_logging()
        self.load_service_configs()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / "service_manager.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
    def load_service_configs(self):
        """Load service configurations based on environment"""
        socketio_implementation = os.getenv('SOCKETIO_IMPLEMENTATION', 'python').lower()
        
        # Socket.IO Server Configuration
        if socketio_implementation == 'python':
            socketio_config = ServiceConfig(
                name="socketio",
                service_type=ServiceType.SOCKETIO,
                implementation=ImplementationType.PYTHON,
                command=[sys.executable, "socketio_server_python.py"],
                port=3001,
                log_file="socketio_python.log"
            )
        else:
            socketio_config = ServiceConfig(
                name="socketio",
                service_type=ServiceType.SOCKETIO,
                implementation=ImplementationType.JAVASCRIPT,
                command=["node", "socketio_server.js"],
                port=3001,
                log_file="socketio_js.log"
            )
        
        # MCP Server Configuration  
        mcp_config = ServiceConfig(
            name="mcp",
            service_type=ServiceType.MCP_SERVER,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "mcp_server.py"],
            log_file="mcp_server.log",
            env_vars={"PYTHONPATH": str(self.base_dir)}
        )
        
        # Plasmo Dev Server Configuration
        plasmo_config = ServiceConfig(
            name="plasmo",
            service_type=ServiceType.PLASMO_DEV,
            implementation=ImplementationType.JAVASCRIPT,  # Will stay JS for now
            command=["pnpm", "dev"],
            log_file="plasmo_dev.log"
        )
        
        # Continuous Test Runner Configuration
        tests_config = ServiceConfig(
            name="continuous_tests",
            service_type=ServiceType.CONTINUOUS_TESTS,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "continuous_test_runner.py"],
            port=8082,
            log_file="continuous_tests.log",
            env_vars={"PYTHONPATH": str(self.base_dir)}
        )
        
        # Dashboard Server Configuration
        dashboard_config = ServiceConfig(
            name="dashboard",
            service_type=ServiceType.DASHBOARD,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "dashboard_server.py"],
            port=8080,
            log_file="dashboard.log",
            env_vars={"PYTHONPATH": str(self.base_dir)}
        )
        
        self.service_configs = {
            "socketio": socketio_config,
            "mcp": mcp_config,
            "plasmo": plasmo_config,
            "tests": tests_config,
            "dashboard": dashboard_config
        }
        
    def print_status(self, message: str, status_type: str = "info"):
        """Print colored status message"""
        color = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "header": Fore.MAGENTA
        }.get(status_type, Fore.WHITE)
        
        print(f"{color}{message}{Style.RESET_ALL}")
        
    def is_service_running(self, service_name: str) -> Tuple[bool, Optional[int]]:
        """Check if a service is running and return PID if found"""
        config = self.service_configs.get(service_name)
        if not config:
            return False, None
            
        # Check our tracked processes first
        if service_name in self.running_processes:
            proc = self.running_processes[service_name]
            if proc.poll() is None:  # Still running
                return True, proc.pid
            else:
                # Process died, remove from tracking
                del self.running_processes[service_name]
                
        # Check system processes for the service
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if not cmdline:
                    continue
                    
                # Check for service-specific patterns
                cmdline_str = ' '.join(cmdline)
                
                if service_name == "socketio":
                    if ("socketio_server.js" in cmdline_str or 
                        "socketio_server_python.py" in cmdline_str):
                        return True, proc.info['pid']
                elif service_name == "mcp":
                    if "mcp_server.py" in cmdline_str:
                        return True, proc.info['pid']
                elif service_name == "plasmo":
                    if "plasmo dev" in cmdline_str or "pnpm dev" in cmdline_str:
                        return True, proc.info['pid']
                elif service_name == "tests":
                    if "continuous_test_runner.py" in cmdline_str:
                        return True, proc.info['pid']
                elif service_name == "dashboard":
                    if "dashboard_server.py" in cmdline_str:
                        return True, proc.info['pid']
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return False, None
        
    async def wait_for_service_ready(self, service_name: str, config: ServiceConfig, proc: subprocess.Popen, timeout: int = 30) -> bool:
        """Wait for a service to signal it's ready"""
        
        # For external services (like Plasmo), just wait a bit and check if process is still running
        if config.service_type == ServiceType.PLASMO_DEV:
            await asyncio.sleep(3)  # Give external services time to start
            return proc.poll() is None
            
        # For our Python services, wait for health endpoint
        if config.port:
            health_url = f"http://localhost:{config.port}/health"
            
            for attempt in range(timeout):
                if proc.poll() is not None:  # Process died
                    return False
                    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_url, timeout=1) as response:
                            if response.status == 200:
                                data = await response.json()
                                if data.get('status') == 'healthy':
                                    return True
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    pass
                    
                await asyncio.sleep(1)
                
        # Fallback: just check if process is running after a short wait
        await asyncio.sleep(2)
        return proc.poll() is None

    def start_service(self, service_name: str) -> bool:
        """Start a service with ready signaling"""
        return asyncio.run(self.start_service_async(service_name))
    
    async def start_service_async(self, service_name: str) -> bool:
        """Start a service asynchronously with ready signaling"""
        config = self.service_configs.get(service_name)
        if not config:
            self.print_status(f"❌ Unknown service: {service_name}", "error")
            return False
            
        # Check if already running
        is_running, pid = self.is_service_running(service_name)
        if is_running:
            self.print_status(f"✅ Service '{service_name}' already running (PID: {pid})", "warning")
            return True
            
        self.print_status(f"🚀 Starting {service_name} ({config.implementation.value})...", "info")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if config.env_vars:
                env.update(config.env_vars)
                
            # Prepare log file
            log_file = None
            if config.log_file:
                log_path = self.logs_dir / config.log_file
                log_file = open(log_path, 'a')
                
            # Start the process
            working_dir = config.working_dir or self.base_dir
            
            proc = subprocess.Popen(
                config.command,
                cwd=working_dir,
                env=env,
                stdout=log_file,
                stderr=subprocess.STDOUT if log_file else None,
                preexec_fn=None if sys.platform == "win32" else os.setsid
            )
            
            self.running_processes[service_name] = proc
            
            # Wait for service to be ready (with smart timeout)
            self.print_status(f"⏳ Waiting for {service_name} to be ready...", "info")
            
            is_ready = await self.wait_for_service_ready(service_name, config, proc)
            
            if is_ready:
                self.print_status(f"✅ Service '{service_name}' started and ready (PID: {proc.pid})", "success")
                return True
            else:
                self.print_status(f"❌ Service '{service_name}' failed to become ready", "error")
                return False
                
        except Exception as e:
            self.print_status(f"❌ Failed to start '{service_name}': {e}", "error")
            return False
            
    async def start_all_services_async(self) -> Dict[str, bool]:
        """Start all services in parallel with smart ready detection"""
        services = ["mcp", "socketio", "dashboard", "plasmo", "tests"]
        
        self.print_status("🚀 Starting all services in parallel...", "header")
        
        # Start all services concurrently
        tasks = []
        for service in services:
            task = asyncio.create_task(self.start_service_async(service))
            tasks.append((service, task))
            
        # Wait for all to complete
        results = {}
        for service, task in tasks:
            try:
                results[service] = await task
            except Exception as e:
                self.print_status(f"❌ Error starting {service}: {e}", "error")
                results[service] = False
                
        return results
            
    def stop_service(self, service_name: str) -> bool:
        """Stop a service"""
        self.print_status(f"🛑 Stopping {service_name}...", "info")
        
        is_running, pid = self.is_service_running(service_name)
        if not is_running:
            self.print_status(f"✅ Service '{service_name}' is not running", "warning")
            return True
            
        try:
            # Try to stop our tracked process first
            if service_name in self.running_processes:
                proc = self.running_processes[service_name]
                proc.terminate()
                
                # Wait for graceful shutdown
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    
                del self.running_processes[service_name]
                
            # Kill any remaining processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if not cmdline:
                        continue
                        
                    cmdline_str = ' '.join(cmdline)
                    should_kill = False
                    
                    if service_name == "socketio":
                        should_kill = ("socketio_server.js" in cmdline_str or 
                                     "socketio_server_python.py" in cmdline_str)
                    elif service_name == "mcp":
                        should_kill = "mcp_server.py" in cmdline_str
                    elif service_name == "plasmo":
                        should_kill = "plasmo dev" in cmdline_str or "pnpm dev" in cmdline_str
                    elif service_name == "tests":
                        should_kill = "continuous_test_runner.py" in cmdline_str
                    elif service_name == "dashboard":
                        should_kill = "dashboard_server.py" in cmdline_str
                        
                    if should_kill:
                        process = psutil.Process(proc.info['pid'])
                        process.terminate()
                        time.sleep(1)
                        if process.is_running():
                            process.kill()
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            self.print_status(f"✅ Service '{service_name}' stopped", "success")
            return True
            
        except Exception as e:
            self.print_status(f"❌ Failed to stop '{service_name}': {e}", "error")
            return False
            
    def restart_service(self, service_name: str) -> bool:
        """Restart a service"""
        self.print_status(f"🔄 Restarting {service_name}...", "info")
        self.stop_service(service_name)
        time.sleep(2)
        return self.start_service(service_name)
        
    def get_service_status(self) -> Dict[str, dict]:
        """Get status of all services"""
        status = {}
        for service_name in self.service_configs:
            is_running, pid = self.is_service_running(service_name)
            config = self.service_configs[service_name]
            
            status[service_name] = {
                "running": is_running,
                "pid": pid,
                "implementation": config.implementation.value,
                "port": config.port,
                "command": ' '.join(config.command)
            }
            
        return status
        
    def print_service_status(self):
        """Print formatted service status"""
        self.print_status("=== Service Status ===", "header")
        status = self.get_service_status()
        
        for service_name, info in status.items():
            status_icon = "✅" if info["running"] else "❌"
            impl_info = f"({info['implementation']})"
            port_info = f" - Port {info['port']}" if info['port'] else ""
            pid_info = f" - PID {info['pid']}" if info['pid'] else ""
            
            self.print_status(f"{status_icon} {service_name.upper()}: {impl_info}{port_info}{pid_info}", 
                            "success" if info["running"] else "error")

# CLI Interface
@click.group()
@click.pass_context
def cli(ctx):
    """Cross-platform service manager for Plasmo extension"""
    ctx.ensure_object(dict)
    ctx.obj['manager'] = ServiceManager()

@cli.command()
@click.argument('service_name')
@click.pass_context
def start(ctx, service_name):
    """Start a service"""
    manager = ctx.obj['manager']
    manager.start_service(service_name)

@cli.command()
@click.argument('service_name')  
@click.pass_context
def stop(ctx, service_name):
    """Stop a service"""
    manager = ctx.obj['manager']
    manager.stop_service(service_name)

@cli.command()
@click.argument('service_name')
@click.pass_context  
def restart(ctx, service_name):
    """Restart a service"""
    manager = ctx.obj['manager']
    manager.restart_service(service_name)

@cli.command()
@click.pass_context
def status(ctx):
    """Show status of all services"""
    manager = ctx.obj['manager']
    manager.print_service_status()

@cli.command()
@click.pass_context
def start_all(ctx):
    """Start all services in parallel with ready detection"""
    manager = ctx.obj['manager']
    
    async def run_parallel_start():
        results = await manager.start_all_services_async()
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        if successful == total:
            manager.print_status(f"✅ All {total} services started successfully!", "success")
        else:
            manager.print_status(f"⚠️ {successful}/{total} services started successfully", "warning")
            
        return all(results.values())
    
    return asyncio.run(run_parallel_start())

@cli.command()
@click.pass_context
def stop_all(ctx):
    """Stop all services"""
    manager = ctx.obj['manager']
    services = ["tests", "plasmo", "socketio", "mcp"]
    
    for service in services:
        manager.stop_service(service)
        time.sleep(1)

if __name__ == "__main__":
    cli() 