# FastMCP Server for Cursor Integration

This directory contains a FastMCP (Model Context Protocol) server that provides AI-powered development tools for your Cursor IDE and other MCP clients. The server integrates seamlessly with your Plasmo browser extension project and now includes **Chrome Debug Protocol support** for live debugging and console log monitoring.

## 🚀 Quick Start

### Option 1: HTTP Mode (Default - for Cursor IDE)
```bash
# Automated setup
./setup_mcp.sh

# Start HTTP server
python3 mcp_server.py
# or
./start_mcp.sh
```

### Option 2: STDIO Mode (for Claude Desktop and local tools)
```bash
# Start STDIO server
python3 mcp_server.py --stdio
# or
./start_mcp_stdio.sh
```

### Option 3: Chrome Debug Protocol Setup
```bash
./setup_chrome_debug.sh  # Sets up Chrome debugging
./setup_mcp.sh           # Sets up MCP server
```

## 🌐 NEW: Dual Transport Support

The MCP server now supports both HTTP and STDIO transports:

### 🖥️ HTTP Mode (Default)
- **Best for**: Cursor IDE, web-based deployments, microservices
- **URL**: `http://127.0.0.1:8000/mcp`
- **Usage**: `python3 mcp_server.py` or `python3 mcp_server.py --http`

### 📟 STDIO Mode
- **Best for**: Claude Desktop, local tools, command-line integration
- **Communication**: Standard input/output
- **Usage**: `python3 mcp_server.py --stdio`

## 📋 Prerequisites

- Python 3.7 or higher
- pip3 (Python package installer)
- **For HTTP mode**: Cursor IDE or MCP client with HTTP support
- **For STDIO mode**: Claude Desktop or MCP client with subprocess management
- **For Chrome debugging**: Google Chrome

## 🛠 Installation Steps

1. **Install Python dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Choose your transport mode**:

   **For HTTP Mode (Cursor IDE)**:
   ```bash
   python3 mcp_server.py
   ```
   
   **For STDIO Mode (Claude Desktop)**:
   ```bash
   python3 mcp_server.py --stdio
   ```

3. **Configure your client**:

   **Cursor IDE Configuration**:
   - Open Cursor settings (`Cmd/Ctrl + ,`)
   - Search for "mcp" or "Model Context Protocol"
   - Add this configuration to your `settings.json`:

   ```json
   {
     "mcpServers": {
       "cursor-dev-assistant": {
         "url": "http://127.0.0.1:8000/mcp"
       }
     }
   }
   ```

   **Claude Desktop Configuration**:
   - Open Claude Desktop settings
   - Add this configuration:

   ```json
   {
     "mcpServers": {
       "cursor-dev-assistant": {
         "command": "python",
         "args": ["/path/to/your/mcp_server.py", "--stdio"]
       }
     }
   }
   ```

4. **Restart your client** (Cursor IDE or Claude Desktop)

5. **Test the integration**:
   - Open a new chat
   - Ask: "What tools are available from the MCP server?"
   - Try: "Launch Chrome with debugging enabled"

## 🔧 Available Tools

The MCP server provides the following tools in both HTTP and STDIO modes:

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

### HTTP Mode with Cursor IDE
```bash
# Start HTTP server
python3 mcp_server.py

# Use in Cursor IDE
# Ask: "Read the package.json file"
# Ask: "Launch Chrome with debugging and monitor console logs"
```

### STDIO Mode with Claude Desktop
```bash
# Start STDIO server
python3 mcp_server.py --stdio

# Use in Claude Desktop
# Ask: "Show me the project structure"
# Ask: "Connect to Chrome and get available tabs"
```

### Command Line Options
```bash
python3 mcp_server.py                    # HTTP mode (default)
python3 mcp_server.py --stdio            # STDIO mode
python3 mcp_server.py --http             # Explicitly HTTP mode
python3 mcp_server.py --port 9000        # Custom port (HTTP mode)
python3 mcp_server.py --host 0.0.0.0     # Bind to all interfaces (HTTP mode)
python3 mcp_server.py --path /custom     # Custom HTTP path
```

## 🔧 Server Management

### Start Server
```bash
# HTTP mode
./start_mcp.sh
python3 mcp_server.py

# STDIO mode
./start_mcp_stdio.sh
python3 mcp_server.py --stdio
```

### Stop Server
**HTTP mode**: Press `Ctrl+C` in the terminal where the server is running

**STDIO mode**: The server runs per-session and is managed by the client

### Check if Running (HTTP mode only)
```bash
curl http://127.0.0.1:8000/mcp
```

### View Logs
Server logs appear in the terminal. For HTTP mode background operation:
```bash
nohup python3 mcp_server.py > mcp_server.log 2>&1 &
```

## 🛠 Customization

The server is designed to be easily customizable:

1. **Add new tools**: Edit `mcp_server.py` and add functions with `@mcp.tool()` decorator
2. **Change HTTP settings**: Use command-line arguments `--host`, `--port`, `--path`
3. **Change Chrome debug port**: Modify `CHROME_DEBUG_PORT` variable in `mcp_server.py`
4. **Add authentication**: Implement auth middleware (see FastMCP docs)

## 📚 Documentation

- See this README for comprehensive setup instructions
- [FastMCP Documentation](https://gofastmcp.com/)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [Plasmo Framework Documentation](https://docs.plasmo.com/)

## 🤝 Integration with Plasmo

This MCP server is specifically useful for Plasmo browser extension development:

- **Manifest analysis**: Read and analyze your extension manifest
- **Content script management**: Analyze content scripts in the `contents/` directory
- **Asset management**: List and analyze assets
- **Build optimization**: Analyze build outputs in `.plasmo/` directory
- **Live debugging**: Debug your extension's JavaScript in real-time *(NEW!)*
- **Console monitoring**: Monitor extension console output *(NEW!)*

## 🔒 Security Notes

- Only read-only git commands are allowed
- File operations are limited to the project directory
- Database operations use safe SQLite queries
- All operations include proper error handling
- Chrome debugging requires explicit user consent

## 🆘 Troubleshooting

### Server won't start
- **HTTP mode**: Check if port 8000 is available: `lsof -i :8000`
- **STDIO mode**: Check Python path and dependencies
- Verify Python dependencies: `pip3 list | grep fastmcp`

### Client doesn't see the server
- **HTTP mode**: Ensure server is running before starting client
- **STDIO mode**: Check command path in client configuration
- **HTTP mode**: Check URL in client settings matches `http://127.0.0.1:8000/mcp`
- Restart client after configuration

### Tools not working
- Check server logs for errors
- Verify file paths are relative to project root
- Ensure proper file permissions
- For Chrome debugging issues, see Chrome setup instructions

### Chrome debugging issues
- Ensure Chrome is launched with `--remote-debugging-port=9222`
- Check WebSocket permissions with `--remote-allow-origins=*`
- Verify Chrome Debug Protocol port is not blocked by firewall

## 🎉 You're All Set!

Your FastMCP server is ready to supercharge your development with AI-powered tools in both Cursor IDE and Claude Desktop. The server provides comprehensive file operations, code analysis, project structure insights, safe git operations, and cutting-edge Chrome Debug Protocol integration to help you build better browser extensions faster.

**Choose your mode**:
- 🖥️ **HTTP mode** for Cursor IDE and web-based workflows
- 📟 **STDIO mode** for Claude Desktop and local tool integration

Happy coding! 🚀 