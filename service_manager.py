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
import platform
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
    CHROME_DEBUG = "chrome_debug"

class ImplementationType(Enum):
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    CHROME = "chrome"

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
        self.platform = platform.system().lower()
        
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
        
    def get_chrome_executables(self) -> List[str]:
        """Get list of possible Chrome executable paths for current platform"""
        if self.platform == "darwin":  # macOS
            return [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        elif self.platform == "linux":
            return [
                "google-chrome",
                "google-chrome-stable", 
                "chromium-browser",
                "chromium"
            ]
        elif self.platform == "windows":
            return [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "chrome.exe"
            ]
        else:
            return ["chrome", "chromium"]
            
    def find_chrome_executable(self) -> Optional[str]:
        """Find the Chrome executable on the system"""
        executables = self.get_chrome_executables()
        
        for exe in executables:
            # Check if it's an absolute path and exists
            if os.path.isabs(exe) and os.path.isfile(exe) and os.access(exe, os.X_OK):
                return exe
            # Check if it's in PATH
            elif subprocess.run(["which", exe], capture_output=True, text=True).returncode == 0:
                result = subprocess.run(["which", exe], capture_output=True, text=True)
                return result.stdout.strip()
                
        return None
        
    def get_chrome_debug_args(self, debug_port: int = 9222) -> List[str]:
        """Get Chrome launch arguments for debug mode"""
        profile_dir = self.base_dir / "chrome-debug-profile"
        profile_dir.mkdir(exist_ok=True)
        
        return [
            f"--remote-debugging-port={debug_port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check", 
            "--disable-features=VizDisplayCompositor",
            f"--user-data-dir={profile_dir}",
            "--new-window"
        ]
        
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
            command=[sys.executable, "packages/mcp-server/mcp_server.py", "--host", "127.0.0.1", "--port", "8000"],
            port=8000,
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
            command=[sys.executable, "dashboard_stunning.py"],
            port=8080,
            log_file="dashboard.log",
            env_vars={"PYTHONPATH": str(self.base_dir)}
        )
        
        # MCP Dashboard Configuration
        mcp_dashboard_config = ServiceConfig(
            name="mcp_dashboard",
            service_type=ServiceType.DASHBOARD,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "mcp_dashboard.py"],
            port=8081,
            log_file="mcp_dashboard.log",
            env_vars={"PYTHONPATH": str(self.base_dir)}
        )
        
        # Chrome Debug Configuration
        chrome_executable = self.find_chrome_executable()
        if chrome_executable:
            chrome_config = ServiceConfig(
                name="chrome_debug",
                service_type=ServiceType.CHROME_DEBUG,
                implementation=ImplementationType.CHROME,
                command=[chrome_executable] + self.get_chrome_debug_args(),
                port=9222,
                log_file="chrome_debug.log",
                auto_restart=True
            )
        else:
            # Create a placeholder config that will show Chrome as unavailable
            chrome_config = ServiceConfig(
                name="chrome_debug",
                service_type=ServiceType.CHROME_DEBUG,
                implementation=ImplementationType.CHROME,
                command=["chrome-not-found"],
                port=9222,
                log_file="chrome_debug.log",
                auto_restart=True
            )
        
        self.service_configs = {
            "socketio": socketio_config,
            "mcp": mcp_config,
            "plasmo": plasmo_config,
            "tests": tests_config,
            "dashboard": dashboard_config,
            "mcp_dashboard": mcp_dashboard_config,
            "chrome_debug": chrome_config
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
                    if ("dashboard_server.py" in cmdline_str or 
                        "dashboard_fasthtml.py" in cmdline_str or
                        "dashboard_stunning.py" in cmdline_str):
                        return True, proc.info['pid']
                elif service_name == "mcp_dashboard":
                    if "mcp_dashboard.py" in cmdline_str:
                        return True, proc.info['pid']
                elif service_name == "chrome_debug":
                    if ("chrome-debug-profile" in cmdline_str and 
                        "remote-debugging-port" in cmdline_str):
                        return True, proc.info['pid']
                        
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
                
        return False, None
        
    async def wait_for_service_ready(self, service_name: str, config: ServiceConfig, proc: subprocess.Popen, timeout: int = 30) -> bool:
        """Wait for a service to signal it's ready"""
        
        # For Chrome Debug, check if debug port is accessible
        if config.service_type == ServiceType.CHROME_DEBUG:
            debug_url = f"http://localhost:{config.port}/json"
            
            for attempt in range(timeout):
                if proc.poll() is not None:  # Process died
                    return False
                    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(debug_url, timeout=2) as response:
                            if response.status == 200:
                                data = await response.json()
                                if isinstance(data, list):  # Chrome returns list of tabs
                                    return True
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    pass
                    
                await asyncio.sleep(1)
            return False
        
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
            
        # Special handling for Chrome Debug
        if service_name == "chrome_debug":
            if config.command[0] == "chrome-not-found":
                self.print_status("❌ Chrome executable not found! Please install Chrome.", "error")
                return False
                
            # Kill any existing Chrome debug instances
            self._kill_existing_chrome_debug()
            
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
            if service_name == "chrome_debug":
                # Chrome needs special handling for background execution
                if self.platform == "windows":
                    proc = subprocess.Popen(
                        config.command,
                        stdout=log_file,
                        stderr=log_file,
                        env=env,
                        cwd=config.working_dir or self.base_dir,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    proc = subprocess.Popen(
                        config.command,
                        stdout=log_file,
                        stderr=log_file,
                        env=env,
                        cwd=config.working_dir or self.base_dir
                    )
            else:
                proc = subprocess.Popen(
                    config.command,
                    stdout=log_file,
                    stderr=log_file,
                    env=env,
                    cwd=config.working_dir or self.base_dir
                )
                
            # Track the process
            self.running_processes[service_name] = proc
            
            # Wait for service to be ready
            self.print_status(f"⏳ Waiting for {service_name} to be ready...")
            ready = await self.wait_for_service_ready(service_name, config, proc)
            
            if ready:
                self.print_status(f"✅ Service '{service_name}' started and ready (PID: {proc.pid})", "success")
                if service_name == "chrome_debug":
                    self.print_status(f"🌐 Chrome Debug URL: http://localhost:{config.port}")
                return True
            else:
                self.print_status(f"❌ Service '{service_name}' failed to become ready", "error")
                proc.terminate()
                if service_name in self.running_processes:
                    del self.running_processes[service_name]
                return False
                
        except Exception as e:
            self.print_status(f"❌ Failed to start {service_name}: {e}", "error")
            return False
        finally:
            if log_file:
                log_file.close()
                
    def _kill_existing_chrome_debug(self):
        """Kill any existing Chrome instances using the debug profile"""
        try:
            if self.platform in ["darwin", "linux"]:
                subprocess.run(["pkill", "-f", "chrome-debug-profile"], 
                             capture_output=True, check=False)
            elif self.platform == "windows":
                subprocess.run(["taskkill", "/F", "/FI", "WINDOWTITLE eq chrome-debug-profile*"], 
                             capture_output=True, check=False)
            time.sleep(1)  # Give processes time to terminate
        except Exception as e:
            logger.warning(f"Could not kill existing Chrome processes: {e}")

    async def start_all_services_async(self) -> Dict[str, bool]:
        """Start all services in parallel with ready detection"""
        self.print_status("🚀 Starting all services in parallel...", "header")
        
        results = {}
        tasks = []
        
        for service_name in self.service_configs.keys():
            task = asyncio.create_task(self.start_service_async(service_name))
            tasks.append((service_name, task))
            
        # Wait for all services to start
        for service_name, task in tasks:
            try:
                results[service_name] = await task
            except Exception as e:
                self.print_status(f"❌ Error starting {service_name}: {e}", "error")
                results[service_name] = False
                
        # Print summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        if successful == total:
            self.print_status(f"✅ All {total} services started successfully!", "success")
        else:
            failed = total - successful
            self.print_status(f"⚠️  {successful}/{total} services started ({failed} failed)", "warning")
            
        return results

    def stop_service(self, service_name: str) -> bool:
        """Stop a specific service"""
        config = self.service_configs.get(service_name)
        if not config:
            self.print_status(f"❌ Unknown service: {service_name}", "error")
            return False
            
        is_running, pid = self.is_service_running(service_name)
        if not is_running:
            self.print_status(f"⚠️  Service '{service_name}' is not running", "warning")
            return True
            
        self.print_status(f"🛑 Stopping {service_name}...")
        
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
                    proc.wait()
                    
                del self.running_processes[service_name]
                
            # Also kill any system processes
            if pid:
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()
                        
                except psutil.NoSuchProcess:
                    pass  # Process already dead
                    
            # Special handling for Chrome Debug
            if service_name == "chrome_debug":
                self._kill_existing_chrome_debug()
                
            self.print_status(f"✅ Service '{service_name}' stopped", "success")
            return True
            
        except Exception as e:
            self.print_status(f"❌ Error stopping {service_name}: {e}", "error")
            return False

    def restart_service(self, service_name: str) -> bool:
        """Restart a specific service"""
        self.print_status(f"🔄 Restarting {service_name}...")
        self.stop_service(service_name)
        time.sleep(2)  # Brief pause between stop and start
        return self.start_service(service_name)

    def get_service_status(self) -> Dict[str, dict]:
        """Get status of all services"""
        status = {}
        
        for service_name, config in self.service_configs.items():
            is_running, pid = self.is_service_running(service_name)
            
            status[service_name] = {
                'running': is_running,
                'pid': pid,
                'port': config.port,
                'implementation': config.implementation.value,
                'auto_restart': config.auto_restart
            }
            
        return status

    def print_service_status(self):
        """Print formatted service status"""
        self.print_status("=== Service Status ===", "header")
        
        status = self.get_service_status()
        
        for service_name, info in status.items():
            status_icon = "✅" if info['running'] else "❌"
            service_display = service_name.upper().replace('_', ' ')
            
            status_line = f"{status_icon} {service_display}: ({info['implementation']})"
            
            if info['port']:
                status_line += f" - Port {info['port']}"
                
            if info['running'] and info['pid']:
                status_line += f" - PID {info['pid']}"
                
            self.print_status(status_line)

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
    success = manager.start_service(service_name)
    sys.exit(0 if success else 1)

@cli.command()
@click.argument('service_name')  
@click.pass_context
def stop(ctx, service_name):
    """Stop a service"""
    manager = ctx.obj['manager']
    success = manager.stop_service(service_name)
    sys.exit(0 if success else 1)

@cli.command()
@click.argument('service_name')
@click.pass_context  
def restart(ctx, service_name):
    """Restart a service"""
    manager = ctx.obj['manager']
    success = manager.restart_service(service_name)
    sys.exit(0 if success else 1)

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
        failed = sum(1 for success in results.values() if not success)
        return failed == 0
    
    success = asyncio.run(run_parallel_start())
    sys.exit(0 if success else 1)

@cli.command()
@click.pass_context
def stop_all(ctx):
    """Stop all services"""
    manager = ctx.obj['manager']
    
    manager.print_status("🛑 Stopping all services...", "header")
    
    results = {}
    for service_name in manager.service_configs.keys():
        results[service_name] = manager.stop_service(service_name)
        
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    if successful == total:
        manager.print_status(f"✅ All {total} services stopped successfully!", "success")
    else:
        failed = total - successful
        manager.print_status(f"⚠️  {successful}/{total} services stopped ({failed} failed)", "warning")

if __name__ == "__main__":
    cli() 