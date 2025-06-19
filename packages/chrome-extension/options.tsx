import { useState, useEffect } from "react"

import "./options.css"

function OptionsIndex() {
  const [settings, setSettings] = useState({
    notifications: true,
    theme: "light",
    autoUpdate: false
  })

  useEffect(() => {
    // Load settings from Chrome storage
    chrome.storage.sync.get(["settings"], (result) => {
      if (result.settings) {
        setSettings(result.settings)
      }
    })
  }, [])

  const saveSettings = () => {
    chrome.storage.sync.set({ settings }, () => {
      console.log("Settings saved")
      // Show a success message
      const saveBtn = document.getElementById("save-btn")
      if (saveBtn) {
        saveBtn.textContent = "Saved!"
        setTimeout(() => {
          saveBtn.textContent = "Save Settings"
        }, 2000)
      }
    })
  }

  const handleChange = (key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  return (
    <div className="options-container">
      <div className="header">
        <h1>Extension Options</h1>
        <p>Configure your extension settings below</p>
      </div>

      <div className="settings-section">
        <h3>General Settings</h3>
        
        <div className="setting-item">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={settings.notifications}
              onChange={(e) => handleChange("notifications", e.target.checked)}
            />
            <span className="checkmark"></span>
            Enable notifications
          </label>
          <p className="setting-description">
            Receive notifications when important events occur
          </p>
        </div>

        <div className="setting-item">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={settings.autoUpdate}
              onChange={(e) => handleChange("autoUpdate", e.target.checked)}
            />
            <span className="checkmark"></span>
            Auto-update content
          </label>
          <p className="setting-description">
            Automatically refresh content in the background
          </p>
        </div>

        <div className="setting-item">
          <label className="select-label">
            Theme:
            <select
              value={settings.theme}
              onChange={(e) => handleChange("theme", e.target.value)}
              className="theme-select"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">System</option>
            </select>
          </label>
          <p className="setting-description">
            Choose your preferred color theme
          </p>
        </div>
      </div>

      <div className="actions">
        <button id="save-btn" onClick={saveSettings} className="save-btn">
          Save Settings
        </button>
      </div>
    </div>
  )
}

export default OptionsIndex
