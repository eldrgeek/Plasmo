# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Plasmo browser extension monorepo with MCP (Model Context Protocol) server for Chrome Debug Protocol automation, multi-agent AI coordination, and real-time communication services.

**Stack**: Plasmo, TypeScript/React, FastMCP Python, Chrome Debug Protocol, Socket.IO, Firebase, PNPM workspaces
**Package/workspace manager**: pnpm workspaces. Some packages are pure Python.

## Architecture

```
packages/
├── chrome-extension/     # Main Plasmo extension (TypeScript/React)
├── mcp-server/          # 30+ tools for browser automation (Python)
├── socketio-server/     # Real-time communication (Node.js/Python)
├── dashboard-framework/ # Monitoring dashboard (Python)
├── firebase-chat/       # Chat backend with Discord UI (Firebase/React)
├── collaboraition/      # Multi-agent coordination (Python) [note: typo in package name]
└── testing-framework/   # Test utilities (TypeScript)
```

## Quick Commands

### Development Setup
```bash
# Install dependencies for all packages
pnpm install

# Start Chrome extension development
pnpm dev

# Build extension for production
pnpm build && pnpm package

# Start all services
python launch_all.py
```

### Individual Services
```bash
# MCP server (critical for automation)
pnpm start-mcp
# or directly: cd packages/mcp-server && ./start_mcp.sh

# Socket.IO communication server
pnpm start-socketio

# Monitoring dashboard
pnpm start-dashboard

# Start collaboration tools
pnpm start-collaborAItion  # [note: package name contains a typo in repo]
```

### Development with Chrome Debug Protocol
```bash
# Launch Chrome with debugging flags (macOS/Linux)
./chrome_debug_launcher.py

# Test enhanced functionality
./run_enhanced_tests.sh

# Auto-reload setup for extension development
# (Uses Chrome extension auto-reload on file changes)
```

## Environment Requirements

- **Node**: >= 18.0.0
- **PNPM**: >= 8.0.0  
- **Python**: >= 3.8
- **Chrome/Chromium**: Required for extension testing

## Critical Development Notes

### MCP Server (packages/mcp-server/)
- **Always use existing server on port 8000** - do not start new servers
- **JSON serialization**: Use `make_json_safe()` for Chrome Debug responses
- **Chrome Debug Protocol**: Use INTEGER request IDs only (`int(time.time() * 1000000) % 1000000`)
- Chrome debugging requires `--remote-debugging-port=9222 --remote-allow-origins=*`
- There are duplicate mcp_server.py files; always use `packages/mcp-server/mcp_server.py`

### Chrome Extension Development (packages/chrome-extension/)
- **Manifest V3 only** - no V2 compatibility
- **Chrome storage APIs** - never use localStorage in extension contexts
- **React 18 patterns** with hooks and concurrent features
- **TypeScript strict mode** required
- Extension service worker IDs change on Chrome restart

### Multi-Agent System (agents/)
- **Agent templates** in `agents/agent_templates/` for spawning specialized AI agents
- **Inter-agent messaging** through MCP messaging system
- **Founder Agent** acts as project coordinator
- **Recruiter Agent** spawns specialist agents based on needs
- Agent system located at `/Users/MikeWolf/Projects/Plasmo/agents/` but can work on peer projects

### Common Issues & Solutions

**403 WebSocket errors**: Add `--remote-allow-origins=*` to Chrome flags
**Extension not found**: Check service worker is running and ID is current
**MCP tools unavailable**: Restart Cursor/WARP after server changes
**Integer ID errors**: Chrome Debug Protocol requires integers, not strings
**Package typo**: The "collaboraition" package name contains a typo in the repo

## File Structure Guidance

### Configuration Files
- `pnpm-workspace.yaml`: Workspace configuration
- `pyproject.toml`: Python package configuration
- `setup.py`: Cross-platform setup script with auto Python installation

### Key Directories
- `docs/`: Comprehensive documentation organized by topic
- `agents/`: Multi-agent AI system with specialized agent templates
- `capture_ui/`: Tauri-based instant task capture application
- `.cursor/rules/`: Cursor IDE-specific development rules and patterns

### Testing
- Jest configuration in `packages/firebase-chat/firebase-discord-chat/tests/jest.config.js`
- Enhanced testing with `run_enhanced_tests.sh`
- Chrome extension testing through MCP server tools

## Integration Points

### MCP Server Tools (30+ available)
- Secure file operations with path validation
- Chrome Debug Protocol automation
- Real-time console monitoring  
- JavaScript execution with async correlation
- Git integration (read-only commands)
- System information gathering

### Firebase Integration
- Discord-style chat application
- Real-time messaging and notifications
- Firebase console automation with Playwright
- Authentication providers setup

### Socket.IO Communication
- Real-time messaging between services
- Cross-agent communication protocol
- WebSocket fallback support

## Development Workflow

1. **Start MCP server first**: `pnpm start-mcp` (runs on port 8000)
2. **Launch Chrome with debug flags**: `./chrome_debug_launcher.py`
3. **Start extension development**: `pnpm dev`
4. **Use MCP tools** for browser automation and debugging
5. **Multi-agent coordination** through agent spawning system

## Security & Performance

- **Path validation** on all file operations
- **JSON serialization** safety for complex objects  
- **WebSocket connection management** with automatic cleanup
- **Thread safety** for concurrent operations
- **Resource monitoring** and cleanup procedures