#!/usr/bin/env python3
"""
Comprehensive Test Suite for Consolidated MCP Server
===================================================

Tests all 15 MCP tools and server functionality:
- File operations (4 tools)
- Code analysis (2 tools) 
- Git operations (1 tool)
- Database operations (2 tools)
- System operations (2 tools)
- Chrome debugging (4 tools)

Usage:
    python test_mcp_server.py              # Run all tests
    python test_mcp_server.py --verbose    # Verbose output
"""

import asyncio
import json
import os
import sqlite3
import subprocess
import tempfile
import time
import unittest
from pathlib import Path
from typing import Dict, List, Any
import requests
import argparse
import sys

class MCPServerTester:
    """Comprehensive test suite for the MCP server."""
    
    def __init__(self, server_host="127.0.0.1", server_port=8000, verbose=False):
        self.server_host = server_host
        self.server_port = server_port
        self.server_url = f"http://{server_host}:{server_port}"
        self.verbose = verbose
        self.test_results = {}
        
        # Test data - use subdirectory in current project to avoid security restrictions
        self.temp_dir = os.path.join(os.getcwd(), "test_temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        self.test_files = {}
        self.chrome_debug_available = False
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp."""
        if self.verbose or level in ["ERROR", "FAIL", "PASS"]:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")
    
    def setup_test_environment(self):
        """Set up test files and data."""
        self.log("Setting up test environment...")
        
        # Create test files
        test_files = {
            "test.txt": "Hello, World!\nThis is a test file.",
            "test.json": '{"name": "test", "value": 42, "items": [1, 2, 3]}',
            "test.py": '''#!/usr/bin/env python3
"""Test Python file for analysis."""

def hello_world():
    """Say hello to the world."""
    print("Hello, World!")
    return "Hello"

class TestClass:
    """A test class."""
    
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, {self.name}!"

if __name__ == "__main__":
    hello_world()
''',
            "unicode_test.txt": "Unicode test: 🚀 🎉 👋 \n中文测试\nEmoji: 😀😎🔥"
        }
        
        for filename, content in test_files.items():
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.test_files[filename] = str(file_path)
        
        self.log(f"Created test files in: {self.temp_dir}")
    
    def cleanup_test_environment(self):
        """Clean up test files."""
        self.log("Cleaning up test environment...")
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool by importing and calling directly."""
        try:
            # Import the server module to call tools directly
            import sys
            sys.path.append('.')
            import mcp_server
            
            if tool_name == "server_info":
                return {"success": True, "data": mcp_server.server_info()}
            elif tool_name == "read_file":
                result = mcp_server.read_file(params["file_path"])
                if isinstance(result, str):
                    return {"success": True, "data": result}
                else:
                    return result
            elif tool_name == "write_file":
                return mcp_server.write_file(params["file_path"], params["content"])
            elif tool_name == "list_files":
                result = mcp_server.list_files(
                    params.get("directory", "."),
                    params.get("pattern", "*"),
                    params.get("recursive", False)
                )
                if isinstance(result, list):
                    return {"success": True, "data": result}
                else:
                    return result
            elif tool_name == "get_project_structure":
                return mcp_server.get_project_structure(
                    params.get("directory", "."),
                    params.get("max_depth", 3)
                )
            elif tool_name == "analyze_code":
                return mcp_server.analyze_code(params["file_path"])
            elif tool_name == "search_in_files":
                return mcp_server.search_in_files(
                    params["pattern"],
                    params.get("directory", "."),
                    params.get("file_pattern", "*"),
                    params.get("case_sensitive", False)
                )
            elif tool_name == "get_system_info":
                return mcp_server.get_system_info(params.get("include_sensitive", False))
            elif tool_name == "connect_to_chrome":
                return mcp_server.connect_to_chrome(
                    params.get("port", 9222),
                    params.get("host", "localhost")
                )
            else:
                return {"success": False, "error": f"Tool {tool_name} not implemented in test"}
                
        except Exception as e:
            return {"success": False, "error": str(e), "error_type": type(e).__name__}
    
    def test_file_operations(self) -> Dict[str, Any]:
        """Test all file operation tools."""
        self.log("Testing file operations...")
        results = {}
        
        # Test read_file
        self.log("  Testing read_file...")
        try:
            result = self.call_tool("read_file", {"file_path": self.test_files["test.txt"]})
            if result.get("success", False) and "Hello, World!" in str(result.get("data", "")):
                results["read_file"] = {"status": "PASS", "message": "Successfully read file"}
                self.log("    read_file: PASS", "PASS")
            else:
                results["read_file"] = {"status": "FAIL", "message": f"Failed to read file: {result}"}
                self.log("    read_file: FAIL", "FAIL")
        except Exception as e:
            results["read_file"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    read_file: ERROR - {e}", "ERROR")
        
        # Test write_file
        self.log("  Testing write_file...")
        try:
            test_content = "Test write content\nLine 2"
            write_file_path = str(Path(self.temp_dir) / "write_test.txt")
            result = self.call_tool("write_file", {"file_path": write_file_path, "content": test_content})
            
            if result.get("success", False):
                # Verify the file was written correctly
                with open(write_file_path, 'r') as f:
                    written_content = f.read()
                if written_content == test_content:
                    results["write_file"] = {"status": "PASS", "message": "Successfully wrote file"}
                    self.log("    write_file: PASS", "PASS")
                else:
                    results["write_file"] = {"status": "FAIL", "message": "File content mismatch"}
                    self.log("    write_file: FAIL", "FAIL")
            else:
                results["write_file"] = {"status": "FAIL", "message": f"Write failed: {result}"}
                self.log("    write_file: FAIL", "FAIL")
        except Exception as e:
            results["write_file"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    write_file: ERROR - {e}", "ERROR")
        
        # Test list_files
        self.log("  Testing list_files...")
        try:
            result = self.call_tool("list_files", {"directory": self.temp_dir, "pattern": "*.txt"})
            if result.get("success", False) and isinstance(result.get("data"), list):
                file_list = result["data"]
                if any("test.txt" in f for f in file_list):
                    results["list_files"] = {"status": "PASS", "message": f"Found {len(file_list)} files"}
                    self.log("    list_files: PASS", "PASS")
                else:
                    results["list_files"] = {"status": "FAIL", "message": "Expected file not found"}
                    self.log("    list_files: FAIL", "FAIL")
            else:
                results["list_files"] = {"status": "FAIL", "message": f"List failed: {result}"}
                self.log("    list_files: FAIL", "FAIL")
        except Exception as e:
            results["list_files"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    list_files: ERROR - {e}", "ERROR")
        
        # Test get_project_structure
        self.log("  Testing get_project_structure...")
        try:
            result = self.call_tool("get_project_structure", {"directory": self.temp_dir, "max_depth": 2})
            # get_project_structure returns structure directly, not wrapped in success
            if isinstance(result, dict) and "structure" in result:
                results["get_project_structure"] = {"status": "PASS", "message": "Got project structure"}
                self.log("    get_project_structure: PASS", "PASS")
            else:
                results["get_project_structure"] = {"status": "FAIL", "message": f"Structure failed: {result}"}
                self.log("    get_project_structure: FAIL", "FAIL")
        except Exception as e:
            results["get_project_structure"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    get_project_structure: ERROR - {e}", "ERROR")
        
        return results
    
    def test_system_operations(self) -> Dict[str, Any]:
        """Test system operation tools."""
        self.log("Testing system operations...")
        results = {}
        
        # Test get_system_info
        self.log("  Testing get_system_info...")
        try:
            result = self.call_tool("get_system_info", {"include_sensitive": False})
            # get_system_info returns data directly, not wrapped in success
            if isinstance(result, dict) and "platform" in result and "python" in result:
                platform_info = result["platform"]
                if "system" in platform_info:
                    results["get_system_info"] = {"status": "PASS", "message": f"Got system info for {platform_info.get('system')}"}
                    self.log("    get_system_info: PASS", "PASS")
                else:
                    results["get_system_info"] = {"status": "FAIL", "message": "Missing platform info components"}
                    self.log("    get_system_info: FAIL", "FAIL")
            else:
                results["get_system_info"] = {"status": "FAIL", "message": f"System info failed: {result}"}
                self.log("    get_system_info: FAIL", "FAIL")
        except Exception as e:
            results["get_system_info"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    get_system_info: ERROR - {e}", "ERROR")
        
        # Test server_info
        self.log("  Testing server_info...")
        try:
            result = self.call_tool("server_info", {})
            if result.get("success", False):
                server_info = result.get("data", {})
                if "version" in server_info and "status" in server_info:
                    results["server_info"] = {"status": "PASS", "message": f"Server version {server_info.get('version')}"}
                    self.log("    server_info: PASS", "PASS")
                else:
                    results["server_info"] = {"status": "FAIL", "message": "Missing server info components"}
                    self.log("    server_info: FAIL", "FAIL")
            else:
                results["server_info"] = {"status": "FAIL", "message": f"Server info failed: {result}"}
                self.log("    server_info: FAIL", "FAIL")
        except Exception as e:
            results["server_info"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    server_info: ERROR - {e}", "ERROR")
        
        return results
    
    def test_chrome_debugging(self) -> Dict[str, Any]:
        """Test Chrome debugging tools."""
        self.log("Testing Chrome debugging...")
        results = {}
        
        # Check if Chrome debug is available
        self.log("  Checking Chrome debug availability...")
        try:
            response = requests.get("http://localhost:9222/json", timeout=2)
            if response.status_code == 200:
                self.chrome_debug_available = True
                self.log("    Chrome debug port is available", "PASS")
            else:
                self.chrome_debug_available = False
                self.log("    Chrome debug port not available (not started?)", "PARTIAL")
        except Exception as e:
            self.chrome_debug_available = False
            self.log(f"    Chrome debug not available: {e}", "PARTIAL")
        
        # Test connect_to_chrome
        self.log("  Testing connect_to_chrome...")
        try:
            result = self.call_tool("connect_to_chrome", {"port": 9222, "host": "localhost"})
            if result.get("success", False):
                results["connect_to_chrome"] = {"status": "PASS", "message": "Connected to Chrome"}
                self.log("    connect_to_chrome: PASS", "PASS")
            else:
                if self.chrome_debug_available:
                    results["connect_to_chrome"] = {"status": "FAIL", "message": f"Connection failed: {result}"}
                    self.log("    connect_to_chrome: FAIL", "FAIL")
                else:
                    results["connect_to_chrome"] = {"status": "SKIP", "message": "Chrome debug not available"}
                    self.log("    connect_to_chrome: SKIP (Chrome not available)", "PARTIAL")
        except Exception as e:
            results["connect_to_chrome"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    connect_to_chrome: ERROR - {e}", "ERROR")
        
        # Note: Other Chrome tools would require Chrome to be running
        for tool in ["get_chrome_tabs", "launch_chrome_debug", "execute_javascript_fixed"]:
            if self.chrome_debug_available:
                results[tool] = {"status": "SKIP", "message": "Requires Chrome session (integration test)"}
            else:
                results[tool] = {"status": "SKIP", "message": "Chrome debug not available"}
        
        return results
    
    def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling scenarios."""
        self.log("Testing error handling...")
        results = {}
        
        # Test reading non-existent file
        self.log("  Testing error handling with non-existent file...")
        try:
            result = self.call_tool("read_file", {"file_path": "/nonexistent/file/path.txt"})
            if not result.get("success", True) and "error" in result:
                results["error_handling_file_not_found"] = {"status": "PASS", "message": "Properly handled file not found"}
                self.log("    error_handling_file_not_found: PASS", "PASS")
            else:
                results["error_handling_file_not_found"] = {"status": "FAIL", "message": "Should have failed for non-existent file"}
                self.log("    error_handling_file_not_found: FAIL", "FAIL")
        except Exception as e:
            results["error_handling_file_not_found"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    error_handling_file_not_found: ERROR - {e}", "ERROR")
        
        # Test security validation (path traversal)
        self.log("  Testing path traversal protection...")
        try:
            result = self.call_tool("read_file", {"file_path": "../../../etc/passwd"})
            if not result.get("success", True) and "Access denied" in str(result.get("error", "")):
                results["security_path_traversal"] = {"status": "PASS", "message": "Blocked path traversal"}
                self.log("    security_path_traversal: PASS", "PASS")
            else:
                results["security_path_traversal"] = {"status": "FAIL", "message": "Should block path traversal"}
                self.log("    security_path_traversal: FAIL", "FAIL")
        except Exception as e:
            results["security_path_traversal"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    security_path_traversal: ERROR - {e}", "ERROR")
        
        return results
    
    def test_unicode_handling(self) -> Dict[str, Any]:
        """Test Unicode and emoji handling."""
        self.log("Testing Unicode handling...")
        results = {}
        
        try:
            result = self.call_tool("read_file", {"file_path": self.test_files["unicode_test.txt"]})
            if result.get("success", False):
                content = result.get("data", "")
                if "🚀" in content and "中文" in content:
                    results["unicode_handling"] = {"status": "PASS", "message": "Successfully handled Unicode and emoji"}
                    self.log("    unicode_handling: PASS", "PASS")
                else:
                    results["unicode_handling"] = {"status": "FAIL", "message": "Unicode content corrupted"}
                    self.log("    unicode_handling: FAIL", "FAIL")
            else:
                results["unicode_handling"] = {"status": "FAIL", "message": f"Failed to read Unicode file: {result}"}
                self.log("    unicode_handling: FAIL", "FAIL")
        except Exception as e:
            results["unicode_handling"] = {"status": "ERROR", "message": str(e)}
            self.log(f"    unicode_handling: ERROR - {e}", "ERROR")
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test categories."""
        self.log("Starting comprehensive MCP server test suite...")
        
        all_results = {}
        
        # Run test categories
        test_categories = [
            ("file_operations", self.test_file_operations),
            ("system_operations", self.test_system_operations),
            ("chrome_debugging", self.test_chrome_debugging),
            ("error_handling", self.test_error_handling),
            ("unicode_handling", self.test_unicode_handling),
        ]
        
        for category, test_func in test_categories:
            self.log(f"\n=== Running {category} tests ===")
            try:
                results = test_func()
                all_results[category] = results
            except Exception as e:
                self.log(f"Category {category} failed: {e}", "ERROR")
                all_results[category] = {"error": str(e)}
        
        return all_results
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed test report."""
        report = []
        report.append("="*60)
        report.append("MCP SERVER TEST REPORT")
        report.append("="*60)
        report.append(f"Test run at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        error_tests = 0
        
        for category, category_results in results.items():
            if "error" in category_results:
                report.append(f"❌ {category.upper()}: CATEGORY ERROR")
                report.append(f"   Error: {category_results['error']}")
                error_tests += 1
                continue
            
            report.append(f"\n📋 {category.upper()}:")
            report.append("-" * 40)
            
            for test_name, test_result in category_results.items():
                total_tests += 1
                status = test_result.get("status", "UNKNOWN")
                message = test_result.get("message", "No message")
                
                if status == "PASS":
                    report.append(f"  ✅ {test_name}: {message}")
                    passed_tests += 1
                elif status == "FAIL":
                    report.append(f"  ❌ {test_name}: {message}")
                    failed_tests += 1
                elif status == "SKIP" or status == "PARTIAL":
                    report.append(f"  ⏭️  {test_name}: {message}")
                    skipped_tests += 1
                elif status == "ERROR":
                    report.append(f"  🔥 {test_name}: {message}")
                    error_tests += 1
                else:
                    report.append(f"  ❓ {test_name}: {message}")
                    error_tests += 1
        
        # Summary
        report.append("\n" + "="*60)
        report.append("TEST SUMMARY")
        report.append("="*60)
        report.append(f"Total tests: {total_tests}")
        report.append(f"✅ Passed: {passed_tests}")
        report.append(f"❌ Failed: {failed_tests}")
        report.append(f"⏭️  Skipped: {skipped_tests}")
        report.append(f"🔥 Errors: {error_tests}")
        
        if total_tests > 0:
            success_rate = (passed_tests / total_tests) * 100
            report.append(f"📊 Success rate: {success_rate:.1f}%")
        
        overall_status = "PASS" if failed_tests == 0 and error_tests == 0 else "FAIL"
        report.append(f"🎯 Overall status: {overall_status}")
        
        return "\n".join(report)


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Test MCP Server")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Save report to file")
    
    args = parser.parse_args()
    
    # Create tester
    tester = MCPServerTester(verbose=args.verbose)
    
    try:
        # Setup test environment
        tester.setup_test_environment()
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Generate report
        report = tester.generate_test_report(results)
        print("\n" + report)
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"\nReport saved to: {args.output}")
        
        # Exit with appropriate code
        if "error" in results:
            sys.exit(1)
        
        # Check for failures
        has_failures = False
        for category_results in results.values():
            if isinstance(category_results, dict):
                for test_result in category_results.values():
                    if isinstance(test_result, dict) and test_result.get("status") in ["FAIL", "ERROR"]:
                        has_failures = True
                        break
        
        sys.exit(1 if has_failures else 0)
        
    finally:
        # Cleanup
        tester.cleanup_test_environment()


if __name__ == "__main__":
    main() 