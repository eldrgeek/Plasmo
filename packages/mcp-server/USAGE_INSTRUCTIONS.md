# MCP Server Usage Instructions

## Quick Start

### 1. Start Development Environment

```bash
# Start with zero-downtime proxy
python start_development_mode.py

# Or start with verbose logging
python start_development_mode.py --verbose
```

### 2. Connect Claude CLI

Use the correct command `claude` (not `claude-code`) with the **proxy server**:

```bash
# ✅ RECOMMENDED: Connect to proxy for zero-downtime development
claude --server-url http://127.0.0.1:8001/mcp

# ❌ NOT RECOMMENDED: Direct connection (will restart on server changes)
# claude --server-url http://127.0.0.1:8000/mcp
```

**Why use the proxy?**
- No interruptions when server restarts
- Continuous development workflow
- Better debugging experience

### 3. Connect Claude Desktop

Configure in `~/.claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "plasmo-proxy": {
      "command": "python",
      "args": [
        "/path/to/mcp_testing_proxy.py",
        "--stdio"
      ]
    }
  }
}
```

## Available Tools

The MCP server provides 37 tools across these categories:

### Agent Management (8 tools)
- `register_agent_with_name` - Register agent with custom name
- `get_current_agent_name` - Get current agent identity
- `messages` - Multi-agent messaging system
- `notify` - Send notifications between agents
- `launch_claude_instance` - Launch new Claude instances
- `list_claude_instances` - List active instances
- `send_inter_instance_message` - Inter-instance communication
- `coordinate_claude_instances` - Coordinate multiple instances

### File Operations (6 tools)
- `smart_write_file` - Advanced file writing with backups
- `smart_read_file` - Auto-encoding detection
- `smart_edit_file` - Precise line-based editing
- `patch_file` - Atomic multi-change operations
- `file_manager` - Advanced file operations
- `get_project_structure` - Directory analysis

### Chrome Debug Protocol (4 tools)
- `connect_to_chrome` - WebSocket connection
- `get_chrome_tabs` - Tab management
- `launch_chrome_debug` - Chrome instance launching
- `execute_javascript` - JavaScript execution

### Service Management (8 tools)
- `service_status` - Get service status
- `start_service` / `stop_service` / `restart_service`
- `start_all_services` / `stop_all_services`
- `service_logs` - Get service logs
- `service_health_check` - Health monitoring

### Firebase Operations (4 tools)
- `firebase_setup_new_project` - Create Firebase project
- `firebase_configure_existing_project` - Configure existing project
- `firebase_project_status` - Get project status
- `firebase_batch_operations` - Batch operations

### System Information (4 tools)
- `analyze_code` - Code analysis and metrics
- `get_system_info` - System information
- `server_info` - MCP server status
- `health` - Health endpoint

### Browser Automation (3 tools)
- `send_orchestration_command` - Multi-LLM orchestration
- `inject_prompt_native` - Native keyboard automation
- `focus_and_type_native` - Application focus and typing

## Development Workflow

### Zero-Downtime Development

1. **Start the development environment:**
   ```bash
   python start_development_mode.py
   ```

2. **Connect your Claude client to the proxy:**
   ```bash
   claude --server-url http://127.0.0.1:8001/mcp
   ```

3. **Edit MCP server code** - Server automatically restarts, clients stay connected

4. **Test your changes** - No need to reconnect clients

### Testing

Run comprehensive tests:

```bash
# Run all tests
python run_comprehensive_tests.py

# Run with verbose output
python run_comprehensive_tests.py --verbose

# Run tests in parallel
python run_comprehensive_tests.py --parallel

# Save test report
python run_comprehensive_tests.py --save-report
```

### Proxy Management

Test and configure the proxy:

```bash
# Test proxy setup
python setup_proxy.py --test

# Generate client configs
python setup_proxy.py --config

# Start proxy only
python setup_proxy.py --start
```

## Common Commands

### Claude CLI Examples

```bash
# Basic connection
claude --server-url http://127.0.0.1:8001/mcp

# List available tools
claude --server-url http://127.0.0.1:8001/mcp --list-tools

# Use a specific tool
claude --server-url http://127.0.0.1:8001/mcp --tool health

# Interactive mode
claude --server-url http://127.0.0.1:8001/mcp --interactive
```

### File Operations

```bash
# Read a file
claude --tool smart_read_file --args '{"file_path": "/path/to/file.txt"}'

# Write a file
claude --tool smart_write_file --args '{"file_path": "/path/to/file.txt", "content": "Hello World"}'

# Edit a file
claude --tool smart_edit_file --args '{"file_path": "/path/to/file.txt", "operation": "replace_line", "line_number": 1, "content": "New content"}'
```

### Chrome Debugging

```bash
# Connect to Chrome
claude --tool connect_to_chrome --args '{"port": 9222}'

# Get tabs
claude --tool get_chrome_tabs

# Execute JavaScript
claude --tool execute_javascript --args '{"code": "console.log(\"Hello\")", "tab_id": "tab_id_here"}'
```

## Configuration

### Environment Variables

```bash
export MCP_SERVER_PORT=8000
export MCP_PROXY_PORT=8001
export MCP_LOG_LEVEL=INFO
export CHROME_DEBUG_PORT=9222
```

### Server Configuration

Edit `mcp_server.py` for custom configuration:

```python
# Server settings
SERVER_PORT = 8000
DEBUG_MODE = True
ENABLE_CORS = True

# Chrome settings
CHROME_DEBUG_PORT = 9222
CHROME_AUTO_LAUNCH = False

# File operation settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
BACKUP_FILES = True
```

## Troubleshooting

### Common Issues

1. **Connection refused**
   ```bash
   # Check if server is running
   curl http://127.0.0.1:8000/health
   
   # Start the server
   python mcp_server.py
   ```

2. **Proxy not working**
   ```bash
   # Test proxy health
   curl http://127.0.0.1:8001/health
   
   # Restart proxy
   python setup_proxy.py --start
   ```

3. **Chrome debugging not working**
   ```bash
   # Launch Chrome with debugging
   python -c "from chrome_debug_client import launch_chrome_debug; launch_chrome_debug()"
   ```

4. **File permission errors**
   ```bash
   # Check file permissions
   chmod +x start_development_mode.py
   chmod +x setup_proxy.py
   ```

### Debug Mode

Enable verbose logging:

```bash
# Server with debug logging
python mcp_server.py --debug

# Development mode with verbose output
python start_development_mode.py --verbose

# Tests with verbose output
python run_comprehensive_tests.py --verbose
```

### Health Checks

```bash
# Check server health
curl http://127.0.0.1:8000/health

# Check proxy health  
curl http://127.0.0.1:8001/health

# Run comprehensive health check
python run_comprehensive_tests.py
```

## Performance Tips

1. **Use the proxy for development** - Eliminates client restart overhead
2. **Enable parallel testing** - Faster test execution
3. **Use file watching** - Automatic server restart on changes
4. **Monitor resource usage** - Check system performance

## Security Notes

1. **Path validation** - All file operations validate paths for security
2. **Input sanitization** - User inputs are properly validated
3. **Chrome debugging** - Only connect to trusted Chrome instances
4. **Network access** - Server runs on localhost by default

## Support

- Check logs in the server output
- Run health checks: `python run_comprehensive_tests.py`
- Test proxy: `python setup_proxy.py --test`
- Review documentation in `MODULAR_ARCHITECTURE.md`