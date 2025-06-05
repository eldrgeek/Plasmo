# Claude Desktop Configuration for FastMCP Server

This guide shows how to configure the FastMCP server to work with Claude Desktop using STDIO mode.

## 🚀 Quick Setup

1. **Start the server in STDIO mode to test it works**:
   ```bash
   python3 mcp_server.py --stdio
   # Press Ctrl+C to stop after testing
   ```

2. **Locate your Claude Desktop config file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. **Add the server configuration**:
   
   Replace the contents of your config file with (or add to existing config):
   ```json
   {
     "mcpServers": {
       "cursor-dev-assistant": {
         "command": "python",
         "args": ["/absolute/path/to/your/mcp_server.py", "--stdio"],
         "env": {
           "PYTHONPATH": "/absolute/path/to/your/project"
         }
       }
     }
   }
   ```

   **Important**: Replace `/absolute/path/to/your/mcp_server.py` with the actual absolute path to your `mcp_server.py` file.

   Example:
   ```json
   {
     "mcpServers": {
       "cursor-dev-assistant": {
         "command": "python",
         "args": ["/Users/yourname/Projects/Plasmo/mcp_server.py", "--stdio"],
         "env": {
           "PYTHONPATH": "/Users/yourname/Projects/Plasmo"
         }
       }
     }
   }
   ```

4. **Restart Claude Desktop**

5. **Test the integration**:
   - Open Claude Desktop
   - Ask: "What tools are available from the MCP server?"
   - Try: "Show me the structure of my project"

## 🔧 Available Tools in STDIO Mode

### 📁 File Operations
- **read_file** - Read file contents
- **write_file** - Write content to files  
- **list_files** - List directory contents with pattern matching

### 💻 Project Analysis
- **get_project_structure** - Analyze project directory structure
- **analyze_code** - Get code metrics and analysis
- **search_in_files** - Search for patterns across files

### 🗄️ Version Control
- **run_git_command** - Execute safe git commands (read-only)

### 🌐 Chrome Debug Protocol
- **launch_chrome_debug** - Launch Chrome with debugging enabled
- **connect_to_chrome** - Connect to Chrome debug instance
- **get_chrome_tabs** - List available browser tabs
- **start_console_monitoring** - Begin monitoring console output
- **get_console_logs** - Retrieve captured console logs
- **clear_console_logs** - Clear console log history
- **execute_javascript** - Run JavaScript in Chrome tab
- **set_breakpoint** - Set debugging breakpoints
- **get_chrome_debug_info** - Get comprehensive debug information

### 🗃️ Database Operations
- **create_sqlite_db** - Create SQLite databases
- **query_sqlite_db** - Query SQLite databases

### ⚙️ System Information
- **get_system_info** - Get system and environment information
- **server_info** - Get MCP server information

## 💡 Example Prompts

Once configured, you can use these prompts in Claude Desktop:

### File and Project Analysis
- "Show me the structure of my project"
- "Read the package.json file and explain the dependencies"
- "Search for 'TODO' comments in all JavaScript files"
- "Analyze the code in popup.tsx and give me metrics"
- "List all TypeScript files in the contents directory"

### Git Operations
- "What's the git status of this repository?"
- "Show me the latest git commits"
- "What branches are available in this repository?"

### Chrome Debugging
- "Launch Chrome with debugging enabled"
- "Connect to Chrome and show me available tabs"
- "Start monitoring console logs for the first tab"
- "Execute JavaScript: console.log('Hello from Claude!') in the active tab"
- "Get the latest console errors from Chrome"

### Database Operations
- "Create a SQLite database for storing user preferences"
- "Query the database to show all tables"

## 🔧 Configuration Options

### Environment Variables

You can set additional environment variables in the config:

```json
{
  "mcpServers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["/path/to/mcp_server.py", "--stdio"],
      "env": {
        "PYTHONPATH": "/path/to/project",
        "DEBUG": "true",
        "CHROME_DEBUG_PORT": "9222"
      }
    }
  }
}
```

### Multiple Servers

You can configure multiple MCP servers:

```json
{
  "mcpServers": {
    "cursor-dev-assistant": {
      "command": "python",
      "args": ["/path/to/mcp_server.py", "--stdio"]
    },
    "another-server": {
      "command": "node",
      "args": ["/path/to/other_server.js"]
    }
  }
}
```

## 🔒 Security Notes

- The server runs with the same permissions as Claude Desktop
- File operations are limited to your project directory
- Only read-only git commands are allowed
- Chrome debugging requires explicit user consent

## 🆘 Troubleshooting

### Server not found
- Verify the absolute path to `mcp_server.py` is correct
- Check that Python is in your PATH
- Try running the command manually in terminal

### Tools not available
- Restart Claude Desktop after configuration changes
- Check Claude Desktop logs for error messages
- Verify dependencies are installed: `pip3 list | grep fastmcp`

### Chrome debugging issues
- Ensure Chrome is installed and accessible
- Check if port 9222 is available: `lsof -i :9222`
- Try launching Chrome manually with debugging enabled

### Permission errors
- Check file permissions on the server script
- Ensure Python has read access to your project directory
- On macOS, you may need to grant permissions to Claude Desktop

## 📝 Config File Template

Use the provided `claude_desktop_config.json` as a template:

1. Copy `claude_desktop_config.json` to your Claude Desktop config location
2. Update the paths to match your system
3. Restart Claude Desktop

## 🎉 Happy Coding!

Your FastMCP server is now ready to assist with your development tasks in Claude Desktop! The server provides powerful file operations, code analysis, project insights, git operations, and Chrome debugging capabilities to help you build better applications faster. 