#!/usr/bin/env python3
"""
Chrome Extension Manager
========================
Python replacement for get_extension_id.sh and configure_extension.sh
Manages Chrome extension detection and configuration.
"""

import os
import sys
import json
import platform
import subprocess
import click
from pathlib import Path
from typing import Dict, List, Optional, Tuple
try:
    from colorama import Fore, Style, init
    init()
except ImportError:
    # Graceful fallback if colorama not available
    class Fore:
        CYAN = GREEN = YELLOW = RED = MAGENTA = ""
    class Style:
        RESET_ALL = ""

class ChromeExtensionManager:
    def __init__(self):
        self.platform = platform.system().lower()
        self.chrome_config_dir = self._get_chrome_config_dir()
        self.extensions_dir = self.chrome_config_dir / "Default" / "Extensions"
        self.preferences_file = self.chrome_config_dir / "Default" / "Preferences"
        
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
        
    def _get_chrome_config_dir(self) -> Path:
        """Get Chrome configuration directory for current platform"""
        if self.platform == "darwin":  # macOS
            return Path.home() / "Library" / "Application Support" / "Google" / "Chrome"
        elif self.platform == "linux":
            return Path.home() / ".config" / "google-chrome"
        elif self.platform == "windows":
            return Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
        else:
            return Path.home() / ".config" / "google-chrome"
            
    def get_extension_id(self, extension_name: str = "plasmo") -> Optional[str]:
        """Find extension ID by searching Chrome preferences and extensions directory"""
        self.print_status(f"🔍 Looking for {extension_name} Chrome extension ID...")
        
        # Method 1: Search Chrome preferences
        extension_id = self._search_preferences(extension_name)
        if extension_id:
            return extension_id
            
        # Method 2: Search extensions directory
        extension_id = self._search_extensions_directory(extension_name)
        if extension_id:
            return extension_id
            
        # Method 3: Look for development extension
        extension_id = self._find_dev_extension()
        if extension_id:
            return extension_id
            
        self.print_status("❌ Extension not found", "error")
        self._print_manual_instructions()
        return None
        
    def _search_preferences(self, extension_name: str) -> Optional[str]:
        """Search Chrome preferences file for extension"""
        if not self.preferences_file.exists():
            self.print_status(f"Chrome preferences not found: {self.preferences_file}", "warning")
            return None
            
        try:
            self.print_status("📁 Checking Chrome preferences...")
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
            extensions = prefs.get('extensions', {}).get('settings', {})
            
            for ext_id, ext_data in extensions.items():
                manifest = ext_data.get('manifest', {})
                name = manifest.get('name', '').lower()
                
                if extension_name.lower() in name:
                    self.print_status(f"✅ Found extension: {manifest.get('name')} (ID: {ext_id})", "success")
                    return ext_id
                    
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            self.print_status(f"Error reading preferences: {e}", "warning")
            
        return None
        
    def _search_extensions_directory(self, extension_name: str) -> Optional[str]:
        """Search extensions directory for extension"""
        if not self.extensions_dir.exists():
            self.print_status(f"Extensions directory not found: {self.extensions_dir}", "warning")
            return None
            
        self.print_status("📂 Checking Chrome extensions directory...")
        
        try:
            for ext_dir in self.extensions_dir.iterdir():
                if ext_dir.is_dir() and len(ext_dir.name) == 32:  # Extension IDs are 32 chars
                    manifest_path = self._find_manifest_in_extension(ext_dir)
                    if manifest_path:
                        try:
                            with open(manifest_path, 'r', encoding='utf-8') as f:
                                manifest = json.load(f)
                                
                            name = manifest.get('name', '').lower()
                            if extension_name.lower() in name:
                                self.print_status(f"✅ Found extension: {manifest.get('name')} (ID: {ext_dir.name})", "success")
                                return ext_dir.name
                                
                        except (json.JSONDecodeError, FileNotFoundError):
                            continue
                            
        except PermissionError:
            self.print_status("Permission denied accessing extensions directory", "warning")
            
        return None
        
    def _find_manifest_in_extension(self, ext_dir: Path) -> Optional[Path]:
        """Find manifest.json in extension directory (may be in version subdirectory)"""
        # Check root directory first
        manifest_path = ext_dir / "manifest.json"
        if manifest_path.exists():
            return manifest_path
            
        # Check version subdirectories
        try:
            for version_dir in ext_dir.iterdir():
                if version_dir.is_dir():
                    manifest_path = version_dir / "manifest.json"
                    if manifest_path.exists():
                        return manifest_path
        except PermissionError:
            pass
            
        return None
        
    def _find_dev_extension(self) -> Optional[str]:
        """Look for development extension in build directory"""
        build_dir = Path.cwd() / "build" / "chrome-mv3-dev"
        if build_dir.exists():
            self.print_status("🔧 Found development build directory")
            self.print_status(f"   Path: {build_dir}")
            self.print_status("   Load this as unpacked extension in Chrome")
            
        return None
        
    def _print_manual_instructions(self):
        """Print manual instructions for finding extension ID"""
        self.print_status("")
        self.print_status("💡 To get the extension ID manually:")
        self.print_status("   1. Open Chrome and go to chrome://extensions/")
        self.print_status("   2. Enable Developer mode (toggle in top right)")
        self.print_status("   3. Find your extension and copy the ID")
        self.print_status("   4. The ID is a 32-character string like: abcdefghijklmnopqrstuvwxyz123456")
        
        build_dir = Path.cwd() / "build" / "chrome-mv3-dev"
        if build_dir.exists():
            self.print_status(f"   5. Or load unpacked extension from: {build_dir}")
            
    def list_all_extensions(self) -> List[Dict[str, str]]:
        """List all installed Chrome extensions"""
        extensions = []
        
        if not self.preferences_file.exists():
            self.print_status("Chrome preferences not found", "warning")
            return extensions
            
        try:
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
            ext_settings = prefs.get('extensions', {}).get('settings', {})
            
            for ext_id, ext_data in ext_settings.items():
                manifest = ext_data.get('manifest', {})
                extensions.append({
                    'id': ext_id,
                    'name': manifest.get('name', 'Unknown'),
                    'version': manifest.get('version', 'Unknown'),
                    'enabled': ext_data.get('state', 0) == 1
                })
                
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            self.print_status(f"Error reading preferences: {e}", "error")
            
        return extensions
        
    def print_extension_info(self, extension_id: str):
        """Print detailed information about a specific extension"""
        if not self.preferences_file.exists():
            self.print_status("Chrome preferences not found", "warning")
            return
            
        try:
            with open(self.preferences_file, 'r', encoding='utf-8') as f:
                prefs = json.load(f)
                
            ext_settings = prefs.get('extensions', {}).get('settings', {})
            ext_data = ext_settings.get(extension_id)
            
            if not ext_data:
                self.print_status(f"Extension {extension_id} not found", "error")
                return
                
            manifest = ext_data.get('manifest', {})
            
            self.print_status(f"Extension Information:", "header")
            self.print_status(f"  ID: {extension_id}")
            self.print_status(f"  Name: {manifest.get('name', 'Unknown')}")
            self.print_status(f"  Version: {manifest.get('version', 'Unknown')}")
            self.print_status(f"  Description: {manifest.get('description', 'No description')}")
            self.print_status(f"  Enabled: {'Yes' if ext_data.get('state', 0) == 1 else 'No'}")
            
            # Show permissions
            permissions = manifest.get('permissions', [])
            if permissions:
                self.print_status(f"  Permissions: {', '.join(permissions)}")
                
        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            self.print_status(f"Error reading extension info: {e}", "error")

