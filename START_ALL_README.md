# Complete Development Environment Startup

## Overview

The `start_all.sh` script provides a comprehensive way to start all development services with auto-restart functionality.

## Usage

```bash
./start_all.sh
```

## Services Started

### 1. **MCP Server** (Port 8000)
- **Auto-restart**: Monitors `*.py` files via `start_mcp_auto_restart.sh`
- **Endpoint**: `http://localhost:8000/mcp`
- **Purpose**: Chrome Debug Protocol integration and "Tell Bolt to..." functionality

### 2. **Plasmo Dev Server** 
- **Auto-reload**: Built-in hot reload for extension files
- **Purpose**: Chrome extension development with live updates
- **Watches**: `*.ts`, `*.tsx`, extension manifest, popup files

### 3. **SocketIO Server** (Port 3001)
- **Auto-restart**: Monitors `socketio_server.js` and `cursor_ai_injector.py` via nodemon
- **Endpoint**: `http://localhost:3001`
- **Purpose**: Real-time communication and automation control

### 4. **Continuous Test Runner**
- **Auto-restart**: Monitors test files and source code changes
- **Purpose**: Automated testing and validation
- **Watches**: `*.ts`, `*.tsx`, `*.js`, `*.jsx`, `*.html`, `*.css`, `*.py`

## Auto-Restart Features

- **MCP Server**: Restarts within 2-5 seconds of Python file changes
- **Plasmo Dev**: Built-in hot reload for instant extension updates
- **SocketIO Server**: Nodemon-based restart for server and injector changes
- **Test Runner**: Automatic test execution on code changes

## What It Does

1. **Cleanup**: Stops any existing service instances
2. **Sequential Startup**: Starts services with proper timing delays
3. **Process Management**: Tracks PIDs and creates logs
4. **Status Reporting**: Shows all running services and endpoints

## Log Files

All services create detailed logs in the `logs/` directory:
- `logs/mcp_server.log` - MCP server output and restarts
- `logs/plasmo_dev.log` - Extension build and hot reload events
- `logs/socketio_server.log` - Socket.IO server and automation logs
- `logs/continuous_testing.log` - Test execution results

## Stopping Services

**Option 1**: Use the provided command:
```bash
pkill -f 'start_mcp_auto_restart|mcp_server.py|plasmo.*dev|socketio_server.js|continuous_test_runner'
```

**Option 2**: Individual service stopping:
```bash
pkill -f "mcp_server.py"           # Stop MCP server
pkill -f "plasmo.*dev"             # Stop Plasmo dev server
pkill -f "socketio_server.js"      # Stop SocketIO server
pkill -f "continuous_test_runner"  # Stop test runner
```

## Development Workflow

1. **Start**: `./start_all.sh` - Everything starts with auto-restart
2. **Develop**: Make changes to any files - services auto-restart/reload
3. **Debug**: Use Chrome Debug Protocol tools via MCP server
4. **Test**: Continuous testing runs automatically
5. **Stop**: Use pkill commands when done

## Integration Benefits

- **Seamless Development**: All services coordinate automatically
- **Chrome Extension**: Live updates via Plasmo dev server
- **Automation**: "Tell Bolt to..." commands via MCP server
- **Real-time Control**: SocketIO for interactive automation
- **Quality Assurance**: Continuous testing ensures code quality

## Health Checks

- **MCP Server**: `http://localhost:8000/mcp`
- **SocketIO Controller**: `http://localhost:3001`
- **Extension**: Automatically reloads in Chrome via Plasmo
- **Tests**: Results visible in `logs/continuous_testing.log`

## Troubleshooting

- **Port conflicts**: Services will clean up existing instances
- **Missing dependencies**: Script will install nodemon if needed
- **File not found**: Optional services (like SocketIO) will be skipped gracefully
- **Permission issues**: Make sure scripts are executable (`chmod +x`)

This comprehensive setup enables full-stack development with automated tooling, real-time updates, and seamless Chrome extension debugging. 