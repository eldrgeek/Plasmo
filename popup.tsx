import { useState } from "react"

import "./style.css"

function IndexPopup() {
  const [data, setData] = useState("")

  const handleClick = () => {
    setData("Hello from Plasmo!")
  }

  const openOptionsPage = () => {
    chrome.runtime.openOptionsPage()
  }

  return (
    <div className="plasmo-container">
      <h2>My Plasmo Extension</h2>
      <p>Welcome to your Chrome extension built with Plasmo!</p>
      
      <div className="button-group">
        <button onClick={handleClick} className="primary-btn">
          Click Me
        </button>
        <button onClick={openOptionsPage} className="secondary-btn">
          Open Options
        </button>
      </div>
      
      {data && (
        <div className="message">
          {data}
        </div>
      )}
      
      <div className="info">
        <p>This extension demonstrates:</p>
        <ul>
          <li>React components in popup</li>
          <li>State management</li>
          <li>Chrome APIs integration</li>
          <li>Custom styling</li>
        </ul>
      </div>
    </div>
  )
}

export default IndexPopup
