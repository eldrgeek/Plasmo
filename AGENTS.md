# AI Agents & Tools for Plasmo Extension Development

## Overview
This project integrates multiple AI-powered tools and agents to enhance the development experience for Plasmo browser extensions. The primary integration is through an MCP (Model Context Protocol) server that provides Chrome Debug Protocol access to AI assistants.

## Available Agents & Tools

### 1. Cursor AI Assistant (Primary)
**Purpose**: Main development assistant with full project context
**Capabilities**:
- Code generation and refactoring
- Real-time extension debugging through MCP server
- Chrome Debug Protocol integration
- Console log monitoring and analysis
- Extension auto-reload management

**MCP Tools Available**:
- `connect_to_chrome()` - Establish debugging connection
- `get_chrome_tabs()` - List available browser tabs
- `get_chrome_debug_info()` - Comprehensive debug status
- `start_console_monitoring(tab_id)` - Begin log capture
- `get_console_logs()` - Retrieve captured logs
- `execute_javascript(code, tab_id)` - Run code in browser context
- `set_breakpoint(url, line, tab_id)` - Set debugging breakpoints
- `launch_chrome_debug()` - Start Chrome with debugging enabled

### 2. FastMCP Server
**Purpose**: Bridge between AI assistants and Chrome Debug Protocol
**Location**: `mcp_server.py`
**Port**: `http://127.0.0.1:8000`

**Key Features**:
- Real-time Chrome debugging integration
- Extension service worker monitoring
- Console log aggregation
- JavaScript execution in browser context
- WebSocket connection management

**JSON Serialization**: All tools return JSON-safe data structures, handling complex Chrome Debug Protocol objects automatically.

### 3. Chrome Debug Protocol Interface
**Purpose**: Low-level browser automation and debugging
**Configuration**: 
- Debug port: `9222`
- Required flags: `--remote-debugging-port=9222 --remote-allow-origins=*`
- Launch script: `./launch-chrome-debug.sh`

## Workflow Integration

### Extension Development Cycle
1. **Start Chrome**: Use `launch_chrome_debug()` or run `./launch-chrome-debug.sh`
2. **Connect MCP**: AI assistant connects via `connect_to_chrome()`
3. **Monitor Extension**: Use `start_console_monitoring()` for real-time logs
4. **Debug Issues**: Execute JavaScript, set breakpoints, analyze logs
5. **Auto-reload**: Extension rebuilds and reloads automatically on file changes

### AI-Assisted Debugging
The AI assistant can:
- Analyze console logs for errors and patterns
- Suggest fixes based on Chrome Debug Protocol data
- Execute diagnostic JavaScript in extension context
- Monitor extension lifecycle events
- Track service worker registration and updates

### Code Analysis & Generation
- **Context-aware**: AI has full access to extension source code
- **Real-time feedback**: Immediate testing through Chrome debug tools
- **Auto-correction**: AI can identify and fix common extension issues
- **Performance monitoring**: Track extension metrics through debug tools

## Setup Instructions

### For AI Assistants
1. Ensure MCP server is running: `./start_mcp.sh`
2. Connect to Chrome debug session
3. Use available MCP tools for debugging and monitoring
4. Restart Cursor if MCP tools are not available

### For Developers
1. Install dependencies: `pip install -r requirements.txt`
2. Configure Cursor MCP integration (see `MCP_README.md`)
3. Launch Chrome with debugging: `./launch-chrome-debug.sh`
4. Start development with AI assistance enabled

## Best Practices

### For AI Interactions
- Use `get_chrome_debug_info()` first to understand current state
- Monitor console logs continuously during development
- Execute small test scripts to verify extension functionality
- Use parallel tool calls for efficiency when gathering multiple data points

### Error Handling
- Always check Chrome connection status before debugging operations
- Handle WebSocket timeouts gracefully
- Verify extension service worker is active before monitoring
- Account for service worker ID changes on Chrome restart

### Performance Considerations
- Limit console log retention to prevent memory issues
- Use targeted JavaScript execution rather than broad monitoring
- Clear logs periodically with `clear_console_logs()`
- Monitor multiple tabs selectively based on development needs

## Advanced Features

### Extension Service Worker Debugging
- Automatic detection of Plasmo extension service workers
- Real-time console log streaming
- JavaScript injection for runtime diagnostics
- Breakpoint setting in extension code

### Multi-tab Development
- Support for debugging multiple browser tabs simultaneously
- Tab-specific console log filtering
- Cross-tab extension testing capabilities
- Coordinated debugging across extension contexts

### Automated Testing Integration
- AI-generated test scenarios based on extension behavior
- Automated console log analysis for error detection
- Performance metric collection through debug tools
- Regression testing through Chrome automation

## Troubleshooting

### Common Issues
- **MCP connection failed**: Check if server is running on port 8000
- **Chrome debug unavailable**: Verify Chrome launched with debug flags
- **Extension not found**: Ensure extension is loaded and service worker is active
- **WebSocket errors**: Check `--remote-allow-origins=*` flag is set

### Debug Commands
```bash
# Start MCP server
./start_mcp.sh

# Launch Chrome with debugging
./launch-chrome-debug.sh

# Check server status
curl http://127.0.0.1:8000/health

# View logs
tail -f mcp_server.log
```

This integration provides a powerful development environment where AI assistants have direct access to browser debugging capabilities, enabling sophisticated extension development and troubleshooting workflows. 