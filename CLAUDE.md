# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Plasmo browser extension monorepo with MCP server for Chrome Debug Protocol automation and multi-agent AI coordination.

**Stack**: Plasmo, TypeScript/React, FastMCP Python, Chrome Debug Protocol, Socket.IO, Firebase, PNPM workspaces

## Critical Rules

1. **MCP Server**: Always use existing server on port 8000 - DO NOT start new servers
2. **Chrome Debug Protocol**: Use INTEGER request IDs only (`int(time.time() * 1000000) % 1000000`)
3. **JSON Serialization**: Always use `make_json_safe()` for Chrome Debug responses

## Quick Commands

```bash
# Development
pnpm install && pnpm dev        # Setup and run extension
python launch_all.py             # Start all services
./chrome_debug_launcher.py      # Launch Chrome with debug flags

# Individual Services
pnpm start-mcp                   # MCP server only
pnpm start-socketio              # Socket.IO server
pnpm start-dashboard             # Dashboard
<!-- [REVIEW] Typo: should be "collaboration" not "collaboraition" -->
pnpm start-collaborAItion        # Collaboration tools

# Testing & Quality
./run_enhanced_tests.sh          # Run tests
black .                          # Format Python
```

## Architecture

```
packages/
├── chrome-extension/     # Main Plasmo extension
├── mcp-server/          # 30+ tools for automation
├── socketio-server/     # Real-time communication  
├── dashboard-framework/ # Monitoring
├── firebase-chat/       # Chat backend
├── collaborAItion/      # Multi-agent coordination
└── testing-framework/   # Test utilities
```

## Development Guidelines

### Chrome Extension
- Manifest V3 only
- Chrome storage APIs (never localStorage)
- React 18 hooks patterns
- TypeScript strict mode

### MCP Server  
- JSON-serializable returns only
- Integer request IDs for Chrome Debug
- Test with `make_json_safe()`

### Common Issues
- **403 WebSocket**: Add `--remote-allow-origins=*` flag
- **Integer ID errors**: Use integers, not strings
- **MCP tools unavailable**: Restart after server changes




## Environment Requirements
- Node.js >= 18.0.0
- PNPM >= 8.0.0  
- Python >= 3.8
- Chrome/Chromium

## 📦 Stashed Experiments

**Dec 2024 LLM Collaboration** (`stash@{0}`)
- Attempted LLM-to-LLM automation (broken async, mock implementations)
- Recovery: `git stash apply stash@{0}`
- Core insight: Direct MCP Playwright tools work better than wrappers

---

<!-- [QUESTIONS FOR USER]:
1. Should we fix the "collaboraition" typo throughout the codebase?
2. The duplicate Claude instance management sections (lines 5-11 and 215-237) could be merged
3. The Firebase section seems disconnected - is it actively used?
4. The agent coordination protocol references a messaging system that isn't clearly defined
5. Should the stash documentation be temporary (remove after 30 days)?
6. Many testing scripts mentioned - are they all still valid/working?
-->