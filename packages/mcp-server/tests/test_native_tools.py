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

if __name__ == "__main__":
    unittest.main()
