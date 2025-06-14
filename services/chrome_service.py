#!/usr/bin/env python3
"""
Chrome Debug Service
====================
Manages Chrome browser instances with debugging enabled.
Handles special case: ensures at least one Chrome instance is always running.
"""

import asyncio
import aiohttp
import subprocess
import psutil
import time
from typing import Dict, Any, Optional
from .service_base import ManagedService, ServiceStatus


class ChromeService(ManagedService):
    """Chrome debug service with special instance management"""
    
    async def start(self) -> bool:
        """Start Chrome with special instance detection"""
        # Check if any Chrome debug instance is already running
        if self._is_chrome_debug_running():
            self.logger.info("Chrome debug instance already running, not starting another")
            self.status = ServiceStatus.RUNNING
            self.pid = self._get_chrome_debug_pid()
            return True
        
        # No Chrome debug instance found, start one
        return await super().start()
    
    async def health_check(self) -> bool:
        """Enhanced health check for Chrome Debug Protocol"""
        self.last_health_check = time.time()
        
        # Check if Chrome debug instance exists (any instance)
        if not self._is_chrome_debug_running():
            self.health_status = False
            self.logger.warning("No Chrome debug instances found")
            return False
        
        # Check Chrome Debug Protocol endpoint
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"http://localhost:{self.config.port}/json") as response:
                    if response.status == 200:
                        data = await response.json()
                        # Update metrics with Chrome info
                        self.update_metrics({
                            "tabs_count": len(data),
                            "chrome_version": self._get_chrome_version(),
                            "debug_port": self.config.port
                        })
                        self.health_status = True
                        return True
        except Exception as e:
            self.logger.error(f"Chrome Debug Protocol health check failed: {e}")
        
        self.health_status = False
        return False
    
    def _is_chrome_debug_running(self) -> bool:
        """Check if any Chrome instance is running with debug port"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if any(f"--remote-debugging-port={self.config.port}" in arg for arg in cmdline):
                        return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return False
    
    def _get_chrome_debug_pid(self) -> Optional[int]:
        """Get PID of Chrome debug instance"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    if any(f"--remote-debugging-port={self.config.port}" in arg for arg in cmdline):
                        return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return None
    
    def _get_chrome_version(self) -> str:
        """Get Chrome version for metrics"""
        try:
            result = subprocess.run([
                self.config.command[1] if len(self.config.command) > 1 else "chrome",
                "--version"
            ], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            return "Unknown"
    
    async def stop(self) -> bool:
        """Stop Chrome with special handling"""
        # Only stop if we started this instance
        if self.pid and self._get_chrome_debug_pid() == self.pid:
            return await super().stop()
        else:
            self.logger.info("Not stopping Chrome - instance not managed by this service")
            self.status = ServiceStatus.STOPPED
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """Get Chrome service status with additional info"""
        status = super().get_status()
        status.update({
            "chrome_instances": self._count_chrome_instances(),
            "debug_url": f"http://localhost:{self.config.port}",
            "managed_instance": self.pid == self._get_chrome_debug_pid()
        })
        return status
    
    def _count_chrome_instances(self) -> int:
        """Count total Chrome instances"""
        count = 0
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and 'chrome' in proc.info['name'].lower():
                    count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return count 