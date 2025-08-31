# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 CRITICAL: Claude Instance Management Rules

**IMPORTANT REMINDERS:**
1. **MCP Server**: Should ALWAYS be running continuously on port 8000 - DO NOT start new servers
2. **Claude Command**: Use `claude` (not `claude-code`) - Install from https://claude.ai/code
3. **New Instances**: Connect to existing server, register unique agent names via tools
4. **Connection**: Use `claude --server-url http://localhost:8000` (or 8001 for proxy)

## Project Overview

This is a Plasmo browser extension monorepo with integrated MCP (Model Context Protocol) server architecture. The project enables AI-assisted development through Chrome Debug Protocol integration and multi-agent coordination.

## Key Technologies

- **Plasmo Framework**: Chrome extension development framework
- **TypeScript/React**: Extension UI and logic
- **FastMCP Python Server**: MCP server for Chrome debugging and AI coordination
- **Chrome Debug Protocol**: Browser automation and debugging
- **Socket.IO**: Real-time communication between services
- **Firebase**: Chat application backend
- **PNPM**: Package manager (workspaces)

## Development Commands

### Primary Development
```bash
# Install dependencies
pnpm install

# Development mode (Chrome extension)
pnpm dev

# Build extension
pnpm build

# Package extension for distribution
pnpm package

# Start all services
python launch_all.py
```

### Service Management
```bash
# Start MCP server only
pnpm start-mcp

# Start Socket.IO server
pnpm start-socketio

# Start dashboard
pnpm start-dashboard

# Start collaboration tools
pnpm start-collaboraition
```

### Testing & Quality
```bash
# Run enhanced tests
./run_enhanced_tests.sh

# Test Linux compatibility
./test_linux_compatibility.sh

# Format Python code
black .

# Type checking (use tsc in extension directory)
cd packages/chrome-extension && npx tsc --noEmit
```

## Architecture Overview

### Monorepo Structure
```
packages/
├── chrome-extension/     # Main Plasmo extension
├── mcp-server/          # FastMCP server for AI integration
├── socketio-server/     # Real-time communication
├── dashboard-framework/ # Monitoring dashboards
├── firebase-chat/       # Firebase chat application
├── collaboraition/      # Multi-agent coordination
└── testing-framework/   # Test utilities
```

### MCP Server Integration
The MCP server (`packages/mcp-server/mcp_server.py`) provides 30+ tools for:
- Chrome Debug Protocol automation
- File operations with advanced features
- Multi-agent messaging and coordination
- Error tracking and recovery
- Performance monitoring

### Extension Architecture
- **Popup**: Main user interface (`popup.tsx`)
- **Background**: Service worker with tab management (`background.ts`)
- **Content Scripts**: Page interaction (`contents/main.ts`)
- **Options**: Settings page (`options.tsx`)

## Development Guidelines

### Chrome Extension Development
- Use Manifest V3 APIs exclusively
- Implement proper message passing between contexts
- Use Chrome storage APIs (never localStorage in extension contexts)
- Handle async Chrome API calls with proper error handling
- Follow React 18 patterns with hooks

### MCP Server Development
- Always ensure return values are JSON-serializable
- Use `make_json_safe()` helper for object conversion
- Chrome Debug Protocol requires INTEGER request IDs (not strings)
- Use `int(time.time() * 1000000) % 1000000` for request IDs
- Test Chrome flag compatibility for debugging features

### Code Quality Standards
- TypeScript strict mode enabled
- Use proper error handling and try-catch blocks
- Follow established patterns in `.cursor/rules/`
- Import types with `import type` syntax
- Group imports: external libraries first, then local modules

## Critical Configuration

### Chrome Debug Setup
```bash
# Launch Chrome with debug flags
./chrome_debug_launcher.py

# Required flags:
--remote-debugging-port=9222 
--remote-allow-origins=*
```

### MCP Server Connection
- **HTTP Mode**: `python mcp_server.py` (port 8000)
- **STDIO Mode**: `python mcp_server.py --stdio`
- **Proxy Mode**: Uses `mcp_proxy.py` for multi-client support

## Testing Strategy

### Extension Testing
- Test functionality both standalone and through MCP debugging
- Verify auto-reload works with file changes
- Use MCP server console monitoring for debugging
- Test cross-browser compatibility

### MCP Server Testing
- Test all tools with JSON serialization
- Verify Chrome Debug Protocol integration
- Test WebSocket connections and error handling
- Validate multi-agent coordination features

## Common Issues & Solutions

### Chrome Debug Protocol
- **403 WebSocket errors**: Ensure `--remote-allow-origins=*` flag
- **Integer ID errors**: Use integer request IDs, not strings
- **Extension not found**: Check service worker is running
- **MCP tools unavailable**: Restart application after server changes

### File Management
- Never commit `__pycache__/`, `*.log`, or Chrome profile contents
- Use `.gitignore` patterns for build artifacts
- Document Chrome version compatibility for debugging features

## Performance Considerations

- Extension contexts have memory limitations
- Use efficient message passing patterns
- Implement proper cleanup for WebSocket connections
- Monitor service worker lifecycle events
- Use lazy loading for large components

## Security Guidelines

- Never commit secrets or API keys
- Use proper input validation for all user inputs
- Implement CSP headers for extension pages
- Validate all Chrome API permissions
- Use secure communication protocols

## Multi-Agent Coordination

The project supports coordinating multiple AI agents through:
- **Message passing**: File-based messaging system
- **Task distribution**: Parallel execution across agents
- **Error coordination**: Shared error tracking
- **Resource sharing**: Coordinated file operations

## Firebase Integration

For chat applications:
- Configure Firebase project with `firebase-console-automation.js`
- Use Firestore for real-time messaging
- Implement proper authentication flows
- Follow Firebase security rules

## Environment Setup

### Required Tools
- Node.js >= 18.0.0
- PNPM >= 8.0.0
- Python >= 3.8
- Chrome/Chromium browser

### Environment Variables
Check `shared/environment.env.example` for required configuration.

## 🚨 IMPORTANT: Claude Instance Management

### MCP Server Should Always Be Running
- **CRITICAL**: The main MCP server should be running continuously on port 8000
- **DO NOT** start new MCP servers for each Claude instance
- **USE**: Existing running server for all Claude instances and connections

### Claude CLI Command
- **CORRECT COMMAND**: `claude` (not `claude-code`)
- **INSTALLATION**: Install Claude CLI from [https://claude.ai/code](https://claude.ai/code)
- **VERIFICATION**: Run `which claude` to verify installation

### Claude Instance Coordination
- **Main Server**: Always run on port 8000 (main development server)
- **Proxy Server**: Port 8001 (for zero-downtime development)
- **New Instances**: Should connect to existing servers, not create new ones
- **Agent Names**: Each instance should register with unique agent name via MCP tools

### Correct Instance Launch Process
1. **Ensure main MCP server is running** (port 8000)
2. **Launch Claude CLI** with connection to existing server
3. **Register agent name** using `register_agent_with_name` tool
4. **Coordinate** through existing messaging system

## Debugging Tips

1. **Enable verbose logging** in MCP server for detailed debugging
2. **Use Chrome DevTools** for extension debugging
3. **Monitor service logs** in `logs/` directory
4. **Check MCP tool responses** for serialization issues
5. **Verify permissions** for Chrome Debug Protocol access

## Support & Resources

- **Documentation**: See `docs/` directory for detailed guides
- **Testing**: Use `tests/` directory for test examples
- **Examples**: Check `examples/` for implementation patterns
- **Migration**: See `MIGRATION_STATUS.md` for current architecture state