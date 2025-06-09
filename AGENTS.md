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
- **NEW**: Continuous testing automation with file watching
- **NEW**: Multi-service coordination and health monitoring

**MCP Tools Available**:
- `connect_to_chrome()` - Establish debugging connection
- `get_chrome_tabs()` - List available browser tabs
- `get_chrome_debug_info()` - Comprehensive debug status
- `start_console_monitoring(tab_id)` - Begin log capture
- `get_console_logs()` - Retrieve captured logs
- `execute_javascript_fixed(code, tab_id)` - **Enhanced** reliable JavaScript execution with WebSocket filtering
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

### 4. Continuous Testing System **[NEW]**
**Purpose**: Automated test execution triggered by file changes
**Location**: `continuous_test_runner.py`
**Integration**: SocketIO server + Chrome Debug Protocol

**Key Features**:
- **File Monitoring**: Watches `.ts`, `.tsx`, `.js`, `.jsx`, `.html`, `.css`, `.py` files
- **Auto-Test Execution**: Triggers tests via CDP when files change
- **Real-time Results**: Sends test outcomes to SocketIO API
- **WebSocket Filtering**: Handles Chrome extension message noise
- **DevTools Conflict Resolution**: Ensures clean CDP environment

**Test Triggers**:
```python
# File patterns that trigger testing
WATCH_PATTERNS = [
    "*.ts", "*.tsx", "*.js", "*.jsx",  # JavaScript/TypeScript changes
    "*.html", "*.css",                  # UI changes  
    "*.py"                             # Backend changes
]

# Test commands executed via CDP
TEST_COMMANDS = {
    'frontend': 'await window.testRunner.run()',
    'ui': 'await window.validateUI()',
    'backend': 'await window.testBackendIntegration()'
}
```

### 5. Service Orchestration System **[NEW]**
**Purpose**: Coordinated management of development services
**Services**: MCP Server + SocketIO Server + Plasmo Dev + Continuous Testing
**Configuration**: `.vscode/tasks.json` with auto-start on workspace open

**Service Architecture**:
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │    │ SocketIO Server │    │   Plasmo Dev    │
│   Port: 8000    │    │   Port: 3001    │    │  Auto-reload    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Continuous Test │
                    │    Runner       │
                    │  File Watcher   │
                    └─────────────────┘
```

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
- **🆕 Use step-by-step MCP tool execution** rather than direct Python scripts for E2E workflows
- **🆕 Always use Claude.ai-specific DevTools URLs** for proper debugging context

### End-to-End Testing Workflow **[NEW - PROVEN]**
The **step-by-step MCP tool approach** has proven 100% successful for orchestration testing:

1. **Health Check**: `health()` - Verify MCP server operational status
2. **Chrome Connection**: `connect_to_chrome()` - Establish debug session  
3. **Tab Discovery**: `get_chrome_tabs()` - Find target AI service tabs
4. **DevTools Access**: Opens in separate tab via `chrome-devtools://devtools/bundled/devtools_app.html?ws=localhost:9222/devtools/page/{TAB_ID}`
5. **Prompt Injection**: `execute_javascript_fixed()` - Inject prompts into contenteditable divs
6. **Response Extraction**: `execute_javascript_fixed()` - Read AI service responses

**⚠️ DevTools Setup Requirements**: 
- **Popup Blocker**: Must allow popups on target site (major issue if blocked)
- **Automatic Docking**: Chrome security prevents programmatic sidebar docking
- **Manual Docking**: Use ⋮ → Dock side → Dock to right after DevTools opens
- **Alternative**: Use MCP server's console monitoring instead of DevTools UI

**Critical Success Factors**:
- Never use standalone Python scripts that attempt MCP tool calls
- Always use MCP tools through Cursor interface, step by step
- Target specific tabs with proper DevTools URLs
- Use contenteditable manipulation for prompt injection
- Allow response time before extraction (3-5 seconds)

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

## Critical Learnings & Best Practices **[NEW]**

### WebSocket Message Filtering
**Problem**: Chrome extensions flood CDP WebSocket with contextual messages, causing command timeouts
**Solution**: Filter messages by command ID and ignore extension noise

