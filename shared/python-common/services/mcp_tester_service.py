#!/usr/bin/env python3
"""
MCP Tester Service
==================

Service for running MCP protocol tests through the service manager.
Provides automated testing, monitoring, and validation of MCP servers.
"""

import os
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .service_base import ServiceBase


class MCPTesterService(ServiceBase):
    """Service for managing MCP protocol testing."""
    
    def __init__(self):
        super().__init__()
        self.service_name = "MCP_TESTER"
        self.description = "MCP Protocol Testing Service"
        
        # Service configuration
        self.test_script = "packages/mcp-server/mcp_protocol_tester.py"
        self.test_modes = ["direct", "proxy"]
        self.continuous_testing = False
        self.test_interval = 300  # 5 minutes default
        
        # Test results tracking
        self.last_test_results = {}
        self.test_history = []
        self.max_history = 50
        
    def get_status_details(self) -> Dict[str, Any]:
        """Get detailed service status including test results."""
        base_status = super().get_status_details()
        
        # Add MCP tester specific details
        base_status.update({
            "test_script": self.test_script,
            "test_modes": self.test_modes,
            "continuous_testing": self.continuous_testing,
            "test_interval": self.test_interval,
            "last_test_results": self.last_test_results,
            "test_history_count": len(self.test_history),
            "available_tests": self._get_available_tests()
        })
        
        return base_status
    
    def _get_available_tests(self) -> List[str]:
        """Get list of available tests from the tester script."""
        try:
            result = subprocess.run(
                ["python", self.test_script, "--list-tests"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse the test list from output
                lines = result.stdout.strip().split('\n')
                tests = []
                for line in lines:
                    if line.strip().startswith('- '):
                        tests.append(line.strip()[2:])
                return tests
            else:
                return ["Error getting test list"]
                
        except Exception as e:
            return [f"Error: {str(e)}"]
    
    def is_healthy(self) -> bool:
        """Check if the MCP tester service is healthy."""
        # Check if test script exists
        if not os.path.exists(self.test_script):
            return False
        
        # Check if we can run the help command
        try:
            result = subprocess.run(
                ["python", self.test_script, "--list-tests"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_dependencies(self) -> List[str]:
        """Get service dependencies."""
        # MCP tester depends on the MCP server being available
        return ["MCP"]
    
    def start_service(self) -> bool:
        """Start the MCP tester service (continuous mode)."""
        if self.continuous_testing:
            try:
                # Start continuous testing in background
                self.service_process = subprocess.Popen(
                    ["python", self.test_script, "--verbose"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                time.sleep(2)  # Give it time to start
                
                if self.service_process.poll() is None:
                    self.is_running = True
                    return True
                else:
                    return False
                    
            except Exception as e:
                self.last_error = str(e)
                return False
        else:
            # For non-continuous mode, we're always "running" 
            # as tests are run on-demand
            self.is_running = True
            return True
    
    def stop_service(self) -> bool:
        """Stop the MCP tester service."""
        self.continuous_testing = False
        
        if self.service_process:
            try:
                self.service_process.terminate()
                self.service_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.service_process.kill()
                self.service_process.wait()
            
            self.service_process = None
        
        self.is_running = False
        return True
    
    def run_test(self, test_name: Optional[str] = None, mode: str = "direct", verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test or all tests."""
        cmd = ["python", self.test_script]
        
        if verbose:
            cmd.append("--verbose")
        
        if mode in self.test_modes:
            cmd.extend(["--mode", mode])
        
        if test_name:
            cmd.extend(["--test", test_name])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            test_result = {
                "success": result.returncode == 0,
                "mode": mode,
                "test_name": test_name or "all",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timestamp": time.time()
            }
            
            # Store results
            self.last_test_results[f"{mode}_{test_name or 'all'}"] = test_result
            self._add_to_history(test_result)
            
            return test_result
            
        except subprocess.TimeoutExpired:
            error_result = {
                "success": False,
                "error": "Test timed out",
                "mode": mode,
                "test_name": test_name or "all",
                "timestamp": time.time()
            }
            self.last_test_results[f"{mode}_{test_name or 'all'}"] = error_result
            return error_result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "mode": mode,
                "test_name": test_name or "all",
                "timestamp": time.time()
            }
            self.last_test_results[f"{mode}_{test_name or 'all'}"] = error_result
            return error_result
    
    def run_comparative_tests(self) -> Dict[str, Any]:
        """Run tests against both direct and proxy modes for comparison."""
        results = {}
        
        for mode in self.test_modes:
            self.log(f"Running tests in {mode} mode...")
            results[mode] = self.run_test(mode=mode, verbose=True)
        
        # Generate comparison
        comparison = self._compare_test_results(results)
        results["comparison"] = comparison
        
        return results
    
    def _compare_test_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare test results between different modes."""
        comparison = {
            "modes_tested": list(results.keys()),
            "all_passed": all(r.get("success", False) for r in results.values()),
            "differences": [],
            "performance": {}
        }
        
        # Check for differences in success/failure
        if len(results) >= 2:
            modes = list(results.keys())
            for i, mode1 in enumerate(modes):
                for mode2 in modes[i+1:]:
                    r1 = results[mode1]
                    r2 = results[mode2]
                    
                    if r1.get("success") != r2.get("success"):
                        comparison["differences"].append({
                            "type": "success_mismatch",
                            "mode1": mode1,
                            "mode2": mode2,
                            "mode1_success": r1.get("success"),
                            "mode2_success": r2.get("success")
                        })
        
        return comparison
    
    def _add_to_history(self, result: Dict[str, Any]):
        """Add test result to history."""
        self.test_history.append(result)
        
        # Trim history if too long
        if len(self.test_history) > self.max_history:
            self.test_history = self.test_history[-self.max_history:]
    
    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of recent test results."""
        if not self.test_history:
            return {"message": "No tests have been run yet"}
        
        recent_tests = self.test_history[-10:]  # Last 10 tests
        
        summary = {
            "total_tests_run": len(self.test_history),
            "recent_tests": len(recent_tests),
            "recent_success_rate": sum(1 for t in recent_tests if t.get("success", False)) / len(recent_tests),
            "recent_tests_details": recent_tests,
            "available_modes": self.test_modes,
            "service_healthy": self.is_healthy()
        }
        
        return summary
    
    def enable_continuous_testing(self, interval: int = 300):
        """Enable continuous testing mode."""
        self.continuous_testing = True
        self.test_interval = interval
        self.log(f"Enabled continuous testing with {interval}s interval")
    
    def disable_continuous_testing(self):
        """Disable continuous testing mode."""
        self.continuous_testing = False
        self.log("Disabled continuous testing")
    
    def log(self, message: str, level: str = "INFO"):
        """Log a message with service context."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [MCP_TESTER] [{level}] {message}") 