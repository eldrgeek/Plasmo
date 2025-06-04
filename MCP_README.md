# FastMCP Server for Cursor Integration

This directory contains a FastMCP (Model Context Protocol) server that provides AI-powered development tools for your Cursor IDE. The server integrates seamlessly with your Plasmo browser extension project.

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
./setup_mcp.sh
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Run the server
python3 mcp_server.py
```

## 📋 Prerequisites

- Python 3.7 or higher
- pip3 (Python package installer)
- Cursor IDE

## 🛠 Installation Steps

1. **Install Python dependencies**:
   ```bash
   pip3 install fastmcp uvicorn
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
   Tools available: 11
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

## 🔧 Available Tools

The MCP server provides the following tools:

### File Operations
- **`read_file`** - Read file contents
- **`write_file`** - Write content to files
- **`list_files`** - List directory contents with pattern matching

### Project Analysis
- **`get_project_structure`** - Analyze project directory structure
- **`analyze_code`** - Get code metrics and analysis
- **`search_in_files`** - Search for patterns across files

### Version Control
- **`run_git_command`** - Execute safe git commands (read-only)

### Database Operations
- **`create_sqlite_db`** - Create SQLite databases
- **`query_sqlite_db`** - Query SQLite databases

### System Information
- **`get_system_info`** - Get system and environment information
- **`server_info`** - Get MCP server information

## 💡 Example Usage

Once set up, you can use natural language prompts in Cursor like:

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
- **Error handling**: Graceful error handling for all operations

## 🐛 Troubleshooting

### Server won't start
- Check if port 8000 is available: `lsof -i :8000`
- Try a different port by modifying `SERVER_PORT` in `mcp_server.py`

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
├── mcp_server.py          # Main MCP server
├── requirements.txt       # Python dependencies
├── setup_mcp.sh          # Automated setup script
├── MCP_README.md         # This file
├── package.json          # Your Plasmo project config
├── popup.tsx             # Your Plasmo popup
├── background.ts         # Your Plasmo background script
└── ...                   # Other Plasmo files
```

## 🔄 Server Management

### Start the server
```bash
python3 mcp_server.py
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

## 📝 Customization

You can customize the server by modifying `mcp_server.py`:

- **Change port**: Modify `SERVER_PORT` variable
- **Add new tools**: Create new functions with `@mcp.tool()` decorator
- **Modify existing tools**: Edit the existing tool functions
- **Add authentication**: Implement authentication middleware

## 🤝 Integration with Plasmo

This MCP server is specifically useful for Plasmo browser extension development:

- **Manifest analysis**: Read and analyze your extension manifest
- **Content script management**: Analyze content scripts in the `contents/` directory
- **Asset management**: List and analyze assets
- **Build optimization**: Analyze build outputs in `.plasmo/` directory

## 📚 Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Cursor IDE Documentation](https://docs.cursor.sh/)
- [Plasmo Framework Documentation](https://docs.plasmo.com/)

## 🆘 Support

If you encounter issues:

1. Check the server logs for error messages
2. Verify Python and pip versions
3. Ensure all dependencies are installed correctly
4. Check Cursor settings configuration
5. Restart both the server and Cursor IDE 