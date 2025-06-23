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
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import click
from colorama import Fore, Style, init
from dotenv import load_dotenv
import threading
from concurrent.futures import ThreadPoolExecutor
import fnmatch

# File watching imports
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = None

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
    MCP_TESTING_PROXY = "mcp_testing_proxy"  
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
    # File watching configuration
    watch_patterns: List[str] = field(default_factory=list)  # Files/patterns to watch
    watch_dirs: List[str] = field(default_factory=list)      # Directories to watch
    ignore_patterns: List[str] = field(default_factory=list) # Patterns to ignore
    validation_command: Optional[List[str]] = None           # Command to validate before restart
    validation_port: Optional[int] = None                    # Alternative port for validation
    restart_delay: float = 2.0                               # Delay before restart (seconds)
    debounce_delay: float = 1.0                              # Delay to debounce multiple file changes

@dataclass 
class RestartManager:
    """Manages service restarts with proper async task tracking"""
    service_manager: 'ServiceManager'
    pending_restarts: Dict[str, asyncio.Task] = field(default_factory=dict)
    last_event_times: Dict[str, float] = field(default_factory=dict)
    
    async def schedule_restart(self, service_name: str, file_path: str):
        """Schedule a service restart using async tasks"""
        config = self.service_manager.service_configs.get(service_name)
        if not config:
            logger.error(f"❌ No config found for service: {service_name}")
            return
            
        current_time = time.time()
        
        # Debounce rapid file changes for this service
        if (service_name in self.last_event_times and 
            current_time - self.last_event_times[service_name] < config.debounce_delay):
            logger.debug(f"⏰ Debouncing {service_name} restart (too recent)")
            return
            
        self.last_event_times[service_name] = current_time
        logger.info(f"🎯 Scheduling restart: {Path(file_path).name} -> {service_name}")
        
        # Cancel existing restart task if any
        if service_name in self.pending_restarts:
            logger.debug(f"⏰ Cancelling previous restart task for {service_name}")
            self.pending_restarts[service_name].cancel()
            
        # Create new restart task (not daemon!)
        self.pending_restarts[service_name] = asyncio.create_task(
            self._execute_delayed_restart(service_name, file_path)
        )
    
    async def _execute_delayed_restart(self, service_name: str, file_path: str):
        """Execute restart after delay with proper error handling"""
        config = self.service_manager.service_configs.get(service_name)
        if not config:
            return
            
        try:
            # Wait for restart delay
            await asyncio.sleep(config.restart_delay)
            
            # Perform restart with validation
            logger.info(f"🔄 Starting validated restart of {service_name}")
            result = await self.service_manager.restart_service_with_validation(service_name)
            logger.info(f"✅ Restart completed for {service_name} (result: {result})")
            
        except asyncio.CancelledError:
            logger.info(f"🛑 Restart cancelled for {service_name}")
            raise
        except Exception as e:
            logger.error(f"❌ Restart failed for {service_name}: {e}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
        finally:
            # Clean up task reference
            if service_name in self.pending_restarts:
                del self.pending_restarts[service_name]
                logger.debug(f"🧹 Cleaned up restart task for {service_name}")
    
    async def cleanup_all_tasks(self):
        """Cancel all pending restart tasks"""
        logger.info(f"🧹 Cancelling {len(self.pending_restarts)} pending restart tasks...")
        
        for service_name, task in self.pending_restarts.items():
            logger.debug(f"🛑 Cancelling restart task for {service_name}")
            task.cancel()
        
        # Wait for all cancellations to complete
        if self.pending_restarts:
            await asyncio.gather(*self.pending_restarts.values(), return_exceptions=True)
        
        self.pending_restarts.clear()
        logger.info("✅ All restart tasks cancelled")

class AdvancedFileFilter:
    """Advanced file filtering with comprehensive ignore patterns"""
    
    def __init__(self):
        self.global_ignore_patterns = [
            # Chrome debug profile files
            "chrome-debug-profile/**",
            "**/chrome-debug-profile/**",
            "**/Policy/**",
            "**/GCM Store/**", 
            "**/.com.google.Chrome.*",
            "**/BrowserMetrics/**",
            "**/SingletonLock",
            "**/SingletonSocket", 
            "**/SingletonCookie",
            "**/Variations",
            "**/Last Version",
            "**/RunningChromeVersion",
            "**/ChromeFeatureState",
            "**/ukm_db-wal",
            "**/System Profile/**",
            "**/segmentation_platform/**",
            
            # Build and cache directories
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/.git/**",
            "**/.plasmo/**",
            "**/build/**",
            "**/dist/**",
            "**/logs/**",
            
            # Temporary files
            "**/*.log",
            "**/*.pyc",
            "**/*.pyo",
            "**/.DS_Store",
            "**/Thumbs.db",
            "**/*.tmp",
            "**/*.backup.*",
            "**/*~",
            
            # IDE files
            "**/.vscode/**",
            "**/.idea/**",
            "**/*.swp",
            "**/*.swo"
        ]
    
    def should_ignore_file(self, file_path: str) -> bool:
        """Check if file should be ignored using enhanced patterns"""
        file_path = Path(file_path)
        
        try:
            # Check against each ignore pattern using pathlib matching
            for pattern in self.global_ignore_patterns:
                if file_path.match(pattern):
                    return True
                    
            # Check if any parent directory matches common ignore patterns
            for parent in file_path.parents:
                parent_name = parent.name
                if parent_name in ['chrome-debug-profile', '__pycache__', 'node_modules', '.git', '.plasmo', 'logs']:
                    return True
                    
        except Exception as e:
            logger.debug(f"Error checking ignore pattern for {file_path}: {e}")
            
        return False

# File watching setup - only if watchdog is available
if WATCHDOG_AVAILABLE:
    class SharedFileChangeHandler(FileSystemEventHandler):
        """Shared file change handler for all services"""
        
        def __init__(self, service_manager):
            self.service_manager = service_manager
            self.restart_manager = RestartManager(service_manager)
            self.file_filter = AdvancedFileFilter()
            self.last_event_times: Dict[str, float] = {}
            
        def should_restart_service(self, service_name: str, event_path: str) -> bool:
            """Enhanced service restart decision logic"""
            config = self.service_manager.service_configs.get(service_name)
            if not config or not config.watch_patterns:
                return False
            
            # Global ignore check first
            if self.file_filter.should_ignore_file(event_path):
                return False
            
            # Service-specific ignore patterns
            for ignore_pattern in config.ignore_patterns:
                if fnmatch.fnmatch(event_path, ignore_pattern) or fnmatch.fnmatch(Path(event_path).name, ignore_pattern):
                    return False
            
            # Check if file matches any watch patterns
            event_file = Path(event_path)
            
            for pattern in config.watch_patterns:
                # Handle simple filename matching
                if event_file.name == pattern:
                    return True
                
                # Handle pattern matching 
                if fnmatch.fnmatch(str(event_file), pattern) or fnmatch.fnmatch(event_file.name, pattern):
                    return True
                
                # Handle full path pattern matching
                if fnmatch.fnmatch(event_path, f"*{pattern}*") or fnmatch.fnmatch(event_path, f"*/{pattern}"):
                    return True
            
            return False

        def on_modified(self, event):
            """Handle file modification events"""
            if event.is_directory:
                return
                
            logger.debug(f"📝 File changed: {event.src_path}")
            
            # Check which services should be restarted
            services_to_restart = []
            for service_name in self.service_manager.watched_services:
                if self.should_restart_service(service_name, event.src_path):
                    services_to_restart.append(service_name)
                    logger.info(f"✅ Match found: {Path(event.src_path).name} matches {event.src_path} for {service_name}")
            
            if services_to_restart:
                logger.info(f"🔄 Services to restart: {services_to_restart}")
                
                # Schedule restart for each affected service using async tasks
                for service_name in services_to_restart:
                    # Use asyncio to schedule the restart properly
                    try:
                        # Try to get the current event loop
                        loop = asyncio.get_running_loop()
                        # Schedule the restart task in the current loop
                        loop.create_task(self.restart_manager.schedule_restart(service_name, event.src_path))
                    except RuntimeError:
                        # No running loop - this shouldn't happen in our new architecture
                        # but we'll handle it gracefully by running in a new event loop
                        logger.warning(f"⚠️ No running event loop, creating new loop for {service_name} restart")
                        import threading
                        def run_restart():
                            try:
                                asyncio.run(self.restart_manager.schedule_restart(service_name, event.src_path))
                            except Exception as e:
                                logger.error(f"❌ Failed to run restart for {service_name}: {e}")
                        # Use a regular thread (not daemon) for better cleanup
                        thread = threading.Thread(target=run_restart)
                        thread.start()

    # Legacy FileChangeHandler for compatibility
    class FileChangeHandler:
        def __init__(self, service_manager, service_name: str):
            pass
else:
    # Dummy handlers when watchdog is not available
    class SharedFileChangeHandler:
        def __init__(self, service_manager):
            pass
            
    class FileChangeHandler:
        def __init__(self, service_manager, service_name: str):
            pass

class ServiceManager:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd()
        self.logs_dir = self.base_dir / "logs"
        self.running_processes: Dict[str, subprocess.Popen] = {}
        self.platform = platform.system().lower()
        
        # New async-based file watching components
        self.master_observer: Optional[Observer] = None
        self.master_handler: Optional['SharedFileChangeHandler'] = None
        self.watched_services: Set[str] = set()
        self.restart_manager: Optional[RestartManager] = None
        self.shutdown_event: Optional[asyncio.Event] = None
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging and load configurations
        self.setup_logging()
        self.load_service_configs()
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = self.logs_dir / "service_manager.log"
        logging.basicConfig(
            level=logging.INFO,  # Back to normal logging level
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
                working_dir="packages/socketio-server",
                port=3001,
                log_file="socketio_python.log",
                # File watching configuration
                watch_patterns=["socketio_server_python.py", "cursor_ai_injector.py"],
                watch_dirs=["packages/socketio-server"],
                ignore_patterns=["*.log", "__pycache__/*", "node_modules/*"],
                validation_command=[sys.executable, "-m", "py_compile", "socketio_server_python.py"],
                validation_port=3002,
                restart_delay=3.0,
                debounce_delay=2.0
            )
        else:
            socketio_config = ServiceConfig(
                name="socketio",
                service_type=ServiceType.SOCKETIO,
                implementation=ImplementationType.JAVASCRIPT,
                command=["node", "socketio_server.js"],
                working_dir="packages/socketio-server",
                port=3001,
                log_file="socketio_js.log",
                # File watching configuration
                watch_patterns=["socketio_server.js", "package.json"],
                watch_dirs=["packages/socketio-server"],
                ignore_patterns=["*.log", "node_modules/*"],
                validation_command=["node", "--check", "socketio_server.js"],
                validation_port=3002,
                restart_delay=2.0,
                debounce_delay=1.0
            )
        
        # MCP Server Configuration  
        mcp_config = ServiceConfig(
            name="mcp",
            service_type=ServiceType.MCP_SERVER,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "packages/mcp-server/mcp_server.py", "--host", "127.0.0.1", "--port", "8000"],
            port=8000,
            log_file="mcp_server.log",
            env_vars={"PYTHONPATH": str(self.base_dir)},
            # File watching configuration - specific to MCP server
            watch_patterns=["packages/mcp-server/mcp_server.py", "packages/mcp-server/requirements.txt"],
            watch_dirs=[],  # Don't watch whole directories to avoid conflicts
            ignore_patterns=[
                "*.log", "__pycache__/*", "*.pyc", 
                "chrome-debug-profile/*", "chrome-debug-profile/**/*",
                "node_modules/*", ".git/*", ".DS_Store",
                "build/*", "dist/*", ".plasmo/*",
                "logs/*", "*.backup.*"
            ],
            validation_command=[sys.executable, "-m", "py_compile", "packages/mcp-server/mcp_server.py"],
            validation_port=8002,  # Changed from 8001 to avoid conflict with proxy
            restart_delay=4.0,
            debounce_delay=2.0
        )
        
        # MCP Testing Proxy Configuration
        mcp_proxy_config = ServiceConfig(
            name="mcp_proxy",
            service_type=ServiceType.MCP_TESTING_PROXY,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "mcp_testing_proxy.py", "--host", "127.0.0.1", "--port", "8001"],
            working_dir="packages/mcp-server",
            port=8001,
            log_file="mcp_testing_proxy.log",
            env_vars={"PYTHONPATH": str(self.base_dir)},
            # File watching configuration - specific to proxy files only
            watch_patterns=["packages/mcp-server/mcp_testing_proxy.py"],
            watch_dirs=[],  # Don't watch whole directories to avoid conflicts
            ignore_patterns=["*.log", "__pycache__/*", "*.pyc", "chrome-debug-profile/*"],
            validation_command=[sys.executable, "-m", "py_compile", "packages/mcp-server/mcp_testing_proxy.py"],
            validation_port=8003,
            restart_delay=3.0,
            debounce_delay=2.0
        )
        
        # Plasmo Dev Server Configuration
        plasmo_config = ServiceConfig(
            name="plasmo",
            service_type=ServiceType.PLASMO_DEV,
            implementation=ImplementationType.JAVASCRIPT,  # Will stay JS for now
            command=["npm", "run", "dev"],
            working_dir="packages/chrome-extension",
            port=1012,  # Plasmo default dev port
            log_file="plasmo_dev.log",
            # File watching configuration (Plasmo has its own file watching)
            watch_patterns=["package.json", "tsconfig.json", "plasmo.config.ts"],
            watch_dirs=["contents", "popup.tsx", "background.ts"],
            ignore_patterns=["build/*", "dist/*", "node_modules/*", ".plasmo/*"],
            validation_command=["npm", "run", "build", "--", "--dry-run"],  # Build validation
            restart_delay=5.0,
            debounce_delay=3.0
        )
        
        # Continuous Test Runner Configuration
        tests_config = ServiceConfig(
            name="continuous_tests",
            service_type=ServiceType.CONTINUOUS_TESTS,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "tests/continuous_test_runner.py"],
            port=8082,
            log_file="continuous_tests.log",
            env_vars={"PYTHONPATH": str(self.base_dir)},
            # File watching configuration
            watch_patterns=["continuous_test_runner.py", "test_*.py"],
            watch_dirs=["tests"],
            ignore_patterns=["*.log", "__pycache__/*", "*.pyc"],
            validation_command=[sys.executable, "-m", "py_compile", "tests/continuous_test_runner.py"],
            validation_port=8083,
            restart_delay=3.0,
            debounce_delay=2.0
        )
        
        # Dashboard Server Configuration
        dashboard_config = ServiceConfig(
            name="dashboard",
            service_type=ServiceType.DASHBOARD,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "launch_dashboard.py"],
            working_dir="packages/dashboard-framework",
            port=8080,
            log_file="dashboard.log",
            env_vars={"PYTHONPATH": str(self.base_dir)},
            # File watching configuration - specific to main dashboard files
            watch_patterns=["packages/dashboard-framework/launch_dashboard.py", "packages/dashboard-framework/dashboard_*.py", "packages/dashboard-framework/requirements.txt"],
            watch_dirs=[],  # Don't watch whole directories to avoid conflicts
            ignore_patterns=["*.log", "__pycache__/*", "*.pyc"],
            validation_command=[sys.executable, "-m", "py_compile", "launch_dashboard.py"],
            validation_port=8090,
            restart_delay=3.0,
            debounce_delay=2.0
        )
        
        # MCP Dashboard Configuration
        mcp_dashboard_config = ServiceConfig(
            name="mcp_dashboard",
            service_type=ServiceType.DASHBOARD,
            implementation=ImplementationType.PYTHON,
            command=[sys.executable, "mcp_dashboard.py"],
            working_dir="packages/dashboard-framework",
            port=8081,
            log_file="mcp_dashboard.log",
            env_vars={"PYTHONPATH": str(self.base_dir)},
            # File watching configuration - specific to MCP dashboard only
            watch_patterns=["packages/dashboard-framework/mcp_dashboard.py"],
            watch_dirs=[],  # Don't watch whole directories to avoid conflicts
            ignore_patterns=["*.log", "__pycache__/*", "*.pyc"],
            validation_command=[sys.executable, "-m", "py_compile", "mcp_dashboard.py"],
            validation_port=8091,
            restart_delay=3.0,
            debounce_delay=2.0
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
                auto_restart=True,
                # Chrome doesn't need file watching as it auto-reloads extensions
                watch_patterns=[],
                watch_dirs=[],
                ignore_patterns=["chrome-debug-profile/*"],
                restart_delay=5.0,
                debounce_delay=3.0
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
            "mcp_proxy": mcp_proxy_config,
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
                        "dashboard_stunning.py" in cmdline_str or
                        "launch_dashboard.py" in cmdline_str):
                        return True, proc.info['pid']
                elif service_name == "mcp_dashboard":
                    if "mcp_dashboard.py" in cmdline_str:
                        return True, proc.info['pid']
                elif service_name == "mcp_proxy":
                    if "mcp_testing_proxy.py" in cmdline_str:
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
            
        # For MCP services, just check if process is running after a short wait
        if config.service_type in [ServiceType.MCP_SERVER, ServiceType.MCP_TESTING_PROXY]:
            await asyncio.sleep(2)  # Give MCP services time to start
            return proc.poll() is None
            
        # For our Python services, wait for health endpoint
        if config.port:
            # Dashboard service uses root endpoint, others use /health
            if config.service_type == ServiceType.DASHBOARD:
                health_url = f"http://localhost:{config.port}/"
            else:
                health_url = f"http://localhost:{config.port}/health"
            
            for attempt in range(timeout):
                if proc.poll() is not None:  # Process died
                    return False
                    
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_url, timeout=1) as response:
                            if response.status == 200:
                                # Dashboard returns HTML, other services return JSON
                                if config.service_type == ServiceType.DASHBOARD:
                                    return True  # Any 200 response is good for dashboard
                                else:
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
                    
                # Start file watching if configured and service started successfully
                if config.auto_restart and (config.watch_patterns or config.watch_dirs):
                    self.start_file_watching(service_name)
                    
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
        
        # Stop file watching first
        self.stop_file_watching(service_name)
        
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
            file_watching = service_name in self.watched_services
            
            status[service_name] = {
                'running': is_running,
                'pid': pid,
                'port': config.port,
                'implementation': config.implementation.value,
                'auto_restart': config.auto_restart,
                'file_watching': file_watching,
                'watch_patterns': config.watch_patterns,
                'validation_enabled': bool(config.validation_command)
            }
            
        return status
    
    def get_all_status(self) -> Dict[str, dict]:
        """Alias for get_service_status for dashboard compatibility"""
        return self.get_service_status()

    def print_service_status(self):
        """Print formatted service status"""
        self.print_status("=== Service Status ===", "header")
        
        status = self.get_service_status()
        
        for service_name, info in status.items():
            status_icon = "✅" if info['running'] else "❌"
            watch_icon = "👁️" if info['file_watching'] else "⚫"
            validation_icon = "🧪" if info['validation_enabled'] else "⚫"
            
            service_display = service_name.upper().replace('_', ' ')
            
            status_line = f"{status_icon} {service_display}: ({info['implementation']}) {watch_icon} {validation_icon}"
            
            if info['port']:
                status_line += f" - Port {info['port']}"
                
            if info['running'] and info['pid']:
                status_line += f" - PID {info['pid']}"
                
            self.print_status(status_line)
            
            # Show watch patterns if file watching is active
            if info['file_watching'] and info['watch_patterns']:
                self.print_status(f"   👁️  Watching: {', '.join(info['watch_patterns'])}", "info")

    async def validate_service_health(self, service_name: str) -> bool:
        """Validate service without alternate port testing"""
        config = self.service_configs.get(service_name)
        if not config:
            return True
            
        # Only do configuration validation (no port testing)
        if config.validation_command:
            return await self._validate_configuration(service_name)
        
        return True  # No validation required

    async def _validate_configuration(self, service_name: str) -> bool:
        """Validate service configuration files"""
        config = self.service_configs.get(service_name)
        if not config or not config.validation_command:
            return True
            
        self.print_status(f"🧪 Validating {service_name} configuration...", "info")
        
        try:
            # Prepare environment for validation
            env = os.environ.copy()
            if config.env_vars:
                env.update(config.env_vars)
                
            # Run validation command with timeout using async subprocess
            process = await asyncio.create_subprocess_exec(
                *config.validation_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=config.working_dir or self.base_dir,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0
            )
            
            if process.returncode == 0:
                self.print_status(f"✅ Configuration validation passed for {service_name}", "success")
                return True
            else:
                self.print_status(f"❌ Configuration validation failed for {service_name}", "error")
                self.print_status(f"   Error: {stderr.decode()}", "error")
                return False
                
        except asyncio.TimeoutError:
            self.print_status(f"⏰ Configuration validation timeout for {service_name}", "error")
            return False
        except Exception as e:
            self.print_status(f"❌ Configuration validation error for {service_name}: {e}", "error")
            return False

    def start_file_watching(self, service_name: str, force_enable: bool = False):
        """Start file watching for a service using shared watcher"""
        if not WATCHDOG_AVAILABLE:
            self.print_status("⚠️  Watchdog not available. Install with: pip install watchdog", "warning")
            return
            
        config = self.service_configs.get(service_name)
        if not config or not config.watch_patterns:
            return  # No file watching configured
        
        # Only enable file watching in persistent mode (start-all) or when forced
        if not force_enable and not getattr(self, '_persistent_mode', False):
            self.print_status(f"💡 File watching available for {service_name} (use 'start-all' for auto-restart)", "info")
            return
        
        # Initialize shared watcher if needed
        if self.master_observer is None:
            self._initialize_shared_watcher()
        
        # Add service to watched services
        self.watched_services.add(service_name)
        
        # Display watch info for this service
        self.print_status(f"👁️  Adding {service_name} to shared file watcher...", "info")
        if config.watch_patterns:
            self.print_status(f"   🎯 Files: {', '.join([Path(p).name for p in config.watch_patterns])}")
        if config.ignore_patterns:
            self.print_status(f"   🚫 Ignoring: {', '.join(config.ignore_patterns)}")
        
        self.print_status(f"✅ File watcher enabled for {service_name}", "success")
    
    def enable_persistent_mode(self):
        """Enable persistent mode for long-running processes with file watching"""
        self._persistent_mode = True
        self.print_status("🔄 Persistent mode enabled - file watching will be active", "info")
    
    def _initialize_shared_watcher(self) -> bool:
        """Initialize the shared file watcher system (legacy method for backward compatibility)"""
        if self.master_observer is not None:
            return True
            
        try:
            # Initialize restart manager if not already done
            if self.restart_manager is None:
                self.restart_manager = RestartManager(self)
            
            # Create shared handler and observer
            self.master_handler = SharedFileChangeHandler(self)
            # Set the restart manager in the handler
            self.master_handler.restart_manager = self.restart_manager
            
            self.master_observer = Observer()
            
            # Watch the entire project recursively
            self.master_observer.schedule(
                self.master_handler, 
                str(self.base_dir), 
                recursive=True
            )
            
            # Start the shared observer
            self.master_observer.start()
            
            self.print_status(f"🔍 Shared file watcher initialized", "success")
            self.print_status(f"   📁 Watching: {self.base_dir} (recursive)", "info")
            self.print_status(f"   🚫 Ignoring: chrome-debug-profile, node_modules, __pycache__, .git", "info")
            
            return True
            
        except Exception as e:
            self.print_status(f"❌ Failed to initialize shared file watcher: {e}", "error")
            return False
            
    def stop_file_watching(self, service_name: str):
        """Stop file watching for a service"""
        if service_name in self.watched_services:
            self.watched_services.remove(service_name)
            
            # Cancel any pending restarts for this service
            if (self.master_handler and 
                hasattr(self.master_handler, 'pending_restarts') and 
                service_name in self.master_handler.pending_restarts):
                self.master_handler.pending_restarts[service_name].cancel()
                del self.master_handler.pending_restarts[service_name]
            
            self.print_status(f"🛑 File watcher stopped for {service_name}")
            
            # If no more services are watching, stop the shared observer
            if not self.watched_services and self.master_observer:
                self.master_observer.stop()
                self.master_observer.join()
                self.master_observer = None
                self.master_handler = None
                self.print_status("🔍 Shared file watcher stopped (no services watching)")
        else:
            self.print_status(f"⚠️  {service_name} was not being watched")
        
    async def restart_service_with_validation(self, service_name: str) -> bool:
        """Restart service with simplified validation"""
        config = self.service_configs.get(service_name)
        if not config:
            self.print_status(f"❌ Unknown service: {service_name}", "error")
            return False
            
        self.print_status(f"🔄 Validating and restarting {service_name}...", "header")
        
        # Step 1: Configuration validation only (no port testing)
        if not await self.validate_service_health(service_name):
            self.print_status(f"❌ Validation failed for {service_name}", "error")
            return False
        
        # Step 2: Stop current service
        self.print_status(f"🛑 Stopping current {service_name} instance...")
        self.stop_service(service_name)
        
        # Step 3: Wait before restart
        await asyncio.sleep(config.restart_delay)
        
        # Step 4: Start service
        self.print_status(f"🚀 Starting validated {service_name}...")
        success = await self.start_service_async(service_name)
        
        if success:
            self.print_status(f"✅ {service_name} restarted successfully", "success")
        else:
            self.print_status(f"❌ Failed to restart {service_name}", "error")
        
        return success

    async def start_with_file_watching(self):
        """Start services with proper async file watching"""
        try:
            # Initialize shutdown event
            self.shutdown_event = asyncio.Event()
            
            # Start all services
            await self.start_all_services_async()
            
            # Initialize async file watching if any services need it
            services_with_watching = [
                name for name, config in self.service_configs.items()
                if config.watch_patterns and config.auto_restart
            ]
            
            if services_with_watching:
                self.print_status(f"🔄 File watching will be active for: {', '.join(services_with_watching)}", "info")
                
                # Only initialize if not already done
                if self.master_observer is None:
                    await self._initialize_async_file_watching()
                
                # Enable file watching for each service that supports it
                for service_name in services_with_watching:
                    if service_name in self.running_processes:  # Only if service is actually running
                        self.start_file_watching(service_name, force_enable=True)
                
                # Wait for shutdown signal
                self.print_status("🔄 File watching active. Services will auto-restart on changes. Press Ctrl+C to stop.", "info")
                self.print_status(f"👁️  Watching: {', '.join(sorted(self.watched_services))}", "info")
                self.print_status("💡 Use --daemon flag to run silently in background.", "info")
                
                await self.shutdown_event.wait()
            else:
                self.print_status("✅ All services started. No file watching configured.", "info")
                
        except KeyboardInterrupt:
            self.print_status("🛑 Received shutdown signal...", "info")
        finally:
            await self.graceful_shutdown()
    
    async def _initialize_async_file_watching(self):
        """Initialize file watching with async restart manager"""
        if not WATCHDOG_AVAILABLE:
            self.print_status("⚠️  Watchdog not available. Install with: pip install watchdog", "warning")
            return False
            
        try:
            # Initialize restart manager
            self.restart_manager = RestartManager(self)
            
            # Create shared handler and observer
            self.master_handler = SharedFileChangeHandler(self)
            # Update the handler to use our restart manager
            self.master_handler.restart_manager = self.restart_manager
            
            self.master_observer = Observer()
            
            # Watch the entire project recursively
            self.master_observer.schedule(
                self.master_handler, 
                str(self.base_dir), 
                recursive=True
            )
            
            # Start the shared observer
            self.master_observer.start()
            
            self.print_status(f"🔍 Shared file watcher initialized", "success")
            self.print_status(f"   📁 Watching: {self.base_dir} (recursive)", "info")
            self.print_status(f"   🚫 Ignoring: chrome-debug-profile, node_modules, __pycache__, .git", "info")
            
            return True
            
        except Exception as e:
            self.print_status(f"❌ Failed to initialize shared file watcher: {e}", "error")
            return False

    async def graceful_shutdown(self):
        """Perform graceful shutdown of all components"""
        self.print_status("🧹 Starting graceful shutdown...", "info")
        
        # Signal shutdown
        if self.shutdown_event:
            self.shutdown_event.set()
        
        # Stop file watching and cancel restart tasks
        if self.restart_manager:
            await self.restart_manager.cleanup_all_tasks()
        
        # Stop file observer
        if self.master_observer:
            self.master_observer.stop()
            # Run observer join in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            with ThreadPoolExecutor() as executor:
                await loop.run_in_executor(executor, self.master_observer.join)
            self.master_observer = None
            self.master_handler = None
            self.watched_services.clear()
        
        # Stop all services
        for service_name in list(self.service_configs.keys()):
            if service_name in self.running_processes:
                self.stop_service(service_name)
        
        self.print_status("✅ Graceful shutdown complete", "success")
    
    def cleanup(self):
        """Synchronous cleanup for backward compatibility"""
        self.print_status("🧹 Cleaning up service manager...", "info")
        
        # Stop shared file watcher
        if self.master_observer:
            # Stop observer
            self.master_observer.stop()
            self.master_observer.join()
            self.master_observer = None
            self.master_handler = None
            self.watched_services.clear()
        
        self.print_status("✅ Service manager cleanup complete", "success")

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
@click.option('--daemon', is_flag=True, help='Run in daemon mode with persistent file watching')
@click.pass_context
def start_all(ctx, daemon):
    """Start all services with async file watching"""
    manager = ctx.obj['manager']
    
    async def run_with_watching():
        # Enable persistent mode
        manager.enable_persistent_mode()
        
        # Check if any services have file watching configured
        services_with_watching = [
            name for name, config in manager.service_configs.items()
            if config.watch_patterns and config.auto_restart
        ]
        
        if services_with_watching:
            manager.print_status(f"🚀 Starting all services in parallel...", "info")
            manager.print_status(f"🔄 Persistent mode enabled - file watching will be active", "info")
            
            # Start with file watching
            await manager.start_with_file_watching()
        else:
            # Just start services without file watching
            manager.print_status(f"🚀 Starting all services in parallel...", "info")
            await manager.start_all_services_async()
            manager.print_status("✅ All services started. No file watching configured.", "info")
    
    try:
        asyncio.run(run_with_watching())
    except KeyboardInterrupt:
        manager.print_status("🛑 Shutdown requested by user", "info")
    except Exception as e:
        manager.print_status(f"❌ Error during startup: {e}", "error")
        sys.exit(1)