```python
# CRITICAL: Use command-specific message filtering
async def execute_reliable_cdp(websocket, command):
    command_id = int(time.time() * 1000)  # Unique ID
    command['id'] = command_id
    
    # Send command
    await websocket.send(json.dumps(command))
    
    # Listen ONLY for our command response
    while True:
        message = await websocket.recv()
        data = json.loads(message)
        
        # IGNORE extension noise - only process our command
        if data.get('id') == command_id:
            return data.get('result')
        # Continue listening, ignore other messages
```

### DevTools Interference Prevention
**Problem**: DevTools open on same tab blocks external CDP operations
**Solution**: Always check and close DevTools before CDP automation

```python
# CRITICAL: Ensure DevTools is closed before CDP operations
def ensure_clean_cdp_environment(tab_id):
    """
    DevTools and external CDP cannot operate on same tab simultaneously.
    Must close DevTools before running automated tests.
    """
    # Check if DevTools is attached
    # Close DevTools if open
    # Wait for clean state
    # Proceed with CDP operations
```

### Extension Context Noise Patterns
Common extension events that flood WebSocket (IGNORE these):
- `Runtime.executionContextCreated`
- `Runtime.executionContextDestroyed`
- `Page.frameNavigated`
- `Network.requestWillBeSent`
- `Network.responseReceived`

### Claude.ai Automation Patterns **[NEW - PROVEN]**
**Working selectors and methods for Claude.ai interaction**:

```javascript
// Proven prompt injection method
const promptDiv = document.querySelector('div[contenteditable="true"][data-testid*="chat"], div[contenteditable="true"] p');
if (promptDiv) {
    promptDiv.textContent = 'Your prompt here';
    
    // Trigger input events
    promptDiv.dispatchEvent(new Event('input', { bubbles: true }));
    promptDiv.dispatchEvent(new Event('change', { bubbles: true }));
}

// Proven send button method
const sendButton = document.querySelector('button[type="submit"], button[aria-label*="Send"], button:has(svg)');
if (sendButton && !sendButton.disabled) {
    sendButton.click();
}

// Proven response extraction method
setTimeout(() => {
    const responses = document.querySelectorAll('div[data-is-streaming="false"]');
    const lastResponse = responses[responses.length - 1];
    return lastResponse ? lastResponse.textContent : 'No response found';
}, 3000);
```

### Continuous Testing Integration
**Workflow**: File change → Test trigger → CDP execution → Real-time results
```
File Watcher → Debounce → CDP Test → SocketIO API → Web UI Update
```

**Test Execution Pattern**:
1. File change detected
2. Wait for debounce period (1-3 seconds)
3. Ensure clean CDP environment (close DevTools)
4. Execute test command via filtered WebSocket
5. Parse results and send to SocketIO API
6. Update real-time web interface

## Troubleshooting

### Common Issues
- **MCP connection failed**: Check if server is running on port 8000
- **Chrome debug unavailable**: Verify Chrome launched with debug flags
- **Extension not found**: Ensure extension is loaded and service worker is active
- **WebSocket errors**: Check `--remote-allow-origins=*` flag is set
- **🆕 DevTools won't open**: Check popup blocker - must allow popups on target site
- **🆕 CDP command timeouts**: Ensure message filtering by command ID is implemented
- **🆕 "Failed to enable Runtime domain"**: Close DevTools on target tab before CDP operations
- **🆕 Extension message noise**: Filter WebSocket messages, ignore extension context events
- **🆕 Test runner not triggering**: Check file watcher patterns and service dependencies

### Advanced Debugging
```bash
# Check WebSocket message flow (shows extension noise)
curl -N -H "Connection: Upgrade" -H "Upgrade: websocket" ws://localhost:9222/devtools/page/[TAB_ID]

# Verify all services are running
./check_services.sh

# Monitor continuous testing logs
tail -f logs/continuous_testing.log

# Test CDP connection manually
python3 quick_cdp_test.py

# Check service health endpoints
curl http://localhost:8000/health  # MCP Server
curl http://localhost:3001/api/status  # SocketIO Server
```

### Service Coordination Issues
```bash
# If services fail to start in correct order
./stop_all_services.sh
sleep 2
./start_all_services.sh

# Check service dependencies
./check_services.sh

# View service startup logs
tail -f logs/mcp_server.log
tail -f logs/socketio_server.log  
tail -f logs/continuous_testing.log
```

This integration provides a powerful development environment where AI assistants have direct access to browser debugging capabilities, enabling sophisticated extension development and troubleshooting workflows. ./