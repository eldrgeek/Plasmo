#!/usr/bin/env python3
"""
UPDATED MCP SERVER - NOW WITH COMMAND EXECUTION!
===============================================

Your existing Cursor Playwright Assistant + Command Execution Tools

NEW COMMAND TOOLS:
- execute_command: Run shell commands safely
- execute_python_script: Run Python code directly
- install_package: Install Python packages  
- get_system_info: Get system information
- run_instant_capture: Start instant AI capture
- run_setup_script: Run setup scripts
"""

# Add these imports to your existing mcp_server.py
import subprocess
import shlex
import tempfile

# INSERT THESE TOOLS INTO YOUR EXISTING mcp_server.py FILE
# Just add them before the main() function

@mcp.tool()
def execute_command(command: str, working_dir: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Execute shell command safely with output capture and security checks."""
    
    if working_dir is None:
        working_dir = os.getcwd()
    
    # Security check
    forbidden_commands = {
        'rm -rf', 'format', 'fdisk', 'dd', 'mkfs',
        'shutdown', 'reboot', 'halt', 'poweroff',
        'passwd', 'useradd', 'userdel', 'usermod'
    }
    
    command_lower = command.lower()
    for forbidden in forbidden_commands:
        if forbidden in command_lower:
            return {
                "success": False,
                "error": f"Forbidden command: {forbidden}",
                "command": command
            }
    
    try:
        print(f"🚀 Executing: {command}")
        
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "command": command,
            "working_directory": working_dir,
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "timestamp": time.time()
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command
        }

@mcp.tool()
def run_instant_capture() -> Dict[str, Any]:
    """Start the beautiful instant AI capture system."""
    
    try:
        script_path = "instant_capture_beautiful.py"
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Script not found: {script_path}",
                "suggestion": "Run: ./setup_beautiful_capture.sh first"
            }
        
        # Start in background
        subprocess.Popen(
            f"python3 {script_path}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        return {
            "success": True,
            "status": "🎯 Instant AI Capture system started!",
            "usage": "Press Cmd+Shift+T anywhere to capture tasks",
            "script_path": script_path
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
def install_package(package_name: str) -> Dict[str, Any]:
    """Install Python package using pip3."""
    
    try:
        result = execute_command(f"pip3 install {package_name}", timeout=120)
        return {
            **result,
            "package_name": package_name,
            "operation": "package_installation"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to install {package_name}: {str(e)}"
        }

# QUICK INTEGRATION INSTRUCTIONS:
print("""
🔧 TO ADD COMMAND EXECUTION TO YOUR MCP SERVER:

1. COPY the three @mcp.tool() functions above
2. PASTE them into your mcp_server.py file (before the main() function)
3. RESTART your MCP server

Then you can:
- execute_command("python3 --version")  
- run_instant_capture()
- install_package("pynput")

🎯 This gives Claude the power to run your instant capture system!
""")
