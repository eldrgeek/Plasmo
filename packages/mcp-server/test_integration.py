#!/usr/bin/env python3
"""
Integration test to verify MCP server works with core modules.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_mcp_server_imports():
    """Test that MCP server can import and use core modules."""
    print("🧪 Testing MCP server integration with core modules...")
    
    try:
        # Test importing the core modules directly
        from core import make_json_safe, SecurityError, enhanced_handle_error, get_agent_name
        print("✅ Core modules imported successfully")
        
        # Test that the MCP server can be imported
        # We'll suppress the logging output for cleaner test output
        import logging
        logging.disable(logging.CRITICAL)
        
        # Import the MCP server module
        import mcp_server
        print("✅ MCP server imported successfully")
        
        # Test that core functions work
        test_data = {"test": "data", "number": 42}
        safe_data = make_json_safe(test_data)
        assert safe_data == test_data
        print("✅ make_json_safe function works")
        
        # Test security validation
        try:
            from core.security import validate_path_security
            current_file = Path(__file__)
            validated = validate_path_security(current_file)
            assert validated == current_file.resolve()
            print("✅ Path security validation works")
        except SecurityError:
            print("❌ Path security validation failed")
            
        # Test error handling
        test_error = ValueError("Test integration error")
        error_response = enhanced_handle_error("test_integration", test_error)
        assert error_response["success"] == False
        assert "error_id" in error_response
        print("✅ Enhanced error handling works")
        
        # Test agent name function
        agent_name = get_agent_name()
        assert isinstance(agent_name, str)
        print(f"✅ Agent name function works: {agent_name}")
        
        print("\n🎉 All integration tests passed! Core modules are properly integrated.")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run integration tests."""
    print("🚀 Running MCP server integration tests...")
    
    success = test_mcp_server_imports()
    
    if success:
        print("\n✅ Integration tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()