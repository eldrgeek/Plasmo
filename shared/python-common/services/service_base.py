#!/usr/bin/env python3
"""
Service Base Classes
====================
Base classes and enums for the unified service management system.
"""

import os
import sys
import time
import signal
import subprocess
import psutil
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod


class ServiceStatus(Enum):
    """Service status enumeration"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    UNKNOWN = "unknown"


class ServiceType(Enum):
    """Service type enumeration"""
    SOCKETIO = "socketio"
    MCP_SERVER = "mcp_server"
    PLASMO_DEV = "plasmo_dev"
    TESTING = "testing"
    CHROME_DEBUG = "chrome_debug"
    TUNNELING = "tunneling"
    DASHBOARD = "dashboard"


@dataclass
class ServiceConfig:
    """Configuration for a service"""
    name: str
    service_type: ServiceType
    command: List[str]
    working_dir: Optional[str] = None
    port: Optional[int] = None
    ports: List[int] = field(default_factory=list)  # For services with multiple ports
    log_file: Optional[str] = None
    auto_restart: bool = True
    env_vars: Optional[Dict[str, str]] = None
    health_check_url: Optional[str] = None
    health_check_interval: int = 30
    startup_timeout: int = 60
    dependencies: List[str] = field(default_factory=list)  # Service dependencies
    file_watchers: List[str] = field(default_factory=list)  # Files to watch for auto-reload


class ServiceBase(ABC):
    """Base class for all services"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self.status = ServiceStatus.STOPPED
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self.restart_count: int = 0
        self.last_health_check: Optional[float] = None
        self.health_status: bool = False
        self.metrics: Dict[str, Any] = {}
        
        # Setup logging
        self.logger = logging.getLogger(f"service.{self.config.name}")
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup service-specific logging"""
        if self.config.log_file:
            log_path = Path("logs") / self.config.log_file
            log_path.parent.mkdir(exist_ok=True)
            
            handler = logging.FileHandler(log_path)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    @abstractmethod
    async def start(self) -> bool:
        """Start the service"""
        pass
    
    @abstractmethod
    async def stop(self) -> bool:
        """Stop the service"""
        pass
    
    @abstractmethod
    async def restart(self) -> bool:
        """Restart the service"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check service health"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive service status"""
        uptime = None
        if self.start_time and self.status == ServiceStatus.RUNNING:
            uptime = time.time() - self.start_time
            
        return {
            "name": self.config.name,
            "type": self.config.service_type.value,
            "status": self.status.value,
            "pid": self.pid,
            "port": self.config.port,
            "ports": self.config.ports,
            "uptime": uptime,
            "restart_count": self.restart_count,
            "health_status": self.health_status,
            "last_health_check": self.last_health_check,
            "metrics": self.metrics,
            "log_file": self.config.log_file
        }
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage statistics"""
        if not self.pid:
            return {}
            
        try:
            process = psutil.Process(self.pid)
            return {
                "cpu_percent": process.cpu_percent(),
                "memory_info": process.memory_info()._asdict(),
                "memory_percent": process.memory_percent(),
                "num_threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "connections": len(process.connections())
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {}
    
    def is_running(self) -> bool:
        """Check if service is currently running"""
        if not self.pid:
            return False
            
        try:
            process = psutil.Process(self.pid)
            return process.is_running() and self.status == ServiceStatus.RUNNING
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False
    
    async def wait_for_ready(self, timeout: int = None) -> bool:
        """Wait for service to be ready"""
        timeout = timeout or self.config.startup_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self.health_check():
                return True
            await asyncio.sleep(1)
            
        return False
    
    def update_metrics(self, metrics: Dict[str, Any]):
        """Update service metrics"""
        self.metrics.update(metrics)
        self.metrics["last_updated"] = time.time()


class ManagedService(ServiceBase):
    """Base class for services that run external processes"""
    
    async def start(self) -> bool:
        """Start the service process"""
        if self.is_running():
            self.logger.info(f"Service {self.config.name} is already running")
            return True
            
        self.status = ServiceStatus.STARTING
        self.logger.info(f"Starting service {self.config.name}...")
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if self.config.env_vars:
                env.update(self.config.env_vars)
            
            # Start process
            self.process = subprocess.Popen(
                self.config.command,
                cwd=self.config.working_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.pid = self.process.pid
            self.start_time = time.time()
            
            # Wait for service to be ready
            if await self.wait_for_ready():
                self.status = ServiceStatus.RUNNING
                self.logger.info(f"Service {self.config.name} started successfully (PID: {self.pid})")
                return True
            else:
                self.logger.error(f"Service {self.config.name} failed to become ready")
                await self.stop()
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to start service {self.config.name}: {e}")
            self.status = ServiceStatus.ERROR
            return False
    
    async def stop(self) -> bool:
        """Stop the service process"""
        if not self.is_running():
            self.status = ServiceStatus.STOPPED
            return True
            
        self.status = ServiceStatus.STOPPING
        self.logger.info(f"Stopping service {self.config.name}...")
        
        try:
            if self.process:
                # Graceful shutdown
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    self.process.kill()
                    self.process.wait()
                    
            self.status = ServiceStatus.STOPPED
            self.stop_time = time.time()
            self.pid = None
            self.process = None
            
            self.logger.info(f"Service {self.config.name} stopped successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop service {self.config.name}: {e}")
            self.status = ServiceStatus.ERROR
            return False
    
    async def restart(self) -> bool:
        """Restart the service"""
        self.logger.info(f"Restarting service {self.config.name}...")
        self.restart_count += 1
        
        if await self.stop():
            await asyncio.sleep(2)  # Brief pause between stop and start
            return await self.start()
        return False
    
    async def health_check(self) -> bool:
        """Basic health check - override in subclasses for specific checks"""
        self.last_health_check = time.time()
        
        # Basic process check
        if not self.is_running():
            self.health_status = False
            return False
        
        # Port check if specified
        if self.config.port:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', self.config.port))
                sock.close()
                self.health_status = result == 0
                return self.health_status
            except Exception:
                self.health_status = False
                return False
        
        self.health_status = True
        return True


class ServiceOrchestrator:
    """Simple service orchestrator for dashboard integration"""
    
    def __init__(self):
        self.services: Dict[str, ServiceBase] = {}
        self.logger = logging.getLogger("service.orchestrator")
    
    def register_service(self, name: str, service: ServiceBase):
        """Register a service"""
        self.services[name] = service
        self.logger.info(f"Registered service: {name}")
    
    async def get_all_service_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered services"""
        status = {}
        for name, service in self.services.items():
            status[name] = service.get_status()
        
        # Mock data for dashboard testing
        if not status:
            status = {
                "socketio": {
                    "name": "Socket.IO Server", 
                    "status": "running", 
                    "port": 3001, 
                    "pid": 12345,
                    "uptime": 3600
                },
                "mcp": {
                    "name": "MCP Server", 
                    "status": "running", 
                    "port": 8001, 
                    "pid": 12346,
                    "uptime": 3600
                },
                "plasmo": {
                    "name": "Plasmo Dev Server", 
                    "status": "running", 
                    "port": 1012, 
                    "pid": 12347,
                    "uptime": 3600
                },
                "testing": {
                    "name": "Testing Service", 
                    "status": "stopped", 
                    "port": 8082
                },
                "chrome_debug": {
                    "name": "Chrome Debug", 
                    "status": "running", 
                    "port": 9222, 
                    "pid": 12348,
                    "uptime": 3600
                }
            }
        
        return status
    
    async def start_service(self, name: str) -> bool:
        """Start a specific service"""
        if name in self.services:
            return await self.services[name].start()
        return False
    
    async def stop_service(self, name: str) -> bool:
        """Stop a specific service"""
        if name in self.services:
            return await self.services[name].stop()
        return False
    
    async def restart_service(self, name: str) -> bool:
        """Restart a specific service"""
        if name in self.services:
            return await self.services[name].restart()
        return False 