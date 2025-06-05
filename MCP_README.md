# FastMCP Server for Cursor Integration

This directory contains a FastMCP (Model Context Protocol) server that provides AI-powered development tools for your Cursor IDE. The server integrates seamlessly with your Plasmo browser extension project and now includes **Chrome Debug Protocol support** for live debugging and console log monitoring.

## 🚀 Quick Start

### Option 1: Automated Setup (with Chrome Debug Protocol)
```bash
./setup_chrome_debug.sh  # New! Sets up Chrome debugging
./setup_mcp.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies (including Chrome debug support)
pip3 install -r requirements.txt

# Run the server
python3 mcp_server.py
```

## 🌐 NEW: Chrome Debug Protocol Integration

The MCP server now includes comprehensive Chrome Debug Protocol support for:
- **Live console log monitoring** from Chrome tabs
- **JavaScript execution** in browser context
- **Breakpoint setting** for debugging
- **Real-time debugging** of web applications

### Quick Chrome Debug Start:
1. **Launch Chrome with debugging**: `./launch-chrome-debug.sh`
2. **Start MCP server**: `python3 mcp_server.py`
3. **Ask AI**: "Connect to Chrome and start monitoring console logs"

📖 **For detailed Chrome debugging documentation, see: [CHROME_DEBUG_README.md](CHROME_DEBUG_README.md)**

## 📋 Prerequisites

- Python 3.7 or higher
- pip3 (Python package installer)
- Cursor IDE
- **Google Chrome** (for debug protocol features)

## 🛠 Installation Steps

1. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Start the MCP server**:
   ```bash
   python3 mcp_server.py
   ```
   
   You should see output like:
   ```
   🚀 FastMCP Server Starting
   ========================
   Server: http://127.0.0.1:8000
   Transport: HTTP
   Tools available: 19
   
   🔧 Chrome Debug Protocol Support Added!
   Chrome Debug Port: 9222
   ```

3. **Configure Cursor IDE**:
   - Open Cursor settings (`Cmd/Ctrl + ,`)
   - Search for "mcp" or "Model Context Protocol"
   - Add this configuration to your `settings.json`:

   ```json
   {
     "mcpServers": {
       "cursor-dev-assistant": {
         "url": "http://127.0.0.1:8000"
       }
     }
   }
   ```

4. **Restart Cursor IDE**

5. **Test the integration**:
   - Open a new chat in Cursor
   - Ask: "What tools are available from the MCP server?"
   - Try: "Launch Chrome with debugging enabled"

## 🔧 Available Tools

The MCP server provides the following tools:

### 📁 File Operations
- **`read_file`** - Read file contents
- **`write_file`** - Write content to files
- **`list_files`** - List directory contents with pattern matching

### 💻 Project Analysis
- **`get_project_structure`** - Analyze project directory structure
- **`analyze_code`** - Get code metrics and analysis
- **`search_in_files`** - Search for patterns across files

### 🗄️ Version Control
- **`run_git_command`** - Execute safe git commands (read-only)

### 🌐 Chrome Debug Protocol *(NEW!)*
- **`launch_chrome_debug`** - Launch Chrome with debugging enabled
- **`connect_to_chrome`** - Connect to Chrome debug instance
- **`get_chrome_tabs`** - List available browser tabs
- **`start_console_monitoring`** - Begin monitoring console output
- **`get_console_logs`** - Retrieve captured console logs
- **`clear_console_logs`** - Clear console log history
- **`execute_javascript`** - Run JavaScript in Chrome tab
- **`set_breakpoint`** - Set debugging breakpoints
- **`get_chrome_debug_info`** - Get comprehensive debug information

### 🗃️ Database Operations
- **`create_sqlite_db`** - Create SQLite databases
- **`query_sqlite_db`** - Query SQLite databases

### ⚙️ System Information
- **`get_system_info`** - Get system and environment information
- **`server_info`** - Get MCP server information

## 💡 Example Usage

Once set up, you can use natural language prompts in Cursor like:

### For Chrome debugging *(NEW!)*:
- "Launch Chrome with debugging enabled"
- "Connect to Chrome and show me available tabs"
- "Start monitoring console logs for the React app tab"
- "Get the latest console errors from Chrome"
- "Execute JavaScript: document.title in the first tab"
- "Set a breakpoint at line 42 in main.js"
- "Clear all console logs and start fresh monitoring"

### For your Plasmo project:
- "Show me the structure of my Plasmo extension project"
- "Read the manifest permissions from package.json"
- "Analyze the code in popup.tsx"
- "Search for 'chrome.storage' usage in all TypeScript files"
- "What's the git status of this repository?"

