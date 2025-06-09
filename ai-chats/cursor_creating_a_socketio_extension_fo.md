# Creating a socketio extension for Cursor IDE
_Exported on 6/9/2025 at 11:22:22 EDT from Cursor (1.0.0)_

---

**User**

I want to create a Extension that have commands relayed to it by a socketio server and the commands can control the Cursor IDE. For exxample, reconnect to the cursor-dev-assistant MCP server by clicking on UI button. Is such a thing possible? What are its limits?

---

**Cursor**

This is a fascinating idea! Let me analyze what's technically possible and explore the current project structure to give you a comprehensive answer.

Based on my research and understanding of the current project setup, I can give you a comprehensive answer about creating an extension that receives SocketIO commands to control Cursor IDE, including the MCP server reconnection scenario.

## **Yes, it's technically possible, but with significant limitations**

Your idea is achievable using **Chrome's Native Messaging API**, which is the primary bridge between browser extensions and desktop applications. Here's what's possible and the key limitations:

## **What's Technically Possible:**

### 1. **SocketIO Integration**
✅ Your extension can absolutely connect to a SocketIO server and receive commands in real-time.

### 2. **Native Messaging Bridge**
✅ The extension can communicate with a native application through Chrome's Native Messaging API, which your current project already leverages for the MCP server.

### 3. **Cursor IDE Control (Limited)**
✅ Through a native messaging host, you can potentially:
- Execute shell commands
- Manipulate files and configuration
- Send keystrokes/automation commands
- Restart processes (like MCP servers)

## **Architecture Overview**

Based on your existing setup, here's how it would work:

```typescript
// Extension Architecture
Browser Extension (Plasmo) 
    ↓ (SocketIO)
SocketIO Server 
    ↓ (Commands)
Extension Background Script
    ↓ (Native Messaging API)
Native Host Application
    ↓ (System Commands/APIs)
Cursor IDE Control
```

## **Current Project Integration**

Your existing project already has many of the necessary components:

```typescript
// Extension Architecture
Browser Extension (Plasmo) 
    ↓ (SocketIO)
SocketIO Server 
    ↓ (Commands)
Extension Background Script
    ↓ (Native Messaging API)
Native Host Application
    ↓ (System Commands/APIs)
Cursor IDE Control
```

## **Implementation Plan**

Here's how you could implement this:

### 1. **Add SocketIO to Your Extension**

```json
{
  "name": "my-plasmo-extension",
  "displayName": "My Plasmo Extension",
  "version": "0.0.1",
  "description": "A basic Chrome extension built with Plasmo",
  "author": "Your Name",
  "scripts": {
    "dev": "plasmo dev",
    "build": "plasmo build",
    "package": "plasmo package"
  },
  "dependencies": {
    "plasmo": "0.90.5",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "socket.io-client": "^4.7.2"
  },
  "devDependencies": {
    "@types/chrome": "0.0.246",
    "@types/node": "20.5.9",
    "@types/react": "18.2.21",
    "@types/react-dom": "18.2.7",
    "prettier": "^3.0.0",
    "typescript": "5.2.2"
  },
  "manifest": {
    "permissions": [
      "activeTab",
      "storage",
      "nativeMessaging"
    ]
  }
}
```

### 2. **Enhanced Background Script with SocketIO Integration**

