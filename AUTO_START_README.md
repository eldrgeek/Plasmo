# Auto-Start Development Environment

This project is configured to automatically start both the **MCP Server** and **Plasmo dev server** when you open the workspace in Cursor/VS Code.

## 🚀 Auto-Start Configuration

### Method 1: VS Code Tasks (Recommended)
The workspace is configured with VS Code tasks that automatically run when you open the project:

**Files Created:**
- `.vscode/tasks.json` - Task definitions
- `.vscode/settings.json` - Workspace settings  
- `.vscode/launch.json` - Debug configurations

**What Happens Automatically:**
1. **MCP Server** starts on `http://127.0.0.1:8000/mcp`
2. **Plasmo dev server** starts with auto-reload
3. Both run in separate terminal panels
4. Services continue running until manually stopped

### Method 2: Manual Script
If auto-start doesn't work or you prefer manual control:

```bash
./start_dev_environment.sh
```

This script:
- ✅ Checks prerequisites (Python, pnpm)
- 🔧 Starts MCP Server v2.0
- 🎯 Starts Plasmo dev server
- 🛑 Handles cleanup on Ctrl+C

## 📋 Available Tasks

Access via **Terminal > Run Task** or Command Palette (`Cmd+Shift+P`):

| Task | Description |
|------|-------------|
| **Start MCP Server with Auto-Restart** | Launch MCP server with file watching |
| **Start MCP Server (Basic)** | Launch MCP server without auto-restart |
| **Start Plasmo Dev Server** | Launch Plasmo with auto-reload |
| **Stop All Servers** | Kill MCP and Plasmo processes |
| **Restart All Servers** | Stop and restart both services |

## 🔄 Auto-Restart Feature

The MCP server now includes intelligent auto-restart functionality:

### What Files Are Watched
- `mcp_server.py` - Main server file
- `mcp_server.py` - Legacy server file
- `chrome_debug_fixes.py` - Debug utilities
- `requirements.txt` - Python dependencies

### How It Works
1. **File Monitoring**: Checks file modification times every 2 seconds
2. **Change Detection**: Compares timestamps to detect changes
3. **Graceful Restart**: Stops old server, starts new instance
4. **Status Updates**: Shows restart progress in terminal

### Manual Auto-Restart
```bash
# Start MCP server with auto-restart
./start_mcp_auto_restart.sh

# Or use the combined script
./start_dev_environment.sh  # Includes auto-restart
```

## 🔧 Manual Control

### Start Services
```bash
# MCP Server
python3 mcp_server.py --port 8000

# Plasmo Dev Server  
pnpm dev
```

### Stop Services
```bash
# Stop all at once
pkill -f "mcp_server.py|pnpm.*dev"

# Or use VS Code task: "Stop All Servers"
```

## 🐛 Debug Configuration

Launch configurations available in **Run and Debug** panel:

- **Debug MCP Server** - Debug MCP server with breakpoints
- **Launch Chrome for Extension Debug** - Start Chrome with debug flags
- **Debug Extension + MCP** - Combined debugging session

## ⚙️ Configuration Details

### Auto-Start Settings
```json
{
    "task.allowAutomaticTasks": "on",
    "runOptions": {
        "runOn": "folderOpen"  
    }
}
```

### Environment Variables
- `PLASMO_AUTO_RELOAD=true` - Enable auto-reload
- `PYTHONPATH=${workspaceFolder}` - Python path for debugging

## 🔍 Troubleshooting

### Auto-Start Not Working
1. **Check Task Permissions**: 
   - Go to **Cursor > Preferences > Settings**
   - Search for "automatic tasks"
   - Ensure "Allow automatic tasks" is enabled
2. **Verify Configuration**:
   - Check `.vscode/settings.json` has `"task.allowAutomaticTasks": "on"`
   - Ensure tasks.json has `"runOptions": {"runOn": "folderOpen"}`
3. **Manual Test**:
   - Run **Terminal > Run Task > Auto-Start Development Environment**
   - If this works, restart Cursor to enable auto-start
4. **Fallback Options**:
   - Use manual script: `./start_dev_environment.sh`
   - Use individual tasks: "Start MCP Server with Auto-Restart"

### Force Enable Auto-Start
If auto-start still doesn't work, try this:
```bash
# Method 1: Test if tasks work manually
# Terminal > Run Task > Auto-Start Development Environment

# Method 2: Use the manual startup script
./start_dev_environment.sh

# Method 3: Enable in Cursor settings
# File > Preferences > Settings > Search "task.allowAutomaticTasks"
```

### Port Conflicts
```bash
# Check what's using port 8000
lsof -i :8000

# Kill conflicting processes
pkill -f mcp_server
```

### MCP Server Issues
```bash
# Check logs
tail -f mcp_server.log

# Test server directly
curl http://127.0.0.1:8000/mcp
```

### Plasmo Dev Issues
```bash
# Clear Plasmo cache
rm -rf .plasmo

# Reinstall dependencies
pnpm install
```

## 🎯 Development Workflow

1. **Open Project** - Services start automatically
2. **Code Changes** - Plasmo auto-reloads extension
3. **Debug Extension** - Use Chrome debug tools via MCP
4. **Close Project** - Services stop automatically

Perfect for rapid development cycles! 🚀 