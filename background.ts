import { io, Socket } from "socket.io-client"

export { }

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
    reconnectionAttempts: 5
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
