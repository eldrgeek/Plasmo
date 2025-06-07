# MCP Server Testing Suite

## Overview

This comprehensive test suite validates all functionality of the Consolidated MCP Server v2.0, including:

- **File Operations** (4 tools): `read_file`, `write_file`, `list_files`, `get_project_structure`
- **System Operations** (2 tools): `get_system_info`, `server_info`
- **Chrome Debugging** (4 tools): `connect_to_chrome`, `get_chrome_tabs`, `launch_chrome_debug`, `execute_javascript_fixed`
- **Error Handling**: Security validation, Unicode support, and graceful error responses
- **Integration Testing**: Real-world scenarios and edge cases

## Quick Start

### Run All Tests
```bash
# Simple test run
python3 test_mcp_server.py

# Or use the test runner
./run_tests.sh
```

### Verbose Output
```bash
# See detailed test progress
python3 test_mcp_server.py --verbose

# Or with the runner
./run_tests.sh --verbose
```

### Save Test Report
```bash
# Save detailed report to file
python3 test_mcp_server.py --output test_report.txt

# Or with the runner
./run_tests.sh --output test_report.txt
```

## Test Categories

### 1. File Operations Tests

Tests the core file manipulation tools:

- **read_file**: Reading various file types including Unicode content
- **write_file**: Writing files with backup validation
- **list_files**: Directory listing with pattern matching
- **get_project_structure**: Recursive directory structure analysis

**Test Files Created:**
- `test.txt`: Basic text content
- `test.json`: JSON structure validation
- `test.py`: Python code for analysis
- `unicode_test.txt`: Unicode and emoji handling

### 2. System Operations Tests

Validates system information and server status:

- **get_system_info**: Platform, Python version, environment details
- **server_info**: MCP server version, status, and configuration

### 3. Chrome Debugging Tests

Tests Chrome Debug Protocol integration:

- **connect_to_chrome**: WebSocket connection establishment
- **get_chrome_tabs**: Tab enumeration and management
- **launch_chrome_debug**: Chrome instance launching
- **execute_javascript_fixed**: JavaScript execution in browser context

**Note**: Chrome debugging tests require Chrome to be running with debug flags:
```bash
./launch-chrome-debug.sh
```

### 4. Error Handling Tests

Validates robust error handling:

- **File Not Found**: Proper error responses for missing files
- **Path Traversal Protection**: Security validation against `../../../etc/passwd`
- **Permission Errors**: Graceful handling of access denied scenarios
- **Invalid Input**: Validation of malformed parameters

### 5. Unicode Handling Tests

Ensures proper Unicode and emoji support:

- **Emoji Characters**: 🚀 🎉 👋 😀😎🔥
- **International Text**: 中文测试 (Chinese characters)
- **Special Characters**: Various Unicode code points
- **Encoding Safety**: UTF-8 handling with surrogate pairs

## Test Report Format

The test suite generates comprehensive reports with:

### Status Indicators
- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed (unexpected behavior)
- ⏭️ **SKIP**: Test skipped (dependency not available)
- 🔥 **ERROR**: Test encountered an exception

### Sample Report
```
============================================================
MCP SERVER TEST REPORT
============================================================
Test run at: 2024-01-15 14:30:25

📋 FILE_OPERATIONS:
----------------------------------------
  ✅ read_file: Successfully read file
  ✅ write_file: Successfully wrote file
  ✅ list_files: Found 4 files
  ✅ get_project_structure: Got project structure

📋 SYSTEM_OPERATIONS:
----------------------------------------
  ✅ get_system_info: Got system info for darwin
  ✅ server_info: Server version 2.0.0

📋 CHROME_DEBUGGING:
----------------------------------------
  ⏭️ connect_to_chrome: Chrome debug not available
  ⏭️ get_chrome_tabs: Chrome debug not available
  ⏭️ launch_chrome_debug: Chrome debug not available
  ⏭️ execute_javascript_fixed: Chrome debug not available

📋 ERROR_HANDLING:
----------------------------------------
  ✅ error_handling_file_not_found: Properly handled file not found
  ✅ security_path_traversal: Blocked path traversal

📋 UNICODE_HANDLING:
----------------------------------------
  ✅ unicode_handling: Successfully handled Unicode and emoji

============================================================
TEST SUMMARY
============================================================
Total tests: 12
✅ Passed: 8
❌ Failed: 0
⏭️ Skipped: 4
🔥 Errors: 0
📊 Success rate: 100.0%
🎯 Overall status: PASS
```

## Test Architecture

### Direct Function Testing

