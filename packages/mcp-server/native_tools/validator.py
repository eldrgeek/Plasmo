"""
Tool Validation System
=====================

Validates tool configurations, checks dependencies, and ensures tools
are executable before they are used by LLMs.
"""

import subprocess
import shutil
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class ToolValidator:
    """Validates tool configurations and runtime requirements."""
    
    def __init__(self):
        self.validation_cache = {}
    
    def validate_tool(self, tool_name: str, tool_config: Dict[str, Any], full_test: bool = False) -> Dict[str, Any]:
        """
        Validate a tool's configuration and runtime requirements.
        
        Args:
            tool_name: Name of the tool
            tool_config: Tool configuration from registry
            full_test: Whether to run full validation including test commands
        
        Returns:
            Validation result with status and details
        """
        result = {
            "tool_name": tool_name,
            "valid": True,
            "checks": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # Check 1: Basic configuration validation
            self._validate_config_structure(tool_config, result)
            
            # Check 2: Script/command existence
            self._validate_script_existence(tool_config, result)
            
            # Check 3: Dependencies validation
            self._validate_dependencies(tool_config, result)
            
            # Check 4: Parameters validation
            self._validate_parameters(tool_config, result)
            
            # Check 5: Test command (if requested and configured)
            if full_test:
                self._validate_test_command(tool_config, result)
            
            # Final validation status
            result["valid"] = len(result["errors"]) == 0
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        return result
    
    def _validate_config_structure(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate basic configuration structure."""
        required_fields = ["name", "description", "category"]
        
        for field in required_fields:
            if field not in config:
                result["errors"].append(f"Missing required field: {field}")
            else:
                result["checks"][f"has_{field}"] = True
        
        # Check for execution method
        has_script = "script" in config
        has_command = "command_template" in config
        
        if not has_script and not has_command:
            result["errors"].append("Tool must have either 'script' or 'command_template'")
        else:
            result["checks"]["has_execution_method"] = True
    
    def _validate_script_existence(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate that script files exist."""
        script = config.get("script")
        
        if script:
            script_path = Path(script)
            
            # Check relative to current directory and common script locations
            search_paths = [
                script_path,
                Path.cwd() / script_path,
                Path.cwd() / "scripts" / script_path.name,
                Path.cwd().parent / script_path  # Check parent directory
            ]
            
            script_found = False
            for path in search_paths:
                if path.exists() and path.is_file():
                    result["checks"]["script_exists"] = True
                    result["checks"]["script_path"] = str(path.resolve())
                    script_found = True
                    break
            
            if not script_found:
                result["errors"].append(f"Script not found: {script}")
                result["checks"]["script_exists"] = False
    
    def _validate_dependencies(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate that tool dependencies are available."""
        validation = config.get("validation", {})
        dependencies = validation.get("dependencies", [])
        
        for dep in dependencies:
            available = self._check_dependency_available(dep)
            result["checks"][f"dependency_{dep}"] = available
            
            if not available:
                result["warnings"].append(f"Dependency not found: {dep}")
    
    def _check_dependency_available(self, dependency: str) -> bool:
        """Check if a dependency is available."""
        # Check if it's a command
        if shutil.which(dependency):
            return True
        
        # Check if it's a Python module
        if dependency.startswith("python") or dependency in ["python3", "python"]:
            return shutil.which("python3") is not None or shutil.which("python") is not None
        
        # Check for common dependencies
        common_deps = {
            "chrome": lambda: shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chrome"),
            "tkinter": lambda: self._check_python_module("tkinter"),
            "pip3": lambda: shutil.which("pip3") or shutil.which("pip"),
        }
        
        if dependency in common_deps:
            return common_deps[dependency]()
        
        # Default: check as command
        return shutil.which(dependency) is not None
    
    def _check_python_module(self, module_name: str) -> bool:
        """Check if a Python module is available."""
        try:
            subprocess.run(
                ["python3", "-c", f"import {module_name}"],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _validate_parameters(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Validate tool parameter definitions."""
        parameters = config.get("parameters", {})
        
        for param_name, param_config in parameters.items():
            if not isinstance(param_config, dict):
                result["warnings"].append(f"Parameter '{param_name}' should be a dictionary")
                continue
            
            # Check parameter type
            param_type = param_config.get("type")
            if not param_type:
                result["warnings"].append(f"Parameter '{param_name}' missing type")
            elif param_type not in ["string", "integer", "boolean", "float"]:
                result["warnings"].append(f"Parameter '{param_name}' has unknown type: {param_type}")
            
            # Check required parameters have no default
            if param_config.get("required", False) and "default" in param_config:
                result["warnings"].append(f"Required parameter '{param_name}' should not have default value")
        
        result["checks"]["parameters_validated"] = True
    
    def _validate_test_command(self, config: Dict[str, Any], result: Dict[str, Any]):
        """Run the tool's test command if configured."""
        validation = config.get("validation", {})
        test_command = validation.get("test_command")
        
        if not test_command:
            result["checks"]["test_command"] = "not_configured"
            return
        
        try:
            # Run test command with timeout
            test_result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if test_result.returncode == 0:
                result["checks"]["test_command"] = "passed"
            else:
                result["checks"]["test_command"] = "failed"
                result["warnings"].append(f"Test command failed: {test_result.stderr}")
                
        except subprocess.TimeoutExpired:
            result["checks"]["test_command"] = "timeout"
            result["warnings"].append("Test command timed out")
        except Exception as e:
            result["checks"]["test_command"] = "error"
            result["warnings"].append(f"Test command error: {str(e)}")
    
    def validate_all_tools(self, tools: Dict[str, Dict[str, Any]], full_test: bool = False) -> Dict[str, Dict[str, Any]]:
        """Validate all tools in the registry."""
        results = {}
        
        for tool_name, tool_config in tools.items():
            results[tool_name] = self.validate_tool(tool_name, tool_config, full_test)
        
        return results
    
    def get_validation_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of validation results."""
        total_tools = len(results)
        valid_tools = sum(1 for r in results.values() if r["valid"])
        tools_with_warnings = sum(1 for r in results.values() if r["warnings"])
        tools_with_errors = sum(1 for r in results.values() if r["errors"])
        
        return {
            "total_tools": total_tools,
            "valid_tools": valid_tools,
            "tools_with_warnings": tools_with_warnings,
            "tools_with_errors": tools_with_errors,
            "validation_rate": valid_tools / total_tools if total_tools > 0 else 0
        }
