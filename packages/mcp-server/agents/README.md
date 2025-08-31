# Agent Management Modules

This directory contains modular components for managing AI agents in the MCP server system. The modules provide a clean, organized approach to agent management, inter-agent communication, and coordination.

## Module Structure

### 1. `agent_management.py`
Core agent management functionality:
- **Agent Registration**: Register agents with the system
- **Custom Naming**: Set custom names for agents (overrides directory-based naming)
- **Agent Discovery**: List and find registered agents
- **Activity Tracking**: Monitor agent activity and status
- **Statistics**: Get agent management statistics

#### Key Functions:
```python
get_agent_name() -> str                    # Get current agent name
register_agent() -> Dict[str, Any]         # Register current agent
set_custom_agent_name(name: str)           # Set custom agent name
get_agent_registration(agent_name: str)    # Get agent info
list_registered_agents() -> List[Dict]     # List all agents
```

### 2. `messaging.py`
Inter-agent messaging system:
- **Message Creation**: Send messages between agents
- **Message Retrieval**: Get messages with filtering
- **Message Threading**: Reply support and conversation tracking
- **Message Management**: Mark as read, delete, search
- **Persistent Storage**: File-based message storage

#### Key Functions:
```python
create_message(to, subject, message, reply_to=None) -> Dict  # Create message
get_messages(agent_name, filters=None) -> List[Dict]         # Get messages
mark_message_read(message_id, agent_name) -> bool            # Mark as read
delete_message(message_id, agent_name) -> bool               # Delete message
search_messages(agent_name, query, fields=None) -> List     # Search messages
```

### 3. `notifications.py`
Real-time notification system:
- **Event-Driven Notifications**: Immediate notification delivery
- **Notification Queuing**: Persistent notification storage
- **Wait/Notify Patterns**: Coordinated agent communication
- **Cancel Flags**: Interrupt waiting agents
- **Async Support**: Event loop integration

#### Key Functions:
```python
send_notification(target_agent, message, sender=None) -> Dict  # Send notification
get_pending_notifications(agent_name) -> List[Dict]            # Get pending
clear_notifications(agent_name, ids=None) -> int              # Clear notifications
wait_for_notifications(agent_name, timeout=None) -> Dict      # Wait for notifications
```

### 4. `claude_instances.py`
Claude instance management:
- **Instance Launching**: Start new Claude instances
- **Instance Coordination**: Coordinate multiple instances
- **Inter-Instance Messaging**: Communication between instances
- **Instance Lifecycle**: Track and manage instance status
- **Integration Layer**: Compatibility with existing tools

#### Key Functions:
```python
launch_claude_instance(role, project_path=None, startup_message=None) -> Dict
list_claude_instances() -> Dict
send_inter_instance_message(target_id, subject, message, sender_role) -> Dict
coordinate_claude_instances(task, instance_ids=None) -> Dict
```

## Usage Examples

### Basic Agent Management
```python
from agents.agent_management import get_agent_name, register_agent, set_custom_agent_name

# Set custom name and register
set_custom_agent_name("ProductManager")
registration = register_agent()
print(f"Registered as: {registration['name']}")
```

### Inter-Agent Messaging
```python
from agents.messaging import create_message, get_messages, mark_message_read

# Send a message
message = create_message(
    to="Developer",
    subject="Code Review Request",
    message="Please review the authentication module"
)

# Get messages for current agent
messages = get_messages("ProductManager")
for msg in messages:
    print(f"From {msg['from']}: {msg['subject']}")
    mark_message_read(msg['id'], "ProductManager")
```

### Notification System
```python
from agents.notifications import send_notification, get_pending_notifications

# Send notification
notification = send_notification("Developer", "Build completed successfully")

# Check for notifications
notifications = get_pending_notifications("ProductManager")
print(f"You have {len(notifications)} pending notifications")
```

### Claude Instance Management
```python
from agents.claude_instances import launch_claude_instance, coordinate_claude_instances

# Launch a specialized instance
result = launch_claude_instance(
    role="code_reviewer",
    project_path="/path/to/project",
    startup_message="Focus on security and performance"
)

# Coordinate multiple instances
coordination = coordinate_claude_instances(
    task="Implement OAuth2 authentication system",
    instance_ids=["instance1", "instance2"]
)
```

## Integration with MCP Server

### Replace Existing Agent Functionality
```python
# Old approach (agent_messaging.py)
from agent_messaging import AgentMessaging
messaging = AgentMessaging()
messaging.create_message(...)

# New modular approach
from agents.messaging import create_message
create_message(...)
```

### MCP Tool Integration
```python
from agents.agent_management import get_agent_name, register_agent
from agents.messaging import create_message, get_messages

@mcp.tool()
def register_agent_with_name(agent_name: str):
    """Register agent with custom name."""
    set_custom_agent_name(agent_name)
    return register_agent()

@mcp.tool()
def send_agent_message(to: str, subject: str, message: str):
    """Send message to another agent."""
    return create_message(to, subject, message)
```

## Testing

Run the test suite to verify functionality:
```bash
python test_agent_modules.py
```

The test suite covers:
- Agent registration and management
- Message creation and retrieval
- Notification sending and receiving
- Claude instance management
- Error handling and edge cases

## File Structure

```
agents/
├── __init__.py              # Module exports and imports
├── agent_management.py      # Core agent management
├── messaging.py             # Inter-agent messaging
├── notifications.py         # Real-time notifications
├── claude_instances.py      # Claude instance management
├── integration_example.py   # MCP server integration example
├── test_agent_modules.py    # Test suite
└── README.md               # This documentation
```

## Data Storage

The modules use file-based storage in the `messages/` directory:
```
messages/
├── agents/                  # Agent registrations
│   └── {agent_name}/
│       └── registration.json
├── messages/                # Inter-agent messages
│   └── {message_id}.json
├── notifications/           # Notification system
│   ├── pending/
│   │   └── {agent}_{notif_id}.json
│   └── cancel_flags/
│       └── {agent}.flag
└── sequence.txt            # Message ID counter
```

## Benefits

1. **Modular Design**: Clean separation of concerns
2. **Better Testability**: Each module can be tested independently
3. **Improved Maintainability**: Easier to update and extend
4. **Thread Safety**: Proper locking mechanisms
5. **Async Support**: Event-driven communication
6. **Backward Compatibility**: Drop-in replacement for existing functionality
7. **Extensibility**: Easy to add new features

## Migration from Old System

1. Replace `agent_messaging.py` imports with modular imports
2. Update MCP tool functions to use new module functions
3. Remove old `AgentMessaging` class instantiation
4. Test thoroughly with existing functionality

The new system maintains full backward compatibility while providing a cleaner, more maintainable architecture.