@click.group()
def cli():
    """Chrome Extension Manager - Python replacement for extension shell scripts"""
    pass

@cli.command()
@click.option('--name', default='plasmo', help='Extension name to search for')
def get_id(name: str):
    """Find Chrome extension ID by name"""
    manager = ChromeExtensionManager()
    extension_id = manager.get_extension_id(name)
    
    if extension_id:
        print(extension_id)  # Output just the ID for scripting
        sys.exit(0)
    else:
        sys.exit(1)

@cli.command()
def list_extensions():
    """List all installed Chrome extensions"""
    manager = ChromeExtensionManager()
    extensions = manager.list_all_extensions()
    
    if not extensions:
        manager.print_status("No extensions found", "warning")
        return
        
    manager.print_status("Installed Chrome Extensions:", "header")
    for ext in extensions:
        status = "✅" if ext['enabled'] else "❌"
        manager.print_status(f"  {status} {ext['name']} (v{ext['version']}) - {ext['id']}")

@cli.command()
@click.argument('extension_id')
def info(extension_id: str):
    """Show detailed information about a specific extension"""
    manager = ChromeExtensionManager()
    manager.print_extension_info(extension_id)

@cli.command()
def paths():
    """Show Chrome configuration paths"""
    manager = ChromeExtensionManager()
    manager.print_status("Chrome Configuration Paths:", "header")
    manager.print_status(f"  Config Directory: {manager.chrome_config_dir}")
    manager.print_status(f"  Extensions Directory: {manager.extensions_dir}")
    manager.print_status(f"  Preferences File: {manager.preferences_file}")
    
    # Check if paths exist
    manager.print_status("")
    manager.print_status("Path Status:")
    manager.print_status(f"  Config Directory: {'✅ Exists' if manager.chrome_config_dir.exists() else '❌ Not found'}")
    manager.print_status(f"  Extensions Directory: {'✅ Exists' if manager.extensions_dir.exists() else '❌ Not found'}")
    manager.print_status(f"  Preferences File: {'✅ Exists' if manager.preferences_file.exists() else '❌ Not found'}")

if __name__ == "__main__":
    cli() 