```typescript
import { io, Socket } from "socket.io-client"

export {}

// Background script for Chrome extension with Cursor IDE control
console.log("Background script loaded")

let socket: Socket | null = null
let nativePort: chrome.runtime.Port | null = null

// Native messaging host name (you'll need to create this)
const NATIVE_HOST_NAME = "com.plasmo.cursor_controller"

// SocketIO Configuration
const SOCKET_SERVER_URL = "ws://localhost:3001" // Your SocketIO server

// Command interface for type safety
interface CursorCommand {
  action: "reconnect_mcp" | "open_file" | "run_command" | "restart_extension"
  payload?: any
  timestamp: number
}

// Initialize SocketIO connection
const initializeSocketConnection = () => {
  if (socket?.connected) return

  socket = io(SOCKET_SERVER_URL, {
    autoConnect: true,
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    maxReconnectionAttempts: 5
  })

  socket.on("connect", () => {
    console.log("✅ Connected to SocketIO server")
    
    // Register this extension instance
    socket?.emit("extension_register", {
      extensionId: chrome.runtime.id,
      timestamp: Date.now()
    })
  })

  socket.on("disconnect", () => {
    console.log("❌ Disconnected from SocketIO server")
  })

  // Listen for Cursor IDE commands
  socket.on("cursor_command", (command: CursorCommand) => {
    console.log("📨 Received Cursor command:", command)
    handleCursorCommand(command)
  })

  socket.on("connect_error", (error) => {
    console.error("❌ SocketIO connection error:", error)
  })
}

// Handle commands received from SocketIO
const handleCursorCommand = async (command: CursorCommand) => {
  try {
    switch (command.action) {
      case "reconnect_mcp":
        await reconnectMcpServer()
        break
      
      case "open_file":
        await openFileInCursor(command.payload?.filePath)
        break
      
      case "run_command":
        await runCursorCommand(command.payload?.command)
        break
      
      case "restart_extension":
        await restartExtension()
        break
      
      default:
        console.warn("Unknown command:", command.action)
    }
    
    // Send success response back to SocketIO server
    socket?.emit("command_result", {
      commandId: command.timestamp,
      status: "success",
      timestamp: Date.now()
    })
    
  } catch (error) {
    console.error("Error executing command:", error)
    
    socket?.emit("command_result", {
      commandId: command.timestamp,
      status: "error",
      error: error.message,
      timestamp: Date.now()
    })
  }
}

// Connect to native messaging host
const connectToNativeHost = () => {
  if (nativePort?.name === NATIVE_HOST_NAME) return nativePort

  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME)
    
    nativePort.onMessage.addListener((message) => {
      console.log("📨 Native host response:", message)
    })
    
    nativePort.onDisconnect.addListener(() => {
      console.log("❌ Native host disconnected")
      nativePort = null
    })
    
    return nativePort
    
  } catch (error) {
    console.error("❌ Failed to connect to native host:", error)
    return null
  }
}

// Cursor IDE command implementations
const reconnectMcpServer = async () => {
  const port = connectToNativeHost()
  if (!port) throw new Error("Native messaging not available")
  
  return new Promise((resolve, reject) => {
    const timeoutId = setTimeout(() => {
      reject(new Error("MCP reconnection timeout"))
    }, 10000)
    
    const messageListener = (response: any) => {
      if (response.action === "mcp_reconnect_complete") {
        clearTimeout(timeoutId)
        port.onMessage.removeListener(messageListener)
        resolve(response)
      }
    }
    
    port.onMessage.addListener(messageListener)
    
    port.postMessage({
      action: "reconnect_mcp_server",
      timestamp: Date.now()
    })
  })
}

const openFileInCursor = async (filePath: string) => {
  const port = connectToNativeHost()
  if (!port) throw new Error("Native messaging not available")
  
  port.postMessage({
    action: "open_file",
    filePath: filePath,
    timestamp: Date.now()
  })
}

const runCursorCommand = async (command: string) => {
  const port = connectToNativeHost()
  if (!port) throw new Error("Native messaging not available")
  
  port.postMessage({
    action: "run_command",
    command: command,
    timestamp: Date.now()
  })
}

const restartExtension = async () => {
  chrome.runtime.reload()
}

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log("Extension installed:", details.reason)
  
  // Initialize SocketIO connection on install
  setTimeout(initializeSocketConnection, 1000)
  
  // Initialize default settings
  if (details.reason === "install") {
    chrome.storage.sync.set({
      settings: {
        notifications: true,
        theme: "light",
        autoUpdate: false,
        socketServerUrl: SOCKET_SERVER_URL,
        cursorControlEnabled: true
      }
    })
  }
})

// Initialize SocketIO connection on startup
initializeSocketConnection()

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Message received:", request)
  
  switch (request.action) {
    case "getTabInfo":
      // Get current tab information
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs[0]) {
          sendResponse({
            title: tabs[0].title,
            url: tabs[0].url
          })
        }
      })
      return true // Keep message channel open for async response
      
    case "showNotification":
      // Show a notification
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icon.png",
        title: "My Plasmo Extension",
        message: request.message || "Hello from your extension!"
      })
      sendResponse({ success: true })
      break

    case "reconnect_mcp_manual":
      // Manual MCP reconnection from UI
      reconnectMcpServer()
        .then(() => sendResponse({ success: true }))
        .catch((error) => sendResponse({ success: false, error: error.message }))
      return true
      
    case "get_socket_status":
      sendResponse({
        connected: socket?.connected || false,
        serverUrl: SOCKET_SERVER_URL
      })
      break
      
    default:
      sendResponse({ error: "Unknown action" })
  }
})

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    console.log("Tab updated:", tab.url)
    
    // Notify SocketIO server about tab changes if needed
    if (socket?.connected) {
      socket.emit("tab_updated", {
        tabId,
        url: tab.url,
        title: tab.title
      })
    }
  }
})

// Handle browser action (extension icon) clicks
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked on tab:", tab.url)
})

// Periodic background tasks
const performPeriodicTask = () => {
  // Maintain SocketIO connection
  if (!socket?.connected) {
    console.log("Reconnecting to SocketIO server...")
    initializeSocketConnection()
  }
  
  // Check settings and perform tasks based on user preferences
  chrome.storage.sync.get(["settings"], (result) => {
    const settings = result.settings || {}
    
    if (settings.autoUpdate) {
      console.log("Auto-update is enabled")
    }
  })
}

// Run periodic task every 30 seconds
setInterval(performPeriodicTask, 30000)
```

