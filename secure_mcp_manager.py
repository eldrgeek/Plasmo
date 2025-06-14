#!/usr/bin/env python3
"""
Secure MCP Server Manager
========================

This script manages the secure version of the MCP server with Cloudflare tunnel integration.
It handles starting, stopping, and monitoring the secure MCP server.
"""

import os
import sys
import subprocess
import logging
import secrets
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import psutil
import click
from dotenv import load_dotenv
import colorama
from colorama import Fore, Style

# Initialize colorama for cross-platform color support
colorama.init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('secure_mcp.log')
    ]
)

class SecureMCPManager:
    def __init__(self):
        self.env_file = Path("environment.env")
        self.venv_path = Path("venv")
        self.load_environment()

    def load_environment(self) -> None:
        """Load environment variables and generate API key if needed."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            
            # Generate API key if not set
            if not os.getenv("MCP_API_KEY"):
                api_key = secrets.token_urlsafe(32)
                with open(self.env_file, "a") as f:
                    f.write(f"\nMCP_API_KEY={api_key}\n")
                os.environ["MCP_API_KEY"] = api_key
                logging.info(f"{Fore.GREEN}Generated new API key{Style.RESET_ALL}")
            
            logging.info(f"{Fore.BLUE}Loaded environment configuration{Style.RESET_ALL}")
        else:
            logging.error(f"{Fore.RED}environment.env file not found{Style.RESET_ALL}")
            sys.exit(1)

    def setup_virtual_env(self) -> None:
        """Set up Python virtual environment and install dependencies."""
        if not self.venv_path.exists():
            logging.info(f"{Fore.BLUE}Creating Python virtual environment...{Style.RESET_ALL}")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], check=True)

        # Determine the pip path based on platform
        pip_path = self.venv_path / "Scripts" / "pip.exe" if os.name == "nt" else self.venv_path / "bin" / "pip"
        
        logging.info(f"{Fore.BLUE}Installing/upgrading dependencies...{Style.RESET_ALL}")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)

    def start_server(self) -> Optional[subprocess.Popen]:
        """Start the secure MCP server."""
        try:
            # Activate virtual environment
            if os.name == "nt":
                python_path = self.venv_path / "Scripts" / "python.exe"
            else:
                python_path = self.venv_path / "bin" / "python"

            # Start secure MCP server
            process = subprocess.Popen(
                [str(python_path), "mcp_server_secure.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Save PID
            with open(".mcp_secure.pid", "w") as f:
                f.write(str(process.pid))

            # Wait a bit to ensure server starts
            time.sleep(2)

            if process.poll() is None:  # Process is still running
                logging.info(f"{Fore.GREEN}Secure MCP server started successfully (PID: {process.pid}){Style.RESET_ALL}")
                return process
            else:
                stdout, stderr = process.communicate()
                logging.error(f"{Fore.RED}Server failed to start:\nSTDOUT: {stdout.decode()}\nSTDERR: {stderr.decode()}{Style.RESET_ALL}")
                return None

        except Exception as e:
            logging.error(f"{Fore.RED}Failed to start secure MCP server: {e}{Style.RESET_ALL}")
            return None

    def stop_server(self) -> None:
        """Stop the secure MCP server."""
        try:
            if Path(".mcp_secure.pid").exists():
                with open(".mcp_secure.pid", "r") as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    process.terminate()
                    process.wait(timeout=5)  # Wait up to 5 seconds for graceful shutdown
                    logging.info(f"{Fore.GREEN}Secure MCP server stopped successfully{Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}Server process not found{Style.RESET_ALL}")
                
                Path(".mcp_secure.pid").unlink()
            else:
                logging.warning(f"{Fore.YELLOW}No server PID file found{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"{Fore.RED}Error stopping server: {e}{Style.RESET_ALL}")

    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        status = {
            "server_running": False,
            "pid": None,
            "uptime": None,
            "api_key_configured": bool(os.getenv("MCP_API_KEY"))
        }

        if Path(".mcp_secure.pid").exists():
            with open(".mcp_secure.pid", "r") as f:
                pid = int(f.read().strip())
                status["pid"] = pid
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    status["server_running"] = True
                    status["uptime"] = time.time() - process.create_time()

        return status

@click.group()
def cli():
    """Secure MCP Server Manager CLI"""
    pass

@cli.command()
def setup():
    """Set up secure MCP server environment"""
    manager = SecureMCPManager()
    manager.setup_virtual_env()
    click.echo(f"{Fore.GREEN}Setup complete!{Style.RESET_ALL}")

@cli.command()
def start():
    """Start secure MCP server"""
    manager = SecureMCPManager()
    manager.setup_virtual_env()  # Ensure dependencies are installed
    process = manager.start_server()
    if not process:
        sys.exit(1)

@cli.command()
def stop():
    """Stop secure MCP server"""
    manager = SecureMCPManager()
    manager.stop_server()

@cli.command()
def status():
    """Check server status"""
    manager = SecureMCPManager()
    status = manager.get_status()
    
    if status["server_running"]:
        uptime = time.strftime('%H:%M:%S', time.gmtime(status["uptime"]))
        print(f"{Fore.GREEN}Server is running (PID: {status['pid']}, Uptime: {uptime}){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Server is not running{Style.RESET_ALL}")
    
    if status["api_key_configured"]:
        print(f"{Fore.GREEN}API key is configured{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}API key is not configured{Style.RESET_ALL}")

@cli.command()
def restart():
    """Restart secure MCP server"""
    manager = SecureMCPManager()
    manager.stop_server()
    time.sleep(2)  # Wait for server to stop
    process = manager.start_server()
    if not process:
        sys.exit(1)

if __name__ == "__main__":
    cli() 