# Multi-Agent Messaging System Guide

## Overview

The MCP server now includes a comprehensive multi-agent messaging system that enables communication between different Cursor instances, MCP servers, and AI agents. This system provides structured messaging with features like sequential IDs, filtering, replies, and cross-repo file access.

## Architecture

### Directory Structure

```
messages/
├── agents/                    # Agent registration directory
│   ├── plasmo/               # Example agent (named after repo directory)
│   │   └── info.json         # Agent registration info
│   ├── plasmo-test/
│   │   └── info.json
│   └── yeshie/
│       └── info.json
├── messages/                  # Active messages
│   ├── 1.json
│   ├── 2.json
│   └── ...
├── deleted/                   # Soft-deleted messages
│   ├── 1.json
│   └── ...
└── sequence.txt              # Global message ID counter
```

### Message Format

```json
{
  "id": 42,
  "to": "target-agent-name",
  "from": "sender-agent-name", 
  "subject": "Message subject",
  "message": "Message content",
  "timestamp": "2025-01-14T10:30:00.000Z",
  "read": false,
  "reply_to": 35  // optional, references original message ID
}
```

### Agent Registration

Agents are automatically registered using the repository root directory name:
- `plasmo` → agent name "plasmo"
- `plasmo-test` → agent name "plasmo-test"  
- `my-project` → agent name "my-project"

Registration stores:
- Agent name
- Full filesystem path to repo
- GitHub remote URL (if available)
- Registration and last active timestamps

## Operations

### Core Operations

#### 1. Register Agent
```python
# Register current agent in messaging system
result = messages("register")
```

#### 2. Send Message
```python
# Send a new message
result = messages("send", {
    "to": "target-agent",
    "subject": "Collaboration Request",
    "message": "Let's work together on the React component!"
})
```

#### 3. Get Messages
```python
# Get all messages for current agent
result = messages("get")

# Get messages with filtering
result = messages("get", {
    "from": "plasmo",
    "unread_only": True,
    "subject_contains": "deployment"
})
```

#### 4. List Message Summaries
```python
# Get message summaries (lightweight view)
result = messages("list")

# With filtering
result = messages("list", {
    "after": "2025-01-01",
    "before": "2025-01-31"
})
```

#### 5. Reply to Message
```python
# Reply to a message
result = messages("reply", {
    "reply_to": 42,
    "message": "Thanks for the suggestion! I'll implement that approach."
})
```

#### 6. Delete Message
```python
# Delete your own message (moves to deleted/)
result = messages("delete", {
    "id": 42
})
```

#### 7. List Agents
```python
# See all registered agents
result = messages("agents")
```

#### 8. Read Agent Files
```python
# Read a file from another agent's repository
result = messages("read_file", {
    "agent": "plasmo-test",
    "file_path": "src/components/Button.tsx"
})
```

### Advanced Filtering

The `get` and `list` operations support powerful filtering:

```python
# Complex filtering example
result = messages("get", {
    "id": 42,                          # Specific message ID
    "from": "plasmo",                  # From specific agent
    "to": "yeshie",                    # To specific agent
    "subject_contains": "deployment",  # Subject contains text
    "unread_only": True,               # Only unread messages
    "after": "2025-01-01",            # After specific date
    "before": "2025-12-31"            # Before specific date
})
```

## Cursor Instance Collaboration Patterns

### 1. Automated Message Polling

Create a script that periodically checks for new messages:

```python
# cursor_collaboration_bot.py
import time
import json
from your_mcp_client import call_mcp_tool

def poll_for_messages():
    """Poll for new messages and handle them automatically."""
    while True:
        try:
            # Check for unread messages
            result = call_mcp_tool("messages", "get", {"unread_only": True})
            
            if result["success"] and result["messages"]:
                for message in result["messages"]:
                    handle_message(message)
            
            time.sleep(30)  # Poll every 30 seconds
            
        except Exception as e:
            print(f"Polling error: {e}")
            time.sleep(60)  # Wait longer on error

def handle_message(message):
    """Handle incoming messages automatically."""
    subject = message["subject"].lower()
    content = message["message"].lower()
    sender = message["from"]
    
    # Auto-respond to common requests
    if "code review" in subject:
        handle_code_review_request(message)
    elif "merge conflict" in content:
        handle_merge_conflict(message)
    elif "deployment" in subject:
        handle_deployment_request(message)
    else:
        # Log for manual review
        print(f"New message from {sender}: {message['subject']}")

def handle_code_review_request(message):
    """Automatically handle code review requests."""
    # Extract file path from message
    # Run automated code analysis
    # Reply with findings
    pass
```

### 2. Interactive Cursor Extension

Create a Cursor extension that integrates with the messaging system:

```typescript
// cursor-messaging-extension.ts
export class CursorMessagingExtension {
    private pollInterval: NodeJS.Timeout;
    
    constructor() {
        this.startPolling();
        this.setupCommands();
    }
    
    private startPolling() {
        this.pollInterval = setInterval(async () => {
            await this.checkForMessages();
        }, 30000); // 30 seconds
    }
    
    private async checkForMessages() {
        try {
            const result = await this.callMcpTool("messages", "get", {
                unread_only: true
            });
            
            if (result.success && result.messages.length > 0) {
                this.showNotification(
                    `${result.messages.length} new messages`,
                    result.messages[0].subject
                );
            }
        } catch (error) {
            console.error("Failed to check messages:", error);
        }
    }
    
    private setupCommands() {
        vscode.commands.registerCommand('cursor-messaging.send', async () => {
            const to = await vscode.window.showInputBox({
                prompt: "Send to agent:"
            });
            
            const subject = await vscode.window.showInputBox({
                prompt: "Subject:"
            });
            
            const message = await vscode.window.showInputBox({
                prompt: "Message:"
            });
            
            if (to && subject && message) {
                await this.sendMessage(to, subject, message);
            }
        });
        
        vscode.commands.registerCommand('cursor-messaging.inbox', async () => {
            await this.showInbox();
        });
    }
    
    private async showInbox() {
        const result = await this.callMcpTool("messages", "list");
        if (result.success) {
            // Show messages in a webview or quick pick
            const items = result.message_summaries.map(msg => ({
                label: msg.subject,
                description: `From: ${msg.from} - ${msg.timestamp}`,
                messageId: msg.id
            }));
            
            const selected = await vscode.window.showQuickPick(items);
            if (selected) {
                await this.showMessage(selected.messageId);
            }
        }
    }
}
```

### 3. Terminal-Based Collaboration

```bash
#!/bin/bash
# cursor_collab.sh - Terminal interface for messaging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_SERVER="http://localhost:8000"

send_message() {
    echo "=== Send Message ==="
    read -p "To: " to
    read -p "Subject: " subject
    echo "Message (end with Ctrl+D):"
    message=$(cat)
    
    curl -X POST "$MCP_SERVER/tools/messages" \
        -H "Content-Type: application/json" \
        -d "{
            \"operation\": \"send\",
            \"payload\": {
                \"to\": \"$to\",
                \"subject\": \"$subject\",
                \"message\": \"$message\"
            }
        }" | jq '.'
}

check_messages() {
    echo "=== Checking Messages ==="
    curl -X POST "$MCP_SERVER/tools/messages" \
        -H "Content-Type: application/json" \
        -d '{"operation": "list"}' | jq '.message_summaries[]'
}

read_message() {
    echo "=== Read Message ==="
    read -p "Message ID: " id
    curl -X POST "$MCP_SERVER/tools/messages" \
        -H "Content-Type: application/json" \
        -d "{
            \"operation\": \"get\",
            \"payload\": {\"id\": $id}
        }" | jq '.messages[0]'
}

case "$1" in
    send) send_message ;;
    check) check_messages ;;
    read) read_message ;;
    *) 
        echo "Usage: $0 {send|check|read}"
        echo "  send  - Send a new message"
        echo "  check - List message summaries"
        echo "  read  - Read a specific message"
        ;;
esac
```

### 4. AI-Driven Collaboration Workflows

```python
# ai_collaboration_workflows.py
class AICollaborationManager:
    def __init__(self):
        self.workflows = {
            "code_review": self.handle_code_review,
            "pair_programming": self.handle_pair_programming,
            "architecture_discussion": self.handle_architecture_discussion,
            "bug_investigation": self.handle_bug_investigation
        }
    
    def handle_code_review(self, message):
        """Handle code review collaboration requests."""
        # Extract file references from message
        # Analyze the code
        # Generate review comments
        # Send structured feedback
        
        code_analysis = self.analyze_referenced_code(message)
        review_comments = self.generate_review_comments(code_analysis)
        
        reply_message = f"""
Code Review Complete for: {message['subject']}

## Summary
{review_comments['summary']}

## Issues Found
{'\n'.join(review_comments['issues'])}

## Suggestions
{'\n'.join(review_comments['suggestions'])}

## Approval Status
{review_comments['approval_status']}
        """
        
        self.send_reply(message['id'], reply_message)
    
    def handle_pair_programming(self, message):
        """Handle pair programming session requests."""
        # Set up shared workspace
        # Coordinate file editing
        # Manage merge conflicts
        pass
    
    def handle_architecture_discussion(self, message):
        """Handle architecture discussion workflows."""
        # Analyze current architecture
        # Generate diagrams
        # Propose alternatives
        # Document decisions
        pass
    
    def handle_bug_investigation(self, message):
        """Handle collaborative bug investigation."""
        # Analyze error logs
        # Trace execution flow
        # Identify root cause
        # Propose fixes
        pass
```

## Collaboration Use Cases

### 1. Code Review Collaboration

