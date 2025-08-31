#!/usr/bin/env python3
"""
MCP COMMAND EXECUTION EXTENSION
===============================
Adds secure command execution capabilities to the existing MCP server

This extension adds:
- execute_command: Run shell commands safely
- execute_python_script: Run Python code directly
- install_package: Install Python packages
- get_system_info: Get system information
- run_instant_capture: Start the instant capture system

Security features:
- Command validation
- Timeout protection  
- Working directory control
- Output capture
- Error handling
"""

import subprocess
import os
import sys
import shlex
import time
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add this to your existing mcp_server.py file

@mcp.tool()
def execute_command(command: str, working_dir: str = None, timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
    """
    Execute a shell command safely with output capture.
    
    Args:
        command: Shell command to execute
        working_dir: Working directory (defaults to current directory)
        timeout: Command timeout in seconds
        capture_output: Whether to capture stdout/stderr
        
    Returns:
        Command execution result with output and status
    """
    
    # Set working directory
    if working_dir is None:
        working_dir = os.getcwd()
    
    # Security check - forbidden commands
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
                "error": f"Forbidden command detected: {forbidden}",
                "command": command,
                "timestamp": time.time()
            }
    
    try:
        print(f"🚀 Executing: {command}")
        print(f"📁 Working directory: {working_dir}")
        
        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        response = {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "command": command,
            "working_directory": working_dir,
            "timestamp": time.time(),
        }
        
        if capture_output:
            response.update({
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
            })
        
        # Log the execution
        status = "✅" if result.returncode == 0 else "❌"
        print(f"{status} Command completed with return code: {result.returncode}")
        
        return response
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout} seconds",
            "command": command,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "command": command,
            "timestamp": time.time()
        }

@mcp.tool()
def execute_python_script(script_content: str, script_name: str = "temp_script.py", working_dir: str = None) -> Dict[str, Any]:
    """
    Execute Python script content directly.
    
    Args:
        script_content: Python code to execute
        script_name: Name for temporary script file
        working_dir: Working directory for execution
        
    Returns:
        Python execution result with output
    """
    
    if working_dir is None:
        working_dir = os.getcwd()
    
    script_path = os.path.join(working_dir, script_name)
    
    try:
        # Write script to temporary file
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        # Execute the script
        result = execute_command(f"python3 {script_path}", working_dir=working_dir)
        
        # Clean up temporary file
        try:
            os.remove(script_path)
        except:
            pass
        
        return {
            **result,
            "script_content": script_content,
            "script_name": script_name,
            "operation": "python_script_execution"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute Python script: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def install_package(package_name: str, pip_command: str = "pip3") -> Dict[str, Any]:
    """
    Install a Python package using pip.
    
    Args:
        package_name: Name of package to install
        pip_command: Pip command to use (pip, pip3, python -m pip)
        
    Returns:
        Installation result
    """
    
    try:
        command = f"{pip_command} install {package_name}"
        result = execute_command(command, timeout=120)  # Longer timeout for installs
        
        return {
            **result,
            "package_name": package_name,
            "pip_command": pip_command,
            "operation": "package_installation"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to install package {package_name}: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        System information including OS, Python version, etc.
    """
    
    try:
        import platform
        
        # Basic system info
        info = {
            "success": True,
            "timestamp": time.time(),
            "system": {
                "os": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "architecture": platform.architecture(),
            },
            "python": {
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable": sys.executable,
                "path": sys.path[:3],  # First few entries
            },
            "environment": {
                "working_directory": os.getcwd(),
                "home_directory": os.path.expanduser("~"),
                "user": os.getenv("USER", "unknown"),
                "shell": os.getenv("SHELL", "unknown"),
            }
        }
        
        # Add additional command outputs
        commands_to_run = {
            "git_version": "git --version",
            "node_version": "node --version", 
            "npm_version": "npm --version",
            "brew_version": "brew --version"
        }
        
        for key, cmd in commands_to_run.items():
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    info[key] = result.stdout.strip()
            except:
                info[key] = "not available"
        
        return info
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get system info: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()
def run_instant_capture() -> Dict[str, Any]:
    """
    Start the instant AI capture system.
    
    Returns:
        Status of the capture system launch
    """
    
    try:
        # Check if the instant capture script exists
        script_path = "instant_capture_beautiful.py"
        if not os.path.exists(script_path):
            return {
                "success": False,
                "error": f"Instant capture script not found: {script_path}",
                "suggestion": "Run the setup script first: ./setup_beautiful_capture.sh"
            }
        
        # Launch the capture system in background
        command = f"python3 {script_path}"
        
        # For background execution, we'll start it and return immediately
        subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        return {
            "success": True,
            "command": command,
            "script_path": script_path,
            "status": "Instant AI Capture system started in background",
            "usage": "Press Cmd+Shift+T anywhere to capture tasks",
            "timestamp": time.time()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start instant capture: {str(e)}",
            "timestamp": time.time()
        }

@mcp.tool()  
def run_setup_script(script_name: str) -> Dict[str, Any]:
    """
    Run a setup script (like setup_beautiful_capture.sh).
    
    Args:
        script_name: Name of setup script to run
        
    Returns:
        Setup execution result
    """
    
    try:
        if not os.path.exists(script_name):
            return {
                "success": False,
                "error": f"Setup script not found: {script_name}"
            }
        
        # Make script executable
        os.chmod(script_name, 0o755)
        
        # Run the setup script
        result = execute_command(f"./{script_name}", timeout=120)
        
        return {
            **result,
            "script_name": script_name,
            "operation": "setup_script_execution"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to run setup script: {str(e)}",
            "timestamp": time.time()
        }

print("""
🔧 Command Execution Tools Added:
=================================
- execute_command: Run shell commands safely
- execute_python_script: Run Python code directly  
- install_package: Install Python packages
- get_system_info: Get system information
- run_instant_capture: Start instant AI capture
- run_setup_script: Run setup scripts

🛡️ Security Features:
- Command validation and forbidden command blocking
- Timeout protection (30s default, 120s for installs)
- Working directory control
- Output capture and error handling
""")
