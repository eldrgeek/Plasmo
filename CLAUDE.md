# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Plasmo browser extension monorepo with MCP server for Chrome Debug Protocol automation and multi-agent AI coordination.

**Stack**: Plasmo, TypeScript/React, FastMCP Python, Chrome Debug Protocol, Socket.IO, Firebase, PNPM workspaces

## 🤖 Multi-Agent Framework

This project includes a sophisticated multi-agent AI framework for coordinating AI agents in software development tasks.

**Key Documentation**:
- `AGENT_FRAMEWORK_OVERVIEW.md` - Comprehensive framework architecture and implementation guide
- `AGENTS.md` - Chrome Debug Protocol integration and browser automation  
- `docs/guides/MULTI_AGENT_MESSAGING_GUIDE.md` - Inter-agent communication system
- `agents/README.md` - Agent templates and spawning system
- `packages/mcp-server/agents/README.md` - Core agent management modules

**Production-Ready Capabilities**:
- Inter-agent messaging with threading and filtering
- Chrome Debug Protocol automation for testing
- Cross-repository collaboration
- Template-based agent specialization
- Real-time notification system

## Critical Rules

1. **MCP Server**: Always use existing server on port 8000 - DO NOT start new servers
2. **Chrome Debug Protocol**: Use INTEGER request IDs only (`int(time.time() * 1000000) % 1000000`)
3. **JSON Serialization**: Always use `make_json_safe()` for Chrome Debug responses

## 🔓 Non-Destructive Tool Permissions

All non-destructive operations are pre-approved and can run without permission:

### File Operations (Read-Only)
- `Read`, `Glob`, `Grep` (all search/read operations)
- `Bash(ls:*)`, `Bash(cat:*)`, `Bash(head:*)`, `Bash(tail:*)`, `Bash(less:*)`, `Bash(more:*)`
- `Bash(find:*)`, `Bash(grep:*)`, `Bash(awk:*)`, `Bash(sed:*)` (when not modifying files)
- `Bash(wc:*)`, `Bash(sort:*)`, `Bash(uniq:*)`, `Bash(file:*)`

### System Information
- `Bash(ps:*)`, `Bash(top:*)`, `Bash(df:*)`, `Bash(du:*)`, `Bash(free:*)`
- `Bash(uname:*)`, `Bash(whoami:*)`, `Bash(pwd:*)`, `Bash(which:*)`
- `Bash(date:*)`, `Bash(cal:*)`, `Bash(uptime:*)`

### Development Tools (Read-Only)
- `Bash(git status:*)`, `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git show:*)`
- `Bash(git branch:*)`, `Bash(git remote:*)` (listing only)
- `Bash(npm ls:*)`, `Bash(pnpm ls:*)`, `Bash(yarn list:*)`
- `Bash(python --version:*)`, `Bash(node --version:*)`, `Bash(pnpm --version:*)`

### Network Diagnostics (Non-Intrusive)
- `Bash(curl:*)` (GET requests to known domains)
- `Bash(wget:*)` (for downloading to temp locations)
- `Bash(ping:*)` (basic connectivity tests)

### Testing & Quality (Non-Modifying)
- `Bash(npm test:*)`, `Bash(pnpm test:*)`, `Bash(pytest:*)` (when tests don't modify source)
- `Bash(eslint:*)`, `Bash(tsc:*)` (linting/type checking without --fix)
- `Bash(black --check:*)` (formatting check without modification)

### Environment & Process Management
- `Bash(export:*)`, `Bash(source:*)` (environment setup)
- `Bash(kill:*)`, `Bash(pkill:*)` (process management for dev servers)
- `Bash(jobs:*)`, `Bash(nohup:*)` (process monitoring)

### Archive Operations (Read-Only)
- `Bash(tar -t:*)`, `Bash(unzip -l:*)` (listing archive contents)

### MCP & Desktop Tools
- All `mcp__*` tools (screenshot, browser automation, etc.)
- All desktop tools for navigation and monitoring
- `WebFetch`, `WebSearch` for research

### Claude Code Integration
- `TodoWrite` for task management
- All task planning and coordination tools

## MCP Server Configuration

### Add to Claude Code

```bash
# Primary method (recommended)
claude mcp add-json "stdioserver-cursor" '{
  "command": "python",
  "args": ["/Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_server.py", "--stdio"],
  "cwd": "/Users/MikeWolf/Projects/Plasmo",
  "description": "Plasmo Stdio Development Assistant"
}'

# Alternative: Direct command
claude mcp add stdioserver-cursor "python /Users/MikeWolf/Projects/Plasmo/packages/mcp-server/mcp_server.py --stdio"

# Verify connection
claude mcp list
```

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
pnpm start-collaboraition        # Collaboration tools

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
├── collaboraition/      # Multi-agent coordination
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

## 🧠 GTD Task Management System

This project uses Getting Things Done (GTD) methodology for organizing tasks and priorities. The system is designed for ADD-friendly workflows with convergent execution focus.

**Key GTD Files:**
- `gtd/master_system.md` - Complete GTD system overview
- `gtd/daily_capture_template.md` - Brain dump template  
- `gtd/weekly_review_template.md` - Weekly review process

**GTD Principles Applied:**
- Inbox processing (2-minute rule)
- Context-based next actions (@Computer, @Mac, @Energy_High, @Energy_Low)
- Project outcome focus with clear next actions
- Weekly reviews for system maintenance
- Convergent vs divergent thinking balance

**PersonalSidekick Integration:**
The GTD system integrates with the PersonalSidekick agent (`agents/mw_personal_assistant_agent.md`) for automated accountability and notification support.

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