"""
Tests for Native Tools System
=============================

Basic tests for the native tool registry, validation, and execution.
"""

import unittest
import tempfile
import yaml
from pathlib import Path
import os
import sys

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from native_tools import ToolRegistry, ToolValidator, ToolExecutor

class TestToolRegistry(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.test_registry_content = {
            "version": 1.0,
            "auto_reload": True,
            "validation_on_change": True,
            "tools": {
                "test_tool": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "category": "testing",
                    "script": "test_script.py",
                    "supports_persistent": False,
                    "requires_review": False,
                    "keywords": ["test", "example"],
                    "parameters": {
                        "message": {
                            "type": "string",
                            "default": "hello",
                            "description": "Test message"
                        }
                    },
                    "use_cases": [
                        "I want to test something",
                        "Run a test"
                    ]
                }
            }
        }
        
        # Create temporary registry file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_registry_content, self.temp_file)
        self.temp_file.close()
        
        self.registry = ToolRegistry(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment."""
        os.unlink(self.temp_file.name)
    
    def test_load_registry(self):
        """Test loading registry from YAML file."""
        self.assertTrue(self.registry.load_registry())
        self.assertEqual(len(self.registry.tools), 1)
        self.assertIn("test_tool", self.registry.tools)
    
    def test_get_tool(self):
        """Test getting a specific tool."""
        tool = self.registry.get_tool("test_tool")
        self.assertIsNotNone(tool)
        self.assertEqual(tool["name"], "test_tool")
        self.assertEqual(tool["category"], "testing")
    
    def test_list_tools(self):
        """Test listing all tools."""
        tools = self.registry.list_tools()
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0]["name"], "test_tool")
    
    def test_list_tools_by_category(self):
        """Test filtering tools by category."""
        tools = self.registry.list_tools("testing")
        self.assertEqual(len(tools), 1)
        
        tools = self.registry.list_tools("nonexistent")
        self.assertEqual(len(tools), 0)
    
    def test_search_by_keywords(self):
        """Test keyword search."""
        matches = self.registry.search_by_keywords(["test"])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "test_tool")
        
        matches = self.registry.search_by_keywords(["nonexistent"])
        self.assertEqual(len(matches), 0)
    
    def test_search_by_use_case(self):
        """Test use case search."""
        matches = self.registry.search_by_use_case("I want to test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "test_tool")
        
        matches = self.registry.search_by_use_case("unrelated intent")
        self.assertEqual(len(matches), 0)
    
    def test_get_tool_categories(self):
        """Test getting available categories."""
        categories = self.registry.get_tool_categories()
        self.assertIn("testing", categories)

class TestToolValidator(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.validator = ToolValidator()
        self.valid_tool_config = {
            "name": "test_tool",
            "description": "A test tool",
            "category": "testing",
            "script": "test_script.py",
            "parameters": {
                "message": {
                    "type": "string",
                    "default": "hello"
                },
                "count": {
                    "type": "integer",
                    "required": True
                }
            }
        }
    
    def test_validate_config_structure(self):
        """Test configuration structure validation."""
        result = self.validator.validate_tool("test_tool", self.valid_tool_config)
        self.assertIn("has_name", result["checks"])
        self.assertIn("has_description", result["checks"])
        self.assertIn("has_category", result["checks"])
        self.assertIn("has_execution_method", result["checks"])
    
    def test_validate_missing_fields(self):
        """Test validation with missing required fields."""
        invalid_config = {"name": "test"}  # Missing description and category
        result = self.validator.validate_tool("test_tool", invalid_config)
        self.assertFalse(result["valid"])
        self.assertTrue(len(result["errors"]) > 0)
    
    def test_validate_parameters(self):
        """Test parameter validation."""
        result = self.validator.validate_tool("test_tool", self.valid_tool_config)
        self.assertIn("parameters_validated", result["checks"])

class TestToolExecutor(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.executor = ToolExecutor()
        self.test_tool_config = {
            "name": "echo_tool",
            "description": "Echo test tool",
            "category": "testing",
            "command_template": "echo {message}",
            "supports_persistent": False,
            "requires_review": False,
            "parameters": {
                "message": {
                    "type": "string",
                    "default": "test"
                }
            }
        }
    
    def test_execute_simple_tool(self):
        """Test executing a simple command-based tool."""
        result = self.executor.execute_tool(
            "echo_tool",
            self.test_tool_config,
            {"message": "hello world"}
        )
        self.assertTrue(result["success"])
        self.assertIn("hello world", result["stdout"])
    
    def test_execute_tool_with_default_params(self):
        """Test executing tool with default parameters."""
        result = self.executor.execute_tool(
            "echo_tool",
            self.test_tool_config,
            {}  # No parameters, should use defaults
        )
        self.assertTrue(result["success"])
        self.assertIn("test", result["stdout"])
    
    def test_execute_nonexistent_mode(self):
        """Test executing tool with invalid mode."""
        result = self.executor.execute_tool(
            "echo_tool",
            self.test_tool_config,
            {},
            "invalid_mode"
        )
        self.assertFalse(result["success"])
        self.assertIn("Invalid execution mode", result["error"])
    
    def test_tool_requires_review(self):
        """Test tool that requires review."""
        review_config = self.test_tool_config.copy()
        review_config["requires_review"] = True
        
        result = self.executor.execute_tool(
            "review_tool",
            review_config,
            {}
        )
        self.assertFalse(result["success"])
        self.assertTrue(result.get("requires_approval", False))
    
    def test_module_based_tool_execution(self):
        """Test executing a module-based tool."""
        module_tool_config = {
            "name": "module_test_tool",
            "description": "Module-based test tool",
            "category": "testing",
            "module": "agents.claude_instances",
            "function": "list_claude_instances",
            "supports_persistent": False,
            "requires_review": False,
            "parameters": {}
        }
        
        result = self.executor.execute_tool(
            "module_test_tool",
            module_tool_config,
            {}
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["returncode"], 0)
        self.assertIn("stdout", result)
    
    def test_module_based_tool_with_parameters(self):
        """Test executing a module-based tool with parameters."""
        module_tool_config = {
            "name": "parameter_test_tool",
            "description": "Module-based tool with parameters",
            "category": "testing",
            "module": "agents.claude_instances",
            "function": "list_claude_instances",
            "supports_persistent": False,
            "requires_review": False,
            "parameters": {
                "include_inactive": {
                    "type": "boolean",
                    "default": False
                }
            }
        }
        
        result = self.executor.execute_tool(
            "parameter_test_tool",
            module_tool_config,
            {"include_inactive": True}
        )
        self.assertTrue(result["success"])
    
    def test_persistent_module_tool(self):
        """Test executing a module-based tool in persistent mode."""
        module_tool_config = {
            "name": "persistent_module_tool",
            "description": "Persistent module-based tool",
            "category": "testing",
            "module": "agents.claude_instances",
            "function": "list_claude_instances",
            "supports_persistent": True,
            "requires_review": False,
            "parameters": {}
        }
        
        result = self.executor.execute_tool(
            "persistent_module_tool",
            module_tool_config,
            {},
            "persistent"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "started")
    
    def test_background_module_tool(self):
        """Test executing a module-based tool in background mode."""
        module_tool_config = {
            "name": "background_module_tool",
            "description": "Background module-based tool",
            "category": "testing",
            "module": "agents.claude_instances",
            "function": "list_claude_instances",
            "supports_persistent": True,
            "requires_review": False,
            "parameters": {}
        }
        
        result = self.executor.execute_tool(
            "background_module_tool",
            module_tool_config,
            {},
            "background"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "started")
    
    def test_get_tool_status(self):
        """Test getting status of running tools."""
        # Start a persistent tool first
        module_tool_config = {
            "name": "status_test_tool",
            "description": "Tool for status testing",
            "category": "testing",
            "module": "agents.claude_instances",
            "function": "list_claude_instances",
            "supports_persistent": True,
            "requires_review": False,
            "parameters": {}
        }
        
        # Start the tool
        start_result = self.executor.execute_tool(
            "status_test_tool",
            module_tool_config,
            {},
            "persistent"
        )
        self.assertTrue(start_result["success"])
        
        # Check status
        status = self.executor.get_tool_status("status_test_tool")
        self.assertIn("status", status)
        
        # Stop the tool
        stop_result = self.executor.stop_tool("status_test_tool")
        self.assertTrue(stop_result["success"])

class TestMCPIntegration(unittest.TestCase):
    """Test MCP server integration with native tools."""
    
    def setUp(self):
        """Set up test environment."""
        # Import MCP server components
        try:
            from mcp_server import tool_registry, tool_executor
            self.tool_registry = tool_registry
            self.tool_executor = tool_executor
            self.mcp_available = True
        except ImportError:
            self.mcp_available = False
    
    def test_mcp_tools_available(self):
        """Test that MCP tools are available."""
        if not self.mcp_available:
            self.skipTest("MCP server not available for testing")
        
        self.assertIsNotNone(self.tool_registry)
        self.assertIsNotNone(self.tool_executor)
    
    def test_list_available_tools_mcp(self):
        """Test MCP list_available_tools function."""
        if not self.mcp_available:
            self.skipTest("MCP server not available for testing")
        
        try:
            from mcp_server import list_available_tools
            result = list_available_tools()
            self.assertTrue(result["success"])
            self.assertIn("tools", result)
            self.assertGreater(len(result["tools"]), 0)
        except ImportError:
            self.skipTest("MCP tools not available")
    
    def test_discover_tools_by_intent_mcp(self):
        """Test MCP discover_tools_by_intent function."""
        if not self.mcp_available:
            self.skipTest("MCP server not available for testing")
        
        try:
            from mcp_server import discover_tools_by_intent
            result = discover_tools_by_intent("I want to capture something")
            self.assertTrue(result["success"])
            self.assertIn("suggestions", result)
        except ImportError:
            self.skipTest("MCP tools not available")
    
    def test_execute_native_tool_mcp(self):
        """Test MCP execute_native_tool function."""
        if not self.mcp_available:
            self.skipTest("MCP server not available for testing")
        
        try:
            from mcp_server import execute_native_tool
            result = execute_native_tool("list_claude_instances", {})
            self.assertTrue(result["success"])
        except ImportError:
            self.skipTest("MCP tools not available")

class TestRealWorldTools(unittest.TestCase):
    """Test real-world tool execution scenarios."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry("tools.yaml")
        self.executor = ToolExecutor()
    
    def test_firebase_tools_discovery(self):
        """Test discovering Firebase tools."""
        firebase_tools = self.registry.search_by_keywords(["firebase"])
        self.assertGreater(len(firebase_tools), 0)
        
        # Check that Firebase tools have proper module configuration
        for tool in firebase_tools:
            tool_config = self.registry.get_tool(tool["name"])
            self.assertIsNotNone(tool_config)
            self.assertIn("module", tool_config)
            self.assertIn("function", tool_config)
    
    def test_agent_tools_discovery(self):
        """Test discovering agent management tools."""
        agent_tools = self.registry.search_by_keywords(["claude", "agent"])
        self.assertGreater(len(agent_tools), 0)
        
        # Check that agent tools have proper module configuration
        for tool in agent_tools:
            tool_config = self.registry.get_tool(tool["name"])
            self.assertIsNotNone(tool_config)
            self.assertIn("module", tool_config)
            self.assertIn("function", tool_config)
    
    def test_service_tools_discovery(self):
        """Test discovering service orchestration tools."""
        service_tools = self.registry.search_by_keywords(["service", "orchestration"])
        self.assertGreater(len(service_tools), 0)
        
        # Check that service tools have proper module configuration
        for tool in service_tools:
            tool_config = self.registry.get_tool(tool["name"])
            self.assertIsNotNone(tool_config)
            self.assertIn("module", tool_config)
            self.assertIn("function", tool_config)
    
    def test_capture_tools_discovery(self):
        """Test discovering capture tools."""
        capture_tools = self.registry.search_by_use_case("I want to capture something")
        self.assertGreater(len(capture_tools), 0)
        
        # Check that capture tools have proper configuration
        for tool in capture_tools:
            tool_config = self.registry.get_tool(tool["name"])
            self.assertIsNotNone(tool_config)
            self.assertIn("script", tool_config)  # Capture tools use scripts
    
    def test_tool_categories_completeness(self):
        """Test that all tools are properly categorized."""
        categories = self.registry.get_tool_categories()
        self.assertGreater(len(categories), 0)
        
        # Check that all tools have categories
        for tool_name, tool_config in self.registry.tools.items():
            self.assertIn("category", tool_config)
            self.assertIn(tool_config["category"], categories)
    
    def test_tool_metadata_completeness(self):
        """Test that all tools have complete metadata."""
        required_fields = ["name", "description", "category", "keywords", "use_cases"]
        
        for tool_name, tool_config in self.registry.tools.items():
            for field in required_fields:
                self.assertIn(field, tool_config, f"Tool {tool_name} missing {field}")
            
            # Check that tools have either module+function or script
            has_module = "module" in tool_config and "function" in tool_config
            has_script = "script" in tool_config
            has_command = "command_template" in tool_config
            
            self.assertTrue(
                has_module or has_script or has_command,
                f"Tool {tool_name} must have module+function, script, or command_template"
            )

if __name__ == "__main__":
    unittest.main()
