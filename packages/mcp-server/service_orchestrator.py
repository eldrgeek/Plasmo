#!/usr/bin/env python3
"""
Service Orchestrator for Round Table
====================================

Centralized service management through MCP server tools.
Handles starting, stopping, monitoring, and auto-restart of all services.
"""

import os
import sys
import json
import time
import signal
import psutil
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict
import requests

logger = logging.getLogger(__name__)

@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    description: str
    command: List[str]
    working_dir: str
    port: Optional[int] = None
    health_check_url: Optional[str] = None
    restart_on_failure: bool = True
    auto_restart_on_file_change: bool = False
    watch_files: List[str] = None
    environment: Dict[str, str] = None
    dependencies: List[str] = None  # Services that must start before this one
    
    def __post_init__(self):
        if self.watch_files is None:
            self.watch_files = []
        if self.environment is None:
            self.environment = {}
        if self.dependencies is None:
            self.dependencies = []

@dataclass 
class ServiceStatus:
    """Current status of a service"""
    name: str
    pid: Optional[int] = None
    status: str = "stopped"  # stopped, starting, running, failed, restarting
    port: Optional[int] = None
    started_at: Optional[str] = None
    last_restart: Optional[str] = None
    restart_count: int = 0
    health_status: str = "unknown"  # healthy, unhealthy, unknown
    logs_tail: List[str] = None
    
    def __post_init__(self):
        if self.logs_tail is None:
            self.logs_tail = []

