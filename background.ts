export {}

// Background script for Chrome extension
console.log("Background script loaded")

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log("Extension installed:", details.reason)
  
  // Initialize default settings
  if (details.reason === "install") {
    chrome.storage.sync.set({
      settings: {
        notifications: true,
        theme: "light",
        autoUpdate: false
      }
    })
  }
})

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
      
    default:
      sendResponse({ error: "Unknown action" })
  }
})

// Listen for tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url) {
    console.log("Tab updated:", tab.url)
    
    // You can add logic here to react to page changes
    // For example, inject content scripts or update extension state
  }
})

// Handle browser action (extension icon) clicks
chrome.action.onClicked.addListener((tab) => {
  console.log("Extension icon clicked on tab:", tab.url)
  
  // This will only trigger if no popup is defined
  // Since we have a popup, this won't normally execute
})

// Periodic background tasks (optional)
const performPeriodicTask = () => {
  console.log("Performing periodic background task")
  
  // Check settings and perform tasks based on user preferences
  chrome.storage.sync.get(["settings"], (result) => {
    const settings = result.settings || {}
    
    if (settings.autoUpdate) {
      // Perform auto-update tasks
      console.log("Auto-update is enabled")
    }
  })
}

// Run periodic task every 5 minutes (300000 ms)
setInterval(performPeriodicTask, 300000)
