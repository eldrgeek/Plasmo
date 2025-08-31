#!/usr/bin/env python3
"""
Test script for core modules to verify functionality.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Test imports
try:
    from core import (
        make_json_safe, 
        SecurityError, 
        validate_path_security, 
        is_path_safe,
        enhanced_handle_error,
        handle_error,
        log_agent_error,
        get_error_suggestion,
        get_last_errors,
        clear_agent_errors,
        set_custom_agent_name,
        get_agent_name,
        ServerState,
        server_state,
        run_background_task,
        get_server_state
    )
    print("✅ All core modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_json_utils():
    """Test JSON utilities."""
    print("\n🧪 Testing JSON utilities...")
    
    # Test basic types
    assert make_json_safe("hello") == "hello"
    assert make_json_safe(42) == 42
    assert make_json_safe(True) == True
    assert make_json_safe(None) is None
    
    # Test datetime
    dt = datetime.now()
    assert isinstance(make_json_safe(dt), str)
    
    # Test complex objects
    data = {
        "string": "test",
        "number": 123,
        "list": [1, 2, 3],
        "dict": {"nested": True},
        "datetime": dt
    }
    safe_data = make_json_safe(data)
    json.dumps(safe_data)  # Should not raise
    
    print("✅ JSON utilities tests passed")


def test_security():
    """Test security utilities."""
    print("\n🧪 Testing security utilities...")
    
    # Test valid path
    current_dir = Path.cwd()
    test_file = current_dir / "test.txt"
    
    try:
        validated = validate_path_security(test_file)
        assert validated == test_file.resolve()
        print("✅ Valid path validation passed")
    except SecurityError:
        print("❌ Valid path validation failed")
    
    # Test invalid path
    invalid_path = Path("/etc/passwd")
    try:
        validate_path_security(invalid_path)
        print("❌ Invalid path validation should have failed")
    except SecurityError:
        print("✅ Invalid path validation correctly rejected")
    
    # Test is_path_safe
    assert is_path_safe(test_file) == True
    assert is_path_safe(invalid_path) == False
    
    print("✅ Security utilities tests passed")


def test_error_handling():
    """Test error handling utilities."""
    print("\n🧪 Testing error handling utilities...")
    
    # Test agent name functions
    original_name = get_agent_name()
    set_custom_agent_name("TestAgent")
    assert get_agent_name() == "TestAgent"
    
    # Test error logging
    test_error = ValueError("Test error")
    error_id = log_agent_error("test_operation", test_error, {"test": "context"})
    assert isinstance(error_id, str)
    
    # Test error suggestion
    suggestion = get_error_suggestion(test_error, "test_operation")
    assert "Invalid parameter value" in suggestion
    
    # Test enhanced error handling
    error_response = enhanced_handle_error("test_op", test_error, {"key": "value"})
    assert error_response["success"] == False
    assert error_response["operation"] == "test_op"
    assert error_response["error_type"] == "ValueError"
    assert "error_id" in error_response
    
    # Test get_last_errors
    errors = get_last_errors()
    assert errors["success"] == True
    assert len(errors["errors"]) > 0
    
    # Test clear_agent_errors
    clear_result = clear_agent_errors()
    assert clear_result["success"] == True
    
    print("✅ Error handling utilities tests passed")


def test_server_state():
    """Test server state management."""
    print("\n🧪 Testing server state management...")
    
    # Test ServerState creation
    state = ServerState()
    assert hasattr(state, 'active_tasks')
    assert hasattr(state, 'chrome_instances')
    assert hasattr(state, 'connection_lock')
    
    # Test global server state
    global_state = get_server_state()
    assert isinstance(global_state, ServerState)
    
    print("✅ Server state management tests passed")


def main():
    """Run all tests."""
    print("🚀 Running core modules tests...")
    
    test_json_utils()
    test_security()
    test_error_handling()
    test_server_state()
    
    print("\n🎉 All tests passed! Core modules are working correctly.")


if __name__ == "__main__":
    main()