### General development:
- "List all TypeScript files in the contents directory"
- "Show me the project structure up to 2 levels deep"
- "Search for TODO comments in JavaScript files"
- "Analyze the background.ts file for code metrics"

## 🔒 Security Features

- **Safe git commands only**: Only read-only git operations are allowed
- **File system protection**: Write operations create directories safely
- **Command timeout**: Git commands timeout after 30 seconds
- **Chrome debug isolation**: Uses separate Chrome profile for debugging
- **Error handling**: Graceful error handling for all operations

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Try a different port by modifying `SERVER_PORT` in `mcp_server.py`

### Chrome debugging issues *(NEW!)*
- Ensure Chrome is installed and accessible
- Check if port 9222 is available: `lsof -i :9222`
- Try launching Chrome manually: `./launch-chrome-debug.sh`
- See detailed troubleshooting in [CHROME_DEBUG_README.md](CHROME_DEBUG_README.md)

### Cursor doesn't recognize the server
- Ensure the server is running before starting Cursor
- Check the server URL in Cursor settings matches the running server
- Restart Cursor after adding the configuration

### Tools not working
- Check server logs for errors
- Verify file paths are correct relative to the project root
- Ensure proper permissions for file operations

## 📁 Project Structure

```
your-plasmo-project/
├── mcp_server.py              # Main MCP server
├── requirements.txt           # Python dependencies
├── setup_mcp.sh              # Automated setup script
├── start_mcp.sh              # Start server with auto-reload (UPDATED!)
├── setup_chrome_debug.sh     # Chrome debug setup (NEW!)
├── launch-chrome-debug.sh    # Chrome launcher (NEW!)
├── test_chrome_debug.py      # Chrome debug test script (NEW!)
├── demo_auto_reload.sh       # Auto-reload demonstration (NEW!)
├── MCP_README.md             # This file
├── CHROME_DEBUG_README.md    # Chrome debugging guide (NEW!)
├── AUTO_RELOAD_README.md     # Auto-reload feature guide (NEW!)
├── chrome-debug-profile/     # Chrome debug profile directory (NEW!)
├── package.json              # Your Plasmo project config
├── popup.tsx                 # Your Plasmo popup
├── background.ts             # Your Plasmo background script
└── ...                       # Other Plasmo files
```

## 🔄 Server Management

### Start the server
```bash
python3 mcp_server.py
```

### Start with Auto-Reload *(NEW!)*
```bash
./start_mcp.sh
```
**Features:**
- 🔄 **Automatic restart** when `mcp_server.py` is modified
- 👁️ **File watching** using `fswatch` (macOS/Linux) or polling fallback
- 🛑 **Graceful shutdown** with Ctrl+C
- 📊 **Timestamps and status** for all operations

**For optimal performance, install fswatch:**
```bash
brew install fswatch  # macOS
# or
sudo apt-get install fswatch  # Ubuntu/Debian
```

### Stop the server
Press `Ctrl+C` in the terminal where the server is running

### Run in background
```bash
nohup python3 mcp_server.py > mcp_server.log 2>&1 &
```

### Check if server is running
```bash
curl http://127.0.0.1:8000/health
```

### Test Chrome debugging *(NEW!)*
```bash
python3 test_chrome_debug.py
```

## 📝 Customization

You can customize the server by modifying `mcp_server.py`:

- **Change port**: Modify `SERVER_PORT` variable
- **Chrome debug port**: Modify `CHROME_DEBUG_PORT` variable
- **Add new tools**: Create new functions with `@mcp.tool()` decorator
- **Modify existing tools**: Edit the existing tool functions
- **Add authentication**: Implement authentication middleware

## 🤝 Integration with Plasmo

This MCP server is specifically useful for Plasmo browser extension development:

- **Manifest analysis**: Read and analyze your extension manifest
- **Content script management**: Analyze content scripts in the `contents/` directory
- **Asset management**: List and analyze assets
- **Build optimization**: Analyze build outputs in `.plasmo/` directory
- **Live debugging**: Debug your extension's JavaScript in real-time *(NEW!)*
- **Console monitoring**: Monitor extension console output *(NEW!)*

## 📚 Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Cursor IDE Documentation](https://docs.cursor.sh/)
- [Plasmo Framework Documentation](https://docs.plasmo.com/)

## 🆘 Support

If you encounter issues:

1. Check the server logs for error messages
2. Verify Python and pip versions
3. Ensure all dependencies are installed correctly
4. Check Cursor settings configuration
5. For Chrome debugging issues, see [CHROME_DEBUG_README.md](CHROME_DEBUG_README.md) 