@cli.command()
@click.pass_context
def stop_all(ctx):
    """Stop all services"""
    manager = ctx.obj['manager']
    
    services = list(manager.service_configs.keys())
    failed_services = []
    
    for service_name in services:
        if not manager.stop_service(service_name):
            failed_services.append(service_name)
    
    if failed_services:
        manager.print_status(f"❌ Failed to stop: {', '.join(failed_services)}", "error")
        sys.exit(1)
    else:
        manager.print_status("✅ All services stopped", "success")
        # Clean up resources
        manager.cleanup()
        sys.exit(0)

@cli.command()
@click.argument('service_name')
@click.option('--force', is_flag=True, help='Force enable file watching even outside start-all mode')
@click.pass_context
def enable_watch(ctx, service_name, force):
    """Enable file watching for a service"""
    manager = ctx.obj['manager']
    
    if service_name not in manager.service_configs:
        manager.print_status(f"❌ Unknown service: {service_name}", "error")
        sys.exit(1)
        
    config = manager.service_configs[service_name]
    if not config.watch_patterns:
        manager.print_status(f"⚠️  No file watching patterns configured for {service_name}", "warning")
        sys.exit(1)
        
    if service_name in manager.watched_services:
        manager.print_status(f"⚠️  File watching already enabled for {service_name}", "warning")
        sys.exit(0)
    
    if force:
        manager.print_status("⚠️  Forced file watching will only work while this command runs", "warning")
        manager.print_status("💡 Use 'start-all' for persistent file watching", "info")
        
    manager.start_file_watching(service_name, force_enable=force)
    
    if force:
        manager.print_status("🔄 File watcher is active. Press Ctrl+C to stop.", "info")
        try:
            # Keep the process alive so the file watcher can work
            import signal
            signal.pause()
        except KeyboardInterrupt:
            manager.print_status("🛑 File watching stopped", "info")
    else:
        manager.print_status(f"💡 Use 'start-all' to enable persistent file watching for {service_name}", "info")

