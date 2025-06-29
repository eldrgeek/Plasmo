#!/usr/bin/env python3
"""
ProjectYeshie Setup Script
=========================

Cross-platform setup script for Cursor IDE + Playwright Server Integration.
Automatically handles Python installation, dependencies, and configuration.

Usage:
    python setup.py
    ./setup.py  (on Unix systems)
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def print_step(message):
    """Print a formatted step message"""
    print(f"\n🚀 {message}")
    print("=" * (len(message) + 4))

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def run_command(command, check=True, shell=False):
    """Run a command safely with error handling"""
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(command, capture_output=True, text=True, check=check, shell=shell)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command) if isinstance(command, list) else command}")
        print_error(f"Error: {e.stderr}")
        return None
    except FileNotFoundError:
        print_error(f"Command not found: {command[0] if isinstance(command, list) else command}")
        return None

def check_python():
    """Check if Python 3.7+ is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print_success(f"Python found: {version}")
        
        # Check version
        version_info = sys.version_info
        if version_info.major >= 3 and version_info.minor >= 7:
            return True
        else:
            print_error(f"Python 3.7+ required, found {version_info.major}.{version_info.minor}")
            return False
    except:
        return False

def install_python():
    """Attempt to install Python on various platforms"""
    system = platform.system().lower()
    
    print_step("Python 3.7+ not found. Attempting to install...")
    
    if system == "darwin":  # macOS
        print_info("Installing Python via Homebrew...")
        # Check if Homebrew is available
        if run_command(["which", "brew"], check=False):
            run_command(["brew", "install", "python@3.11"])
        else:
            print_error("Homebrew not found. Please install Python manually:")
            print_info("1. Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print_info("2. Install Python: brew install python@3.11")
            return False
            
    elif system == "linux":
        print_info("Installing Python via package manager...")
        # Try different package managers
        if run_command(["which", "apt"], check=False):
            run_command(["sudo", "apt", "update"])
            run_command(["sudo", "apt", "install", "-y", "python3", "python3-pip", "python3-venv"])
        elif run_command(["which", "yum"], check=False):
            run_command(["sudo", "yum", "install", "-y", "python3", "python3-pip"])
        elif run_command(["which", "dnf"], check=False):
            run_command(["sudo", "dnf", "install", "-y", "python3", "python3-pip"])
        elif run_command(["which", "pacman"], check=False):
            run_command(["sudo", "pacman", "-S", "--noconfirm", "python", "python-pip"])
        else:
            print_error("Package manager not found. Please install Python manually.")
            return False
            
    elif system == "windows":
        print_info("Please install Python manually from https://python.org")
        print_info("Make sure to check 'Add Python to PATH' during installation")
        return False
    else:
        print_error(f"Unsupported platform: {system}")
        return False
    
    return True

def create_virtual_environment():
    """Create Python virtual environment"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print_success("Virtual environment already exists")
        return True
    
    print_step("Creating Python virtual environment...")
    result = run_command([sys.executable, "-m", "venv", "venv"])
    if result:
        print_success("Virtual environment created")
        return True
    else:
        print_error("Failed to create virtual environment")
        return False

def get_venv_python():
    """Get the Python executable from the virtual environment"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def install_dependencies():
    """Install Python dependencies"""
    print_step("Installing Python dependencies...")
    
    venv_python = get_venv_python()
    
    # Upgrade pip first
    print_info("Upgrading pip...")
    result = run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    if not result:
        print_error("Failed to upgrade pip")
        return False
    
    # Install requirements
    print_info("Installing requirements...")
    result = run_command([str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"])
    if not result:
        print_error("Failed to install requirements")
        return False
    
    # Install Playwright browsers
    print_info("Installing Playwright browsers...")
    result = run_command([str(venv_python), "-m", "playwright", "install", "chromium"])
    if result:
        print_success("Dependencies installed successfully")
        return True
    else:
        print_error("Failed to install Playwright browsers")
        return False

def create_directories():
    """Create necessary project directories"""
    print_step("Creating project directories...")
    
    directories = ["examples", "docs", "tests", "screenshots", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print_success("Project directories created")

def make_scripts_executable():
    """Make Python scripts executable on Unix systems"""
    if platform.system() != "Windows":
        print_step("Making scripts executable...")
        
        scripts = ["setup.py", "start-server.py"]
        for script in scripts:
            if Path(script).exists():
                os.chmod(script, 0o755)
        
        print_success("Scripts made executable")

def create_cursor_config():
    """Create Cursor IDE configuration file"""
    print_step("Creating Cursor configuration...")
    
    project_path = Path.cwd().absolute()
    
    config = {
        "mcpServers": {
            "project-yeshie-playwright": {
                "command": "python",
                "args": [
                    str(project_path / "mcp_server.py"),
                    "--stdio"
                ],
                "cwd": str(project_path),
                "env": {
                    "PYTHONPATH": str(project_path)
                }
            }
        }
    }
    
    with open("cursor-config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print_success("Cursor configuration created")

def create_start_script():
    """Create the start-server.py script"""
    print_step("Creating start server script...")
    
    start_script_content = '''#!/usr/bin/env python3
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
        print("\\n🛑 Server stopped by user")
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
'''
    
    with open("start-server.py", "w") as f:
        f.write(start_script_content)
    
    print_success("Start server script created")

def print_final_instructions():
    """Print final setup instructions"""
    print("\n🎉 Setup completed successfully!")
    print("=" * 40)
    print()
    print("📋 Next steps:")
    print("1. Configure Cursor IDE:")
    print("   - Open Cursor settings (Cmd+, or Ctrl+,)")
    print("   - Search for 'mcp'")
    print("   - Add the configuration from cursor-config.json")
    print()
    print("2. Start the server:")
    print("   python start-server.py")
    print("   (or ./start-server.py on Unix systems)")
    print()
    print("3. Test in Cursor:")
    print("   Ask: 'Launch a browser and navigate to GitHub to create a repository'")
    print()
    print("4. Create GitHub repository:")
    print("   Use the browser automation tools to create 'ProjectYeshie' on GitHub")
    print()
    print("📖 See README.md for detailed usage instructions.")

def main():
    """Main setup function"""
    print_step("Setting up ProjectYeshie - Cursor Playwright Server...")
    
    # Check/install Python
    if not check_python():
        if not install_python():
            print_error("Python installation failed. Please install Python 3.7+ manually.")
            sys.exit(1)
        
        # Re-check after installation
        if not check_python():
            print_error("Python still not available after installation attempt.")
            sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create project structure
    create_directories()
    create_start_script()
    make_scripts_executable()
    create_cursor_config()
    
    # Final instructions
    print_final_instructions()

if __name__ == "__main__":
    main() 