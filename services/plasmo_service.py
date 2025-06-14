#!/usr/bin/env python3
"""
Plasmo Dev Service
==================
Manages Plasmo development server with special directory-based detection.
Handles special case: one instance per directory (can have multiple across directories).
"""

import asyncio
import aiohttp
import os
import psutil
import time
from pathlib import Path
from typing import Dict, Any, List
from .service_base import ManagedService, ServiceStatus


class PlasmoService(ManagedService):
    """Plasmo development service with directory-based instance management"""
    
    async def start(self) -> bool:
        """Start Plasmo dev server with directory detection"""
        # Check if PNPM dev is already running in this directory
        if self._is_pnpm_dev_running_in_dir():
            self.logger.info(f"PNPM dev already running in {self.config.working_dir}")
            self.status = ServiceStatus.RUNNING
            self.pid = self._get_pnpm_dev_pid_in_dir()
            return True
        
        # No instance in this directory, start one
        return await super().start()
    
    async def health_check(self) -> bool:
        """Enhanced health check for Plasmo dev server"""
        self.last_health_check = time.time()
        
        # Check if process is running in our directory
        if not self._is_pnpm_dev_running_in_dir():
            self.health_status = False
            return False
        
        # Check HTTP endpoint if available
        if self.config.port:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                    async with session.get(f"http://localhost:{self.config.port}") as response:
                        if response.status in [200, 404]:  # 404 is OK for dev server root
                            # Update metrics with build info
                            self.update_metrics({
                                "build_status": "running",
                                "port": self.config.port,
                                "directory": self.config.working_dir,
                                "other_instances": len(self._get_all_pnpm_dev_instances())
                            })
                            self.health_status = True
                            return True
            except Exception as e:
                self.logger.debug(f"HTTP health check failed (may be normal): {e}")
        
        # If no HTTP port, just check process
        self.health_status = True
        return True
    
    def _is_pnpm_dev_running_in_dir(self) -> bool:
        """Check if PNPM dev is running in current working directory"""
        target_dir = os.path.abspath(self.config.working_dir or os.getcwd())
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                if proc.info['name'] and 'node' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if len(cmdline) > 0 and any('pnpm' in arg for arg in cmdline):
                        if any('dev' in arg for arg in cmdline):
                            try:
                                proc_cwd = proc.cwd()
                                if os.path.abspath(proc_cwd) == target_dir:
                                    return True
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                continue
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return False
    
    def _get_pnpm_dev_pid_in_dir(self) -> int:
        """Get PID of PNPM dev instance in current directory"""
        target_dir = os.path.abspath(self.config.working_dir or os.getcwd())
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                if proc.info['name'] and 'node' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if len(cmdline) > 0 and any('pnpm' in arg for arg in cmdline):
                        if any('dev' in arg for arg in cmdline):
                            try:
                                proc_cwd = proc.cwd()
                                if os.path.abspath(proc_cwd) == target_dir:
                                    return proc.info['pid']
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                continue
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return None
    
    def _get_all_pnpm_dev_instances(self) -> List[Dict[str, Any]]:
        """Get all PNPM dev instances across all directories"""
        instances = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
                if proc.info['name'] and 'node' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if len(cmdline) > 0 and any('pnpm' in arg for arg in cmdline):
                        if any('dev' in arg for arg in cmdline):
                            try:
                                instances.append({
                                    'pid': proc.info['pid'],
                                    'directory': proc.cwd(),
                                    'cmdline': ' '.join(cmdline)
                                })
                            except (psutil.AccessDenied, psutil.NoSuchProcess):
                                continue
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        return instances
    
    async def stop(self) -> bool:
        """Stop Plasmo dev server with directory awareness"""
        # Only stop if we started this instance or it's in our directory
        current_pid = self._get_pnpm_dev_pid_in_dir()
        if self.pid and current_pid == self.pid:
            return await super().stop()
        else:
            self.logger.info("Not stopping PNPM dev - instance not managed by this service")
            self.status = ServiceStatus.STOPPED
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get Plasmo service status with additional info"""
        status = super().get_status()
        status.update({
            "directory": self.config.working_dir,
            "all_instances": self._get_all_pnpm_dev_instances(),
            "managed_instance": self.pid == self._get_pnpm_dev_pid_in_dir(),
            "dev_url": f"http://localhost:{self.config.port}" if self.config.port else None
        })
        return status 