class ServiceOrchestrator:
    """Main service orchestration class"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.services_config = {}
        self.services_status = {}
        self.processes = {}  # pid -> subprocess.Popen
        self.monitoring_thread = None
        self.monitoring_active = False
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Load service configurations
        self._load_service_configs()
        
        # Start monitoring thread
        self.start_monitoring()
    
    def _load_service_configs(self):
        """Load service configurations"""
        # Define all Round Table services
        services = [
            ServiceConfig(
                name="mcp_server",
                description="Main MCP Server with tool orchestration",
                command=["python3", "packages/mcp-server/mcp_server.py", "--port", "8000"],
                working_dir=str(self.project_root),
                port=8000,
                health_check_url="http://localhost:8000/health",
                auto_restart_on_file_change=True,
                watch_files=["packages/mcp-server/*.py"],
                dependencies=[]
            ),
            ServiceConfig(
                name="socketio_server", 
                description="SocketIO Server for real-time communication",
                command=["node", "socketio_server.js"],
                working_dir=str(self.project_root),
                port=3001,
                health_check_url="http://localhost:3001/health",
                auto_restart_on_file_change=True,
                watch_files=["socketio_server.js", "cursor_ai_injector.py"]
            ),
            ServiceConfig(
                name="socketio_server_python",
                description="Python SocketIO Server alternative", 
                command=["python3", "packages/socketio-server/socketio_server_python.py"],
                working_dir=str(self.project_root),
                port=3002,
                auto_restart_on_file_change=True,
                watch_files=["packages/socketio-server/*.py"]
            ),
            ServiceConfig(
                name="plasmo_dev",
                description="Plasmo Chrome Extension Development Server",
                command=["pnpm", "dev"],
                working_dir=str(self.project_root),
                auto_restart_on_file_change=True,
                watch_files=["packages/chrome-extension/**/*"]
            ),
            ServiceConfig(
                name="dashboard",
                description="Development Dashboard",
                command=["python3", "packages/dashboard-framework/mcp_dashboard.py"],
                working_dir=str(self.project_root),
                port=8080,
                health_check_url="http://localhost:8080/health",
                dependencies=["mcp_server"]
            ),
            ServiceConfig(
                name="collaboration_dashboard",
                description="CollaborAItion Dashboard",
                command=["python3", "packages/collaborAItion/dashboard.py"],
                working_dir=str(self.project_root),
                port=8081,
                health_check_url="http://localhost:8081/health",
                dependencies=["mcp_server"]
            ),
            ServiceConfig(
                name="dt_server",
                description="Desktop Automation Server",
                command=["python3", "dt_server.py"],
                working_dir=str(self.project_root),
                port=8082,
                health_check_url="http://localhost:8082/health"
            ),
            ServiceConfig(
                name="continuous_testing",
                description="Continuous Test Runner",
                command=["python3", "tests/continuous_test_runner.py"],
                working_dir=str(self.project_root),
                auto_restart_on_file_change=True,
                watch_files=["tests/*.py", "packages/**/*.py", "*.py"],
                dependencies=["mcp_server"]
            )
        ]
        
        # Store configurations
        for service in services:
            self.services_config[service.name] = service
            self.services_status[service.name] = ServiceStatus(name=service.name)
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            logger.info("🔍 Service monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
            logger.info("🛑 Service monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                for service_name in self.services_config:
                    self._check_service_health(service_name)
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)
    
    def _check_service_health(self, service_name: str):
        """Check health of a specific service"""
        status = self.services_status[service_name]
        config = self.services_config[service_name]
        
        # Check if process is still running
        if status.pid and not psutil.pid_exists(status.pid):
            logger.warning(f"🔴 Service {service_name} (PID {status.pid}) is no longer running")
            status.status = "failed"
            status.pid = None
            
            # Auto-restart if enabled
            if config.restart_on_failure and status.restart_count < 5:
                logger.info(f"🔄 Auto-restarting {service_name}")
                self.restart_service(service_name)
        
        # Health check via HTTP if configured
        if status.status == "running" and config.health_check_url:
            try:
                response = requests.get(config.health_check_url, timeout=5)
                status.health_status = "healthy" if response.status_code == 200 else "unhealthy"
            except:
                status.health_status = "unhealthy"
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status for a service"""
        if service_name not in self.services_status:
            return {"error": f"Service {service_name} not found"}
        
        status = self.services_status[service_name]
        config = self.services_config[service_name]
        
        # Get recent logs
        log_file = self.logs_dir / f"{service_name}.log"
        recent_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r') as f:
                    recent_logs = f.readlines()[-10:]  # Last 10 lines
            except:
                pass
        
        return {
            **asdict(status),
            "config": asdict(config),
            "recent_logs": recent_logs,
            "log_file": str(log_file)
        }
    
    def list_all_services(self) -> Dict[str, Any]:
        """Get status of all services"""
        return {
            name: self.get_service_status(name) 
            for name in self.services_config
        }
    
    def start_service(self, service_name: str, wait_for_health: bool = True) -> Dict[str, Any]:
        """Start a specific service"""
        if service_name not in self.services_config:
            return {"success": False, "error": f"Service {service_name} not found"}
        
        config = self.services_config[service_name]
        status = self.services_status[service_name]
        
        # Check if already running
        if status.status == "running" and status.pid and psutil.pid_exists(status.pid):
            return {"success": True, "message": f"Service {service_name} is already running"}
        
        # Check dependencies
        for dep in config.dependencies:
            dep_status = self.services_status[dep]
            if dep_status.status != "running":
                return {"success": False, "error": f"Dependency {dep} is not running"}
        
        try:
            # Update status
            status.status = "starting"
            status.started_at = datetime.now().isoformat()
            
            # Prepare environment
            env = os.environ.copy()
            env.update(config.environment)
            
            # Prepare log file
            log_file = self.logs_dir / f"{service_name}.log"
            
            # Start the process
            with open(log_file, 'a') as log_f:
                log_f.write(f"\n--- Starting {service_name} at {datetime.now()} ---\n")
                
                process = subprocess.Popen(
                    config.command,
                    cwd=config.working_dir,
                    env=env,
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid  # Create new process group
                )
            
            # Store process
            self.processes[process.pid] = process
            status.pid = process.pid
            status.status = "running"
            status.port = config.port
            
            logger.info(f"✅ Started {service_name} (PID: {process.pid})")
            
            # Wait for health check if configured
            if wait_for_health and config.health_check_url:
                self._wait_for_health(service_name, timeout=30)
            
            return {
                "success": True,
                "service": service_name,
                "pid": process.pid,
                "port": config.port,
                "status": status.status
            }
            
        except Exception as e:
            status.status = "failed"
            logger.error(f"❌ Failed to start {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def stop_service(self, service_name: str, force: bool = False) -> Dict[str, Any]:
        """Stop a specific service"""
        if service_name not in self.services_status:
            return {"success": False, "error": f"Service {service_name} not found"}
        
        status = self.services_status[service_name]
        
        if not status.pid or not psutil.pid_exists(status.pid):
            status.status = "stopped"
            status.pid = None
            return {"success": True, "message": f"Service {service_name} was not running"}
        
        try:
            # Try graceful shutdown first
            if not force:
                os.killpg(os.getpgid(status.pid), signal.SIGTERM)
                time.sleep(3)
                
                # Check if it stopped
                if not psutil.pid_exists(status.pid):
                    status.status = "stopped"
                    status.pid = None
                    logger.info(f"🛑 Gracefully stopped {service_name}")
                    return {"success": True, "message": f"Service {service_name} stopped gracefully"}
            
            # Force kill if graceful didn't work or force=True
            os.killpg(os.getpgid(status.pid), signal.SIGKILL)
            time.sleep(1)
            
            status.status = "stopped"
            status.pid = None
            
            # Remove from processes dict
            if status.pid in self.processes:
                del self.processes[status.pid]
            
            logger.info(f"🛑 Force stopped {service_name}")
            return {"success": True, "message": f"Service {service_name} force stopped"}
            
        except Exception as e:
            logger.error(f"❌ Error stopping {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def restart_service(self, service_name: str) -> Dict[str, Any]:
        """Restart a specific service"""
        status = self.services_status[service_name]
        
        # Stop first
        stop_result = self.stop_service(service_name)
        if not stop_result["success"]:
            return stop_result
        
        # Wait a moment
        time.sleep(2)
        
        # Update restart tracking
        status.restart_count += 1
        status.last_restart = datetime.now().isoformat()
        status.status = "restarting"
        
        # Start again
        return self.start_service(service_name)
    
    def start_all_services(self, exclude: List[str] = None) -> Dict[str, Any]:
        """Start all services in dependency order"""
        if exclude is None:
            exclude = []
        
        results = {}
        started = []
        
        # Sort services by dependencies
        sorted_services = self._topological_sort()
        
        for service_name in sorted_services:
            if service_name in exclude:
                continue
                
            result = self.start_service(service_name)
            results[service_name] = result
            
            if result["success"]:
                started.append(service_name)
            else:
                logger.error(f"❌ Failed to start {service_name}, stopping startup")
                break
            
            # Small delay between services
            time.sleep(2)
        
        return {
            "success": len(started) > 0,
            "started_services": started,
            "results": results,
            "total_started": len(started)
        }
    
    def stop_all_services(self, force: bool = False) -> Dict[str, Any]:
        """Stop all running services"""
        results = {}
        stopped = []
        
        # Stop in reverse dependency order
        sorted_services = list(reversed(self._topological_sort()))
        
        for service_name in sorted_services:
            status = self.services_status[service_name]
            if status.status == "running":
                result = self.stop_service(service_name, force)
                results[service_name] = result
                if result["success"]:
                    stopped.append(service_name)
        
        return {
            "success": True,
            "stopped_services": stopped,
            "results": results,
            "total_stopped": len(stopped)
        }
    
    def _topological_sort(self) -> List[str]:
        """Sort services by dependencies"""
        # Simple topological sort
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(service_name):
            if service_name in temp_visited:
                raise ValueError(f"Circular dependency detected: {service_name}")
            if service_name in visited:
                return
                
            temp_visited.add(service_name)
            config = self.services_config[service_name]
            
            for dep in config.dependencies:
                if dep in self.services_config:
                    visit(dep)
            
            temp_visited.remove(service_name)
            visited.add(service_name)
            result.append(service_name)
        
        for service_name in self.services_config:
            if service_name not in visited:
                visit(service_name)
        
        return result
    
    def _wait_for_health(self, service_name: str, timeout: int = 30):
        """Wait for service to become healthy"""
        config = self.services_config[service_name]
        status = self.services_status[service_name]
        
        if not config.health_check_url:
            return
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(config.health_check_url, timeout=5)
                if response.status_code == 200:
                    status.health_status = "healthy"
                    logger.info(f"✅ {service_name} is healthy")
                    return
            except:
                pass
            time.sleep(2)
        
        logger.warning(f"⚠️ {service_name} health check timeout")
        status.health_status = "unhealthy"

# Global orchestrator instance
orchestrator = None

def get_orchestrator() -> ServiceOrchestrator:
    """Get or create the global orchestrator instance"""
    global orchestrator
    if orchestrator is None:
        orchestrator = ServiceOrchestrator()
    return orchestrator
