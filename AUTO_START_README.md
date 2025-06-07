# Auto-Start Development Environment

This document describes the automatic startup system for the Plasmo extension development environment, including MCP server integration with Cursor.

## Overview

The development environment includes:
- **MCP Server**: Runs in stdio mode for Cursor integration
- **SocketIO Server**: Real-time communication (port 3001)
- **Plasmo Dev Server**: Extension development with hot reload
- **MCP Protocol Testing**: Validates MCP server functionality

## VS Code Task Integration

### Auto-Start on Folder Open

When you open the project in Cursor/VS Code, the following tasks automatically start:

```json
{
  "label": "Auto-Start All Services",
  "dependsOrder": "parallel",
  "dependsOn": [
    "Start MCP Server for Cursor",
    "Start SocketIO Server", 
    "Start Plasmo Dev"
  ],
  "runOptions": {
    "runOn": "folderOpen"
  }
}
```

### Individual Service Tasks

#### MCP Server for Cursor
```json
{
  "label": "Start MCP Server for Cursor",
  "command": "python3",
  "args": ["mcp_server.py", "--stdio"],
  "presentation": {
    "reveal": "never"  // Runs silently for Cursor
  }
}
```

This starts the MCP server in **stdio mode** which is required for Cursor integration. The server communicates via stdin/stdout rather than HTTP.

#### SocketIO Server
```json
{
  "label": "Start SocketIO Server",
  "command": "nodemon",
  "args": ["--watch", "socketio_server.js", "--exec", "node socketio_server.js"]
}
```

#### Plasmo Dev Server
```json
{
  "label": "Start Plasmo Dev",
  "command": "pnpm",
  "args": ["dev"]
}
```

## Manual Control

### Start All Services
Use the Command Palette (`Cmd+Shift+P`):
1. Type "Tasks: Run Task"
2. Select "Auto-Start All Services"

### Stop All Services
Use the Command Palette:
1. Type "Tasks: Run Task" 
2. Select "Stop All Services"

Or run manually:
```bash
./stop_all_services.sh
```

### Check Service Status
```bash
./check_services.sh
```

## Testing Integration

### MCP Protocol Tests
Run tests that go through the actual MCP protocol:
```bash
python3 test_mcp_protocol.py --verbose
```

Or via VS Code task:
1. Command Palette → "Tasks: Run Task"
2. Select "Run MCP Tests"

The MCP protocol tests validate:
- Server initialization and communication
- Tool discovery (`tools/list`)
- File operations through MCP protocol
- System operations through MCP protocol
- Code analysis through MCP protocol

### Legacy Direct Tests
For comparison, direct function call tests:
```bash
./run_tests.sh --verbose
```

## MCP Server Integration

### Cursor Configuration
The MCP server is configured in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["/path/to/mcp_server.py", "--stdio"],
      "env": {
        "PYTHONPATH": "/path/to/project"
      }
    }
  }
}
```

### Stdio vs HTTP Mode
- **Stdio Mode**: Used by Cursor for MCP integration
  - Started with: `python3 mcp_server.py --stdio`
  - Communication via stdin/stdout JSON-RPC
  - Required for Cursor MCP tools to work

- **HTTP Mode**: Used for standalone testing
  - Started with: `python3 mcp_server.py` (default)
  - REST API on http://localhost:8000
  - Used by `start_all_services.sh`

## File Watching and Auto-Restart

### MCP Server Auto-Restart
The MCP server automatically restarts when these files change:
- `mcp_server.py`
- `chrome_debug_fixes.py`
- `requirements.txt`

### SocketIO Server Auto-Restart
Auto-restarts when these files change:
- `socketio_server.js`
- `cursor_ai_injector.py`

### Plasmo Dev Server
Built-in hot reload for:
- TypeScript/React files
- CSS files
- Extension manifest

## Log Files
All services log to the `logs/` directory:
- `logs/mcp_server.log` - MCP server output
- `logs/socketio_server.log` - SocketIO server output  
- `logs/plasmo_dev.log` - Plasmo development server output

## Troubleshooting

### MCP Server Not Connecting to Cursor
1. Check that MCP server is running in stdio mode (not HTTP mode)
2. Verify `claude_desktop_config.json` path and configuration
3. Restart Cursor after configuration changes
4. Check VS Code tasks are using `--stdio` flag

### Services Not Auto-Starting
1. Ensure `.vscode/settings.json` has: `"task.allowAutomaticTasks": "on"`
2. Check `.vscode/tasks.json` syntax
3. Verify all required files exist (`mcp_server.py`, `socketio_server.js`, `package.json`)

### Port Conflicts
- SocketIO Server: Uses port 3001
- MCP Server (HTTP mode): Uses port 8000
- Plasmo Dev: Uses dynamic port (usually 1012, 1013, etc.)

### Permission Issues
Make scripts executable:
```bash
chmod +x start_all_services.sh
chmod +x stop_all_services.sh  
chmod +x check_services.sh
```

## Development Workflow

### Typical Development Session
1. Open project in Cursor → Services auto-start
2. MCP tools become available in Cursor
3. Extension auto-reloads on file changes
4. Use MCP protocol tests to validate changes
5. Use "Stop All Services" when done

### When MCP Server Changes
1. Edit `mcp_server.py`
2. Auto-restart detects changes and restarts server
3. Run `python3 test_mcp_protocol.py` to validate
4. Cursor automatically reconnects to updated server

### Chrome Debugging Integration  
1. Start Chrome with debug flags: `./launch-chrome-debug.sh`
2. Use MCP tools for Chrome automation
3. Monitor extension behavior through MCP server logs

## Architecture Benefits

### Parallel Service Startup
- All services start simultaneously for faster development setup
- Independent restart capabilities
- Isolated logging and monitoring

### MCP Protocol Integration
- Real MCP protocol validation ensures Cursor compatibility
- Tests the actual communication layer used by Cursor
- Validates JSON-RPC message handling

### Hot Reload Support
- MCP server changes don't require manual restart
- Extension changes immediately reflect in browser
- SocketIO server updates maintain WebSocket connections

This setup provides a complete development environment with automatic MCP server integration, real-time testing, and seamless Cursor workflow integration. 