The test suite uses direct function calls rather than HTTP requests for faster execution:

```python
# Import and call server functions directly
import mcp_server_consolidated
result = mcp_server_consolidated.read_file("/path/to/file")
```

### Test Environment Management

- **Temporary Directory**: All test files created in isolated temp directory
- **Automatic Cleanup**: Resources cleaned up after test completion
- **No Side Effects**: Tests don't modify project files

### Error Isolation

Each test is isolated with comprehensive exception handling:

```python
try:
    result = self.call_tool("tool_name", params)
    # Validate result
except Exception as e:
    # Handle and report error appropriately
```

## Chrome Debug Integration Testing

### Prerequisites

For full Chrome debugging tests, ensure Chrome is running with debug flags:

```bash
# Start Chrome with debugging enabled
./launch-chrome-debug.sh

# Verify Chrome debug port is accessible
curl http://localhost:9222/json
```

### Debug Test Scenarios

When Chrome debug is available, additional integration tests run:

1. **Connection Establishment**: WebSocket connection to Chrome
2. **Tab Management**: Enumerate and select browser tabs
3. **JavaScript Execution**: Run code in browser context
4. **Console Monitoring**: Real-time console log capture

## Continuous Integration

### Exit Codes

The test suite uses standard exit codes:

- `0`: All tests passed
- `1`: Some tests failed or encountered errors

### Automated Testing

```bash
#!/bin/bash
# CI/CD integration example

# Run tests and capture exit code
./run_tests.sh --output ci_report.txt
TEST_RESULT=$?

if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All MCP server tests passed"
    # Deploy or continue pipeline
else
    echo "❌ MCP server tests failed"
    cat ci_report.txt
    exit 1
fi
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'mcp_server_consolidated'
   ```
   **Solution**: Ensure you're running tests from the project root directory

2. **Chrome Debug Not Available**
   ```
   ⏭️ connect_to_chrome: Chrome debug not available
   ```
   **Solution**: Start Chrome with `./launch-chrome-debug.sh`

3. **Permission Errors**
   ```
   🔥 write_file: ERROR - Permission denied
   ```
   **Solution**: Check file permissions and available disk space

4. **Unicode Errors**
   ```
   🔥 unicode_handling: ERROR - UnicodeDecodeError
   ```
   **Solution**: Ensure proper UTF-8 locale settings

### Debug Mode

For detailed debugging, use verbose mode:

```bash
python3 test_mcp_server.py --verbose 2>&1 | tee debug.log
```

## Extending the Test Suite

### Adding New Tests

1. **Create Test Method**:
   ```python
   def test_new_feature(self) -> Dict[str, Any]:
       """Test new MCP server feature."""
       results = {}
       # Add test logic
       return results
   ```

2. **Add to Test Categories**:
   ```python
   test_categories = [
       # ... existing categories
       ("new_feature", self.test_new_feature),
   ]
   ```

3. **Update Documentation**: Add description to this README

### Test Data Management

For tests requiring specific data:

```python
def setup_custom_test_data(self):
    """Create custom test files for specific scenarios."""
    custom_files = {
        "custom_test.json": '{"test": "data"}',
        # Add more test files as needed
    }
    # Create files in self.temp_dir
```

## Performance Considerations

- **Fast Execution**: Direct function calls instead of HTTP requests
- **Parallel Safe**: Tests can run concurrently (each creates isolated temp directory)
- **Resource Cleanup**: Automatic cleanup prevents disk space issues
- **Minimal Dependencies**: Uses only standard library where possible

## Security Testing

The test suite includes security validation:

- **Path Traversal**: Attempts to access files outside project directory
- **Input Validation**: Tests malformed and malicious inputs
- **Permission Boundaries**: Validates file access controls
- **Error Information**: Ensures errors don't leak sensitive information

## Integration with Development Workflow

### Pre-commit Testing
```bash
# Add to your pre-commit hook
./run_tests.sh --output pre_commit_report.txt
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Test MCP Server
  run: |
    ./run_tests.sh --output ${{ github.workspace }}/test_report.txt
    
- name: Upload Test Report
  uses: actions/upload-artifact@v3
  with:
    name: mcp-test-report
    path: test_report.txt
```

---

## Summary

This test suite provides comprehensive validation of the MCP server with:

- **15 MCP Tools** tested across 5 categories
- **Security validation** with path traversal protection
- **Unicode support** including emojis and international characters
- **Chrome debugging integration** when available
- **Detailed reporting** with clear pass/fail indicators
- **CI/CD ready** with standard exit codes and report generation

Run `./run_tests.sh --help` for all available options. 