#!/usr/bin/env python3
"""
Chrome Debug Launcher
=====================
Python replacement for launch-chrome-debug.sh
Launches Chrome with debugging enabled for MCP server integration.
"""

import os
import sys
import platform
import subprocess
import signal
import time
import click
from pathlib import Path
from typing import List, Optional
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    # Graceful fallback if colorama not available
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = ""
    class Style:
        RESET_ALL = ""

class ChromeDebugLauncher:
    def __init__(self):
        self.platform = platform.system().lower()
        self.profile_dir = Path.cwd() / "chrome-debug-profile"
        self.debug_port = 9222
        self.chrome_path = None
        
    def print_status(self, message: str, status_type: str = "info"):
        """Print colored status message"""
        color = {
            "info": Fore.CYAN,
            "success": Fore.GREEN,
            "warning": Fore.YELLOW,
            "error": Fore.RED,
            "header": Fore.MAGENTA
        }.get(status_type, "")
        
        print(f"{color}{message}{Style.RESET_ALL}")
        
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
            
    def find_chrome_executable(self) -> bool:
        """Find the Chrome executable on the system"""
        executables = self.get_chrome_executables()
        
        for exe in executables:
            # Check if it's an absolute path and exists
            if os.path.isabs(exe) and os.path.isfile(exe) and os.access(exe, os.X_OK):
                self.chrome_path = exe
                return True
            # Check if it's in PATH
            elif subprocess.run(["which", exe], capture_output=True, text=True).returncode == 0:
                result = subprocess.run(["which", exe], capture_output=True, text=True)
                self.chrome_path = result.stdout.strip()
                return True
                
        self.print_status("❌ Chrome executable not found!", "error")
        self.print_status(f"Tried: {', '.join(executables)}", "error")
        return False
        
    def kill_existing_chrome(self):
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
            self.print_status(f"Warning: Could not kill existing Chrome processes: {e}", "warning")
            
    def setup_profile_directory(self):
        """Create Chrome profile directory if it doesn't exist"""
        self.profile_dir.mkdir(exist_ok=True)

    def get_chrome_args(self) -> List[str]:
        """Get Chrome launch arguments"""
        return [
            f"--remote-debugging-port={self.debug_port}",
            "--remote-allow-origins=*",
            "--no-first-run",
            "--no-default-browser-check", 
            "--disable-features=VizDisplayCompositor",
            f"--user-data-dir={self.profile_dir}",
            "--new-window"
        ]
        
    def launch_chrome(self) -> bool:
        """Launch Chrome with debug configuration"""
        if not self.find_chrome_executable():
            return False

        self.kill_existing_chrome()
        self.setup_profile_directory()

        cmd = [self.chrome_path] + self.get_chrome_args()

        try:
            if self.platform == "windows":
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.print_status("✅ Chrome launched with debugging enabled!", "success")
            self.print_status(f"🌐 Debug URL: http://localhost:{self.debug_port}")
            self.print_status("📋 Connect MCP server with: connect_to_chrome()")

            return True
            
        except Exception as e:
            self.print_status(f"❌ Failed to launch Chrome: {e}", "error")
            return False

@click.command()
@click.option('--port', default=9222, help='Debug port (default: 9222)')
@click.option('--profile-dir', default='chrome-debug-profile', help='Chrome profile directory')
def main(port: int, profile_dir: str):
    """Launch Chrome with debugging enabled for MCP server integration"""
    launcher = ChromeDebugLauncher()
    launcher.debug_port = port
    launcher.profile_dir = Path.cwd() / profile_dir
    
    success = launcher.launch_chrome()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 