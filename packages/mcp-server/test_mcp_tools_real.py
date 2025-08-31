#!/usr/bin/env python3
"""
Real Implementation Test Suite for All MCP Tools
================================================

This test suite tests all MCP tools using the actual running server
instead of mocks, providing real-world validation.

Usage:
    python test_mcp_tools_real.py
    python test_mcp_tools_real.py --server-url http://localhost:8001
    python test_mcp_tools_real.py -v  # Verbose output
"""

import json
import os
import sys
import tempfile
import time
import unittest
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
import argparse

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test utilities
from test_utils import (
    ensure_server_running, 
    call_mcp_tool,
    setup_test_environment,
    cleanup_test_environment,
    check_server_health
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestMCPToolsReal(unittest.TestCase):
    """Real implementation tests for all MCP tools."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class with server connection."""
        logger.info("🚀 Setting up MCP Tools Real Implementation Tests")
        
        # Get server URL from command line or use default
        cls.server_url = getattr(cls, '_server_url', None) or ensure_server_running()
        
        if not cls.server_url:
            raise RuntimeError("Could not connect to or start MCP server")
        
        # Verify server is healthy
        is_healthy, info = check_server_health(cls.server_url)
        if not is_healthy:
            raise RuntimeError(f"MCP server at {cls.server_url} is not healthy")
        
        logger.info(f"✅ Connected to MCP server at {cls.server_url}")
        if info:
            logger.info(f"   Server status: {info}")
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="mcp_real_test_")
        self.test_file = os.path.join(self.test_dir, "test_file.txt")
        
        # Register a unique agent name for this test run
        self.test_agent_name = f"test_agent_{int(time.time() * 1000) % 1000000}"
        
    def tearDown(self):
        """Clean up test environment."""
        # Clean up test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)
    
    # ========================================
    # AGENT MANAGEMENT TOOLS (8 tools)
    # ========================================
    
    def test_register_agent_with_name(self):
        """Test agent registration with custom name using real server."""
        result = call_mcp_tool(
            self.server_url,
            "register_agent_with_name",
            {"agent_name": self.test_agent_name}
        )
        
        self.assertIn("agent_name", result)
        self.assertEqual(result["agent_name"], self.test_agent_name)
        self.assertIn("registration_time", result)
        
        # Verify we can get the same name back
        get_result = call_mcp_tool(self.server_url, "get_current_agent_name")
        self.assertEqual(get_result.get("agent_name"), self.test_agent_name)
    
    def test_get_current_agent_name(self):
        """Test getting current agent name from real server."""
        result = call_mcp_tool(self.server_url, "get_current_agent_name")
        
        self.assertIn("agent_name", result)
        self.assertIn("is_custom", result)
        self.assertIsInstance(result["is_custom"], bool)
    
    def test_messages_operation(self):
        """Test messaging operations with real server."""
        # First register our agent
        call_mcp_tool(self.server_url, "register_agent_with_name", 
                     {"agent_name": self.test_agent_name})
        
        # Send a message
        send_result = call_mcp_tool(
            self.server_url,
            "messages",
            {
                "operation": "send",
                "payload": {
                    "to": "test_recipient",
                    "subject": "Real Test Message",
                    "message": "Hello from real test!"
                }
            }
        )
        
        self.assertTrue(send_result.get("success", False))
        self.assertIn("message_id", send_result)
        
        # Get messages
        get_result = call_mcp_tool(
            self.server_url,
            "messages",
            {"operation": "get"}
        )
        
        self.assertIn("messages", get_result)
        self.assertIsInstance(get_result["messages"], list)
    
    def test_notify_operation(self):
        """Test notification operations with real server."""
        result = call_mcp_tool(
            self.server_url,
            "notify",
            {
                "operation": "notify",
                "target_agent": "test_target",
                "message": "Test notification from real test"
            }
        )
        
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("operation"), "notify")
    
    def test_launch_claude_instance(self):
        """Test Claude instance launching (metadata only, won't actually launch)."""
        result = call_mcp_tool(
            self.server_url,
            "launch_claude_instance",
            {
                "role": "test_assistant",
                "project_path": self.test_dir
            }
        )
        
        # The actual launch might fail in test environment, but we should get a response
        self.assertIn("success", result)
        if result.get("success"):
            self.assertIn("instance_id", result)
    
    def test_list_claude_instances(self):
        """Test listing Claude instances with real server."""
        result = call_mcp_tool(self.server_url, "list_claude_instances")
        
        self.assertIn("instances", result)
        self.assertIsInstance(result.get("instances", []), list)
        
    def test_get_last_errors(self):
        """Test error retrieval from real server."""
        result = call_mcp_tool(
            self.server_url,
            "get_last_errors",
            {"limit": 5}
        )
        
        self.assertIn("errors", result)
        self.assertIsInstance(result["errors"], list)
        self.assertIn("total_errors", result)
    
    # ========================================
    # FILE OPERATIONS TOOLS (6 tools)
    # ========================================
    
    def test_smart_write_file(self):
        """Test smart file writing with real server."""
        content = "Hello from real test!"
        
        result = call_mcp_tool(
            self.server_url,
            "smart_write_file",
            {
                "file_path": self.test_file,
                "content": content,
                "create_dirs": True
            }
        )
        
        self.assertTrue(result.get("success", False))
        self.assertIn("bytes_written", result)
        
        # Verify file was actually written
        self.assertTrue(os.path.exists(self.test_file))
        with open(self.test_file, 'r') as f:
            self.assertEqual(f.read(), content)
    
    def test_smart_read_file(self):
        """Test smart file reading with real server."""
        # First write a file
        content = "Test content for reading 📚"
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Read it back
        result = call_mcp_tool(
            self.server_url,
            "smart_read_file",
            {"file_path": self.test_file}
        )
        
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("content"), content)
        self.assertIn("encoding", result)
        self.assertIn("size", result)
    
    def test_smart_edit_file(self):
        """Test smart file editing with real server."""
        # Create initial file
        with open(self.test_file, 'w') as f:
            f.write("Line 1\nLine 2\nLine 3")
        
        # Edit the file
        result = call_mcp_tool(
            self.server_url,
            "smart_edit_file",
            {
                "file_path": self.test_file,
                "operation": "replace_line",
                "line_number": 2,
                "content": "Modified Line 2"
            }
        )
        
        self.assertTrue(result.get("success", False))
        
        # Verify the edit
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(lines[1].strip(), "Modified Line 2")
    
    def test_patch_file(self):
        """Test file patching with real server."""
        # Create initial file
        with open(self.test_file, 'w') as f:
            f.write("Original line 1\nOriginal line 2\nOriginal line 3")
        
        # Apply patches
        result = call_mcp_tool(
            self.server_url,
            "patch_file",
            {
                "file_path": self.test_file,
                "patches": [
                    {
                        "operation": "replace",
                        "line_number": 1,
                        "content": "Patched line 1"
                    },
                    {
                        "operation": "replace", 
                        "line_number": 3,
                        "content": "Patched line 3"
                    }
                ]
            }
        )
        
        self.assertTrue(result.get("success", False))
        self.assertEqual(result.get("patches_applied"), 2)
    
    def test_file_manager(self):
        """Test file manager operations with real server."""
        # Create a test file
        with open(self.test_file, 'w') as f:
            f.write("Test content for file manager")
        
        # Test copy operation
        dest_file = os.path.join(self.test_dir, "copy_test.txt")
        result = call_mcp_tool(
            self.server_url,
            "file_manager",
            {
                "operation": "copy",
                "file_path": self.test_file,
                "destination": dest_file
            }
        )
        
        self.assertTrue(result.get("success", False))
        self.assertTrue(os.path.exists(dest_file))
        
        # Test delete operation
        delete_result = call_mcp_tool(
            self.server_url,
            "file_manager",
            {
                "operation": "delete",
                "file_path": dest_file,
                "confirm": True
            }
        )
        
        self.assertTrue(delete_result.get("success", False))
        self.assertFalse(os.path.exists(dest_file))
    
    def test_get_project_structure(self):
        """Test project structure analysis with real server."""
        # Create a small project structure
        os.makedirs(os.path.join(self.test_dir, "src"))
        os.makedirs(os.path.join(self.test_dir, "tests"))
        
        with open(os.path.join(self.test_dir, "README.md"), 'w') as f:
            f.write("# Test Project")
        with open(os.path.join(self.test_dir, "src", "main.py"), 'w') as f:
            f.write("print('Hello')")
        
        result = call_mcp_tool(
            self.server_url,
            "get_project_structure",
            {
                "directory": self.test_dir,
                "max_depth": 2
            }
        )
        
        self.assertIn("structure", result)
        self.assertIn("total_files", result)
        self.assertIn("total_directories", result)
        self.assertGreaterEqual(result["total_files"], 2)
    
    # ========================================
    # SYSTEM INFORMATION TOOLS (4 tools)
    # ========================================
    
    def test_analyze_code(self):
        """Test code analysis with real server."""
        # Create a Python file
        code_file = os.path.join(self.test_dir, "test_code.py")
        with open(code_file, 'w') as f:
            f.write('''
def hello_world():
    """Say hello."""
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

if __name__ == "__main__":
    hello_world()
    obj = TestClass()
    print(obj.get_value())
''')
        
        result = call_mcp_tool(
            self.server_url,
            "analyze_code",
            {"file_path": code_file}
        )
        
        self.assertIn("metrics", result)
        metrics = result["metrics"]
        self.assertEqual(metrics["functions"], 1)
        self.assertEqual(metrics["classes"], 1)
        self.assertGreater(metrics["lines"], 10)
    
    def test_get_system_info(self):
        """Test system information retrieval with real server."""
        result = call_mcp_tool(
            self.server_url,
            "get_system_info",
            {"include_sensitive": False}
        )
        
        self.assertIn("system", result)
        self.assertIn("platform", result["system"])
        self.assertIn("python_version", result["system"])
        self.assertIn("memory", result)
    
    def test_server_info(self):
        """Test server information with real server."""
        result = call_mcp_tool(self.server_url, "server_info")
        
        self.assertIn("server", result)
        self.assertIn("name", result["server"])
        self.assertIn("version", result["server"])
        self.assertIn("tools_available", result)
    
    def test_health(self):
        """Test health endpoint with real server."""
        result = call_mcp_tool(self.server_url, "health")
        
        self.assertEqual(result.get("status"), "healthy")
        self.assertIn("uptime", result)
        self.assertIn("timestamp", result)
    
    # ========================================
    # CHROME DEBUG PROTOCOL TOOLS
    # ========================================
    
    def test_chrome_tools_metadata(self):
        """Test Chrome tools respond appropriately when Chrome not available."""
        # These tests verify the tools handle absence of Chrome gracefully
        
        # Test launch_chrome_debug
        launch_result = call_mcp_tool(self.server_url, "launch_chrome_debug")
        self.assertIn("success", launch_result)
        # Tool should handle Chrome not being available gracefully
        
        # Test connect_to_chrome
        connect_result = call_mcp_tool(
            self.server_url,
            "connect_to_chrome",
            {"port": 9222}
        )
        self.assertIn("success", connect_result)
        
        # Test get_chrome_tabs  
        tabs_result = call_mcp_tool(
            self.server_url,
            "get_chrome_tabs",
            {"connection_id": "localhost:9222"}
        )
        self.assertIn("success", tabs_result)
    
    # ========================================
    # SERVICE MANAGEMENT TOOLS
    # ========================================
    
    def test_service_tools(self):
        """Test service management tools with real server."""
        # Test service_status
        status_result = call_mcp_tool(self.server_url, "service_status")
        self.assertIn("services", status_result)
        
        # Test service_health_check
        health_result = call_mcp_tool(self.server_url, "service_health_check")
        self.assertIn("services", health_result)
        self.assertIn("summary", health_result)
        
        # Test service_logs (might not have logs)
        logs_result = call_mcp_tool(
            self.server_url,
            "service_logs",
            {"service_name": "test_service", "lines": 10}
        )
        # Should at least return a response
        self.assertIsInstance(logs_result, dict)
    
    # ========================================
    # FIREBASE TOOLS (Metadata only)
    # ========================================
    
    def test_firebase_tools_metadata(self):
        """Test Firebase tools respond appropriately in test environment."""
        # Test firebase_project_status
        status_result = call_mcp_tool(
            self.server_url,
            "firebase_project_status",
            {"project_id": "test-project"}
        )
        self.assertIn("success", status_result)
        
        # These tools would need real Firebase credentials to work fully
        # We're just testing they respond appropriately
    
    # ========================================
    # AUTOMATION TOOLS
    # ========================================
    
    def test_automation_tools_metadata(self):
        """Test automation tools respond appropriately."""
        # Test send_orchestration_command
        orch_result = call_mcp_tool(
            self.server_url,
            "send_orchestration_command",
            {
                "command_type": "test",
                "targets": ["test_target"],
                "prompt": "Test prompt"
            }
        )
        self.assertIsInstance(orch_result, dict)
        
        # The actual automation would require browser/system access
        # We're verifying the tools are available and respond

    # ========================================
    # ERROR HANDLING TESTS
    # ========================================
    
    def test_error_handling_invalid_tool(self):
        """Test handling of invalid tool names."""
        result = call_mcp_tool(
            self.server_url,
            "non_existent_tool",
            {}
        )
        
        self.assertFalse(result.get("success", True))
        self.assertIn("error", result)
    
    def test_error_handling_invalid_params(self):
        """Test handling of invalid parameters."""
        # Try to read non-existent file
        result = call_mcp_tool(
            self.server_url,
            "smart_read_file",
            {"file_path": "/definitely/does/not/exist/file.txt"}
        )
        
        self.assertFalse(result.get("success", True))
        self.assertIn("error", result)
    
    def test_error_handling_security(self):
        """Test security error handling."""
        # Try path traversal
        result = call_mcp_tool(
            self.server_url,
            "smart_read_file",
            {"file_path": "../../../etc/passwd"}
        )
        
        # Should be blocked by security
        self.assertFalse(result.get("success", True))


def run_real_tests(server_url: Optional[str] = None, verbose: bool = False):
    """Run the real implementation tests."""
    # Set server URL if provided
    if server_url:
        TestMCPToolsReal._server_url = server_url
    
    # Configure logging
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMCPToolsReal)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 Real Implementation Test Results:")
    print(f"   • Tests Run: {result.testsRun}")
    print(f"   • Failures: {len(result.failures)}")
    print(f"   • Errors: {len(result.errors)}")
    print(f"   • Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 60)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real implementation tests for MCP tools")
    parser.add_argument("--server-url", help="MCP server URL (default: auto-detect)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    success = run_real_tests(args.server_url, args.verbose)
    sys.exit(0 if success else 1)