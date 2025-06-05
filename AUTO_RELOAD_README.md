# MCP Server Auto-Reload Feature

The `start_mcp.sh` script now includes automatic reload functionality that watches for changes in `mcp_server.py` and automatically restarts the server when modifications are detected.

## 🚀 Quick Start

```bash
# Start the server with auto-reload
./start_mcp.sh
```

## 🎯 Features

### ✨ Automatic Reloading
- 👁️ **File Watching**: Monitors `mcp_server.py` for changes
- 🔄 **Instant Restart**: Automatically restarts the server when files change
- 📊 **Status Logging**: Shows timestamps and process information
- 🛑 **Graceful Shutdown**: Clean exit with Ctrl+C

### 🔧 Multi-Platform Support
1. **fswatch** (Recommended) - macOS/Linux
2. **inotifywait** - Linux
3. **Polling Fallback** - Cross-platform

### 💻 Installation Options

**For optimal performance, install fswatch:**
```bash
# macOS
brew install fswatch

# Ubuntu/Debian
sudo apt-get install fswatch

# CentOS/RHEL
sudo yum install fswatch
```

**If fswatch is not available, the script will:**
- Try `inotifywait` on Linux systems
- Fall back to polling method (works everywhere)

## 📋 Usage Examples

### Basic Usage
```bash
# Start with auto-reload
./start_mcp.sh

# Make changes to mcp_server.py
# Server automatically restarts!
```

### Development Workflow
```bash
# Terminal 1: Start server with auto-reload
./start_mcp.sh

# Terminal 2: Edit your code
vim mcp_server.py
# Save the file - server restarts automatically

# Terminal 3: Test your changes
curl http://127.0.0.1:8000/tools/server_info
```

### Demo Mode
```bash
# See auto-reload in action
./demo_auto_reload.sh test
```

## 🎬 Sample Output

When you start the server:
```
🚀 Starting FastMCP Server for Cursor with Auto-Reload...
==========================================================
✅ Dependencies verified
🌐 Starting server on http://127.0.0.1:8000
🔄 Auto-reload enabled - watching mcp_server.py for changes

To stop the server, press Ctrl+C

14:30:15 🟢 Starting MCP server...
14:30:16 📡 Server started with PID: 12345
14:30:16 👁️  Using fswatch for file monitoring
14:30:16 🎯 Auto-reload is active!
14:30:16 📝 Edit mcp_server.py and save to see auto-reload in action
14:30:16 ⚡ File watcher PID: 12346
```

When you modify `mcp_server.py`:
```
14:32:45 🔄 File change detected - restarting server...
14:32:45 🔴 Stopping server (PID: 12345)...
14:32:45 ✅ Server stopped
14:32:46 🟢 Starting MCP server...
14:32:47 📡 Server started with PID: 12347
14:32:47 ✨ Server reloaded successfully!
```

## 🛠️ How It Works

### 1. File Monitoring
The script uses different methods based on availability:

**fswatch (Best)**
```bash
fswatch -o mcp_server.py | while read f; do restart_server; done &
```

**inotifywait (Linux)**
```bash
while inotifywait -e modify mcp_server.py; do restart_server; done &
```

**Polling (Fallback)**
```bash
# Check file modification time every 2 seconds
while true; do
    # Compare current vs last modification time
    # Restart if changed
done
```

### 2. Process Management
- **Graceful Restart**: Stops old server before starting new one
- **PID Tracking**: Keeps track of server and watcher processes
- **Signal Handling**: Proper cleanup on Ctrl+C
- **Background Tasks**: File watching runs in background

### 3. Error Handling
- **Dependency Check**: Verifies fastmcp is installed
- **File Existence**: Ensures mcp_server.py exists
- **Process Cleanup**: Kills all related processes on exit

## 🔧 Customization

### Watch Additional Files
To watch more files, modify the file watcher section:

```bash
# Watch multiple files
fswatch -o mcp_server.py requirements.txt config.py | while read f; do restart_server; done &
```

### Change Polling Interval
For the polling fallback, adjust the sleep time:

```bash
# Check every 1 second instead of 2
sleep 1
```

### Custom Restart Delay
Modify the restart delay:

```bash
restart_server() {
    echo "$(date '+%H:%M:%S') 🔄 File change detected - restarting server..."
    stop_server
    sleep 2  # Increase delay to 2 seconds
    start_server
    echo "$(date '+%H:%M:%S') ✨ Server reloaded successfully!"
}
```

## 🚨 Troubleshooting

### fswatch Not Found
```bash
# Install fswatch for better performance
brew install fswatch  # macOS
sudo apt-get install fswatch  # Linux
```

### Server Won't Stop
```bash
# Find and kill MCP server processes
ps aux | grep mcp_server.py
kill <PID>
```

### Permission Issues
```bash
# Make sure script is executable
chmod +x start_mcp.sh
```

### Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process using the port
kill $(lsof -t -i:8000)
```

## 💡 Tips & Best Practices

### 1. Development Workflow
- Keep auto-reload running during development
- Make small, incremental changes
- Test immediately after each change

### 2. Performance
- Install `fswatch` for fastest file detection
- Avoid editing large files frequently
- Use a proper editor that saves atomically

### 3. Debugging
- Watch the console output for restart notifications
- Check timestamps to verify reload timing
- Use the demo script to test functionality

### 4. Production
- Don't use auto-reload in production
- Use regular `python3 mcp_server.py` for production
- Consider using a process manager like `systemd` or `pm2`

## 🎉 Benefits

### For Development
- ⚡ **Faster iteration** - No manual restart needed
- 🐛 **Better debugging** - Immediate feedback on changes
- 💾 **Save time** - Focus on coding, not process management
- 🔄 **Consistent workflow** - Same process every time

### For Testing
- 🧪 **Live testing** - Changes reflect immediately
- 📊 **Real-time feedback** - See results instantly
- 🔍 **Quick validation** - Test without manual steps

## 📝 Example Development Session

```bash
# Start auto-reload server
./start_mcp.sh

# Edit mcp_server.py - add a new tool
@mcp.tool()
def new_tool():
    return "Hello World"

# Save file → Server restarts automatically!

# Test immediately
curl http://127.0.0.1:8000/tools/new_tool

# Make another change - fix a bug
# Save file → Server restarts again!

# Continue development cycle...
```

This auto-reload feature dramatically improves the development experience by eliminating the manual restart cycle, letting you focus on writing code while the server manages itself! 🚀 