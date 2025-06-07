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