@cli.command()
@click.argument('service_name')
@click.pass_context
def disable_watch(ctx, service_name):
    """Disable file watching for a service"""
    manager = ctx.obj['manager']
    
    if service_name not in manager.service_configs:
        manager.print_status(f"❌ Unknown service: {service_name}", "error")
        sys.exit(1)
        
    if service_name not in manager.watched_services:
        manager.print_status(f"⚠️  File watching not enabled for {service_name}", "warning")
        sys.exit(0)
        
    manager.stop_file_watching(service_name)
    manager.print_status(f"✅ File watching disabled for {service_name}", "success")

@cli.command()
@click.pass_context
def watch_status(ctx):
    """Show file watching status for all services"""
    manager = ctx.obj['manager']
    
    manager.print_status("=== File Watching Status ===", "header")
    
    # Show shared watcher status
    if manager.master_observer and manager.watched_services:
        manager.print_status(f"🔍 Shared Watcher: ACTIVE ({len(manager.watched_services)} services)", "success")
        manager.print_status(f"   📁 Watching: {manager.base_dir} (recursive)", "info")
        manager.print_status(f"   👁️  Services: {', '.join(sorted(manager.watched_services))}", "info")
    else:
        manager.print_status("🔍 Shared Watcher: INACTIVE", "info")
    
    manager.print_status("")  # Empty line
    
    for service_name, config in manager.service_configs.items():
        watching = service_name in manager.watched_services
        watch_icon = "👁️" if watching else "⚫"
        validation_icon = "🧪" if config.validation_command else "⚫"
        
        status_line = f"{watch_icon} {service_name.upper()}: "
        
        if watching:
            status_line += f"WATCHING {validation_icon}"
        elif config.watch_patterns:
            status_line += f"AVAILABLE {validation_icon}"
        else:
            status_line += "NOT CONFIGURED"
            
        manager.print_status(status_line)
        
        # Show details for configured services
        if config.watch_patterns:
            manager.print_status(f"   🎯 Patterns: {', '.join(config.watch_patterns)}", "info")
            if config.validation_command:
                manager.print_status(f"   🧪 Validation: {' '.join(config.validation_command)}", "info")