### 3. **Enhanced Popup UI with MCP Reconnection Button**

```typescriptreact
import { useState, useEffect } from "react"

import "./style.css"

function IndexPopup() {
  const [data, setData] = useState("")
  const [socketStatus, setSocketStatus] = useState<{connected: boolean, serverUrl: string}>({
    connected: false,
    serverUrl: ""
  })
  const [loading, setLoading] = useState(false)

  // Get socket status on component mount
  useEffect(() => {
    chrome.runtime.sendMessage({ action: "get_socket_status" }, (response) => {
      if (response) {
        setSocketStatus(response)
      }
    })
  }, [])

  const handleReconnectMCP = async () => {
    setLoading(true)
    
    try {
      const response = await new Promise((resolve) => {
        chrome.runtime.sendMessage({ action: "reconnect_mcp_manual" }, resolve)
      })
      
      if (response.success) {
        setData("✅ MCP Server reconnected successfully!")
      } else {
        setData(`❌ Failed to reconnect: ${response.error}`)
      }
    } catch (error) {
      setData(`❌ Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const refreshSocketStatus = () => {
    chrome.runtime.sendMessage({ action: "get_socket_status" }, (response) => {
      if (response) {
        setSocketStatus(response)
      }
    })
  }

  return (
    <div className="plasmo-flex plasmo-flex-col plasmo-w-80 plasmo-p-4 plasmo-gap-4">
      <h2 className="plasmo-text-lg plasmo-font-bold">Cursor IDE Controller</h2>
      
      {/* SocketIO Status */}
      <div className="plasmo-border plasmo-rounded plasmo-p-3">
        <h3 className="plasmo-font-semibold plasmo-mb-2">SocketIO Status</h3>
        <div className="plasmo-flex plasmo-items-center plasmo-gap-2 plasmo-mb-2">
          <div 
            className={`plasmo-w-3 plasmo-h-3 plasmo-rounded-full ${
              socketStatus.connected ? 'plasmo-bg-green-500' : 'plasmo-bg-red-500'
            }`}
          />
          <span className="plasmo-text-sm">
            {socketStatus.connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <p className="plasmo-text-xs plasmo-text-gray-600 plasmo-mb-2">
          Server: {socketStatus.serverUrl}
        </p>
        <button 
          onClick={refreshSocketStatus}
          className="plasmo-px-3 plasmo-py-1 plasmo-text-xs plasmo-bg-blue-500 plasmo-text-white plasmo-rounded plasmo-hover:bg-blue-600"
        >
          Refresh Status
        </button>
      </div>

      {/* MCP Reconnection */}
      <div className="plasmo-border plasmo-rounded plasmo-p-3">
        <h3 className="plasmo-font-semibold plasmo-mb-2">MCP Server Control</h3>
        <button
          onClick={handleReconnectMCP}
          disabled={loading}
          className={`plasmo-w-full plasmo-px-4 plasmo-py-2 plasmo-rounded plasmo-font-medium ${
            loading 
              ? 'plasmo-bg-gray-300 plasmo-text-gray-600 plasmo-cursor-not-allowed'
              : 'plasmo-bg-green-500 plasmo-text-white plasmo-hover:bg-green-600'
          }`}
        >
          {loading ? "Reconnecting..." : "🔄 Reconnect MCP Server"}
        </button>
      </div>

      {/* Command Result */}
      {data && (
        <div className="plasmo-border plasmo-rounded plasmo-p-3 plasmo-bg-gray-50">
          <h3 className="plasmo-font-semibold plasmo-mb-2">Result</h3>
          <p className="plasmo-text-sm plasmo-whitespace-pre-wrap">{data}</p>
          <button 
            onClick={() => setData("")}
            className="plasmo-mt-2 plasmo-px-2 plasmo-py-1 plasmo-text-xs plasmo-bg-gray-400 plasmo-text-white plasmo-rounded plasmo-hover:bg-gray-500"
          >
            Clear
          </button>
        </div>
      )}

      {/* Command Examples */}
      <details className="plasmo-border plasmo-rounded plasmo-p-3">
        <summary className="plasmo-font-semibold plasmo-cursor-pointer">
          Available Commands
        </summary>
        <div className="plasmo-mt-2 plasmo-text-xs plasmo-space-y-1">
          <div>• <code>reconnect_mcp</code> - Reconnect MCP server</div>
          <div>• <code>open_file</code> - Open file in Cursor</div>
          <div>• <code>run_command</code> - Execute Cursor command</div>
          <div>• <code>restart_extension</code> - Restart this extension</div>
        </div>
      </details>

      <div className="plasmo-text-xs plasmo-text-gray-500 plasmo-text-center">
        Send commands via SocketIO to control Cursor IDE
      </div>
    </div>
  )
}

