"""
Tool Execution Engine
====================

Executes native tools with parameter validation, security checks,
and process management for both one-time and persistent tools.
"""

import subprocess
import os
import signal
import time
import json
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import logging
import asyncio

logger = logging.getLogger(__name__)

class ToolExecutor:
    """Executes native tools with security and process management."""
    
    def __init__(self):
        self.running_processes = {}  # Track persistent processes
        self.execution_history = []
    
    def execute_tool(
        self,
        tool_name: str,
        tool_config: Dict[str, Any],
        parameters: Dict[str, Any] = None,
        mode: str = "once"
    ) -> Dict[str, Any]:
        """
        Execute a native tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            tool_config: Tool configuration from registry
            parameters: Parameters to pass to the tool
            mode: Execution mode ("once", "persistent", "background")
        
        Returns:
            Execution result with output, status, and metadata
        """
        if parameters is None:
            parameters = {}
        
        # Validate execution mode
        if mode not in ["once", "persistent", "background"]:
            return {
                "success": False,
                "error": f"Invalid execution mode: {mode}",
                "tool_name": tool_name
            }
        
        # Check if tool requires review
        if tool_config.get("requires_review", False):
            return {
                "success": False,
                "error": "Tool requires manual review approval",
                "tool_name": tool_name,
                "requires_approval": True
            }
        
        # Check if persistent mode is supported
        if mode in ["persistent", "background"] and not tool_config.get("supports_persistent", False):
            return {
                "success": False,
                "error": f"Tool does not support {mode} mode",
                "tool_name": tool_name
            }
        
        try:
            # Validate and prepare parameters
            validated_params = self._validate_parameters(tool_config, parameters)
            if "error" in validated_params:
                return {
                    "success": False,
                    "error": validated_params["error"],
                    "tool_name": tool_name
                }
            
            # Build command
            command = self._build_command(tool_config, validated_params["parameters"])
            if "error" in command:
                return {
                    "success": False,
                    "error": command["error"],
                    "tool_name": tool_name
                }
            
            # Execute based on mode
            if mode == "once":
                return self._execute_once(tool_name, command, tool_config)
            elif mode == "persistent":
                return self._execute_persistent(tool_name, command, tool_config)
            elif mode == "background":
                return self._execute_background(tool_name, command, tool_config)
            
        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "tool_name": tool_name
            }
    
    def _validate_parameters(self, tool_config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and prepare tool parameters."""
        param_definitions = tool_config.get("parameters", {})
        validated = {}
        
        # Check required parameters
        for param_name, param_def in param_definitions.items():
            if param_def.get("required", False) and param_name not in parameters:
                return {"error": f"Required parameter missing: {param_name}"}
        
        # Validate and convert parameters
        for param_name, param_def in param_definitions.items():
            value = parameters.get(param_name)
            
            if value is None:
                # Use default if available
                if "default" in param_def:
                    validated[param_name] = param_def["default"]
                continue
            
            # Type validation and conversion
            param_type = param_def.get("type", "string")
            try:
                if param_type == "string":
                    validated[param_name] = str(value)
                elif param_type == "integer":
                    validated[param_name] = int(value)
                elif param_type == "boolean":
                    validated[param_name] = bool(value)
                elif param_type == "float":
                    validated[param_name] = float(value)
                else:
                    validated[param_name] = value
            except (ValueError, TypeError):
                return {"error": f"Invalid type for parameter {param_name}: expected {param_type}"}
            
            # Validate options if specified
            options = param_def.get("options")
            if options and validated[param_name] not in options:
                return {"error": f"Invalid value for {param_name}: must be one of {options}"}
        
        return {"parameters": validated}
    
    def _build_command(self, tool_config: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Build the command to execute."""
        # Check for module-based execution first
        module_name = tool_config.get("module")
        function_name = tool_config.get("function")
        
        if module_name and function_name:
            # Module-based execution
            return {
                "type": "module",
                "module": module_name,
                "function": function_name,
                "parameters": parameters
            }
        
        # Check for script vs command template
        script = tool_config.get("script")
        command_template = tool_config.get("command_template")
        
        if script:
            # Script-based execution
            script_path = Path(script)
            
            # Try to find script in common locations
            search_paths = [
                script_path,
                Path.cwd() / script_path,
                Path.cwd().parent / script_path
            ]
            
            found_script = None
            for path in search_paths:
                if path.exists():
                    found_script = path
                    break
            
            if not found_script:
                return {"error": f"Script not found: {script}"}
            
            # Build command with parameters
            cmd_parts = ["python3", str(found_script)]
            
            # Add parameters as command line arguments
            for param_name, param_value in parameters.items():
                if isinstance(param_value, bool):
                    if param_value:
                        cmd_parts.append(f"--{param_name}")
                else:
                    cmd_parts.extend([f"--{param_name}", str(param_value)])
            
            return {"type": "subprocess", "command": cmd_parts}
        
        elif command_template:
            # Template-based execution
            try:
                command = command_template.format(**parameters)
                return {"type": "subprocess", "command": command.split()}
            except KeyError as e:
                return {"error": f"Missing parameter for template: {e}"}
        
        else:
            return {"error": "No execution method configured"}
    
    def _execute_once(self, tool_name: str, command: Dict[str, Any], tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool once and return results."""
        try:
            if command["type"] == "module":
                # Module-based execution
                module_name = command["module"]
                function_name = command["function"]
                parameters = command["parameters"]
                
                # Import the module dynamically
                module = importlib.import_module(module_name)
                
                # Get the function
                function = getattr(module, function_name)
                
                # Call the function with parameters
                result = function(**parameters)
                
                execution_result = {
                    "success": True,
                    "tool_name": tool_name,
                    "returncode": 0,  # Module execution doesn't have a direct returncode
                    "stdout": str(result),
                    "stderr": "",
                    "execution_mode": "once",
                    "timestamp": time.time()
                }
                
            else:  # subprocess
                command_parts = command["command"]
                result = subprocess.run(
                    command_parts,
                    capture_output=True,
                    text=True,
                    timeout=tool_config.get("timeout", 60)
                )
                
                execution_result = {
                    "success": result.returncode == 0,
                    "tool_name": tool_name,
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "execution_mode": "once",
                    "timestamp": time.time()
                }
            
            # Add to history
            self.execution_history.append(execution_result.copy())
            
            return execution_result
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Tool execution timed out",
                "tool_name": tool_name,
                "execution_mode": "once"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution failed: {str(e)}",
                "tool_name": tool_name,
                "execution_mode": "once"
            }
    
    def _execute_persistent(self, tool_name: str, command: Dict[str, Any], tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool as persistent process."""
        # Check if already running
        if tool_name in self.running_processes:
            proc = self.running_processes[tool_name]
            if proc["process"].poll() is None:  # Still running
                return {
                    "success": True,
                    "message": f"Tool {tool_name} is already running",
                    "tool_name": tool_name,
                    "execution_mode": "persistent",
                    "pid": proc["process"].pid,
                    "status": "already_running"
                }
            else:
                # Process died, remove from tracking
                del self.running_processes[tool_name]
        
        try:
            if command["type"] == "module":
                # Module-based execution (not truly persistent, but we'll track it)
                module_name = command["module"]
                function_name = command["function"]
                parameters = command["parameters"]
                
                # Import the module dynamically
                module = importlib.import_module(module_name)
                
                # Get the function
                function = getattr(module, function_name)
                
                # Call the function with parameters
                result = function(**parameters)
                
                # Track as a "module process" (not a real subprocess)
                self.running_processes[tool_name] = {
                    "process": None,  # No real process
                    "command": command,
                    "started_at": time.time(),
                    "tool_config": tool_config,
                    "module_result": result
                }
                
                return {
                    "success": True,
                    "message": f"Started persistent module tool: {tool_name}",
                    "tool_name": tool_name,
                    "execution_mode": "persistent",
                    "pid": 0,  # No real PID
                    "status": "started",
                    "result": str(result)
                }
                
            else:  # subprocess
                command_parts = command["command"]
                process = subprocess.Popen(
                    command_parts,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Track the process
                self.running_processes[tool_name] = {
                    "process": process,
                    "command": command,
                    "started_at": time.time(),
                    "tool_config": tool_config
                }
                
                return {
                    "success": True,
                    "message": f"Started persistent tool: {tool_name}",
                    "tool_name": tool_name,
                    "execution_mode": "persistent",
                    "pid": process.pid,
                    "status": "started"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start persistent tool: {str(e)}",
                "tool_name": tool_name,
                "execution_mode": "persistent"
            }
    
    def _execute_background(self, tool_name: str, command: Dict[str, Any], tool_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool in background (fire and forget)."""
        try:
            if command["type"] == "module":
                # Module-based execution
                module_name = command["module"]
                function_name = command["function"]
                parameters = command["parameters"]
                
                # Import the module dynamically
                module = importlib.import_module(module_name)
                
                # Get the function
                function = getattr(module, function_name)
                
                # Call the function with parameters (fire and forget)
                function(**parameters)
                
                return {
                    "success": True,
                    "message": f"Started background module tool: {tool_name}",
                    "tool_name": tool_name,
                    "execution_mode": "background",
                    "pid": 0,  # No real PID
                    "status": "started"
                }
                
            else:  # subprocess
                command_parts = command["command"]
                process = subprocess.Popen(
                    command_parts,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
                return {
                    "success": True,
                    "message": f"Started background tool: {tool_name}",
                    "tool_name": tool_name,
                    "execution_mode": "background",
                    "pid": process.pid,
                    "status": "started"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to start background tool: {str(e)}",
                "tool_name": tool_name,
                "execution_mode": "background"
            }
    
    def stop_tool(self, tool_name: str) -> Dict[str, Any]:
        """Stop a persistent or background tool."""
        if tool_name not in self.running_processes:
            return {
                "success": False,
                "error": f"Tool {tool_name} is not running",
                "tool_name": tool_name
            }
        
        try:
            proc_info = self.running_processes[tool_name]
            process = proc_info["process"]
            
            # Handle module-based tools (no real process to terminate)
            if process is None:
                del self.running_processes[tool_name]
                return {
                    "success": True,
                    "message": f"Stopped module tool: {tool_name}",
                    "tool_name": tool_name
                }
            
            # Handle subprocess-based tools
            # Try graceful termination first
            process.terminate()
            
            # Wait for termination
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                process.kill()
                process.wait()
            
            del self.running_processes[tool_name]
            
            return {
                "success": True,
                "message": f"Stopped tool: {tool_name}",
                "tool_name": tool_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to stop tool: {str(e)}",
                "tool_name": tool_name
            }
    
    def get_tool_status(self, tool_name: str = None) -> Dict[str, Any]:
        """Get status of running tools."""
        if tool_name:
            if tool_name not in self.running_processes:
                return {"status": "not_running", "tool_name": tool_name}
            
            proc_info = self.running_processes[tool_name]
            process = proc_info["process"]
            
            # Handle module-based tools (no real process)
            if process is None:
                return {
                    "status": "running",
                    "tool_name": tool_name,
                    "pid": 0,  # No real PID for module tools
                    "started_at": proc_info["started_at"],
                    "runtime": time.time() - proc_info["started_at"],
                    "type": "module"
                }
            
            # Handle subprocess-based tools
            if process.poll() is None:
                return {
                    "status": "running",
                    "tool_name": tool_name,
                    "pid": process.pid,
                    "started_at": proc_info["started_at"],
                    "runtime": time.time() - proc_info["started_at"],
                    "type": "subprocess"
                }
            else:
                # Process died
                del self.running_processes[tool_name]
                return {"status": "stopped", "tool_name": tool_name}
        
        else:
            # Return status of all tools
            statuses = {}
            for name, proc_info in list(self.running_processes.items()):
                process = proc_info["process"]
                
                # Handle module-based tools
                if process is None:
                    statuses[name] = {
                        "status": "running",
                        "pid": 0,
                        "started_at": proc_info["started_at"],
                        "runtime": time.time() - proc_info["started_at"],
                        "type": "module"
                    }
                    continue
                
                # Handle subprocess-based tools
                if process.poll() is None:
                    statuses[name] = {
                        "status": "running",
                        "pid": process.pid,
                        "started_at": proc_info["started_at"],
                        "runtime": time.time() - proc_info["started_at"],
                        "type": "subprocess"
                    }
                else:
                    statuses[name] = {"status": "stopped"}
                    del self.running_processes[name]
            
            return {"running_tools": statuses}
