# Auto-Click Automation for Bolt.new

This project includes Chrome Debug Protocol (CDP) automation to automatically click the Input Prompt button after extension reloads.

## Prerequisites

1. **Chrome with Debug Port**: Launch Chrome with debugging enabled
   ```bash
   ./launch-chrome-debug.sh
   ```

2. **MCP Server Running**: Ensure the MCP server is running for CDP communication
   ```bash
   python3 mcp_server.py
   ```

3. **Bolt.new Tab Open**: Have bolt.new open in a Chrome tab

4. **Extension Loaded**: Make sure your Plasmo extension is loaded and visible on bolt.new

## Usage Options

### Option 1: Simple One-Time Click
```bash
python3 auto_click_simple.py
```
- Connects to Chrome immediately
- Waits 1 second for extension to load
- Clicks the "📝 Input Prompt" button once
- Perfect for testing or manual triggering

### Option 2: Full Automation with Monitoring
```bash
python3 auto_click_automation.py
```
Then choose:
- **1** = Single click test (same as simple version)
- **2** = Continuous monitoring mode (watches for extension reloads)

## How It Works

1. **Chrome Connection**: Uses CDP to connect to Chrome debug port (9222)
2. **Tab Detection**: Finds the bolt.new tab automatically
3. **UI Detection**: Waits for the Plasmo automation UI to load
4. **Button Click**: Finds and clicks the "📝 Input Prompt" button via JavaScript injection
5. **Success Feedback**: Reports success/failure with clear messages

## Typical Workflow

1. Start Chrome with debug port: `./launch-chrome-debug.sh`
2. Open bolt.new in Chrome
3. Load your Plasmo extension (should show automation UI)
4. Run auto-click script: `python3 auto_click_simple.py`
5. Watch as it automatically clicks the Input Prompt button after 1 second

## Troubleshooting

### "No bolt.new tab found"
- Make sure bolt.new is open in Chrome
- Ensure Chrome was launched with debug port enabled

### "Automation UI not found"
- Extension may not be loaded or enabled
- Try refreshing the bolt.new page
- Check that Plasmo extension is working manually first

### "Failed to connect to Chrome"
- Ensure Chrome is running with `./launch-chrome-debug.sh`
- Check that port 9222 is not blocked
- Make sure MCP server can access Chrome debug API

### "Button is disabled"
- Extension may still be loading
- Try waiting a bit longer or running the script again
- Check browser console for any extension errors

## Integration with Development Workflow

This automation is particularly useful for:
- **Testing**: Quickly trigger automation after extension reloads
- **Development**: Auto-start workflows when testing changes
- **Demonstration**: Show automated functionality without manual clicks
- **CI/CD**: Integrate into automated testing pipelines

## Technical Details

- Uses Chrome Debug Protocol (CDP) WebSocket API
- JavaScript injection for DOM manipulation
- Robust error handling and status reporting
- Minimal dependencies (just our existing MCP server)
- Cross-platform compatibility (macOS, Linux, Windows) 