```python
# Agent A requests code review
messages("send", {
    "to": "senior-dev-agent",
    "subject": "Code Review: Authentication Module",
    "message": """
Please review the authentication module I just completed.

Files to review:
- src/auth/AuthService.ts
- src/auth/AuthMiddleware.ts
- tests/auth.test.ts

Key areas of concern:
- Security implementation
- Error handling
- Test coverage

Deadline: Tomorrow morning
    """
})

# Agent B responds with automated review
messages("reply", {
    "reply_to": 123,
    "message": """
Code review completed. Overall looks good with a few suggestions:

SECURITY ISSUES:
- Line 45 in AuthService.ts: Use bcrypt.compare() instead of direct comparison
- Missing rate limiting on login attempts

IMPROVEMENTS:
- Add input validation for email format
- Consider adding refresh token rotation
- Add more edge case tests

APPROVAL: Approved with minor fixes required.
    """
})
```

### 2. Pair Programming Session

```python
# Initiate pair programming
messages("send", {
    "to": "frontend-specialist",
    "subject": "Pair Programming: React Component Refactor",
    "message": """
Want to pair on refactoring the UserProfile component?

Current issues:
- Too many props (15+)
- Mixed responsibilities
- No error boundaries

Proposed approach:
- Split into smaller components
- Use context for shared state
- Add proper error handling

Available now for next 2 hours.
    """
})
```

### 3. Architecture Discussion

```python
# Start architecture discussion
messages("send", {
    "to": "architecture-team",
    "subject": "Architecture Decision: Database Migration Strategy",
    "message": """
Need input on database migration strategy for v2.0.

OPTIONS:

1. Blue-Green Deployment
   - Pros: Zero downtime, easy rollback
   - Cons: 2x infrastructure cost, complex data sync

2. Rolling Migration
   - Pros: Cost-effective, gradual rollout
   - Cons: Extended migration period, compatibility complexity

3. Big Bang Migration
   - Pros: Quick transition, simpler
   - Cons: Downtime, high risk

Current preference: Blue-Green
Concerns: Cost implications

Please review and provide feedback by Friday.
    """
})
```

### 4. Cross-Repository Collaboration

```python
# Read files from other agent's repo
content = messages("read_file", {
    "agent": "shared-components",
    "file_path": "src/Button/Button.tsx"
})

# Send implementation request
messages("send", {
    "to": "ui-library-team",
    "subject": "Request: Add Loading State to Button Component",
    "message": f"""
Reviewed your Button component: {content['file_path']}

Enhancement request:
- Add isLoading prop
- Show spinner when loading
- Disable interaction when loading

Current implementation looks solid. Would you like me to:
1. Submit a PR with the changes?
2. Create a new variant?
3. Extend the existing component?

Let me know your preference!
    """
})
```

## Best Practices

### 1. Message Structure
- Use descriptive subjects
- Include context and background
- Specify deadlines or urgency
- Reference specific files/lines when relevant
- Provide clear action items

### 2. Collaboration Patterns
- Register agents early in setup
- Use consistent naming conventions
- Set up automated polling for responsive collaboration
- Archive completed discussions
- Use tags or prefixes in subjects for categorization

### 3. Security Considerations
- File access is limited to registered agent repositories
- Path traversal protection prevents unauthorized access
- Messages are only visible to intended recipients
- Deletion moves messages to deleted/ (soft delete)

### 4. Performance Optimization
- Use `list` operation for overviews (lightweight)
- Use `get` with filtering for specific queries
- Set up efficient polling intervals
- Clean up old messages periodically

## Integration with Existing Systems

### MCP Server Integration
The messaging system is fully integrated with the existing MCP server and shares the same security model, logging, and error handling patterns.

### Cursor IDE Integration
- Works with existing MCP tools
- Compatible with Cursor's tool calling system
- Can be extended with custom commands
- Supports real-time collaboration workflows

### Git Integration
- Automatically detects GitHub remote URLs
- Can coordinate around branches and PRs
- Supports cross-repository collaboration
- Integrates with existing git workflows

## Troubleshooting

### Common Issues

1. **Agent not found**
   - Ensure target agent is registered: `messages("agents")`
   - Check agent name matches repo directory name

2. **Messages not appearing**
   - Verify agent registration: `messages("register")`
   - Check message directory permissions
   - Confirm MCP server is running

3. **File access denied**
   - Ensure agent is registered with correct repo path
   - Check file exists and is readable
   - Verify path doesn't traverse outside repo

### Debugging Commands

```python
# Check system status
messages("agents")  # List all agents
messages("list")    # Check message count
server_info()       # Verify MCP server status

# Test messaging
messages("send", {
    "to": "self",  # Send to yourself for testing
    "subject": "Test Message",
    "message": "Testing the messaging system"
})
```

This comprehensive messaging system enables sophisticated multi-agent collaboration while maintaining security and performance. It can be extended with additional operations, notification systems, and integration points as needed. 