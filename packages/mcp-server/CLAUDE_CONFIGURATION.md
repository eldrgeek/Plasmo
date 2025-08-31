# Claude Configuration for Zero-Downtime Development

## Overview

This guide shows how to configure Claude CLI to use the proxy server for zero-downtime development. When using the proxy, you can modify and restart the MCP server without interrupting your Claude session.

## Configuration Files

### Claude CLI Configuration

File: `client_configs/claude_cli_config.json`

```json
{
  "server_url": "http://127.0.0.1:8001/mcp",
  "transport": "streamable-http"
}
```

### Claude Desktop Configuration

File: `client_configs/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "plasmo-proxy": {
      "command": "python",
      "args": [
        "/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_testing_proxy.py",
        "--stdio"
      ]
    }
  }
}
```

## Setup Instructions

### 1. Start the Development Environment

```bash
# Start both MCP server and proxy
python start_development_mode.py

# Or start just the proxy (if server is already running)
python start_development_mode.py --proxy-only
```

This will:
- Start MCP server on port 8000
- Start proxy server on port 8001
- Enable file watching for auto-restart
- Provide zero-downtime client connections

### 2. Configure Claude CLI

#### Option A: Use the generated config file
```bash
# Copy the config to your Claude CLI settings location
cp client_configs/claude_cli_config.json ~/.claude/server_config.json
```

#### Option B: Use command line arguments
```bash
# Connect directly to proxy
claude --server-url http://127.0.0.1:8001/mcp

# Or use environment variable
export CLAUDE_SERVER_URL="http://127.0.0.1:8001/mcp"
claude
```

### 3. Configure Claude Desktop

#### Option A: Update existing config
```bash
# Edit your Claude Desktop config
nano ~/.claude/claude_desktop_config.json

# Add the proxy server configuration
{
  "mcpServers": {
    "plasmo-proxy": {
      "command": "python",
      "args": [
        "/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_testing_proxy.py",
        "--stdio"
      ]
    }
  }
}
```

#### Option B: Use the generated config
```bash
# Use the setup script to update your config
python setup_proxy.py --config
```

## Benefits of Using the Proxy

### ✅ **Zero-Downtime Development**
- No need to restart Claude when MCP server changes
- Continuous development workflow
- No lost context or conversation history

### ✅ **Automatic Server Management**
- File watching automatically restarts MCP server
- Health monitoring and recovery
- Graceful error handling

### ✅ **Improved Productivity**
- Faster development cycles
- No interruption during code changes
- Better debugging experience

## Development Workflow

### 1. Start Development Environment
```bash
python start_development_mode.py
```

### 2. Connect Claude CLI to Proxy
```bash
claude --server-url http://127.0.0.1:8001/mcp
```

### 3. Make Changes to MCP Server
- Edit `mcp_server.py` or any module
- Server automatically restarts
- Claude CLI remains connected
- No interruption to your work

### 4. Test Changes
- Tools are immediately available
- No need to reconnect
- Seamless development experience

## Troubleshooting

### Proxy Connection Issues

**Problem:** Claude CLI can't connect to proxy
```bash
# Check proxy health
curl http://127.0.0.1:8001/health

# Check proxy status
python setup_proxy.py --test
```

**Solution:** 
```bash
# Restart proxy
python setup_proxy.py --start

# Or restart full development environment
python start_development_mode.py
```

### MCP Server Issues

**Problem:** Tools not working properly
```bash
# Check MCP server health
curl http://127.0.0.1:8000/health

# Check proxy logs
tail -f mcp_proxy.log
```

**Solution:**
```bash
# Restart development environment
python start_development_mode.py

# Or restart just the MCP server (proxy handles this)
# The proxy will automatically reconnect
```

### Configuration Issues

**Problem:** Wrong server URL
```bash
# Check current configuration
cat client_configs/claude_cli_config.json

# Verify URLs
echo "MCP Server: http://127.0.0.1:8000"
echo "Proxy Server: http://127.0.0.1:8001"
```

**Solution:**
```bash
# Regenerate configurations
python setup_proxy.py --config

# Use correct proxy URL
claude --server-url http://127.0.0.1:8001/mcp
```

## Port Configuration

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| MCP Server | 8000 | http://127.0.0.1:8000 | Direct server connection |
| **Proxy Server** | 8001 | http://127.0.0.1:8001 | **Recommended for development** |

## Best Practices

### 1. Always Use Proxy for Development
```bash
# ✅ Recommended: Use proxy
claude --server-url http://127.0.0.1:8001/mcp

# ❌ Not recommended: Direct connection
claude --server-url http://127.0.0.1:8000/mcp
```

### 2. Start Development Environment First
```bash
# Start proxy and server
python start_development_mode.py

# Then connect Claude
claude --server-url http://127.0.0.1:8001/mcp
```

### 3. Monitor Health
```bash
# Check proxy health regularly
python setup_proxy.py --test

# Run comprehensive tests
python run_comprehensive_tests.py
```

### 4. Use Verbose Mode for Debugging
```bash
# Development environment with verbose logging
python start_development_mode.py --verbose

# Proxy with verbose logging
python setup_proxy.py --start --verbose
```

## Configuration Files Summary

```
packages/mcp-server/
├── client_configs/
│   ├── claude_cli_config.json      # ✅ Use this for Claude CLI
│   ├── claude_desktop_config.json  # ✅ Use this for Claude Desktop
│   └── cursor_ide_config.json      # For Cursor IDE
├── start_development_mode.py       # Start dev environment
├── setup_proxy.py                  # Proxy management
└── mcp_testing_proxy.py           # Proxy server
```

## Environment Variables

```bash
# Set default proxy URL
export CLAUDE_SERVER_URL="http://127.0.0.1:8001/mcp"

# Set proxy configuration
export MCP_PROXY_PORT=8001
export MCP_SERVER_PORT=8000

# Enable debug logging
export MCP_DEBUG=1
```

## Quick Reference

### Start Development
```bash
python start_development_mode.py
```

### Connect Claude CLI
```bash
claude --server-url http://127.0.0.1:8001/mcp
```

### Test Configuration
```bash
python setup_proxy.py --test
```

### Health Check
```bash
curl http://127.0.0.1:8001/health
```

---

**Remember:** Always use the proxy (port 8001) for development to get zero-downtime benefits!