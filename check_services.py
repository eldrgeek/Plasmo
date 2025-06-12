#!/usr/bin/env python3
"""
Cross-platform service status checker for Plasmo extension services.
Python replacement for check_services.sh with enhanced cross-platform support.
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, Optional, Tuple
import click
from colorama import Fore, Style, init
import socket

# Add the current directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from service_manager import ServiceManager, ServiceType

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class ServiceChecker:
    """Enhanced service status checker with health checks"""
    
    def __init__(self):
        self.service_manager = ServiceManager()
        self.base_dir = Path.cwd()
        self.logs_dir = self.base_dir / "logs"
        
    def print_header(self):
        """Print the status check header"""
        print(f"{Fore.MAGENTA}📊 Development Services Status{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}==============================={Style.RESET_ALL}")
        print()
        
    def print_status(self, message: str, status_type: str = "success"):
        """Print colored status message"""
        icons = {
            "success": "✅",
            "error": "❌", 
            "warning": "⚠️",
            "info": "ℹ️"
        }
        
        colors = {
            "success": Fore.GREEN,
            "error": Fore.RED,
            "warning": Fore.YELLOW,
            "info": Fore.BLUE
        }
        
        icon = icons.get(status_type, "•")
        color = colors.get(status_type, Fore.WHITE)
        
        print(f"{color}{icon} {message}{Style.RESET_ALL}")
        
    def check_port(self, port: int, service_name: str) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
            
    def check_http_endpoint(self, url: str, timeout: int = 5) -> Tuple[bool, Optional[str]]:
        """Check if an HTTP endpoint is responding"""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200, None
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
            
    def check_mcp_server(self):
        """Check MCP Server status"""
        self.print_status("Checking MCP Server...", "info")
        
        is_running, pid = self.service_manager.is_service_running("mcp")
        if is_running:
            config = self.service_manager.service_configs["mcp"]
            port = 8000  # Default MCP port
            
            self.print_status(f"MCP Server is running (PID: {pid})")
            
            # Test HTTP health endpoint
            health_url = f"http://localhost:{port}/health"
            is_responding, error = self.check_http_endpoint(health_url)
            
            if is_responding:
                self.print_status("MCP Server health endpoint is responding")
            else:
                self.print_status(f"MCP Server process running but health endpoint not responding: {error}", "warning")
                
        else:
            self.print_status("MCP Server is not running", "error")
            
        print()
        
    def check_socketio_server(self):
        """Check Socket.IO Server status"""
        self.print_status("Checking SocketIO Server...", "info")
        
        is_running, pid = self.service_manager.is_service_running("socketio")
        if is_running:
            config = self.service_manager.service_configs["socketio"]
            port = config.port or 3001
            
            # Check if running with auto-restart
            implementation = config.implementation.value
            auto_restart_info = ""
            
            if implementation == "javascript":
                # Check if nodemon is running
                try:
                    result = subprocess.run(
                        ["pgrep", "-f", "nodemon.*socketio_server.js"], 
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        auto_restart_info = " with auto-restart"
                except:
                    pass
                    
            self.print_status(f"SocketIO Server ({implementation}) is running{auto_restart_info} (PID: {pid}, Port: {port})")
            
            # Test HTTP endpoint
            server_url = f"http://localhost:{port}/"
            is_responding, error = self.check_http_endpoint(server_url)
            
            if is_responding:
                self.print_status("SocketIO Server HTTP endpoint is responding")
            else:
                self.print_status(f"SocketIO Server process running but HTTP endpoint not responding: {error}", "warning")
                
        else:
            self.print_status("SocketIO Server is not running", "error")
            
        print()
        
    def check_plasmo_dev_server(self):
        """Check Plasmo Dev Server status"""
        self.print_status("Checking Plasmo Dev Server...", "info")
        
        is_running, pid = self.service_manager.is_service_running("plasmo")
        if is_running:
            self.print_status(f"Plasmo Dev Server is running (PID: {pid})")
            
            # Check build directory
            build_dir = self.base_dir / "build"
            if build_dir.exists():
                self.print_status("Extension build directory exists")
                
                chrome_build = build_dir / "chrome-mv3-dev"
                if chrome_build.exists():
                    self.print_status("Chrome extension build is available")
                else:
                    self.print_status("Chrome extension build not found", "warning")
            else:
                self.print_status("Build directory not found", "warning")
                
        else:
            self.print_status("Plasmo Dev Server is not running", "error")
            
        print()
        
    def check_auto_restart_processes(self):
        """Check auto-restart processes"""
        self.print_status("Checking auto-restart processes...", "info")
        
        # Check Python file watcher (watchmedo)
        try:
            result = subprocess.run(
                ["pgrep", "-f", "watchmedo.*mcp_server.py"],
                capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip()
                self.print_status(f"Python file watcher is active (watchmedo PID: {pid})")
            else:
                self.print_status("Python file watcher not running (install: pip install watchdog)", "warning")
        except:
            self.print_status("Could not check Python file watcher status", "warning")
            
        # Check nodemon for SocketIO
        try:
            result = subprocess.run(
                ["pgrep", "-f", "nodemon.*socketio_server.js"],
                capture_output=True, text=True  
            )
            if result.returncode == 0 and result.stdout.strip():
                self.print_status("SocketIO file watcher is active (nodemon)")
            else:
                self.print_status("SocketIO file watcher not running", "warning")
        except:
            self.print_status("Could not check SocketIO file watcher status", "warning")
            
        print()
        
    def check_ports(self):
        """Check service ports"""
        self.print_status("Checking ports...", "info")
        
        # Get actual service status and check ports
        status = self.service_manager.get_service_status()
        
        port_checks = [
            (8000, "MCP Server"),
            (3001, "SocketIO Server")
        ]
        
        # Add dynamic ports from service status
        for service_name, service_info in status.items():
            if service_info.get("port") and service_info["port"] not in [8000, 3001]:
                port_checks.append((service_info["port"], f"{service_name.upper()} Server"))
        
        for port, service_name in port_checks:
            if self.check_port(port, service_name):
                self.print_status(f"Port {port} is in use ({service_name})")
            else:
                self.print_status(f"Port {port} is not in use ({service_name} not listening)", "error")
                
        print()
        
    def display_service_urls(self):
        """Display service URLs"""
        self.print_status("Service URLs:", "info")
        print("  • MCP Server: http://localhost:8000")
        print("  • SocketIO Controller: http://localhost:3001")
        print("  • MCP Health Check: http://localhost:8000/health")
        print()
        
    def check_logs(self):
        """Check log file activity"""
        self.print_status("Recent log activity:", "info")
        
        if self.logs_dir.exists():
            log_files = list(self.logs_dir.glob("*.log"))
            if log_files:
                for log_file in sorted(log_files):
                    try:
                        # Count lines
                        with open(log_file, 'r') as f:
                            lines = sum(1 for _ in f)
                            
                        # Get file size
                        size = log_file.stat().st_size
                        size_str = self.format_file_size(size)
                        
                        print(f"  • {log_file.name}: {lines} lines, {size_str}")
                    except Exception as e:
                        print(f"  • {log_file.name}: Error reading file ({e})")
            else:
                self.print_status("No log files found", "warning")
        else:
            self.print_status("Logs directory not found", "warning")
            
        print()
        
    def format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
        
    def display_summary(self):
        """Display service summary"""
        self.print_status("📋 Service Summary:", "info")
        
        status = self.service_manager.get_service_status()
        all_running = True
        
        for service_name, service_info in status.items():
            status_icon = "✅" if service_info["running"] else "❌"
            impl_info = f"({service_info['implementation']})"
            port_info = f" - Port {service_info['port']}" if service_info['port'] else ""
            pid_info = f" - PID {service_info['pid']}" if service_info['pid'] else ""
            
            service_display = service_name.replace("_", " ").title()
            print(f"  {status_icon} {service_display}: {impl_info}{port_info}{pid_info}")
            
            if not service_info["running"]:
                all_running = False
                
        print()
        
        if all_running:
            self.print_status("🎉 All services are running!", "success")
        else:
            self.print_status("⚠️ Some services are not running. Use 'python service_manager.py start-all' to start all services.", "warning")
            
    def run_full_check(self):
        """Run complete service status check"""
        self.print_header()
        self.check_mcp_server()
        self.check_socketio_server()
        self.check_plasmo_dev_server()
        self.check_auto_restart_processes()
        self.check_ports()
        self.display_service_urls()
        self.check_logs()
        self.display_summary()

# CLI Interface
@click.command()
@click.option('--json', 'output_json', is_flag=True, help='Output status in JSON format')
@click.option('--quiet', '-q', is_flag=True, help='Only show errors and warnings')
def main(output_json: bool, quiet: bool):
    """Check status of all Plasmo extension services"""
    
    checker = ServiceChecker()
    
    if output_json:
        # JSON output for programmatic use
        status = checker.service_manager.get_service_status()
        print(json.dumps(status, indent=2))
    else:
        # Human-readable output
        if not quiet:
            checker.run_full_check()
        else:
            # Quick status check
            status = checker.service_manager.get_service_status()
            all_running = all(info["running"] for info in status.values())
            
            if all_running:
                checker.print_status("All services running", "success")
                sys.exit(0)
            else:
                checker.print_status("Some services not running", "error")
                for name, info in status.items():
                    if not info["running"]:
                        checker.print_status(f"{name} is not running", "error")
                sys.exit(1)

if __name__ == "__main__":
    main() 