@cli.command()
@click.argument('service_name')
@click.pass_context
def validate(ctx, service_name):
    """Test validation for a service without restarting"""
    manager = ctx.obj['manager']
    
    if service_name not in manager.service_configs:
        manager.print_status(f"❌ Unknown service: {service_name}", "error")
        sys.exit(1)
        
    async def run_validation():
        health_valid = await manager.validate_service_health(service_name)
        
        if health_valid:
            manager.print_status(f"✅ Validation passed for {service_name}", "success")
            return True
        else:
            manager.print_status(f"❌ Validation failed for {service_name}", "error")
            return False
    
    success = asyncio.run(run_validation())
    sys.exit(0 if success else 1)

@cli.command()
@click.argument('service_name')
@click.pass_context
def restart_validated(ctx, service_name):
    """Restart a service with full validation"""
    manager = ctx.obj['manager']
    
    if service_name not in manager.service_configs:
        manager.print_status(f"❌ Unknown service: {service_name}", "error")
        sys.exit(1)
        
    async def run_restart():
        return await manager.restart_service_with_validation(service_name)
    
    success = asyncio.run(run_restart())
    sys.exit(0 if success else 1)

@cli.command()
@click.pass_context  
def install_deps(ctx):
    """Install optional dependencies for enhanced functionality"""
    manager = ctx.obj['manager']
    
    manager.print_status("📦 Installing optional dependencies...", "info")
    
    dependencies = [
        ("watchdog", "File watching functionality"),
        ("aiohttp", "Async HTTP client for health checks"),
        ("psutil", "Process monitoring")
    ]
    
    failed = []
    
    for package, description in dependencies:
        try:
            result = subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                manager.print_status(f"✅ Installed {package} - {description}", "success")
            else:
                manager.print_status(f"❌ Failed to install {package}", "error")
                failed.append(package)
        except Exception as e:
            manager.print_status(f"❌ Error installing {package}: {e}", "error")
            failed.append(package)
    
    if failed:
        manager.print_status(f"❌ Failed to install: {', '.join(failed)}", "error")
        sys.exit(1)
    else:
        manager.print_status("✅ All dependencies installed successfully", "success")
        manager.print_status("💡 Restart the service manager to use new features", "info")

if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        print("\n🛑 Service manager interrupted")
        sys.exit(0) 