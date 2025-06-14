#!/usr/bin/env python3
"""
LocalTunnel Manager for Plasmo MCP Server
========================================

This script manages LocalTunnel for exposing the MCP server to the internet.
It can start, stop, and check the status of a LocalTunnel process.
"""

import os
import sys
import subprocess
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import psutil
import click

# Try to import colorama, fall back to no colors if not available
try:
    import colorama
    from colorama import Fore, Style
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    # Fallback: no colors
    class Fore:
        BLUE = ""
        GREEN = ""
        YELLOW = ""
        RED = ""
    
    class Style:
        RESET_ALL = ""
    
    HAS_COLORAMA = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('localtunnel.log')
    ]
)

class LocalTunnelManager:
    def __init__(self, port: int = 8000, subdomain: Optional[str] = None):
        self.port = port
        self.subdomain = subdomain
        self.pid_file = Path('.localtunnel.pid')
        self.url_file = Path('.localtunnel.url')

    def check_localtunnel_installed(self) -> bool:
        """Check if LocalTunnel is installed globally."""
        try:
            result = subprocess.run(['which', 'lt'], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False

    def install_localtunnel(self) -> None:
        """Install LocalTunnel globally via npm."""
        logging.info(f"{Fore.YELLOW}Installing localtunnel globally via npm...{Style.RESET_ALL}")
        try:
            subprocess.run(['npm', 'install', '-g', 'localtunnel'], check=True)
            logging.info(f"{Fore.GREEN}localtunnel installed successfully!{Style.RESET_ALL}")
        except subprocess.CalledProcessError as e:
            logging.error(f"{Fore.RED}Failed to install localtunnel: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def start_tunnel(self) -> None:
        """Start LocalTunnel on the specified port."""
        if not self.check_localtunnel_installed():
            self.install_localtunnel()

        # Check if tunnel is already running
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            if psutil.pid_exists(pid):
                logging.warning(f"{Fore.YELLOW}LocalTunnel is already running (PID: {pid}){Style.RESET_ALL}")
                return

        # Build command with optional subdomain
        cmd = ['lt', '--port', str(self.port)]
        if self.subdomain:
            cmd.extend(['--subdomain', self.subdomain])
            logging.info(f"{Fore.BLUE}Starting LocalTunnel on port {self.port} with subdomain '{self.subdomain}'...{Style.RESET_ALL}")
        else:
            logging.info(f"{Fore.BLUE}Starting LocalTunnel on port {self.port}...{Style.RESET_ALL}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Save PID immediately
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for the URL to appear in stdout
            url = None
            for _ in range(30):  # Wait up to 15 seconds
                line = process.stdout.readline()
                if line and 'your url is:' in line:
                    url = line.split('your url is:')[1].strip()
                    break
                elif line and 'https://' in line and 'loca.lt' in line:
                    # Alternative format detection
                    url = line.strip()
                    break
                time.sleep(0.5)
            
            if url:
                with open(self.url_file, 'w') as f:
                    f.write(url)
                logging.info(f"{Fore.GREEN}LocalTunnel started: {url}{Style.RESET_ALL}")
            else:
                # If we have a subdomain, construct the expected URL
                if self.subdomain:
                    expected_url = f"https://{self.subdomain}.loca.lt"
                    with open(self.url_file, 'w') as f:
                        f.write(expected_url)
                    logging.info(f"{Fore.GREEN}LocalTunnel started: {expected_url}{Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}LocalTunnel started but could not determine URL. Check localtunnel.log for details.{Style.RESET_ALL}")
                
        except Exception as e:
            logging.error(f"{Fore.RED}Failed to start LocalTunnel: {e}{Style.RESET_ALL}")
            if self.pid_file.exists():
                self.pid_file.unlink()
            sys.exit(1)

    def stop_tunnel(self) -> None:
        """Stop the LocalTunnel process."""
        try:
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                if psutil.pid_exists(pid):
                    process = psutil.Process(pid)
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        process.kill()
                    logging.info(f"{Fore.GREEN}LocalTunnel stopped (PID: {pid}){Style.RESET_ALL}")
                else:
                    logging.warning(f"{Fore.YELLOW}No running LocalTunnel process found for PID {pid}{Style.RESET_ALL}")
                
                self.pid_file.unlink()
            else:
                logging.warning(f"{Fore.YELLOW}No LocalTunnel PID file found{Style.RESET_ALL}")
            
            if self.url_file.exists():
                self.url_file.unlink()
                
        except Exception as e:
            logging.error(f"{Fore.RED}Error stopping LocalTunnel: {e}{Style.RESET_ALL}")

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of LocalTunnel."""
        status = {'running': False, 'pid': None, 'url': None}
        
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                status['pid'] = pid
                status['running'] = psutil.pid_exists(pid)
            except (ValueError, FileNotFoundError):
                pass
        
        if self.url_file.exists():
            try:
                with open(self.url_file, 'r') as f:
                    status['url'] = f.read().strip()
            except FileNotFoundError:
                pass
        
        return status

@click.group()
def cli():
    """LocalTunnel Manager CLI"""
    pass

@cli.command()
@click.option('--port', default=8000, help='Local port to expose')
@click.option('--subdomain', help='Custom subdomain (e.g., monad-journey)')
def start(port, subdomain):
    """Start LocalTunnel"""
    manager = LocalTunnelManager(port, subdomain)
    manager.start_tunnel()

@cli.command()
def stop():
    """Stop LocalTunnel"""
    manager = LocalTunnelManager()
    manager.stop_tunnel()

@cli.command()
def status():
    """Check LocalTunnel status"""
    manager = LocalTunnelManager()
    status = manager.get_status()
    
    if status['running']:
        print(f"{Fore.GREEN}LocalTunnel is running (PID: {status['pid']}){Style.RESET_ALL}")
        if status['url']:
            print(f"{Fore.BLUE}Tunnel URL: {status['url']}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}LocalTunnel is not running{Style.RESET_ALL}")

if __name__ == "__main__":
    cli() 