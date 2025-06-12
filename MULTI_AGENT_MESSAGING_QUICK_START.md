# Multi-Agent Messaging System - Quick Start Guide

## 🚀 Overview

This guide gets you up and running with the multi-agent messaging system for Cursor collaboration in minutes.

## 📋 Prerequisites

1. **MCP Server Running**: Ensure your MCP server is running on `http://localhost:8000`
2. **Dependencies**: Install required dependencies
   ```bash
   pip install requests  # For Python scripts
   brew install jq       # For bash scripts (macOS)
   # or: apt-get install jq  # (Ubuntu/Debian)
   ```

## 🛠️ Quick Setup

### 1. Start Your MCP Server
```bash
# If not already running
python mcp_server.py
```

### 2. Test the System
```bash
# Run comprehensive tests
python test_messaging_system.py --verbose

# Quick status check
./cursor_collab.sh status
```

### 3. Register Your Agent
```bash
# Register current Cursor instance
./cursor_collab.sh register
```

## 🎯 Basic Usage

### Using the Interactive Terminal Interface

```bash
# Start interactive mode
./cursor_collab.sh

# Or use specific commands
./cursor_collab.sh send     # Send a message
./cursor_collab.sh check    # Check messages
./cursor_collab.sh agents   # List agents
```

### Using the Python Assistant

```bash
# Send a message interactively
python cursor_collaboration_assistant.py send

# Check inbox
python cursor_collaboration_assistant.py inbox

# Start polling for messages
python cursor_collaboration_assistant.py poll

# List all agents
python cursor_collaboration_assistant.py agents
```

## 📬 Collaboration Workflows

### Scenario 1: Code Review Request

**Agent A (requesting review):**
```bash
./cursor_collab.sh send
# To: senior-dev
# Subject: Code Review: User Authentication
# Message: 
# Please review my authentication implementation:
# - src/auth/login.ts
# - src/auth/middleware.ts
# 
# Focus areas:
# - Security best practices
# - Error handling
# - Performance implications
```

**Agent B (reviewer):**
```bash
./cursor_collab.sh check    # See new messages
./cursor_collab.sh read     # Read message ID
./cursor_collab.sh reply    # Send review feedback
```

### Scenario 2: Pair Programming Session

**Initiating agent:**
```bash
python cursor_collaboration_assistant.py send
# To: frontend-expert
# Subject: Pair Programming: React Component Refactor
# Message: Available for 2 hours to refactor UserProfile component.
# Current issues: too many props, mixed concerns.
# Proposed: split into sub-components, add error boundaries.
```

### Scenario 3: Architecture Discussion

**Using the assistant with auto-polling:**
```bash
# Terminal 1 (Agent A)
python cursor_collaboration_assistant.py poll

# Terminal 2 (Agent B) 
python cursor_collaboration_assistant.py send
# Discuss database migration strategies...
```

## 🔧 Advanced Features

### 1. Message Filtering

```python
# From Python scripts or Cursor
messages("get", {
    "from": "specific-agent",
    "subject_contains": "urgent",
    "unread_only": True,
    "after": "2025-01-01"
})
```

### 2. Cross-Repository File Access

```python
# Read files from other agents' repos
content = messages("read_file", {
    "agent": "shared-components",
    "file_path": "src/Button/Button.tsx"
})
```

### 3. Automated Responses

The Python assistant includes auto-responses for:
- **Urgent messages**: Auto-acknowledges and prioritizes
- **Status checks**: Responds with system status
- **Ping messages**: Confirms availability

## 🎨 Cursor IDE Integration

### Method 1: Cursor Command Integration

Add to your Cursor settings:
```json
{
  "mcp.servers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["mcp_server.py", "--stdio"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Method 2: Background Polling

Run in a separate terminal while working in Cursor:
```bash
# Auto-poll for messages every 30 seconds
python cursor_collaboration_assistant.py poll
```

### Method 3: Direct Tool Calls

Use the `messages` tool directly in Cursor:
```python
# Register agent
messages("register")

# Send message
messages("send", {
    "to": "target-agent",
    "subject": "Collaboration Request",
    "message": "Let's work together on this feature!"
})

# Check messages
messages("get", {"unread_only": True})
```

## 📁 Directory Structure Created

When you first use the system, it creates:
```
messages/
├── agents/
│   └── plasmo/              # Your agent (named after repo)
│       └── info.json        # Registration info
├── messages/
│   ├── 1.json              # Message files
│   └── 2.json
├── deleted/                 # Soft-deleted messages
└── sequence.txt            # Message ID counter
```

## 🐛 Troubleshooting

### Common Issues

1. **"Agent not found" error**
   ```bash
   # Ensure target agent is registered
   ./cursor_collab.sh agents
   ```

2. **"Connection failed" error**
   ```bash
   # Check MCP server is running
   curl http://localhost:8000/mcp/tools/server_info
   ```

3. **Permission denied on files**
   ```bash
   # Check script permissions
   chmod +x cursor_collab.sh cursor_collaboration_assistant.py
   ```

### Debug Commands

```bash
# System status check
./cursor_collab.sh status

# Test all functionality
python test_messaging_system.py --verbose

# Check MCP server logs
tail -f mcp_server.log
```

## 🎯 Real-World Examples

### Example 1: Bug Investigation

```bash
# Agent discovers bug
./cursor_collab.sh send
# To: backend-team
# Subject: URGENT: Payment API Timeout
# Message: Seeing 30s timeouts on /api/payments
# Error logs attached. Need immediate investigation.
# Affecting production since 2PM EST.
```

### Example 2: Feature Coordination

```bash
# Product owner coordinates feature work
python cursor_collaboration_assistant.py send
# To: frontend-dev
# Subject: Feature Handoff: User Dashboard
# Message: API endpoints ready for dashboard feature.
# Documentation: /docs/dashboard-api.md
# Timeline: Ready for integration testing by Friday.
```

### Example 3: Knowledge Sharing

```bash
# Share solution with team
messages("send", {
    "to": "team-lead",
    "subject": "Solution: Docker Build Performance",
    "message": """
Found solution for slow Docker builds:

1. Added .dockerignore for node_modules
2. Multi-stage build with dependencies cache
3. Build time reduced from 5min to 45s

Changes in: docker/Dockerfile, .dockerignore
Want me to document this for the team?
    """
})
```

## 🔄 Next Steps

1. **Set up automated polling** in each Cursor instance
2. **Establish team conventions** for message subjects
3. **Create response templates** for common scenarios
4. **Integrate with existing workflows** (CI/CD, code review)
5. **Extend with custom automation** as needed

## 📚 Additional Resources

- **Full Documentation**: `MULTI_AGENT_MESSAGING_GUIDE.md`
- **Test Suite**: `test_messaging_system.py`
- **Interactive Terminal**: `cursor_collab.sh`
- **Python Assistant**: `cursor_collaboration_assistant.py`

Start collaborating immediately with:
```bash
./cursor_collab.sh
```

Happy collaborating! 🎉 