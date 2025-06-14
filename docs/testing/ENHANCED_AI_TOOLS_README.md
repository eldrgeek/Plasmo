# Enhanced AI Assistant Tools v2.2.0

This document describes the enhanced MCP server tools specifically designed for AI assistants like Claude, ChatGPT, and other LLMs working through Cursor IDE.

## 🚀 Why These Enhanced Tools?

AI assistants often struggle with Cursor's built-in tools due to:
- Generic error messages without context
- Lack of agent-specific error tracking
- Limited file operation modes
- No built-in backup or rollback capabilities
- Insufficient metadata about operations

Our enhanced tools solve these problems with:
- **Agent-specific error logging** with detailed context
- **Comprehensive operation metadata** (timing, size changes, etc.)
- **Automatic backup creation** before modifications
- **Multi-mode file operations** (append, prepend, line-based editing)
- **Batch operations** for complex file modifications
- **Enhanced security** with path validation and confirmations

## 📁 Enhanced File Operations

### `smart_write_file`
Advanced file writing with multiple modes and comprehensive error handling.

```python
smart_write_file(
    file_path="example.py",
    content="print('Hello World')",
    mode="overwrite",  # or "append", "prepend"
    backup=True,
    create_dirs=True,
    encoding="utf-8"
)
```

**Features:**
- Multiple write modes (overwrite, append, prepend)
- Automatic backup creation with timestamps
- Directory creation if needed
- Encoding detection and handling
- Performance metrics (execution time, size changes)
- Agent tracking for error logging

### `smart_read_file`
Advanced file reading with encoding detection and metadata.

```python
smart_read_file(
    file_path="example.py",
    encoding="auto",  # auto-detect encoding
    max_size=50*1024*1024,  # 50MB limit
    return_metadata=True
)
```

**Features:**
- Automatic encoding detection (UTF-8, Latin-1, CP1252, etc.)
- File metadata (size, lines, modification time)
- Large file protection
- Performance tracking
- Security validation

### `smart_edit_file`
Precise line-based file editing operations.

```python
smart_edit_file(
    file_path="example.py",
    operation="insert_at_line",
    content="# New comment\n",
    line_number=5,
    backup=True
)
```

**Operations:**
- `insert_at_line`: Insert content at specific line
- `replace_line`: Replace a single line
- `replace_range`: Replace line range
- `find_replace`: Find and replace text
- `delete_line`: Delete specific line
- `delete_range`: Delete line range

### `patch_file`
Apply multiple patches to a file in a single atomic operation.

```python
patch_file(
    file_path="example.py",
    patches=[
        {
            "operation": "insert",
            "line_number": 1,
            "content": "#!/usr/bin/env python3\n"
        },
        {
            "operation": "find_replace",
            "find_text": "old_function",
            "replace_text": "new_function"
        }
    ],
    backup=True,
    validate=True
)
```

**Features:**
- Multiple operations in single transaction
- Validation before applying changes
- Automatic backup creation
- Detailed operation reporting
- Error rollback on failure

### `file_manager`
Advanced file management operations with safety checks.

```python
file_manager(
    operation="copy",
    file_path="source.txt",
    destination="backup.txt",
    confirm=True  # Required for destructive operations
)
```

**Operations:**
- `copy`: Copy files or directories
- `move`: Move files or directories
- `delete`: Delete with confirmation
- `mkdir`: Create directories
- `backup`: Create timestamped backups

## 🔧 Error Management System

### Enhanced Error Logging
Every operation logs detailed error information with:
- Unique error ID for tracking
- Agent name identification
- Full stack trace
- Operation context
- Helpful suggestions
- Timestamp and performance data

### `get_last_errors`
Retrieve recent errors for debugging.

```python
get_last_errors(
    agent_name="Plasmo",  # Optional, auto-detected
    limit=10,
    operation_filter="smart_write"  # Optional filter
)
```

**Returns:**
```json
{
  "success": true,
  "agent_name": "Plasmo",
  "errors": [
    {
      "error_id": "1702345678_abc123",
      "operation": "smart_write_file",
      "error": "Permission denied",
      "error_type": "PermissionError",
      "traceback": "...",
      "context": {...},
      "timestamp": "2024-01-01T12:00:00",
      "suggestion": "Ensure you have write access..."
    }
  ],
  "total_errors": 25,
  "filtered_count": 3
}
```

### `get_error_by_id`
Get specific error details by ID.

```python
get_error_by_id(
    error_id="1702345678_abc123",
    agent_name="Plasmo"
)
```

### `clear_agent_errors`
Clear error log for agent (requires confirmation).

```python
clear_agent_errors(
    agent_name="Plasmo",
    confirm=True  # Must be True to actually clear
)
```

## 🛡️ Security Features

### Path Validation
All file operations validate paths to prevent:
- Directory traversal attacks
- Access outside project directory
- Unauthorized file access

### Operation Confirmations
Destructive operations require explicit confirmation:
- File deletions
- Directory removals
- Error log clearing

### Size Limits
Protection against:
- Large file operations (50MB default limit)
- Memory exhaustion
- Performance degradation

## 📊 Performance Tracking

All enhanced tools provide:
- **Execution time** - How long the operation took
- **Size changes** - Bytes added/removed
- **Line counts** - Lines added/modified/deleted
- **Success metrics** - Operation completion status

## 🔄 Backward Compatibility

The enhanced tools work alongside existing tools:
- `read_file` and `write_file` remain available
- No breaking changes to existing functionality
- Enhanced tools are additive improvements

## 🚦 Usage Examples

### Example 1: Safe File Modification
```python
# Read file with metadata
result = smart_read_file("config.json", return_metadata=True)
if result["success"]:
    content = result["content"]
    metadata = result["metadata"]
    
    # Modify content
    new_content = content.replace("old_value", "new_value")
    
    # Write with backup
    write_result = smart_write_file(
        "config.json",
        new_content,
        backup=True
    )
    
    if not write_result["success"]:
        # Check error details
        errors = get_last_errors(limit=1)
        print(f"Error: {errors['errors'][0]['suggestion']}")
```

### Example 2: Complex File Editing
```python
# Apply multiple patches atomically
patches = [
    {
        "operation": "insert",
        "line_number": 1,
        "content": "# Auto-generated header\n"
    },
    {
        "operation": "find_replace",
        "find_text": "DEBUG = True",
        "replace_text": "DEBUG = False"
    },
    {
        "operation": "replace_line",
        "line_number": 50,
        "content": "# Updated configuration\n"
    }
]

result = patch_file("settings.py", patches, validate=True)
if result["success"]:
    print(f"Applied {result['total_changes']} changes")
else:
    error_details = get_error_by_id(result["error_id"])
    print(f"Patch failed: {error_details['error']['suggestion']}")
```

## 🔧 Server Restart Required

After adding these enhanced tools, restart the MCP server to make them available:

```bash
# Stop existing server
pkill -f mcp_server.py

# Start enhanced server
python mcp_server.py
```

The new tools will be available alongside existing ones in Cursor IDE.

---

## 📈 Version History

- **v2.2.0** - Enhanced AI Assistant Edition with new tools
- **v2.0.0** - Consolidated Edition with basic tools
- **v1.1.1** - Unicode fixes
- **v1.1.0** - Chrome integration
- **v1.0.0** - Initial implementation

For technical support, check the error logs with `get_last_errors()` or review the full traceback in specific error details. 