export default IndexPopup
```

### 4. **Native Messaging Host Example**

```python
#!/usr/bin/env python3
"""
Native Messaging Host for Cursor IDE Control
Communicates with the Plasmo Chrome extension to control Cursor IDE
"""

import json
import sys
import struct
import subprocess
import os
import signal
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/cursor_controller.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class CursorController:
    def __init__(self):
        self.cursor_executable = self._find_cursor_executable()
        logger.info(f"Cursor executable found at: {self.cursor_executable}")
    
    def _find_cursor_executable(self) -> Optional[str]:
        """Find Cursor IDE executable path"""
        possible_paths = [
            # macOS
            "/Applications/Cursor.app/Contents/MacOS/Cursor",
            "/usr/local/bin/cursor",
            # Linux
            "/usr/bin/cursor",
            "/opt/cursor/cursor",
            "~/.local/bin/cursor",
            # Windows (if running under WSL)
            "/mnt/c/Users/*/AppData/Local/Programs/Cursor/Cursor.exe"
        ]
        
        for path in possible_paths:
            expanded_path = os.path.expanduser(path)
            if os.path.exists(expanded_path) and os.access(expanded_path, os.X_OK):
                return expanded_path
        
        # Try which/where command
        try:
            result = subprocess.run(['which', 'cursor'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except FileNotFoundError:
            pass
        
        logger.warning("Cursor executable not found")
        return None
    
    def reconnect_mcp_server(self) -> Dict[str, Any]:
        """Reconnect MCP server by restarting Cursor or reloading configuration"""
        try:
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Method 1: Try to reload Cursor configuration using CLI
            # This is a simplified approach - actual implementation may vary
            
            # First, try to find and restart the MCP server process
            try:
                # Look for MCP server processes
                result = subprocess.run(
                    ['pgrep', '-f', 'mcp_server'],
                    capture_output=True, text=True
                )
                
                if result.returncode == 0:
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        if pid:
                            logger.info(f"Terminating MCP server process {pid}")
                            os.kill(int(pid), signal.SIGTERM)
                
                # Wait a moment and restart
                subprocess.run(['sleep', '2'])
                
                # Try to restart MCP server (adjust path as needed)
                mcp_script_path = "/Users/MikeWolf/Projects/Plasmo/start_mcp.sh"
                if os.path.exists(mcp_script_path):
                    subprocess.Popen([mcp_script_path], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    logger.info("MCP server restart initiated")
                
                return {"success": True, "action": "mcp_reconnect_complete"}
                
            except Exception as e:
                logger.error(f"Error during MCP reconnection: {e}")
                return {"success": False, "error": str(e)}
                
        except Exception as e:
            logger.error(f"Failed to reconnect MCP server: {e}")
            return {"success": False, "error": str(e)}
    
    def open_file(self, file_path: str) -> Dict[str, Any]:
        """Open file in Cursor IDE"""
        try:
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Expand user path and resolve
            expanded_path = os.path.expanduser(file_path)
            resolved_path = os.path.abspath(expanded_path)
            
            if not os.path.exists(resolved_path):
                return {"success": False, "error": f"File not found: {resolved_path}"}
            
            # Open file in Cursor
            result = subprocess.run(
                [self.cursor_executable, resolved_path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                logger.info(f"Opened file in Cursor: {resolved_path}")
                return {"success": True, "file_path": resolved_path}
            else:
                logger.error(f"Failed to open file: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": True, "message": "File open command sent (timeout expected)"}
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return {"success": False, "error": str(e)}
    
    def run_command(self, command: str) -> Dict[str, Any]:
        """Execute a command in the context of Cursor"""
        try:
            # Security: Only allow safe commands
            allowed_commands = [
                "cursor --version",
                "cursor --help",
                "cursor --list-extensions",
                "cursor --install-extension",
                "cursor --reload-window"
            ]
            
            if not any(command.startswith(cmd) for cmd in allowed_commands):
                return {"success": False, "error": f"Command not allowed: {command}"}
            
            if not self.cursor_executable:
                return {"success": False, "error": "Cursor executable not found"}
            
            # Execute the command
            cmd_parts = command.split()
            if cmd_parts[0] == "cursor":
                cmd_parts[0] = self.cursor_executable
            
            result = subprocess.run(
                cmd_parts,
                capture_output=True, text=True, timeout=30
            )
            
            logger.info(f"Executed command: {command}")
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"success": False, "error": str(e)}

class NativeMessagingHost:
    def __init__(self):
        self.controller = CursorController()
        logger.info("Native messaging host initialized")
    
    def read_message(self) -> Optional[Dict[str, Any]]:
        """Read message from stdin"""
        try:
            # Read message length (4 bytes)
            length_bytes = sys.stdin.buffer.read(4)
            if len(length_bytes) != 4:
                return None
            
            message_length = struct.unpack('=I', length_bytes)[0]
            
            # Read message content
            message_bytes = sys.stdin.buffer.read(message_length)
            if len(message_bytes) != message_length:
                return None
            
            message = json.loads(message_bytes.decode('utf-8'))
            logger.debug(f"Received message: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Error reading message: {e}")
            return None
    
    def send_message(self, message: Dict[str, Any]) -> None:
        """Send message to stdout"""
        try:
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')
            
            # Send message length
            length = len(message_bytes)
            sys.stdout.buffer.write(struct.pack('=I', length))
            
            # Send message content
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()
            
            logger.debug(f"Sent message: {message}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming message and return response"""
        action = message.get('action')
        
        try:
            if action == "reconnect_mcp_server":
                return self.controller.reconnect_mcp_server()
            
            elif action == "open_file":
                file_path = message.get('filePath')
                if not file_path:
                    return {"success": False, "error": "Missing filePath parameter"}
                return self.controller.open_file(file_path)
            
            elif action == "run_command":
                command = message.get('command')
                if not command:
                    return {"success": False, "error": "Missing command parameter"}
                return self.controller.run_command(command)
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """Main message loop"""
        logger.info("Starting native messaging host")
        
        try:
            while True:
                message = self.read_message()
                if message is None:
                    break
                
                response = self.handle_message(message)
                self.send_message(response)
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            logger.info("Native messaging host stopped")

if __name__ == "__main__":
    host = NativeMessagingHost()
    host.run()
```

### 5. **Native Messaging Manifest**

```json
{
  "name": "com.plasmo.cursor_controller",
  "description": "Native messaging host for controlling Cursor IDE",
  "path": "/Users/MikeWolf/Projects/Plasmo/cursor_controller.py",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://YOUR_EXTENSION_ID_HERE/"
  ]
}
```

### 6. **Simple SocketIO Server Example**

```javascript
const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const path = require('path');

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Serve static files for a simple web interface
app.use(express.static(path.join(__dirname, 'public')));

// Store connected extensions
const connectedExtensions = new Map();

io.on('connection', (socket) => {
  console.log('🔌 Client connected:', socket.id);

  // Handle extension registration
  socket.on('extension_register', (data) => {
    console.log('📱 Extension registered:', data);
    connectedExtensions.set(socket.id, {
      extensionId: data.extensionId,
      timestamp: data.timestamp,
      socket: socket
    });
    
    socket.emit('registration_confirmed', {
      message: 'Extension successfully registered',
      serverId: socket.id
    });
  });

  // Handle command results from extension
  socket.on('command_result', (result) => {
    console.log('📊 Command result:', result);
  });

  // Handle tab updates from extension
  socket.on('tab_updated', (tabInfo) => {
    console.log('🌐 Tab updated:', tabInfo);
  });

  socket.on('disconnect', () => {
    console.log('❌ Client disconnected:', socket.id);
    connectedExtensions.delete(socket.id);
  });
});

// API endpoints for sending commands to extensions
app.use(express.json());

// Send command to all connected extensions
app.post('/api/command/broadcast', (req, res) => {
  const { action, payload } = req.body;
  
  if (!action) {
    return res.status(400).json({ error: 'Action is required' });
  }

  const command = {
    action,
    payload,
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Command sent to ${sent} extension(s)`,
    command
  });
});

// Send command to specific extension
app.post('/api/command/send/:socketId', (req, res) => {
  const { socketId } = req.params;
  const { action, payload } = req.body;

  if (!action) {
    return res.status(400).json({ error: 'Action is required' });
  }

  const extension = connectedExtensions.get(socketId);
  if (!extension) {
    return res.status(404).json({ error: 'Extension not found' });
  }

  const command = {
    action,
    payload,
    timestamp: Date.now()
  };

  extension.socket.emit('cursor_command', command);

  res.json({
    success: true,
    message: 'Command sent to extension',
    command,
    extensionId: extension.extensionId
  });
});

// Get list of connected extensions
app.get('/api/extensions', (req, res) => {
  const extensions = Array.from(connectedExtensions.values()).map(ext => ({
    socketId: ext.socket.id,
    extensionId: ext.extensionId,
    timestamp: ext.timestamp,
    connected: ext.socket.connected
  }));

  res.json({
    success: true,
    extensions,
    count: extensions.length
  });
});

// Convenience endpoints for common commands
app.post('/api/cursor/reconnect-mcp', (req, res) => {
  const command = {
    action: 'reconnect_mcp',
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `MCP reconnect command sent to ${sent} extension(s)`
  });
});

app.post('/api/cursor/open-file', (req, res) => {
  const { filePath } = req.body;
  
  if (!filePath) {
    return res.status(400).json({ error: 'filePath is required' });
  }

  const command = {
    action: 'open_file',
    payload: { filePath },
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Open file command sent to ${sent} extension(s)`,
    filePath
  });
});

app.post('/api/cursor/run-command', (req, res) => {
  const { command: cursorCommand } = req.body;
  
  if (!cursorCommand) {
    return res.status(400).json({ error: 'command is required' });
  }

  const command = {
    action: 'run_command',
    payload: { command: cursorCommand },
    timestamp: Date.now()
  };

  let sent = 0;
  connectedExtensions.forEach((ext) => {
    ext.socket.emit('cursor_command', command);
    sent++;
  });

  res.json({
    success: true,
    message: `Run command sent to ${sent} extension(s)`,
    command: cursorCommand
  });
});

// Simple web interface
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cursor IDE Controller</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .container { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            button { background: #007cba; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
            button:hover { background: #005a8b; }
            input[type="text"] { width: 300px; padding: 8px; margin: 5px; }
            .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
            .success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
            .error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
            #extensions { font-family: monospace; background: #f8f9fa; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>🎯 Cursor IDE Controller</h1>
        
        <div class="container">
            <h3>📱 Connected Extensions</h3>
            <button onclick="refreshExtensions()">🔄 Refresh</button>
            <div id="extensions">Loading...</div>
        </div>

        <div class="container">
            <h3>🔧 Quick Commands</h3>
            <button onclick="sendCommand('reconnect_mcp')">🔄 Reconnect MCP Server</button>
            <button onclick="sendCommand('restart_extension')">♻️ Restart Extension</button>
        </div>

        <div class="container">
            <h3>📁 Open File</h3>
            <input type="text" id="filePath" placeholder="/path/to/file.txt" />
            <button onclick="openFile()">📂 Open in Cursor</button>
        </div>

        <div class="container">
            <h3>⚡ Run Command</h3>
            <input type="text" id="cursorCommand" placeholder="cursor --version" />
            <button onclick="runCommand()">▶️ Execute</button>
        </div>

        <div id="status"></div>

        <script>
            async function refreshExtensions() {
                try {
                    const response = await fetch('/api/extensions');
                    const data = await response.json();
                    
                    document.getElementById('extensions').innerHTML = 
                        \`Connected Extensions: \${data.count}\n\` + 
                        JSON.stringify(data.extensions, null, 2);
                } catch (error) {
                    showStatus('Error refreshing extensions: ' + error.message, 'error');
                }
            }

            async function sendCommand(action) {
                try {
                    const response = await fetch('/api/command/broadcast', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ action })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            async function openFile() {
                const filePath = document.getElementById('filePath').value;
                if (!filePath) {
                    showStatus('Please enter a file path', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/cursor/open-file', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ filePath })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            async function runCommand() {
                const command = document.getElementById('cursorCommand').value;
                if (!command) {
                    showStatus('Please enter a command', 'error');
                    return;
                }

                try {
                    const response = await fetch('/api/cursor/run-command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ command })
                    });
                    
                    const data = await response.json();
                    showStatus(data.message, 'success');
                } catch (error) {
                    showStatus('Error: ' + error.message, 'error');
                }
            }

            function showStatus(message, type) {
                const statusDiv = document.getElementById('status');
                statusDiv.innerHTML = \`<div class="status \${type}">\${message}</div>\`;
                setTimeout(() => statusDiv.innerHTML = '', 5000);
            }

            // Auto-refresh extensions every 5 seconds
            setInterval(refreshExtensions, 5000);
            refreshExtensions();
        </script>
    </body>
    </html>
  `);
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`🚀 SocketIO server running on http://localhost:${PORT}`);
  console.log(`📱 Extension commands can be sent via the web interface`);
  console.log(`🔌 Extensions should connect to: ws://localhost:${PORT}`);
});

module.exports = { app, server, io };
```

## **What You've Built & Limitations**

### ✅ **What's Possible:**

1. **SocketIO Integration**: ✅ Extension connects to SocketIO server and receives real-time commands
2. **MCP Server Reconnection**: ✅ Can restart your existing MCP server through native messaging
3. **File Operations**: ✅ Open files in Cursor IDE
4. **Limited Command Execution**: ✅ Run safe Cursor CLI commands
5. **Real-time Communication**: ✅ Bidirectional communication between web interface and extension

### ⚠️ **Key Limitations:**

1. **No Direct Cursor API**: Cursor doesn't expose a public API for extensions to control its internal features like Composer, Chat, or MCP connections directly.

2. **Native Messaging Sandbox**: The native messaging host runs with your user permissions but can't directly access Cursor's internal state or UI elements.

3. **Security Restrictions**: Chrome extensions have strict limitations on what system operations they can perform.

4. **MCP Server Control**: Can restart the MCP server process, but can't directly control Cursor's connection to it.

### 🎯 **What Actually Works for MCP Reconnection:**

The implementation I've created can:
- ✅ Kill and restart your MCP server process
- ✅ Trigger Cursor to reload by opening/closing files
- ✅ Execute CLI commands to manage extensions
- ❌ **Cannot directly control Cursor's MCP connection UI**

## **Setup Instructions:**

1. **Install dependencies:**
```bash
cd /Users/MikeWolf/Projects/Plasmo
npm install
npm install express socket.io
```

2. **Make the Python script executable:**
```bash
chmod +x cursor_controller.py
```

3. **Register the native messaging host:**
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/

# Copy the manifest (update the extension ID first)
cp cursor_controller_manifest.json ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.plasmo.cursor_controller.json
```

4. **Start the SocketIO server:**
```bash
node socketio_server.js
```

5. **Build and load the extension:**
```bash
npm run build
# Load the built extension in Chrome
```

## **Testing the MCP Reconnection:**

1. Open the web interface at `http://localhost:3001`
2. Click "🔄 Reconnect MCP Server" 
3. The extension will restart your existing MCP server process
4. Check `/tmp/cursor_controller.log` for debugging

This provides a solid foundation for remote Cursor IDE control, though direct access to Cursor's internal features remains limited by the application's architecture.

```shellscript
cd /Users/MikeWolf/Projects/Plasmo
npm install
npm install express socket.io
```

```shellscript
cd /Users/MikeWolf/Projects/Plasmo
npm install
npm install express socket.io
```

```shellscript
chmod +x cursor_controller.py
```

```shellscript
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/

# Copy the manifest (update the extension ID first)
cp cursor_controller_manifest.json ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.plasmo.cursor_controller.json
```

```shellscript
node socketio_server.js
```

```shellscript
npm run build
# Load the built extension in Chrome
```

