#!/usr/bin/env python3
"""
ProjectYeshie Server Starter
===========================

Cross-platform script to start the MCP server for Cursor IDE integration.

Usage:
    python start-server.py
    ./start-server.py  (on Unix systems)
"""

import sys
import subprocess
import platform
from pathlib import Path

def print_step(message):
    """Print a formatted step message"""
    print(f"🎭 {message}")
    print("=" * (len(message) + 4))

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def get_venv_python():
    """Get the Python executable from the virtual environment"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def check_dependencies():
    """Check if required dependencies are installed"""
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print_error("Virtual environment not found. Please run setup.py first.")
        return False
    
    # Test imports
    test_code = "import fastmcp, playwright; print('Dependencies OK')"
    result = subprocess.run([str(venv_python), "-c", test_code], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print_success("Dependencies verified")
        return True
    else:
        print_error("Dependencies not found. Please run setup.py first.")
        print_error(f"Error: {result.stderr}")
        return False

def start_server():
    """Start the MCP server"""
    print_step("Starting MCP server...")
    
    venv_python = get_venv_python()
    
    print("Server ready for Cursor IDE integration!")
    print("Configure Cursor with the settings from cursor-config.json")
    print()
    print("Press Ctrl+C to stop the server.")
    print()
    
    # Start the server
    try:
        subprocess.run([str(venv_python), "mcp_server.py", "--stdio"])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print_error(f"Server error: {e}")

def main():
    """Main execution function"""
    print_step("Starting Cursor Playwright Assistant...")
    
    if not check_dependencies():
        sys.exit(1)
    
    start_server()

if __name__ == "__main__":
    main()
