# MCP Server Changelog

## [2.2.3] - 2025-06-20 - Complete Fix

### 🛠️ **FINAL RESOLUTION**
- **Fixed Notification System**: Resolved remaining `MESSAGING_ROOT` undefined error preventing server startup
- **Complete Dynamic Path Conversion**: All messaging and notification system paths now use dynamic functions
- **Server Startup Issue**: Fixed the critical `NameError: name 'MESSAGING_ROOT' is not defined` error

### 🔧 **TECHNICAL COMPLETION**
- **Notification Constants Fixed**: Converted remaining notification system constants to dynamic functions:
  - `NOTIFICATIONS_ROOT` → `get_notifications_root()`
  - `NOTIFICATIONS_DIR` → `get_notifications_dir()`
  - `CANCEL_FLAGS_DIR` → `get_cancel_flags_dir()`
- **All Path Dependencies Resolved**: No more import-time path evaluation preventing proper working directory support
- **Server Now Fully Functional**: MCP server can start without constant reference errors

### 🐛 **CRITICAL BUG FIXES**
- Fixed server crash on startup due to undefined `MESSAGING_ROOT` constant
- All notification functions (`create_notification`, `get_pending_notifications`, `delete_notifications`, `set_cancel_flag`, `check_cancel_flag`) now use dynamic paths
- Complete elimination of static path constants that were evaluated at import time

---

## [2.2.2] - 2025-06-20 - Fix Attempt 2

### 🛠️ **CRITICAL FIXES**
- **Fixed Dynamic Messaging Paths**: Messaging directories now respect working directory changes (prevents read-only filesystem errors)
- **Fixed Tool Registration Detection**: Improved tool counting mechanism with FastMCP registry access and manual fallback
- **Fixed Absolute Path Issue**: All messaging paths now use dynamic functions instead of import-time constants
- **Enhanced Error Diagnosis**: Better tool exposure detection for STDIO vs HTTP transports

### 🔧 **TECHNICAL IMPROVEMENTS**
- **Dynamic Path Resolution**: All messaging functions now use `get_*_dir()` functions that respect `Path.cwd()`
- **Better Tool Counting**: FastMCP registry detection with comprehensive fallback to manual tool list
- **Transport-Aware Diagnostics**: Server info now properly distinguishes STDIO and HTTP tool availability

### 🐛 **BUG FIXES**  
- STDIO servers no longer fail with "[Errno 30] Read-only file system: '/messages'"
- Tool count now shows actual available tools instead of 0
- Messaging system works correctly after working directory changes
- Claude Desktop STDIO connections can now access all file operations and messaging

---

## [2.2.1] - 2025-06-20 - Fix Attempt 1

### 🛠️ **FIXES**
- **Fixed Working Directory Issue**: Server now properly sets working directory to project root when launched in STDIO mode
- **Fixed Startup Script Paths**: Updated all startup scripts to use correct `packages/mcp-server/mcp_server.py` path after refactoring
- **Fixed Auto-Restart Monitoring**: Corrected file paths in auto-restart scripts to monitor the right files
- **Added Fix Tracking**: Server info endpoint now includes fix status and diagnostic information

### 🔧 **IMPROVEMENTS**
- **Enhanced Server Info**: Added `fix_status`, `working_directory`, and `debug_info` fields to server info endpoint
- **Better Diagnostics**: Server now reports whether messaging directories exist and project files are accessible
- **Service Manager Integration**: Fixed service manager to properly start/stop/restart MCP server with correct paths

### 🐛 **BUG FIXES**
- Claude Desktop STDIO connections now have correct working directory (`/Users/MikeWolf/Projects/Plasmo` instead of `/`)
- Inter-agent messaging system now works properly with correct file system permissions
- File operations (`smart_read_file`, `smart_write_file`) now use relative paths from project root
- Fixed "Read-only file system" errors in messaging directory

### 📋 **TECHNICAL DETAILS**
- **Issue**: MCP server was running from root directory (`/`) instead of project directory
- **Root Cause**: Startup scripts had outdated paths after code refactoring to `packages/mcp-server/`
- **Solution**: Updated all startup scripts, added wrapper script for guaranteed working directory
- **Verification**: Server info endpoint now shows current working directory and file accessibility

---

## [2.2.0] - 2025-06-19 - Enhanced AI-Assistant Edition

### ✨ **NEW FEATURES**
- Consolidated MCP server with Chrome Debug Protocol integration
- Enhanced file operations with security validation
- Real-time console monitoring and JavaScript execution
- Multi-agent coordination and messaging system
- Firebase automation capabilities
- Advanced Chrome debugging tools

### 🔧 **IMPROVEMENTS**
- FastMCP framework integration for better performance
- Enhanced error handling and logging
- Unicode-safe operations
- Thread-safe resource management
- Comprehensive tool collection (45+ tools)

---

## [2.0.1] - 2025-06-18 - Stability Release

### 🐛 **BUG FIXES**
- Basic HTTP server functionality
- Initial Chrome Debug Protocol support
- Core file operations

---

## [2.0.0] - 2025-06-17 - Major Rewrite

### ✨ **NEW FEATURES**
- Complete rewrite using FastMCP framework
- Chrome Debug Protocol integration
- Enhanced security and validation
- Multi-agent support foundation

### 🔧 **IMPROVEMENTS**
- Better error handling
- Improved logging system
- Enhanced performance
- Modular architecture

---

## [1.0.0] - 2025-06-15 - Initial Release

### ✨ **NEW FEATURES**
- Basic MCP server functionality
- File operations
- Simple HTTP endpoints
- Basic logging

---

## 2024-01-XX - Test Consolidation

### Enhanced Protocol Tester
- **CONSOLIDATED**: Combined `test_proxy_tools.py` functionality into `mcp_protocol_tester.py`
- **NEW**: Added `--target=proxy` option for testing proxy servers
- **NEW**: Added `--simple` flag for quick proxy validation 
- **NEW**: Added `test_simple_proxy_validation()` method with the same logic as standalone proxy tester
- **REMOVED**: `test_proxy_tools.py` (functionality merged into main tester)

#### Usage Examples:
```bash
# Test direct server (all tests)
python mcp_protocol_tester.py

# Test proxy server (all tests)  
python mcp_protocol_tester.py --target=proxy

# Quick proxy validation (simple 3-step test)
python mcp_protocol_tester.py --target=proxy --simple

# Run specific test
python mcp_protocol_tester.py --test=read_file

# List available tests
python mcp_protocol_tester.py --list-tests
```

#### Benefits:
- Single unified testing tool for both direct and proxy testing
- Reduced code duplication and maintenance burden
- Consistent test framework and reporting
- Command-line driven test selection

## Version Format

- **Major.Minor.Patch** (e.g., 2.2.1)
- **Fix Attempts** are indicated in comments for tracking issue resolution
- **Build Time** is dynamically generated for each server instance 