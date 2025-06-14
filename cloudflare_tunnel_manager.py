#!/usr/bin/env python3
"""
Cloudflare Tunnel Manager for Plasmo MCP Server
=============================================

This script manages the setup and operation of Cloudflare tunnels for the Plasmo MCP server.
It handles installation, configuration, and running of cloudflared in a cross-platform way.
"""

import os
import sys
import subprocess
import platform
import json
import time
import logging
import shutil
import webbrowser
from pathlib import Path
from typing import Optional, Dict, Any
import click
from dotenv import load_dotenv
import psutil
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
        logging.FileHandler('cloudflare_tunnel.log')
    ]
)

class TunnelManager:
    def __init__(self):
        self.env_file = Path("environment.env")
        self.config_dir = Path.home() / ".cloudflared"
        self.cert_path = self.config_dir / "cert.pem"
        self.tunnel_name = "plasmo-mcp-server"
        self.load_environment()

    def load_environment(self) -> None:
        """Load environment variables from file."""
        if self.env_file.exists():
            load_dotenv(self.env_file)
            logging.info(f"{Fore.BLUE}Loaded environment configuration{Style.RESET_ALL}")
        else:
            self.create_default_env()

    def create_default_env(self) -> None:
        """Create default environment configuration."""
        default_env = {
            "TUNNEL_NAME": "plasmo-mcp-server",
            "TUNNEL_METRICS_PORT": "9091",
            "MCP_PORT": "8000",
            "SOCKETIO_PORT": "3001",
            "MCP_SECURE_MODE": "true",
            "MCP_RATE_LIMIT": "100",
            "LOG_LEVEL": "INFO"
        }
        
        with open(self.env_file, "w") as f:
            for key, value in default_env.items():
                f.write(f"{key}={value}\n")
        
        logging.info(f"{Fore.GREEN}Created default environment configuration{Style.RESET_ALL}")

    def check_cloudflared_installed(self) -> bool:
        """Check if cloudflared is installed."""
        return shutil.which("cloudflared") is not None

    def install_cloudflared(self) -> None:
        """Install cloudflared based on platform."""
        system = platform.system().lower()
        
        try:
            if system == "darwin":
                subprocess.run(["brew", "install", "cloudflare/cloudflare/cloudflared"], check=True)
            elif system == "linux":
                # Download and install the latest version
                subprocess.run([
                    "curl", "-L",
                    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
                    "-o", "/usr/local/bin/cloudflared"
                ], check=True)
                subprocess.run(["chmod", "+x", "/usr/local/bin/cloudflared"], check=True)
            else:
                logging.error(f"{Fore.RED}Unsupported platform: {system}{Style.RESET_ALL}")
                sys.exit(1)
                
            logging.info(f"{Fore.GREEN}Successfully installed cloudflared{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Failed to install cloudflared: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def check_cloudflare_auth(self) -> bool:
        """Check if cloudflared is authenticated with Cloudflare."""
        return self.cert_path.exists()

    def authenticate_cloudflare(self) -> None:
        """Guide user through Cloudflare authentication process."""
        if not self.check_cloudflare_auth():
            logging.info(f"{Fore.BLUE}Cloudflare authentication required{Style.RESET_ALL}")
            logging.info(f"{Fore.BLUE}1. Make sure you have a Cloudflare account at https://dash.cloudflare.com{Style.RESET_ALL}")
            logging.info(f"{Fore.BLUE}2. Press Enter to open the authentication page in your browser{Style.RESET_ALL}")
            input("Press Enter to continue...")
            
            try:
                subprocess.run(["cloudflared", "login"], check=True)
                
                # Wait for cert.pem to appear
                timeout = 60  # seconds
                start_time = time.time()
                while not self.check_cloudflare_auth():
                    if time.time() - start_time > timeout:
                        logging.error(f"{Fore.RED}Authentication timed out. Please try again.{Style.RESET_ALL}")
                        sys.exit(1)
                    time.sleep(1)
                
                logging.info(f"{Fore.GREEN}Successfully authenticated with Cloudflare{Style.RESET_ALL}")
            except subprocess.CalledProcessError as e:
                logging.error(f"{Fore.RED}Authentication failed: {e}{Style.RESET_ALL}")
                sys.exit(1)
        else:
            logging.info(f"{Fore.GREEN}Already authenticated with Cloudflare{Style.RESET_ALL}")

    def setup_tunnel(self) -> None:
        """Set up Cloudflare tunnel configuration."""
        if not self.check_cloudflared_installed():
            logging.info(f"{Fore.YELLOW}cloudflared not found, installing...{Style.RESET_ALL}")
            self.install_cloudflared()

        # Ensure authenticated with Cloudflare
        self.authenticate_cloudflare()

        # Create tunnel if it doesn't exist
        try:
            tunnel_exists = False
            result = subprocess.run(
                ["cloudflared", "tunnel", "list", "--output", "json"],
                check=True,
                capture_output=True,
                text=True
            )
            
            try:
                tunnels = json.loads(result.stdout)
                tunnel_exists = any(tunnel.get("name") == self.tunnel_name for tunnel in tunnels)
            except json.JSONDecodeError:
                tunnel_exists = False

            if not tunnel_exists:
                logging.info(f"{Fore.BLUE}Creating new tunnel: {self.tunnel_name}{Style.RESET_ALL}")
                subprocess.run(["cloudflared", "tunnel", "create", self.tunnel_name], check=True)
                
                # Get the tunnel URL
                result = subprocess.run(
                    ["cloudflared", "tunnel", "info", self.tunnel_name, "--output", "json"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                tunnel_info = json.loads(result.stdout)
                tunnel_url = tunnel_info.get("url", "")
                
                if tunnel_url:
                    logging.info(f"{Fore.GREEN}Your tunnel URL is: {tunnel_url}{Style.RESET_ALL}")
                    logging.info(f"{Fore.BLUE}You can access your MCP server at: {tunnel_url}/mcp{Style.RESET_ALL}")

        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Failed to create tunnel: {e}{Style.RESET_ALL}")
            sys.exit(1)

        # Create config file
        config = {
            "tunnel": self.tunnel_name,
            "credentials-file": str(self.config_dir / f"{self.tunnel_name}.json"),
            "metrics": f"localhost:{os.getenv('TUNNEL_METRICS_PORT', '9091')}",
            "ingress": [
                {
                    "hostname": os.getenv("CUSTOM_DOMAIN", ""),
                    "service": f"http://localhost:{os.getenv('MCP_PORT', '8000')}"
                },
                {
                    "service": "http_status:404"
                }
            ]
        }

        self.config_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_dir / "config.yml", "w") as f:
            import yaml
            yaml.dump(config, f)

        logging.info(f"{Fore.GREEN}Tunnel configuration complete{Style.RESET_ALL}")
        logging.info(f"{Fore.BLUE}You can now start the tunnel with: python3 {sys.argv[0]} start{Style.RESET_ALL}")

    def start_tunnel(self) -> None:
        """Start the Cloudflare tunnel."""
        if not (self.config_dir / "config.yml").exists():
            logging.error(f"{Fore.RED}Tunnel configuration not found. Run setup first.{Style.RESET_ALL}")
            sys.exit(1)

        try:
            # Start tunnel in the background
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "run", self.tunnel_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Save PID
            with open(".tunnel.pid", "w") as f:
                f.write(str(process.pid))

            logging.info(f"{Fore.GREEN}Tunnel started successfully (PID: {process.pid}){Style.RESET_ALL}")
            return process
        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Failed to start tunnel: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def stop_tunnel(self) -> None:
        """Stop the Cloudflare tunnel."""
        try:
            if Path(".tunnel.pid").exists():
                with open(".tunnel.pid", "r") as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    psutil.Process(pid).terminate()
                    logging.info(f"{Fore.GREEN}Tunnel stopped successfully{Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}Tunnel process not found{Style.RESET_ALL}")
                
                Path(".tunnel.pid").unlink()
            else:
                logging.warning(f"{Fore.YELLOW}No tunnel PID file found{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"{Fore.RED}Error stopping tunnel: {e}{Style.RESET_ALL}")

    def get_status(self) -> Dict[str, Any]:
        """Get tunnel status."""
        status = {
            "tunnel_running": False,
            "config_exists": False,
            "pid": None
        }

        # Check configuration
        status["config_exists"] = (self.config_dir / "config.yml").exists()

        # Check if tunnel is running
        if Path(".tunnel.pid").exists():
            with open(".tunnel.pid", "r") as f:
                pid = int(f.read().strip())
                status["pid"] = pid
                status["tunnel_running"] = psutil.pid_exists(pid)

        return status

@click.group()
def cli():
    """Cloudflare Tunnel Manager CLI"""
    pass

@cli.command()
def setup():
    """Set up Cloudflare tunnel configuration"""
    manager = TunnelManager()
    manager.setup_tunnel()

@cli.command()
def start():
    """Start Cloudflare tunnel"""
    manager = TunnelManager()
    manager.start_tunnel()

@cli.command()
def stop():
    """Stop Cloudflare tunnel"""
    manager = TunnelManager()
    manager.stop_tunnel()

@cli.command()
def status():
    """Check tunnel status"""
    manager = TunnelManager()
    status = manager.get_status()
    
    if status["tunnel_running"]:
        print(f"{Fore.GREEN}Tunnel is running (PID: {status['pid']}){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Tunnel is not running{Style.RESET_ALL}")
    
    if status["config_exists"]:
        print(f"{Fore.GREEN}Configuration exists{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Configuration not found{Style.RESET_ALL}")

if __name__ == "__main__":
    cli() 