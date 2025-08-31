# Multi-Server MCP Proxy Documentation

## Overview

The Multi-Server MCP Proxy is an advanced proxy server that can simultaneously proxy multiple backend MCP servers. It provides dynamic server management, health monitoring, and tool namespace isolation.

## Features

### 🔄 Multi-Server Support
- Proxy multiple MCP servers simultaneously
- Dynamic server configuration at runtime
- Individual server enable/disable functionality
- Health monitoring for all servers

### 🛠️ Dynamic Management
- Add/remove servers via `manage()` tool
- Command-line configuration
- Real-time server status monitoring
- Error tracking and recovery

### 🏥 Health Monitoring
- Individual server health checks
- Bulk health monitoring
- Automatic error tracking
- Response time monitoring

### 🎯 Tool Management
- Server-specific tool forwarding
- Namespace isolation (planned)
- Comprehensive tool listing
- Error handling and fallbacks

## Installation

The proxy is part of the MCP server package and requires:

```bash
pip install -r requirements.txt
```

Key dependencies:
- `fastmcp>=2.6.1`
- `aiohttp>=3.8.5`
- `python-socketio>=5.8.0`

## Usage

### Command Line Interface

```bash
# Basic usage with single server
python mcp_proxy.py --stdio --servers main=http://localhost:8000/mcp

# Multiple servers
python mcp_proxy.py --stdio --servers main=http://localhost:8000/mcp,backup=http://localhost:8001/mcp

# HTTP mode
python mcp_proxy.py --http --port 8001 --servers main=http://localhost:8000/mcp

# Debug mode
python mcp_proxy.py --stdio --servers main=http://localhost:8000/mcp --debug
```

### Server Configuration Format

Servers are configured using the format: `name=url`

Examples:
- `main=http://localhost:8000/mcp`
- `backup=http://localhost:8001/mcp`
- `test=http://localhost:8002/mcp`

Multiple servers are separated by commas:
```
main=http://localhost:8000/mcp,backup=http://localhost:8001/mcp,test=http://localhost:8002/mcp
```

## Management Tools

The proxy provides three main management tools:

### 1. `manage()` Tool

The primary tool for server management:

```python
# Add a new server
manage("add", name="newserver", url="http://localhost:8002/mcp")

# Remove a server
manage("remove", name="newserver")

# List all servers
manage("list")

# Enable/disable servers
manage("enable", name="main")
manage("disable", name="backup")

# Health checks
manage("health", name="main")        # Check specific server
manage("health", name="all")         # Check all servers
```

#### Operations:

| Operation | Parameters | Description |
|-----------|------------|-------------|
| `add` | `name`, `url` | Add a new backend server |
| `remove` | `name` | Remove an existing server |
| `list` | none | List all configured servers |
| `enable` | `name` | Enable a disabled server |
| `disable` | `name` | Disable an active server |
| `health` | `name` or `"all"` | Check server health |

### 2. `proxy_status()` Tool

Get comprehensive proxy status:

```python
proxy_status()
```

Returns:
```json
{
  "proxy_info": {
    "version": "3.0.0",
    "name": "Multi-Server MCP Proxy",
    "type": "multi_server",
    "debug_mode": false
  },
  "servers": {
    "success": true,
    "servers": [...],
    "total_count": 2,
    "enabled_count": 2,
    "healthy_count": 1
  },
  "capabilities": {
    "dynamic_server_management": true,
    "health_monitoring": true,
    "server_isolation": true,
    "transport_modes": ["stdio", "http"]
  }
}
```

### 3. `proxy_health()` Tool

Quick health status:

```python
proxy_health()
```

Returns:
```json
{
  "proxy_healthy": true,
  "total_servers": 2,
  "enabled_servers": 2,
  "healthy_servers": 1,
  "status": "healthy",
  "timestamp": 1703123456.789
}
```

## Server Configuration

### ServerConfig Class

Each server is represented by a `ServerConfig` dataclass:

```python
@dataclass
class ServerConfig:
    name: str                    # Server identifier
    url: str                     # Backend URL
    enabled: bool = True         # Whether server is active
    health_status: str = "unknown"  # Health status
    last_health_check: float = 0    # Last check timestamp
    tool_count: int = 0             # Number of tools
    error_count: int = 0            # Error counter
    last_error: Optional[str] = None  # Last error message
```

### Health Status Values

- `"unknown"` - Not checked yet
- `"healthy"` - Server responding normally
- `"unhealthy"` - Server responding with errors
- `"error"` - Server not responding
- `"proxy_error"` - Failed to create proxy

