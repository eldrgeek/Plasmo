# External Configuration and Influences

This document captures all external configurations, rules, and influences that affect the Plasmo Chrome Extension with MCP Server repository but are not actually stored within the repository itself.

## Table of Contents

1. [Cursor Rules System](#cursor-rules-system)
2. [External Configuration Files](#external-configuration-files)
3. [Claude Desktop Configuration](#claude-desktop-configuration)
4. [Development Environment Dependencies](#development-environment-dependencies)
5. [Chrome Debug Configuration](#chrome-debug-configuration)
6. [System Requirements](#system-requirements)
7. [External Services & APIs](#external-services--apis)
8. [Security Considerations](#security-considerations)

---

## Cursor Rules System

The project uses an extensive Cursor rules system stored in `.cursor/rules/` directory that influences all AI-assisted development:

### Main Rules Files

#### `.cursorrules` (Root Configuration)
```
# Cursor Rules for Plasmo Extension Development with MCP Server

## Project Context
This is a Plasmo browser extension project with an integrated MCP (Model Context Protocol) server for Chrome Debug Protocol integration. The MCP server enables real-time debugging and monitoring of the extension through AI assistance.

## Key Technologies
- **Plasmo**: Browser extension framework
- **TypeScript/React**: Extension UI and logic
- **Python FastMCP**: MCP server for Chrome debugging
- **Chrome Debug Protocol**: Browser automation and debugging
- **WebSocket**: Real-time communication with browser

## Development Guidelines

### MCP Server Development
- Always ensure return values from MCP tools are JSON-serializable (no complex objects)
- Use `make_json_safe()` helper for converting objects to basic types
- Handle Chrome Debug Protocol WebSocket connections carefully
- **CRITICAL: Chrome Debug Protocol requires INTEGER request IDs, not strings**
- Use `int(time.time() * 1000000) % 1000000` for Chrome Debug Protocol request IDs
- Test Chrome flag compatibility when adding new debugging features
- Remember that extension service worker IDs change on Chrome restart

### Chrome Debugging Setup
- Use `./launch-chrome-debug.sh` script for proper Chrome configuration
- Required flags: `--remote-debugging-port=9222 --remote-allow-origins=*`
- Extension debugging requires special WebSocket origin permissions
- Monitor console logs through MCP server tools, not direct WebSocket connections

### Code Organization
- Keep MCP server tools focused and single-purpose
- Document Chrome Debug Protocol interactions thoroughly
- Maintain separation between extension code and debugging infrastructure
- Use proper error handling for WebSocket connections

### File Management
- Never commit `__pycache__/`, `mcp_server.log`, or Chrome profile contents
- Keep `chrome-debug-profile/` directory structure but ignore contents
- Document any new MCP tools in relevant README files

### Extension Development
- Test extension functionality both standalone and through MCP debugging
- Verify auto-reload functionality works with file changes
- Use MCP server console monitoring for debugging extension logic
- Maintain compatibility between extension and debugging infrastructure

### Best Practices
- Test MCP server tools thoroughly before committing
- Handle serialization edge cases proactively
- Document Chrome version compatibility for debugging features
- Keep debugging tools separate from production extension code
- Use parallel tool calls when gathering multiple pieces of information

## Common Issues & Solutions
- **Serialization errors**: Convert objects to dict/list/string before returning
- **WebSocket 403 errors**: Ensure `--remote-allow-origins=*` flag is set
- **Chrome Debug Protocol "integer id" error**: Use integer request IDs, not strings
- **Extension not found**: Check service worker is running and ID is current
- **MCP tools not available**: Restart Cursor after server changes
```

#### Core Architecture Rules (`.cursor/rules/core-architecture.mdc`)
- Plasmo framework conventions for file organization
- Manifest V3 standards and APIs
- React 18 patterns with TypeScript
- Chrome extension message passing patterns
- File naming conventions for extension components

#### AI Assistant Instructions (`.cursor/rules/ai-assistant-instructions.mdc`)
- MCP tool usage strategies
- Code analysis workflows
- Development assistance patterns
- Debug session management
- Response generation guidelines

### Additional Rules Files
**Complete text available in `COMPLETE_CURSOR_RULES.md`**

- `chrome-debug-integration.mdc` (23KB, 814 lines) - Chrome Debug Protocol integration patterns, automated debugging workflows, WebSocket message filtering, DevTools interference prevention
- `ai-assisted-development.mdc` (12KB, 369 lines) - AI-enhanced development workflows, MCP server knowledge injection, context-aware problem solving
- `mcp-server-standards.mdc` (12KB, 330 lines) - MCP server development patterns, v2.0 consolidated architecture, enhanced error handling
- `retrospectives-improvement.mdc` (5.7KB, 201 lines) - Continuous improvement processes, sprint retrospectives, post-mortem procedures
- `specification-standards.mdc` (4.4KB, 203 lines) - Documentation and API standards, OpenAPI specifications, JSDoc standards
- `planning-methodology.mdc` (3.3KB, 112 lines) - Project planning and agile practices, user story standards, Chrome extension planning
- `testing-strategy.mdc` (3.1KB, 122 lines) - Testing approach and implementation, Jest configuration, Chrome API mocking
- `typescript-react-standards.mdc` (2.2KB, 88 lines) - Code quality and React patterns, TypeScript configuration, performance optimization

**Note**: All complete rule file contents are documented in the companion file `COMPLETE_CURSOR_RULES.md` which contains the full text of every `.mdc` file in the `.cursor/rules/` directory.

---

## External Configuration Files

### Claude Desktop Configuration

**Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["/Users/MikeWolf/Projects/Plasmo/mcp_server.py", "--stdio"],
      "env": {
        "PYTHONPATH": "/Users/MikeWolf/Projects/Plasmo"
      }
    }
  }
}
```

**Impact**: This configuration enables Claude Desktop to connect to the project's MCP server, providing AI assistance with direct access to the project's debugging and automation tools.

### Local Claude Desktop Config (Project Copy)
**File**: `claude_desktop_config.json`
**Purpose**: Local copy for reference and backup of the Claude Desktop configuration.

---

## Development Environment Dependencies

### Node.js Dependencies (`package.json`)
```json
{
  "name": "my-plasmo-extension",
  "displayName": "My Plasmo Extension",
  "version": "0.0.1",
  "description": "A basic Chrome extension built with Plasmo",
  "author": "Your Name",
  "scripts": {
    "dev": "plasmo dev",
    "build": "plasmo build",
    "package": "plasmo package"
  },
  "dependencies": {
    "express": "^5.1.0",
    "plasmo": "0.90.5",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "socket.io": "^4.8.1",
    "socket.io-client": "^4.7.2"
  },
  "devDependencies": {
    "@types/chrome": "0.0.246",
    "@types/node": "20.5.9",
    "@types/react": "18.2.21",
    "@types/react-dom": "18.2.7",
    "nodemon": "^3.1.10",
    "prettier": "^3.0.0",
    "typescript": "5.2.2"
  },
  "manifest": {
    "permissions": [
      "activeTab",
      "storage",
      "nativeMessaging"
    ]
  }
}
```

### Python Dependencies (`requirements.txt`)
```
fastmcp>=2.6.1
websockets>=11.0.3
aiohttp>=3.8.5
pychrome>=0.2.3
requests>=2.28.0
```

---

## Chrome Debug Configuration

### Required Chrome Launch Flags
The project requires Chrome to be launched with specific debugging flags:

```bash
--remote-debugging-port=9222
--remote-allow-origins=*
--no-first-run
--no-default-browser-check
--disable-features=VizDisplayCompositor
--user-data-dir=./chrome-debug-profile
```

### Chrome Debug Profile
**Location**: `./chrome-debug-profile/`
**Purpose**: Isolated Chrome profile for debugging
**Note**: Contents are gitignored but directory structure is maintained

### Debug Protocol Access
- **Port**: 9222
- **Host**: localhost
- **Endpoint**: `http://localhost:9222/json`
- **WebSocket**: `ws://localhost:9222/devtools/page/{tabId}`

---

## System Requirements

### Operating System Support
- **Primary**: macOS (Darwin 24.5.0+)
- **Secondary**: Linux (with compatibility scripts)
- **Shell**: Zsh (/bin/zsh)

### Required Software
- **Node.js**: 18+ with pnpm package manager
- **Python**: 3.8+ with virtual environment support
- **Chrome/Chromium**: Latest version with debug protocol support
- **Claude Desktop**: Latest version for MCP integration

### Development Tools
- **Cursor IDE**: With MCP server integration
- **Git**: Version control
- **TypeScript**: 5.2.2+
- **React**: 18.2.0

---

## External Services & APIs

### Chrome Debug Protocol
- **Type**: Local WebSocket API
- **Purpose**: Browser automation and debugging
- **Endpoints**: Tab control, JavaScript execution, console monitoring
- **Authentication**: None (local only)

### Plasmo Framework
- **Type**: Build framework
- **Purpose**: Chrome extension development
- **Configuration**: Automatic with sensible defaults
- **Hot Reload**: Enabled in development mode

### Socket.IO Server
- **Port**: 3001
- **Purpose**: Multi-LLM orchestration
- **Real-time Communication**: Between extension and external AI services

---

## Security Considerations

### Local Network Access
- Chrome debug protocol exposes localhost:9222
- MCP server runs with local Python environment access
- Socket.IO server allows local connections only

### Data Privacy
- Chrome profile data isolated in debug profile
- No external API keys stored in repository
- MCP server logs may contain sensitive debugging data

### Access Controls
- Chrome debug requires explicit flag enablement
- MCP server requires Claude Desktop configuration
- Extension requires manual installation and permissions

---

## Environment Variables & Runtime Configuration

### MCP Server Environment
```bash
PYTHONPATH="/Users/MikeWolf/Projects/Plasmo"
```

### Service Management
- **MCP Server**: Auto-restart on file changes
- **Socket.IO Server**: Auto-reload with nodemon
- **Plasmo Dev Server**: Hot reload on TypeScript/React changes
- **Chrome**: Manual restart required for extension updates

### Log Files (Gitignored)
- `mcp_server.log` - MCP server operations and debugging
- `socketio.log` - Socket.IO server communications
- `.service_pids` - Running service process IDs

---

## Build & Deployment Configuration

### TypeScript Configuration (`tsconfig.json`)
```json
{
  "extends": "plasmo/templates/tsconfig.base",
  "exclude": [
    "node_modules"
  ],
  "include": [
    ".plasmo/index.d.ts",
    "./**/*.ts",
    "./**/*.tsx"
  ],
  "compilerOptions": {
    "paths": {
      "~*": [
        "./*"
      ]
    },
    "baseUrl": "."
  }
}
```

### Git Configuration (`.gitignore`)
```
# Dependencies
node_modules/
__pycache__/

# Build outputs
.plasmo/
build/

# Logs
*.log
socketio.log

# Chrome profile (keep structure, ignore contents)
chrome-debug-profile/*
!chrome-debug-profile/.gitkeep

# Service management
.service_pids

# Environment files
.env*
```

---

## Integration Points

### Cursor IDE Integration
- Rules engine influences all AI assistance
- MCP server provides real-time debugging capabilities
- Automated code analysis and suggestions

### Claude Desktop Integration
- MCP server connection for enhanced AI capabilities
- Direct access to project debugging tools
- Real-time assistance with development tasks

### Chrome Extension Ecosystem
- Manifest V3 compliance
- Chrome Web Store compatibility
- Developer dashboard integration potential

---

## Maintenance & Updates

### Rule System Updates
- Rules should be updated based on project evolution
- New patterns discovered should be documented in appropriate rule files
- AI assistant learns from successful patterns and updates recommendations

### Dependency Management
- Regular updates to Plasmo framework
- Chrome API compatibility monitoring
- Python MCP library updates
- React/TypeScript version management

### Configuration Drift Prevention
- External configurations should be documented here
- Claude Desktop config should be backed up in repository
- Launch scripts should be version controlled

---

## Troubleshooting External Issues

### Claude Desktop MCP Connection
```bash
# Check MCP server is running
ps aux | grep mcp_server.py

# Restart Claude Desktop
killall Claude && open -a Claude

# Verify configuration
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Chrome Debug Protocol Issues
```bash
# Check Chrome is running with debug flags
ps aux | grep chrome | grep remote-debugging-port

# Verify debug endpoint
curl http://localhost:9222/json

# Restart Chrome with proper flags
./launch-chrome-debug.sh
```

### Service Management
```bash
# Check all services
./check_services.sh

# Restart all services
./start_all_services.sh

# Stop all services
./stop_all_services.sh
```

---

This document should be updated whenever external configurations change or new external dependencies are introduced to the project. 