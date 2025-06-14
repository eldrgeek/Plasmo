# Chrome Debug Protocol Integration for MCP Server

This MCP server now includes comprehensive Chrome Debug Protocol (CDP) support for debugging web applications and monitoring console logs directly from Cursor IDE.

## 🚀 Quick Start

### Prerequisites
```bash
# Install additional dependencies
pip install websockets aiohttp pychrome
```

### Basic Usage

1. **Launch Chrome with debugging enabled:**
   ```bash
   ./launch-chrome-debug.sh
   # OR use the MCP tool
   # Ask AI: "Launch Chrome with debugging enabled"
   ```

2. **Connect to Chrome:**
   ```
   Ask AI: "Connect to Chrome and show me available tabs"
   ```

3. **Start monitoring console logs:**
   ```
   Ask AI: "Start monitoring console logs for the first tab"
   ```

4. **Retrieve console logs:**
   ```
   Ask AI: "Get the latest console logs from Chrome"
   ```

## 🛠️ Available Chrome Debug Tools

### Connection Management
- **`launch_chrome_debug()`** - Launch Chrome with debugging enabled
- **`connect_to_chrome(port, host)`** - Connect to running Chrome instance
- **`get_chrome_tabs(connection_id)`** - List available browser tabs
- **`get_chrome_debug_info(connection_id)`** - Get comprehensive debug info

### Console Log Monitoring
- **`start_console_monitoring(tab_id, connection_id)`** - Begin monitoring console output
- **`get_console_logs(tab_id, connection_id, limit)`** - Retrieve captured logs
- **`clear_console_logs(tab_id, connection_id)`** - Clear log history

### JavaScript Execution & Debugging
- **`execute_javascript(code, tab_id, connection_id)`** - Run JavaScript in Chrome tab
- **`set_breakpoint(url, line_number, tab_id, connection_id, condition)`** - Set debugging breakpoints

## 📋 Example Workflows

### Debug a Web Application

1. **Start Chrome with debugging:**
   ```
   "Launch Chrome with debugging enabled"
   ```

2. **Navigate to your application** (in the Chrome window that opens)

3. **Connect and find your tab:**
   ```
   "Connect to Chrome and show me the available tabs"
   ```

4. **Start monitoring:**
   ```
   "Start monitoring console logs for tab [TAB_ID]"
   ```

5. **Use your application** and generate some console output

6. **Check the logs:**
   ```
   "Get the latest 20 console logs"
   ```

### Execute JavaScript for Testing

```
"Execute JavaScript: document.title" in tab [TAB_ID]
"Execute JavaScript: console.log('Hello from MCP!')" in tab [TAB_ID]
"Execute JavaScript: localStorage.getItem('myKey')" in tab [TAB_ID]
```

### Set Breakpoints for Debugging

```
"Set a breakpoint at line 25 in http://localhost:3000/app.js for tab [TAB_ID]"
"Set a conditional breakpoint where x > 10 at line 30 in main.js for tab [TAB_ID]"
```

## 🔧 Configuration

### Default Settings
- **Chrome Debug Port:** 9222
- **Chrome Debug Host:** localhost
- **Profile Directory:** `./chrome-debug-profile`

### Manual Chrome Launch
If you prefer to launch Chrome manually:

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=./chrome-debug-profile

# Linux
google-chrome \
  --remote-debugging-port=9222 \
  --user-data-dir=./chrome-debug-profile

# Windows
chrome.exe \
  --remote-debugging-port=9222 \
  --user-data-dir=./chrome-debug-profile
```

## 📊 Console Log Format

Console logs captured by the MCP server include:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "tab_id": "tab-id-here",
  "connection_id": "localhost:9222",
  "level": "log|info|warn|error",
  "text": "Console message text",
  "source": "console-api|javascript|network",
  "line": 42,
  "column": 15,
  "url": "http://localhost:3000/app.js",
  "stack_trace": [...],
  "raw_message": {...}
}
```

## 🎯 Use Cases

### Frontend Development
- Monitor React/Vue/Angular console output
- Debug API calls and responses
- Track user interactions and state changes
- Catch JavaScript errors in real-time

### Testing & Quality Assurance
- Automated testing with console log verification
- Performance monitoring through console timing
- Error tracking and debugging
- User journey analysis

### DevOps & Monitoring
- Production error monitoring
- Performance metrics collection
- User behavior analytics
- Real-time application health checks

## 🚨 Troubleshooting

### Chrome Won't Connect
1. Ensure Chrome is running with `--remote-debugging-port=9222`
2. Check if port 9222 is available: `lsof -i :9222`
3. Try connecting manually: `curl http://localhost:9222/json`

### No Console Logs Appearing
1. Verify console monitoring is started for the correct tab
2. Check that the tab is active and generating logs
3. Refresh the page to trigger new console output
4. Use `execute_javascript` to manually generate test logs

### Permission Issues
1. Ensure Chrome profile directory is writable
2. Check Chrome security settings
3. Try launching Chrome with `--disable-web-security` for testing

### Tab ID Issues
1. Use `get_chrome_tabs()` to get current tab IDs
2. Tab IDs change when pages are refreshed
3. Monitor multiple tabs by starting monitoring for each

## 🔒 Security Considerations

- Chrome debug mode disables some security features
- Only use debug mode for development/testing
- The debug profile is isolated from your main Chrome profile
- Never run debug mode with sensitive data in production

## 🤖 AI Assistant Examples

Ask your AI assistant in Cursor:

```
"Launch Chrome with debugging, connect to it, and start monitoring console logs for any React application tab"

"Show me all console errors from the last 5 minutes"

"Execute JavaScript to check if jQuery is loaded in the current tab"

"Set a breakpoint in my main.js file at line 150 where the user clicks submit"

"Clear all console logs and start fresh monitoring"

"What Chrome tabs are currently open and which ones have active console monitoring?"
```

## 📝 Notes

- Console logs are stored in memory and will be lost when the MCP server restarts
- Multiple tabs can be monitored simultaneously
- JavaScript execution happens in the context of the selected tab
- Breakpoints work with source maps for TypeScript/JSX debugging
- The Chrome debug profile is separate from your regular browsing profile

Happy debugging! 🐛✨ 