## Examples

### Basic Multi-Server Setup

```bash
# Start proxy with two servers
python mcp_proxy.py --stdio --servers main=http://localhost:8000/mcp,backup=http://localhost:8001/mcp
```

### Dynamic Server Management

```python
# In your MCP client, use the manage tool:

# List current servers
result = manage("list")
print(f"Current servers: {result['servers']}")

# Add a new server
result = manage("add", name="analytics", url="http://localhost:8003/mcp")
if result["success"]:
    print(f"Added server: {result['name']}")

# Check health of all servers
result = manage("health", name="all")
print(f"Health summary: {result['summary']}")

# Disable a problematic server
result = manage("disable", name="backup")
print(f"Server disabled: {result['message']}")
```

### Configuration in Claude Desktop

Update your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "multi-server-proxy": {
      "command": "python",
      "args": [
        "/path/to/mcp_proxy.py",
        "--stdio",
        "--servers", "main=http://localhost:8000/mcp,backup=http://localhost:8001/mcp"
      ],
      "cwd": "/path/to/project",
      "description": "Multi-Server MCP Proxy"
    }
  }
}
```

## Error Handling

The proxy includes comprehensive error handling:

### Server Connection Errors
- Automatic retry logic
- Error counting and tracking
- Fallback to healthy servers
- Detailed error reporting

### Proxy Errors
- Graceful degradation
- Tool isolation
- Request routing fallbacks
- Debug logging

### Health Check Errors
- Timeout handling
- Connection error recovery
- Status tracking
- Automatic retry

## Debugging

### Debug Mode

Enable debug logging:

```bash
python mcp_proxy.py --stdio --servers main=http://localhost:8000/mcp --debug
```

Debug logs are written to `/tmp/mcp_multiproxy_debug.log`.

### Debug Information

The proxy logs:
- Server addition/removal
- Health check results
- Tool forwarding
- Error conditions
- Performance metrics

### Testing

Run the test suite:

```bash
python packages/mcp-server/test_multiproxy.py
```

This tests:
- Basic proxy functionality
- Server management operations
- Health monitoring
- Command-line configuration
- Error handling

## Architecture

### Class Structure

```
MultiServerProxy
├── servers: Dict[str, ServerConfig]
├── proxy: FastMCP
└── logger: Logger

ServerConfig
├── name: str
├── url: str
├── enabled: bool
├── health_status: str
├── last_health_check: float
├── tool_count: int
├── error_count: int
└── last_error: Optional[str]
```

### Request Flow

1. Client sends request to proxy
2. Proxy determines target server(s)
3. Request forwarded to appropriate backend
4. Response aggregated and returned
5. Health status updated

### Tool Forwarding

Currently implements basic forwarding. Future versions will include:
- Namespace prefixing (`server1.tool_name`)
- Tool conflict resolution
- Load balancing
- Failover support

## Limitations

### Current Limitations

1. **Tool Namespace Isolation**: Not fully implemented
2. **Hot Reloading**: Server changes require restart for full effect
3. **Load Balancing**: No automatic load distribution
4. **Persistence**: Server configuration not persisted

### Future Enhancements

- [ ] Full tool namespace isolation
- [ ] Configuration persistence
- [ ] Load balancing algorithms
- [ ] Hot reloading support
- [ ] Metrics collection
- [ ] WebUI for management

## Troubleshooting

### Common Issues

#### Server Not Found
```json
{
  "success": false,
  "error": "Server 'unknown' not found",
  "available_servers": ["main", "backup"]
}
```

**Solution**: Check server name spelling and use `manage("list")` to see available servers.

#### Connection Refused
```json
{
  "success": false,
  "error": "Connection refused",
  "status": "error"
}
```

**Solution**: Verify backend server is running and URL is correct.

#### Tool Not Found
```json
{
  "error": "Tool 'unknown_tool' not found"
}
```

**Solution**: Check if server is enabled and healthy using `manage("health", name="all")`.

### Log Analysis

Check debug logs for detailed information:

```bash
tail -f /tmp/mcp_multiproxy_debug.log
```

Look for:
- Server connection attempts
- Health check failures
- Tool forwarding errors
- Request routing issues

## Support

For issues and questions:
1. Check the debug logs
2. Run the test suite
3. Verify server configurations
4. Review health status

The proxy is designed to be robust and self-healing, with comprehensive error reporting to help diagnose issues quickly. 